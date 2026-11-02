"""Authenticated archive assessment. Exit 2 preserves unresolved science; 1 is error.

Never executes archived code. Extraction is confined to a fresh output directory.
The supplied STEP49 metadata is the authentication trust anchor, not a new API attestation.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import subprocess
import sys
import zipfile

COMMITS = ('4177d52f1ac68f869147c2e3e02e1f8b876546d0',
           '8d87244eb07b7ff6e811596728441aee8b2fd618')
MAX_ARCHIVE = 256 * 1024**2
MAX_MEMBER = 128 * 1024**2
MAX_TOTAL = 512 * 1024**2
MAX_ENTRIES = 4096
REPO = Path(__file__).resolve().parents[1]
OBJECT_STORES = []


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError('Duplicate JSON key: ' + k)
            result[k] = v
        return result
    return json.loads(data.decode('utf-8-sig'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def safe(name, *, directory=False):
    """Validate original ZIP spelling before parsing; never repair unsafe names.

    A directory may have exactly one terminal slash. Both path grammars are
    checked explicitly, independently of the operating system running this code.
    """
    if not isinstance(name, str) or not name:
        raise ValueError('Unsafe archive path: ' + repr(name))
    original_name = name
    # ZIP permits literal backslashes; Windows treats them as separators.
    # Reject the original spelling before splitting or normalizing any path.
    if chr(92) in original_name:
        raise ValueError("Unsafe ZIP member path")
    parts = (name[:-1] if directory and name.endswith('/') else name).split('/')
    if (any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in name)
            or PurePosixPath(name).is_absolute() or PureWindowsPath(name).anchor
            or any(p in ('', '.', '..') or p.endswith((' ', '.'))
                   or any(c in p for c in ':<>"|?*')
                   or re.fullmatch(r'(?i)(con|prn|aux|nul|conin\$|conout\$|com[1-9¹²³]|lpt[1-9¹²³])(\..*)?', p)
                   for p in parts)):
        raise ValueError('Unsafe archive path: ' + repr(name))
    return str(PurePosixPath(*parts))


def extraction_target(destination, name):
    """Reject existing filesystem indirection outside the extraction boundary."""
    target = destination / safe(name)
    if not target.resolve().is_relative_to(destination.resolve()):
        raise ValueError('Unsafe archive extraction target')
    return target


def archive(path, expected):
    """Read all bytes with CRC verification, limits and Windows collision checks."""
    if path.is_symlink() or path.stat().st_size > MAX_ARCHIVE:
        raise ValueError('Archive size/link rejected')
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise ValueError('Incorrect ZIP SHA256')
    members, identities, spellings, total = {}, set(), {}, 0
    # Parse the exact bytes authenticated above, not a second read of the path.
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        entries = z.infolist()
        if len(entries) > MAX_ENTRIES:
            raise ValueError('Archive entry limit')
        # Preflight every original name before normalizing any member path.
        # orig_filename preserves the spelling read from the central directory;
        # filename may already have been changed by ZipInfo on Windows.
        # Validate the serialized spelling for files and directories alike;
        # a fixture must preserve that spelling in both ZIP filename records.
        for entry in entries:
            original_name = entry.orig_filename
            if chr(92) in original_name:
                raise ValueError("Unsafe ZIP member path")
        validated_entries = []
        for entry in entries:
            original_name = entry.orig_filename
            name = safe(original_name, directory=entry.is_dir())
            if entry.orig_filename != entry.filename:
                raise ValueError('Unsafe malformed archive name')
            validated_entries.append((entry, name))
        # Consume only names validated from their original central-directory
        # spelling. No member content is opened until every name passes.
        for entry, name in validated_entries:
            key = name.casefold()
            if key in identities:
                raise ValueError('Duplicate internal path')
            identities.add(key)
            components = name.split('/')
            for i in range(1, len(components) + 1):
                prefix = '/'.join(components[:i])
                prior = spellings.setdefault(prefix.casefold(), prefix)
                if prior != prefix:
                    raise ValueError('Duplicate case-insensitive path component')
            mode = entry.external_attr >> 16
            if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                raise ValueError('Symbolic link/special file rejected')
            if ((stat.S_ISDIR(mode) and not entry.is_dir())
                    or (stat.S_ISREG(mode) and entry.is_dir())
                    or (entry.is_dir() and entry.file_size)):
                raise ValueError('Malformed directory entry')
            total += entry.file_size
            if (entry.file_size > MAX_MEMBER or total > MAX_TOTAL or entry.flag_bits & 1
                    or entry.file_size > max(1, entry.compress_size) * 1000):
                raise ValueError('Archive parsing bound/encryption rejected')
            with z.open(entry) as stream:
                data = stream.read(MAX_MEMBER + 1)
            if len(data) != entry.file_size:
                raise ValueError('Truncated/oversized member')
            if not entry.is_dir():
                members[name] = data
        file_keys = {n.casefold() for n in members}
        for name in identities:
            if any('/'.join(name.split('/')[:i]) in file_keys
                   for i in range(1, len(name.split('/')))):
                raise ValueError('File/directory collision')
    return members


def seals(members):
    result = []
    for name, data in members.items():
        if name.split('/')[-1] not in ('manifest.json', 'input-sha256.json',
                                      'input-manifest.json', 'output-manifest.json'):
            continue
        value = decode(data)
        base = name.rpartition('/')[0]
        records = []
        if isinstance(value, dict):
            mapping = value.get('outputs', value)
            for target, expected in mapping.items():
                if isinstance(expected, dict) and name.endswith('input-manifest.json'):
                    for relative, seal in expected.items():
                        if isinstance(seal, str) and re.fullmatch('[0-9a-f]{64}', seal):
                            records.append(dict(path=target+'/'+relative, expected=seal,
                                                status='EXTERNAL_REFERENCE'))
                    continue
                if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
                    continue
                safe(target)
                key = base + '/' + target if base else target
                records.append(dict(path=key, expected=expected,
                    status='MISSING' if key not in members else
                    'MATCH' if digest(members[key]) == expected else 'MISMATCH'))
        result.append(dict(path=name, records=records,
                           status='VERIFIED' if records and all(r['status'] == 'MATCH' for r in records)
                           else 'UNRESOLVED'))
    return result


def git(*args):
    result = subprocess.run(['git', *args], cwd=REPO, capture_output=True)
    if result.returncode and args and args[0] == 'cat-file':
        for store in OBJECT_STORES:
            probe = subprocess.run(['git', '--git-dir='+str(store), *args],
                                   cwd=REPO, capture_output=True)
            if not probe.returncode:
                return probe
    return result


def recover_objects(output):
    """Fetch exact objects into an isolated store; never writes checkout Git metadata."""
    attempts = []
    missing = [c for c in COMMITS if git('cat-file', '-e', c+'^{commit}').returncode]
    if not missing:
        return attempts
    store = output/'historical-source.git'
    init = subprocess.run(['git', 'init', '--bare', str(store)], capture_output=True)
    if init.returncode:
        return [dict(status='UNAVAILABLE', error=init.stderr.decode(errors='replace'))]
    OBJECT_STORES.append(store)
    for commit in missing:
        try:
            result = subprocess.run(['git', '--git-dir='+str(store), 'fetch', '--no-tags',
                'https://github.com/Nejatbakhsh-y/stellarator-robust-magnetic-optimization.git',
                commit], capture_output=True, timeout=30)
            attempts.append(dict(commit=commit, returncode=result.returncode,
                                 stderr=result.stderr.decode(errors='replace')))
        except subprocess.TimeoutExpired:
            attempts.append(dict(commit=commit, status='NETWORK_TIMEOUT'))
    return attempts


def source(members, run):
    result = []
    for name, raw in members.items():
        if name.split('/')[-1] not in ('source-sha256.json', 'source_sha256.json'):
            continue
        record = decode(raw)
        base = name.rpartition('/')[0]
        env = (base + '/' if base else '') + 'environment.json'
        head = record.get('head')
        mapping = record.get('sha256')
        if mapping is None:
            mapping = record
            head = decode(members[env]).get('head') if env in members else None
        rows = []
        for path, expected in mapping.items():
            safe(path)
            available = bool(re.fullmatch('[0-9a-f]{40}', head or ''))
            obj = git('cat-file', 'blob', head + ':' + path) if available else None
            rows.append(dict(path=path, expected=expected,
                status='UNAVAILABLE' if obj is None or obj.returncode else
                'MATCH' if digest(obj.stdout) == expected else 'MISMATCH'))
            if obj is None or obj.returncode:
                comparison = git('cat-file', 'blob', COMMITS[0]+':'+path)
                rows[-1]['branch_byte_comparison'] = (
                    'UNAVAILABLE' if comparison.returncode else
                    'SAME_BYTES' if digest(comparison.stdout) == expected else 'DIFFERENT_BYTES')
                rows[-1]['comparison_commit'] = COMMITS[0]
        result.append(dict(record=name, recorded_commit=head, run_commit=run['source_sha'],
            association='EXACT' if head == run['source_sha'] else
            'HISTORICAL_MERGE_ASSOCIATION' if {head, run['source_sha']} == set(COMMITS)
            else 'CONFLICT', files=rows))
    return result


def numerical(members):
    """Fresh diagnostics; explicit reuse of transport and independent scalar arithmetic."""
    captures = []
    for name, raw in members.items():
        if name.split('/')[-1] != 'inputs.json':
            continue
        data = decode(raw)
        if data.get('schema') != 'production-upstream-v1':
            captures.append(dict(path=name, status='UNSUPPORTED_INPUT_SCHEMA'))
            continue
        try:
            import numpy as np
            from scipy.optimize import lsq_linear
            import phase2d_step40_validation as transport
            import phase2d_step46_independent as independent
            a = transport.reconstruct(data)
            rows, vectors = {}, {}
            scale = data['config']['imax_A']
            for case in ('dense', 'row3', 'row4'):
                support = data['cases'][case].get('support', list(range(24)))
                M, y = a[case+'_M'], a[case+'_y']
                fit = lsq_linear(M, y, method='trf', lsq_solver='exact',
                                 bounds=(-1, 1), tol=1e-12, max_iter=1000)
                fresh = np.zeros(24)
                fresh[support] = fit.x * scale
                saved = a[case+'_x'] * scale
                vectors[case] = (saved.tolist(), fresh.tolist())
                cert = independent.certificate(M.tolist(), y.tolist(), fit.x.tolist())
                rows[case] = dict(success=bool(fit.success), support=support,
                    M_sha256=digest(M.astype('<f8').tobytes()),
                    y_sha256=digest(y.astype('<f8').tobytes()), certificate=cert,
                    saved_certificate=independent.certificate(M.tolist(), y.tolist(),
                                                               a[case+'_x'][support].tolist()),
                    condition=float(np.linalg.cond(M)),
                    decimal_reference={str(d): independent.reference(M.tolist(), y.tolist(), d)
                                       for d in (60, 90)})
            recovery = {}
            for case, failed in (('row3', 3), ('row4', 6)):
                if data['cases'][case]['failed'] != failed:
                    raise ValueError('Fault identity')
                recovery[case] = independent.intervention(
                    a['fine_A'].tolist(), a['fine_b'].tolist(), a['fine_weights'].tolist(),
                    vectors['dense'][0], vectors[case][0], vectors['dense'][1], vectors[case][1], failed)
            captures.append(dict(path=name, input_sha256=digest(raw), status='EXECUTED',
                                 solver=rows, recovery=recovery,
                                 field_scope='Captured full-grid matrix; independent geometry not recomputed'))
        except ImportError as exc:
            captures.append(dict(path=name, status='ENVIRONMENT_UNAVAILABLE', error=str(exc)))
        except (ValueError, KeyError) as exc:
            captures.append(dict(path=name, status='SCIENTIFIC_OR_INPUT_FAILURE', error=str(exc)))
    return captures


def assess(root, manifest, output):
    auth, provenance, calculations, historical = [], [], [], []
    seen, paths, digests = set(), set(), set()
    for run in manifest['runs']:
        for item in run['artifacts']:
            row = dict(run_id=run['run_id'], artifact_id=item['id'], name=item['name'], file=item['file'])
            try:
                key = item['id']
                if key in seen:
                    raise ValueError('Duplicate archive identity')
                seen.add(key)
                expected = item['github_sha256'].removeprefix('sha256:')
                if item['file'].casefold() in paths or expected in digests:
                    raise ValueError('Duplicate archive path or digest identity')
                paths.add(item['file'].casefold())
                digests.add(expected)
                if expected != item['verified_sha256']:
                    raise ValueError('Conflicting metadata digests')
                path = root / safe(item['file'])
                if not path.resolve().is_relative_to(root.resolve()):
                    raise ValueError('Archive root escape')
                members = archive(path, expected)
                row.update(zip_sha256=expected, archive_authentication='MATCH_STEP49_GITHUB_DIGEST',
                           zip_integrity='PASS', members={k: digest(v) for k, v in members.items()},
                           internal_manifests=seals(members))
                row['internal_manifest_status'] = ('PRESENT' if row['internal_manifests']
                                                   else 'MISSING')
                destination = extraction_target(output, 'authenticated-members/' + str(key))
                for name, raw in members.items():
                    target = extraction_target(destination, name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target = extraction_target(destination, name)
                    with target.open('xb') as stream:
                        stream.write(raw)
                    if digest(target.read_bytes()) != digest(raw):
                        raise RuntimeError('Extracted-file integrity failure')
                row['extracted_file_integrity'] = 'PASS'
                provenance.append(dict(artifact_id=key, sources=source(members, run)))
                calculations.append(dict(artifact_id=key, captures=numerical(members)))
                for name, raw in members.items():
                    if name.endswith('.json') and any(s in name.lower() for s in
                            ('comparison', 'status', 'causal-attribution', 'historical')):
                        historical.append(dict(artifact_id=key, path=name, sha256=digest(raw),
                                               original=decode(raw)))
            except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
                row.update(assessment='REJECTED', error=str(exc))
            auth.append(row)
    index = {}
    for row in auth:
        for name, seal in row.get('members', {}).items():
            index.setdefault((row['run_id'], seal), []).append(
                dict(artifact_id=row['artifact_id'], path=name))
    for row in auth:
        for manifest_record in row.get('internal_manifests', []):
            for record in manifest_record['records']:
                if record['status'] in ('MISSING', 'EXTERNAL_REFERENCE'):
                    candidates = index.get((row['run_id'], record['expected']), [])
                    record['same_run_digest_candidates'] = candidates
                    record['content_recovery'] = 'EXACT_DIGEST_PRESENT' if candidates else 'MISSING'
                    record['path_association'] = 'NOT_PROVEN_BY_DIGEST_ALONE'
    return auth, provenance, dict(fresh=calculations, historical_preserved=historical,
        cross_platform='NO_FRESH_CONTROLLED_MULTI_ENVIRONMENT_EXECUTION',
        unique_root_cause='NOT_ESTABLISHED')


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def main(argv=None):
    p = argparse.ArgumentParser(__doc__)
    for name in ('archive-root', 'manifest', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args(argv)
    root, manifest_path, output = args.archive_root.resolve(), args.manifest.resolve(), args.output.resolve()
    if output.exists() or output.is_relative_to(root) or root.is_relative_to(output):
        print('Require new output without input overlap', file=sys.stderr)
        return 1
    output.mkdir(parents=True, exist_ok=False)
    try:
        manifest = decode(manifest_path.read_bytes())
        retrieval = recover_objects(output)
        auth, sources, numeric = assess(root, manifest, output)
        commits = []
        for c in COMMITS:
            raw = git('cat-file', 'commit', c)
            verified = not raw.returncode and hashlib.sha1(
                b'commit '+str(len(raw.stdout)).encode()+b'\0'+raw.stdout).hexdigest() == c
            commits.append(dict(commit=c, object_verified=verified,
                                object_text=raw.stdout.decode(errors='replace') if verified else None))
        blockers = ['Fresh multi-environment controlled reproduction not established',
                    'Historical scientific failures remain failures',
                    'Independent full-grid Biot-Savart geometry regeneration incomplete',
                    'Unique numerical root cause not established',
                    'README checkpoint acceptance gates not certified by this assessment']
        if len(auth) != 71 or any(r.get('assessment') == 'REJECTED' for r in auth):
            blockers.append('Original archive inventory incomplete or rejected')
        if not all(c['object_verified'] for c in commits):
            blockers.append('Exact historical commit object unavailable')
        write(output/'archive-authentication.json', dict(manifest_sha256=digest(manifest_path.read_bytes()),
              trust_anchor='Supplied STEP49 GitHub artifact metadata; no fresh API attestation', archives=auth))
        write(output/'source-provenance.json', dict(commits=commits, artifacts=sources,
              retrieval_attempts=retrieval, step49_source_records=manifest.get('source_commits'),
              merge_identity_policy='Distinct commits even when tree/workflow blobs coincide'))
        write(output/'numerical-comparisons.json', numeric)
        write(output/'remaining-blockers.json', blockers)
        write(output/'status.json', dict(assessment='COMPLETED_WITH_UNRESOLVED_REQUIREMENTS',
              scientific_comparison='FAIL', production_acceptance='FAIL', overall_scientific_status='INCOMPLETE',
              exit_code=2, archive_count=len(auth), rtol=1e-11, atol=1e-13,
              refinement_limit=1e-4, denominator_guard_T=1e-15,
              output_sha256={n: digest((output/n).read_bytes()) for n in
              ('archive-authentication.json', 'source-provenance.json', 'numerical-comparisons.json', 'remaining-blockers.json')}))
        return 2
    except Exception as exc:
        write(output/'status.json', dict(assessment='UNEXPECTED_EXECUTION_ERROR', error=repr(exc), exit_code=1))
        return 1


if __name__ == '__main__':
    sys.exit(main())
