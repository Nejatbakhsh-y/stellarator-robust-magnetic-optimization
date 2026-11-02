"""Read-only STEP48 provenance review. No scientific acceptance is inferred."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

COMMITS = ('4177d52f1ac68f869147c2e3e02e1f8b876546d0',
           '8d87244eb07b7ff6e811596728441aee8b2fd618')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError('Duplicate JSON key: '+k)
            result[k] = v
        return result
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, capture_output=True)


def valid_path(name):
    return (isinstance(name, str) and bool(name) and '\\' not in name and ':' not in name
            and not PurePosixPath(name).is_absolute()
            and all(p not in ('', '.', '..') for p in name.split('/')))


@lru_cache(maxsize=None)
def blob(repo, commit, name):
    """Resolve object identity before hashing raw stdout; never hash failed output."""
    if not re.fullmatch('[0-9a-f]{40}', commit or ''):
        return dict(status='SOURCE_IDENTITY_INCONSISTENT', error='Invalid commit identity')
    check = git(repo, 'cat-file', '-e', commit+'^{commit}')
    if check.returncode:
        return dict(status='SOURCE_COMMIT_UNAVAILABLE', error=check.stderr.decode(errors='replace'))
    if not valid_path(name):
        return dict(status='MISSING_EVIDENCE', error='Incorrect or unsafe source path')
    obj = git(repo, 'rev-parse', '--verify', commit+':'+name)
    if obj.returncode:
        return dict(status='MISSING_EVIDENCE', error='Path absent in exact commit')
    oid = obj.stdout.decode('ascii').strip()
    raw = git(repo, 'cat-file', 'blob', oid)
    if raw.returncode:
        return dict(status='MISSING_EVIDENCE', object=oid, error='Blob retrieval failed')
    return dict(status='VERIFIED_MATCH', object=oid, actual_sha256=sha(raw.stdout),
                byte_count=len(raw.stdout), crlf_sha256=sha(raw.stdout.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')),
                lf_sha256=sha(raw.stdout.replace(b'\r\n', b'\n')))


def check_source(repo, commit, name, recorded, expected=None, candidates=()):
    result = dict(recorded_commit=commit, recorded_sha256=recorded, path=name,
                  expected_run_commit=expected, **blob(repo, commit, name))
    result['identity_status'] = ('SOURCE_IDENTITY_INCONSISTENT' if expected and expected != commit
                                 else 'VERIFIED_MATCH')
    if 'actual_sha256' in result:
        result['status'] = 'VERIFIED_MATCH' if recorded == result['actual_sha256'] else 'VERIFIED_MISMATCH'
        result['encoding_only_match'] = (result['status'] == 'VERIFIED_MISMATCH' and
                                        recorded in (result['crlf_sha256'], result['lf_sha256']))
    result['matching_other_commits'] = []
    if result['status'] != 'VERIFIED_MATCH':
        for other in candidates:
            probe = blob(repo, other, name)
            if probe.get('actual_sha256') == recorded:
                result['matching_other_commits'].append(dict(commit=other, object=probe['object']))
    result['stale_manifest'] = ('SUPPORTED_BY_OTHER_COMMIT' if result['matching_other_commits']
                                else 'NOT_ESTABLISHED')
    return result


def snapshot(root, exclude=None):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in sorted(root.rglob('*'))
            if p.is_file() and (exclude is None or not p.is_relative_to(exclude))}


def classify_numerical(record):
    solver = record.get('solver', {})
    recovery = record.get('recovery', {})
    complete = (set(solver) == {'dense', 'row3', 'row4'} and
                all(v.get('success') is True and v.get('M_sha256') and v.get('y_sha256')
                    and v.get('saved_certificate') and v.get('fresh_certificate')
                    and all(v.get('decimal_QR', {}).get(d, {}).get('status') == 'INTERIOR_REFERENCE'
                            for d in ('60', '90')) for v in solver.values())
                and set(recovery) == {'row3', 'row4'})
    probes = record.get('independent_geometry_probes', [])
    return dict(independent_calculation='COMPLETE_RECORDED' if complete else 'INCOMPLETE',
                solver_reconstruction='COMPLETE_RECORDED' if complete else 'INCOMPLETE',
                recovery={k: ('PASS' if recovery[k].get('pass_original_tolerance') is True else
                              'FAIL' if recovery[k].get('pass_original_tolerance') is False else 'INCOMPLETE')
                          for k in recovery},
                geometry=('FAIL' if any(p.get('agrees') is False for p in probes) else
                          'SAMPLED_PASS_FULL_GRID_INCOMPLETE' if probes and all(p.get('agrees') is True for p in probes)
                          else 'INCOMPLETE'), geometry_probes=len(probes),
                original_saved_ratio_binding='INCOMPLETE', artifact_origin='MISSING_EVIDENCE')


def archive_status(paths, metadata=None):
    # Metadata is deliberately not an authentication authority for absent bytes.
    return 'MISSING_EVIDENCE' if not paths else 'INCOMPLETE_UNBOUND_ARCHIVES'


def final_status():
    return dict(source_provenance='INCOMPLETE', artifact_authentication='MISSING_EVIDENCE',
                independent_numerical_execution='INCOMPLETE', recovery_ratio_validation='FAIL',
                solver_reproducibility='INCOMPLETE', unique_numerical_root_cause='INCONCLUSIVE',
                scientific_comparison='FAIL', production_acceptance='FAIL',
                overall_scientific_status='INCOMPLETE')


def audit(repo, evidence, assessment):
    prior = load(assessment)
    head = git(repo, 'rev-parse', 'HEAD').stdout.decode().strip()
    history = git(repo, 'log', '--format=%H', '--all', '--', '.github/workflows/ci.yml')
    candidates = list(dict.fromkeys([*COMMITS, head, *history.stdout.decode().splitlines()]))
    out = final_status()
    out.update(head=head, assessment_sha256=sha(assessment.read_bytes()),
               commit_objects={c: dict(available=git(repo, 'cat-file', '-e', c+'^{commit}').returncode == 0,
                                      workflow=blob(repo, c, '.github/workflows/ci.yml'))
                               for c in (*COMMITS, head)}, sources=[], numerical={},
               workflow_history=history.stdout.decode().splitlines(),
               shallow=git(repo, 'rev-parse', '--is-shallow-repository').stdout.decode().strip())
    manifest = assessment.parent/'manifest.json'
    out['assessment_seal'] = ('VERIFIED_MATCH' if manifest.is_file() and
        load(manifest).get(assessment.name) == out['assessment_sha256'] else 'MISSING_EVIDENCE'
        if not manifest.is_file() else 'VERIFIED_MISMATCH')
    out['assessment_origin_authentication'] = 'MISSING_EVIDENCE'
    for run in sorted(evidence.glob('run-*')):
        identity = load(run/'run.json').get('head_sha')
        for path in sorted(run.rglob('*.json')):
            if path.name not in ('source-sha256.json', 'source_sha256.json'):
                continue
            rec = load(path)
            if path.name == 'source_sha256.json':
                rec = dict(head=load(path.parent/'environment.json').get('head'), sha256=rec)
            for name, digest in rec.get('sha256', {}).items():
                out['sources'].append(dict(record=path.relative_to(evidence).as_posix(),
                    **check_source(repo, rec.get('head'), name, digest, identity, candidates)))
    for key, record in prior.get('numerical', {}).items():
        # Historical JSON uses Windows separators; normalize only evidence locations.
        parts = key.replace('\\', '/').split('/')
        if not valid_path('/'.join(parts)):
            raise ValueError('Unsafe capture key')
        capture = evidence.joinpath(*parts)
        item = classify_numerical(record)
        target = capture/'inputs.json'
        seal = capture/'input-sha256.json'
        item['input_authentication'] = ('VERIFIED_MATCH' if target.is_file() and seal.is_file()
            and load(seal).get('inputs.json') == sha(target.read_bytes()) == record.get('input_sha256')
            else 'MISSING_EVIDENCE' if not target.is_file() or not seal.is_file() else 'VERIFIED_MISMATCH')
        matching = [s for s in out['sources'] if s['record'] == '/'.join(parts)+'/source-sha256.json']
        item['source_authentication'] = ('VERIFIED_MATCH' if matching and all(
            s['status'] == 'VERIFIED_MATCH' and s['identity_status'] == 'VERIFIED_MATCH' for s in matching)
            else 'INCOMPLETE')
        out['numerical'][key] = item
    out['independent_numerical_execution'] = 'COMPLETE_RECORDED_LOCAL_REEXECUTION_UNAVAILABLE'
    if not out['numerical'] or any(v['independent_calculation'] == 'INCOMPLETE' for v in out['numerical'].values()):
        out['independent_numerical_execution'] = 'INCOMPLETE'
    out['cross_capture'] = {k: dict(identical_solver_inputs=all(
        v.get('identical_M') is True and v.get('identical_y') is True
        for v in r.get('current_vectors', {}).values()) if r.get('current_vectors') else False,
        unique_solver_cause='INCONCLUSIVE') for k, r in prior.get('cross_capture', {}).items()}
    out['original_zip_count'] = len(list(evidence.rglob('*.zip')))
    out['artifact_authentication'] = archive_status(list(evidence.rglob('*.zip')))
    out['remaining_blockers'] = ['Unavailable older commit and original source artifact bytes',
        'Conflicting upstream run and nested source identities', 'Original ZIP authentication and missing STEP45 artifacts',
        'Failed row3/row4 comparisons; original saved-result binding incomplete',
        'Full-grid geometry, solver conditioning and identical-input controlled cause attribution incomplete',
        'Existing Python 3.11 runtime unavailable; regression and full README gates unverified']
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    for name in ('evidence', 'assessment', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    evidence, assessment, output = (p.resolve() for p in (args.evidence, args.assessment, args.output))
    if output.exists() or not output.is_relative_to(repo/'results') or output.is_relative_to(evidence):
        raise ValueError('Require fresh results directory outside original evidence')
    before = snapshot(evidence)
    output.mkdir(parents=True, exist_ok=False)
    try:
        result = audit(repo, evidence, assessment)
        result['historical_preserved'] = before == snapshot(evidence)
        if not result['historical_preserved']:
            raise RuntimeError('Historical evidence changed')
        code = 2  # Original scientific requirements remain unresolved.
    except Exception as exc:
        result = dict(execution_status='UNEXPECTED_FAILURE', error=repr(exc),
                      historical_preserved=before == snapshot(evidence))
        code = 1
    (output/'status.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return code


if __name__ == '__main__':
    sys.exit(main())
