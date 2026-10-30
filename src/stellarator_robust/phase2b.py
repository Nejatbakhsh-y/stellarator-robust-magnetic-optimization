"""Versioned Phase 2B evidence contracts; legacy evidence is never refreshed."""
import copy
import hashlib
import json
import platform
import subprocess
import importlib.metadata
from pathlib import Path
import numpy as np
from .ci_evidence import compare, compare_study, clearance_paths, runtime

VERSION = 'phase2b-householder-v2-pattern-v2'
BASE = '72c70995b7e6c2f56ec6fad4fa07fd73930e3370'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def preserve_legacy():
    hashes = {}
    for name in subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
                                         'results/quick', 'results/phase2'], text=True).splitlines():
        raw = subprocess.check_output(['git', 'cat-file', '--filters', BASE+':'+name]) if name.startswith('results/quick/') else subprocess.check_output(['git', 'show', BASE+':'+name])
        if raw != Path(name).read_bytes():
            raise AssertionError('Legacy evidence changed: '+name)
        hashes[name] = sha(name)
    return hashes


def environment():
    return dict(**runtime(), platform=platform.platform(),
                packages={p: importlib.metadata.version(p) for p in ('numpy', 'scipy', 'matplotlib', 'pytest')})


def attest(data, actual):
    for key in ('source_commit', 'source_dirty', 'python'):
        if type(data[key]) is not type(actual[key]) or data[key] != actual[key]:
            raise AssertionError('Runtime provenance mismatch: '+key)


def pair(left_root, right_root, version=VERSION, comparator=compare, study_comparator=compare_study):
    """Compare all scientific values; explicitly attest input-hash provenance.

    Worker completion is a separate gate; this function also compares a repeat
    before its parent run has completed. Cross-run callers require PASS workers.
    """
    roots = [Path(left_root), Path(right_root)]
    bundles = []
    for root in roots:
        record = load(root/'execution.json')
        if record['benchmark_version'] != version:
            raise AssertionError('Benchmark version mismatch')
        quick = load(root/'quick/results.json'); study = load(root/'study/study.json')
        if sha(root/'quick/results.json') != record['quick_sha256'] or sha(root/'study/study.json') != record['study_sha256']:
            raise AssertionError('Result hash mismatch')
        attest(quick['metadata'], record['quick_runtime']); attest(study, record['study_runtime'])
        if quick['metadata']['packages'] != record['quick_runtime']['packages']:
            raise AssertionError('Package provenance mismatch')
        if study['phase1_sha256'] != sha(root/'quick/results.json') or (root/'study/phase1_input.json').read_bytes() != (root/'quick/results.json').read_bytes():
            raise AssertionError('Phase 1 input hash/link mismatch')
        if quick['metadata']['config']['geometry_version'] != 'householder-v2' or study['config']['geometry_version'] != 'householder-v2' or study['config']['peak_algorithm'] != 'dyadic-pattern-v2':
            raise AssertionError('Incorrect numerical benchmark')
        bundles.append((quick, study, record))
    a, b = [copy.deepcopy(x[0]) for x in bundles]
    differences, excluded = [], []
    for method in a['solver_status']:
        for key in ('seconds', 'iterations'):
            if key in a['solver_status'][method]:
                for data in (a, b):
                    value = data['solver_status'][method][key]
                    if not isinstance(value, (int, float)) or isinstance(value, bool) or not np.isfinite(value) or value < 0:
                        raise AssertionError('Invalid solver trace')
                excluded.append(dict(path=f'/quick/solver_status/{method}/{key}',
                                     reference=a['solver_status'][method].pop(key), current=b['solver_status'][method].pop(key),
                                     reason='algorithmic timing/iteration trace; all currents, objectives and success/feasibility remain compared'))
    ma, mb = a.pop('metadata'), b.pop('metadata')
    expected_metadata = {'config', 'python', 'packages', 'source_commit', 'source_dirty',
                         'condition_number', 'rank', 'clearance_sampled_m', 'elapsed_seconds', 'units'}
    if ma.keys() != expected_metadata or mb.keys() != expected_metadata:
        raise AssertionError('Missing or unclassified quick metadata')
    comparator(ma['config'], mb['config'], '/quick/config', exact=True)
    for key in ('units', 'condition_number', 'rank', 'clearance_sampled_m'):
        comparator(ma[key], mb[key], '/quick/metadata/'+key, records=differences)
    for key in ('source_commit', 'source_dirty', 'python', 'packages', 'elapsed_seconds'):
        excluded.append(dict(path='/quick/metadata/'+key, reference=ma[key], current=mb[key]))
    for data in (ma, mb):
        if not np.isfinite(data['elapsed_seconds']) or data['elapsed_seconds'] < 0:
            raise AssertionError('Invalid elapsed time')
    sa, sb = [x.pop('scenarios') for x in (a, b)]
    sa = dict(holdout=sa['holdout'], training={'quick': sa['train']})
    sb = dict(holdout=sb['holdout'], training={'quick': sb['train']})
    paths = clearance_paths(sa)
    if paths != clearance_paths(sb):
        raise AssertionError('Scenario dimensions differ')
    comparator(sa, sb, '/scenarios', records=differences, exact=True, approximate_paths=paths)
    comparator(a, b, '/quick', records=differences)
    left, right = [copy.deepcopy(x[1]) for x in bundles]
    excluded.append(dict(path='/study/phase1_sha256', reference=left['phase1_sha256'], current=right['phase1_sha256'],
                         reason='actual input bytes individually hash-verified; all input scientific groups compared above'))
    left['phase1_sha256'] = right['phase1_sha256']
    result = study_comparator(left, right, actual=bundles[1][2]['study_runtime'])
    return dict(status='PASS', rtol=1e-11, atol=1e-13, quick_numeric_differences=differences,
                study_comparison=result, attested_metadata=excluded,
                reference_study_sha256=bundles[0][2]['study_sha256'], current_study_sha256=bundles[1][2]['study_sha256'])


