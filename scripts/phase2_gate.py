"""Failure-sensitive saved-evidence gate; PARTIAL never means continuum certified."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from stellarator_robust.analysis import paired_summary
from stellarator_robust.model import benchmark
from stellarator_robust.peak import coordinates
from stellarator_robust.validation import independent_circle
from stellarator_robust.evidence import file_hash

parser = argparse.ArgumentParser()
parser.add_argument('--output', default='results/phase2')
args = parser.parse_args(); out = Path(args.output)
failed = []
regression_passed = False


def check(condition, name):
    if not condition:
        failed.append(name)


try:
    manifest = json.loads((out/'manifest.json').read_text())
    check(bool(manifest), 'nonempty manifest')
    required = list(Path('src').rglob('*.py'))+list(Path('tests').rglob('*.py'))
    required += list(Path('scripts').glob('*.py'))+list(Path('configs').glob('*.json'))
    required += [out/'study.json', out/'commands.json', out/'reproducibility.json',
                 out/'regression/results.json', out/'regression/audit.json', out/'training_audit.json']
    check(all(p.as_posix() in manifest for p in required), 'manifest completeness')
    for name, digest in manifest.items():
        p = Path(name)
        check(p.is_file() and file_hash(p) == digest, 'hash '+name)
    d = json.loads((out/'study.json').read_text())
    def finite(value):
        if isinstance(value, dict):
            return all(finite(v) for v in value.values())
        if isinstance(value, list):
            return all(finite(v) for v in value)
        return not isinstance(value, float) or np.isfinite(value)
    check(finite(d), 'all finite')
    check(d['units'] == 'm, A, T, rad', 'SI units')
    check(d['config']['holdout_seed'] not in d['config']['training_seeds'], 'disjoint seeds')
    frozen = out/'phase1_input.json'
    check(d['phase1_sha256'] == hashlib.sha256(frozen.read_bytes()).hexdigest(), 'Phase 1 hash')
    check(json.loads(frozen.read_text()) == json.loads(Path('results/quick/results.json').read_text()),
          'historical input unchanged')
    commands = json.loads((out/'commands.json').read_text())
    check(len(commands) == 7 and all(r['returncode'] == 0 for r in commands), 'executed regression commands')
    audit = json.loads((out/'regression/audit.json').read_text())
    check(audit['status'] == 'PASS' and all(audit['gates'].values()), 'Phase 1 independent gates')
    check(audit['results_sha256'] == hashlib.sha256((out/'regression/results.json').read_bytes()).hexdigest(), 'audit result link')
    repeat = json.loads((out/'reproducibility.json').read_text())
    check(repeat['status'] == 'PASS' and repeat['full_phase1_repeat'] and repeat['full_phase2_repeat']
          and repeat['phase1_historical_match'], 'full repeat records')
    check(repeat['study_sha256'] == hashlib.sha256((out/'study.json').read_bytes()).hexdigest(), 'repeat result link')
    check(repeat['regression_sha256'] == audit['results_sha256'], 'regression repeat link')
    training = json.loads((out/'training_audit.json').read_text())
    check(training['status'] == 'PASS' and all(training['checks'].values()), 'training and numerical dual audit')
    check(training['study_sha256'] == repeat['study_sha256'], 'training audit result link')
    negative = json.loads((out/'failure_sensitivity.json').read_text())
    check(negative['status'] == 'PASS' and negative['actual_child_returncode'] == 1,
          'gate rejects invalid evidence')
    check(negative['study_sha256'] == repeat['study_sha256'], 'negative test result link')
    regression_passed = (audit['status'] == 'PASS' and all(audit['gates'].values())
                         and repeat['full_phase1_repeat'] and repeat['phase1_historical_match']
                         and all(r['returncode'] == 0 for r in commands[:6]))
    expected_trials = {(s, n) for s in d['config']['training_seeds'] for n in d['config']['training_counts']}
    check(len(d['trials']) == len(expected_trials) and
          {(t['train_seed'], t['count']) for t in d['trials']} == expected_trials, 'all predeclared trials')
    check(len(d['scenarios']['holdout']) == d['config']['holdout_count'], 'holdout count')
    for i, t in enumerate(d['trials']):
        stats = paired_summary(t['nominal_rms_T'], t['robust_rms_T'],
                               d['config']['bootstrap_seed'], d['config']['bootstrap_resamples'])
        check(stats == t['paired'], f'paired recomputation {i}')
        check(len(t['nominal_rms_T']) == d['config']['holdout_count'], f'paired count {i}')
        check(len(d['scenarios']['training'][f"{t['train_seed']}/{t['count']}"]) == t['count'], f'train count {i}')
        check(t['solver']['success'] and t['solver']['violation'] <= 1e-8, f'solver {i}')
        check(t['objective'] <= t['zero_objective']+1e-8, f'trivial feasible objective {i}')
        for name in ['nominal_current_A', 'robust_current_A']:
            I = np.array(t[name]); check(np.max(abs(I)) <= 3000+1e-8, f'bounds {i}')
            check(np.all(I[np.setdiff1d(np.arange(len(I)), t['support'])] == 0), f'support {i}')
    phase1 = json.loads(Path('results/quick/results.json').read_text())
    c = phase1['metadata']['config']
    _, _, _, coils, error, _ = benchmark(3, 3, 512, c['nphi'], c['ntheta'])
    for name, p in d['peaks'].items():
        check(p['certificate'] is False and p['search']['certificate'] is False, 'no certificate '+name)
        xyz, normals = coordinates([p['search']['best']['angles_rad']])
        B, estimate = independent_circle(xyz, error, 1500.)
        for coil, I in zip(coils, phase1['currents_A'][name]):
            v, e = independent_circle(xyz, coil, I); B += v; estimate += e
        value = float(np.sum(B*normals))
        check(abs(value-p['smooth_reference_T']) < 1e-12, 'independent candidate '+name)
        check(estimate/max(abs(value), 1e-30) < 1e-8, 'quadrature estimate '+name)
        configured = next(r for r in p['segment_refinement'] if r['segments'] == 512)
        check(configured['relative_error'] < 1e-4, 'unchanged segment gate '+name)
except Exception as exc:
    failed.append(type(exc).__name__+': '+str(exc))
record = {'software_status': 'FAIL' if failed else 'PASS',
          'phase1_regression_status': 'PASS' if regression_passed else 'FAIL',
          'scientific_status': 'BLOCKED' if failed else 'PARTIAL', 'failed_checks': failed,
          'limitations': ['No global supremum certificate', 'Only IID synthetic scenarios',
                          'Current-budget matching and correlated errors pending; dual check is numerical'],
          'study_sha256': hashlib.sha256((out/'study.json').read_bytes()).hexdigest() if (out/'study.json').exists() else None}
(out/'gate.json').write_text(json.dumps(record, indent=2)); print(json.dumps(record, indent=2))
raise SystemExit(1 if failed else 0)
