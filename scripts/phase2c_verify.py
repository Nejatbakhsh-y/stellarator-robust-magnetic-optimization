"""Execute the versioned benchmark and repeats, preserving every legacy byte."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from stellarator_robust.phase2c import VERSION, sha, load, preserve_previous, environment, attest, pair
from stellarator_robust.analysis import paired_summary
from stellarator_robust.model import benchmark
from stellarator_robust.peak import coordinates
from stellarator_robust.validation import independent_circle
from stellarator_robust.evidence import file_hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='results/phase2c')
    args = parser.parse_args(); out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    record = dict(benchmark_version=VERSION, status='RUNNING', environment=environment(), steps=[],
                  scientific_status='PARTIAL', legacy_evidence=preserve_previous())
    def save():
        (out/'execution.json').write_text(json.dumps(record, indent=2)+'\n')
    def execute(label, command):
        start = time.monotonic()
        with (out/(label+'.log')).open('w', encoding='utf-8') as log:
            result = subprocess.run([sys.executable, *command], stdout=log, stderr=subprocess.STDOUT)
        record['steps'].append(dict(stage=label, command=['python', *command],
                                    returncode=result.returncode, seconds=time.monotonic()-start))
        save(); print(label, result.returncode, flush=True)
        if result.returncode:
            raise RuntimeError(label+' failed')
    def quick(root, prefix):
        execute(prefix+'quick', ['-m', 'stellarator_robust.cli', 'run', '--config',
                                'configs/phase2c_quick.json', '--output', str(root/'quick')])
        actual = environment(); attest(load(root/'quick/results.json')['metadata'], actual)
        return actual
    def study(root, prefix):
        execute(prefix+'study', ['scripts/phase2_study.py', '--config', 'configs/phase2c_study.json',
                                '--output', str(root/'study'), '--phase1-input', str(root/'quick/results.json')])
        actual = environment(); attest(load(root/'study/study.json'), actual)
        return actual
    save()
    try:
        execute('tests', ['-m', 'pytest', '-q'])
        execute('analytical', ['-m', 'stellarator_robust.cli', 'validate'])
        record['quick_runtime'] = quick(out, '')
        execute('outputs', ['scripts/check_outputs.py', str(out/'quick')])
        execute('independent-audit', ['scripts/audit_quick.py', str(out/'quick')])
        record['study_runtime'] = study(out, '')
        record['quick_sha256'] = sha(out/'quick/results.json')
        record['study_sha256'] = sha(out/'study/study.json'); save()
        repeat = out/'repeat'; repeat.mkdir(parents=True, exist_ok=True)
        repeated = dict(benchmark_version=VERSION, quick_runtime=quick(repeat, 'repeat-'),
                        study_runtime=study(repeat, 'repeat-'), status='DATA_READY')
        repeated.update(quick_sha256=sha(repeat/'quick/results.json'), study_sha256=sha(repeat/'study/study.json'))
        (repeat/'execution.json').write_text(json.dumps(repeated, indent=2)+'\n')
        comparison = pair(out, repeat)
        (out/'reproducibility.json').write_text(json.dumps(comparison, indent=2)+'\n')
        execute('training-audit', ['scripts/phase2_training_audit.py', '--output', str(out/'study'),
                                   '--phase1-input', str(out/'quick/results.json')])
        d = load(out/'study/study.json'); q = load(out/'quick/results.json')
        training = load(out/'study/training_audit.json'); audit = load(out/'quick/audit.json')
        assert training['status'] == 'PASS' and all(training['checks'].values())
        assert training['study_sha256'] == record['study_sha256']
        assert audit['status'] == 'PASS' and all(audit['gates'].values())
        assert audit['results_sha256'] == record['quick_sha256']
        c = q['metadata']['config']
        _, _, _, coils, error, _ = benchmark(c['nt'], c['np'], 512, c['nphi'], c['ntheta'], 'householder-v2')
        candidate_checks = {}
        for name, peak in d['peaks'].items():
            assert peak['certificate'] is False and peak['search']['certificate'] is False
            xyz, normal = coordinates([peak['search']['best']['angles_rad']])
            B, estimate = independent_circle(xyz, error, 1500.)
            for coil, amp in zip(coils, q['currents_A'][name]):
                value, err = independent_circle(xyz, coil, amp); B += value; estimate += err
            saved = peak['smooth_reference_T']; value = float(np.sum(B*normal))
            assert abs(value-saved) < 1e-12
            assert estimate/max(abs(value), 1e-30) < 1e-8
            configured = next(r for r in peak['segment_refinement'] if r['segments'] == 512)
            assert configured['relative_error'] < 1e-4
            candidate_checks[name] = dict(independent_difference_T=abs(value-saved),
                                         configured_relative_error=configured['relative_error'])
        for trial in d['trials']:
            assert paired_summary(trial['nominal_rms_T'], trial['robust_rms_T'],
                                  d['config']['bootstrap_seed'], d['config']['bootstrap_resamples']) == trial['paired']
        record['legacy_evidence'] = preserve_previous()
        gate = dict(software_status='PASS', phase1_regression_status='PASS', scientific_status='PARTIAL',
                    benchmark_version=VERSION, study_sha256=record['study_sha256'],
                    quick_sha256=record['quick_sha256'], candidate_checks=candidate_checks,
                    limitations=['Finite sampled search, no global peak certificate',
                                 'IID synthetic scenarios; no device or confinement validation'])
        (out/'gate.json').write_text(json.dumps(gate, indent=2)+'\n')
        source = list(Path('src').rglob('*.py'))+list(Path('scripts').glob('*.py'))+list(Path('tests').glob('*.py'))+list(Path('configs').glob('*.json'))+[Path('.gitattributes')]
        (out/'source_fingerprints.json').write_text(json.dumps({p.as_posix():file_hash(p) for p in sorted(source)}, indent=2)+'\n')
        record['status'] = 'PASS'
    except Exception as exc:
        record['status'] = 'FAIL'; record['error'] = str(exc)
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