def require_complete(root):
    root = Path(root); record = load(root/'execution.json')
    expected = ['tests', 'analytical', 'quick', 'outputs', 'independent-audit', 'study',
                'repeat-quick', 'repeat-study', 'training-audit']
    if record['status'] != 'PASS' or [s['stage'] for s in record['steps']] != expected or any(s['returncode'] for s in record['steps']):
        raise AssertionError('Worker did not complete all required stages')
    if sha(root/'study/study.json') != record['study_sha256'] or sha(root/'quick/results.json') != record['quick_sha256']:
        raise AssertionError('Worker result hash mismatch')
    gate = load(root/'gate.json'); audit = load(root/'quick/audit.json')
    training = load(root/'study/training_audit.json'); repeat = load(root/'reproducibility.json')
    if (gate['software_status'], gate['phase1_regression_status'], gate['scientific_status']) != ('PASS', 'PASS', 'PARTIAL'):
        raise AssertionError('Scientific gate failed')
    if gate['study_sha256'] != record['study_sha256'] or gate['quick_sha256'] != record['quick_sha256']:
        raise AssertionError('Gate result link mismatch')
    if audit['status'] != 'PASS' or len(audit['gates']) != 9 or not all(audit['gates'].values()) or audit['results_sha256'] != record['quick_sha256']:
        raise AssertionError('Independent audit/link failed')
    if training['status'] != 'PASS' or len(training['checks']) != 5 or not all(training['checks'].values()) or training['study_sha256'] != record['study_sha256']:
        raise AssertionError('Training audit/link failed')
    if repeat['status'] != 'PASS' or repeat['reference_study_sha256'] != record['study_sha256'] or repeat['current_study_sha256'] != sha(root/'repeat/study/study.json'):
        raise AssertionError('Repeat/link failed')
    return record


def verify_manifest(root):
    root = Path(root).resolve()
    manifest = load(root/'manifest.json')
    excluded = {'manifest.json', 'committed-reference-comparison.json'}
    expected = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
                and p.relative_to(root).as_posix() not in excluded}
    if not manifest or manifest.keys() != expected:
        raise AssertionError('Manifest completeness mismatch')
    for name, digest in manifest.items():
        path = (root/name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or sha(path) != digest:
            raise AssertionError('Manifest hash/path mismatch: '+name)
