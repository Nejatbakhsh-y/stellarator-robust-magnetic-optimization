"""Fixed-current peak and predeclared paired IID holdout study; no tuning."""
import argparse
import hashlib
import json
import subprocess
import platform
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from stellarator_robust.model import benchmark, response, surface, field
from stellarator_robust.peak import grid_angles, coordinates, normal_field, local_extrema, lattice_extrema
from stellarator_robust.validation import independent_circle
from stellarator_robust.analysis import paired_summary
from stellarator_robust.uncertainty import scenarios
from stellarator_robust.optimize import baseline, robust


def run(config, output, phase1_input=None):
    cfg = json.loads(Path(config).read_text())
    source = Path(phase1_input or cfg.get('phase1_input', 'results/quick/results.json'))
    phase1 = json.loads(source.read_text())
    c = phase1['metadata']['config']
    out = Path(output); out.mkdir(parents=True, exist_ok=True)
    (out/'phase1_input.json').write_bytes(source.read_bytes())
    assert cfg['holdout_seed'] not in cfg['training_seeds']
    assert len(set(cfg['training_seeds'])) == len(cfg['training_seeds'])
    geometry = cfg.get('geometry_version', 'legacy-v1')
    p, n, w, coils, error, b = benchmark(c['nt'], c['np'], cfg['segments'], c['nphi'], c['ntheta'], geometry)
    methods = ['dense', 'matched_nominal', 'robust']
    currents = {m: np.array(phase1['currents_A'][m]) for m in methods}
    peaks = {m: {'grids': []} for m in methods}; seeds = {m: [] for m in methods}
    for nt, np_ in cfg['grids']:
        for shift in cfg['shifts']:
            angles = grid_angles(nt, np_, shift)
            xyz, normals = coordinates(angles)
            A = response(xyz, normals, coils)
            bg = np.sum(field(xyz, error, 1500.)*normals, axis=1)
            weights = 1+.25*np.cos(angles[:, 0]); weights /= weights.sum()
            for m in methods:
                r = bg+A@currents[m]; idx = int(np.argmax(abs(r)))
                seeds[m].extend(angles[np.argsort(abs(r))[-cfg['seeds_per_grid']:]].tolist())
                peaks[m]['grids'].append({'nt': nt, 'np': np_, 'shift': shift,
                    'sampled_peak_T': float(abs(r[idx])), 'angles_rad': angles[idx].tolist(),
                    'rms_T': float(np.sqrt(weights@(r*r)))})
                if (nt, np_) == tuple(cfg['grids'][-1]) and shift == .5:
                    plt.figure(); plt.imshow(r.reshape(nt, np_)*1e6, origin='lower', aspect='auto',
                        extent=[0, 2*np.pi, 0, 2*np.pi]); plt.colorbar(label='B dot n [microT]')
                    plt.xlabel('phi [rad]'); plt.ylabel('theta [rad]'); plt.tight_layout()
                    plt.savefig(out/f'peak_location_{m}.png'); plt.close()
    for m in methods:
        print('search', m, flush=True)
        evaluate = lambda a: normal_field(a, coils, currents[m], error)
        search = (lattice_extrema(evaluate, seeds[m]) if cfg.get('peak_algorithm') == 'dyadic-pattern-v2'
                  else local_extrema(evaluate, seeds[m], cfg['maxiter'], cfg['maxfev']))
        best = search['best']; angles = np.array([best['angles_rad']])
        xyz, normals = coordinates(angles)
        vector, err = independent_circle(xyz, error, 1500.)
        for coil, I in zip(coils, currents[m]):
            v, e = independent_circle(xyz, coil, I); vector += v; err += e
        reference = float(np.sum(vector*normals))
        refinement = []
        for segments in [256, 512, 1024]:
            _, _, _, cc, ee, _ = benchmark(3, 3, segments, c['nphi'], c['ntheta'], geometry)
            value = float(normal_field(angles, cc, currents[m], ee)[0])
            refinement.append({'segments': segments, 'field_T': value,
                               'absolute_error_T': abs(value-reference),
                               'relative_error': abs(value-reference)/abs(reference)})
        peaks[m].update(search=search, smooth_reference_T=reference,
                        smooth_error_estimate_T=err, segment_refinement=refinement,
                        status='UNRESOLVED', certificate=False)
    plt.figure()
    for m in methods:
        rows = peaks[m]['grids']
        plt.plot([r['nt']*r['np'] for r in rows], [r['sampled_peak_T']*1e6 for r in rows], 'o', label=m)
        plt.axhline(abs(peaks[m]['search']['best']['field_T'])*1e6, linestyle='--')
    plt.xscale('log'); plt.xlabel('surface points (three shifts each)'); plt.ylabel('observed peak [microT]')
    plt.legend(); plt.tight_layout(); plt.savefig(out/'peak_refinement.png'); plt.close()
    # Fixed support and ridge, locked holdout. No hyperparameter selection.
    support = np.flatnonzero(abs(currents['matched_nominal']) > 1e-9)
    D = response(p, n, coils)*c['imax_A']/c['bref_T']; d = b/c['bref_T']
    nominal, _ = baseline(D, d, w, c['ridge'], support)
    pv, nv, av = surface(1., .25, 2*c['nt'], 2*c['np'], .5); wv = av/av.sum()
    bv = np.sum(field(pv, error, 1500.)*nv, axis=1)
    print('holdout', cfg['holdout_count'], flush=True)
    hA, ho, hr = scenarios(pv, nv, coils, cfg['holdout_count'], cfg['holdout_seed'])
    def losses(x):
        r = bv+ho+np.einsum('smj,j->sm', hA, x*c['imax_A'])
        return np.sqrt(np.sum(wv*r*r, axis=1))
    nl = losses(nominal); trials = []; training = {}
    for seed in cfg['training_seeds']:
        for count in cfg['training_counts']:
            print('training', seed, count, flush=True)
            tA, to, tr = scenarios(p, n, coils, count, seed)
            As = tA*c['imax_A']/c['bref_T']; bs = (b+to)/c['bref_T']
            x, status = robust(As, bs, w, support, c['ridge'])
            r = np.einsum('smj,j->sm', As, x)+bs
            objective = float(np.max(np.sum(w*r*r, axis=1))+c['ridge']*(x@x))
            zero = float(np.max(np.sum(w*bs*bs, axis=1)))
            stats = paired_summary(nl, losses(x), cfg['bootstrap_seed'], cfg['bootstrap_resamples'])
            trials.append({'train_seed': seed, 'count': count, 'ridge': c['ridge'],
                'support': support.tolist(), 'nominal_current_A': (nominal*c['imax_A']).tolist(),
                'robust_current_A': (x*c['imax_A']).tolist(), 'solver': status,
                'objective': objective, 'zero_objective': zero,
                'nominal_rms_T': nl.tolist(), 'robust_rms_T': losses(x).tolist(), 'paired': stats,
                'nominal_l1_A': float(sum(abs(nominal))*c['imax_A']),
                'robust_l1_A': float(sum(abs(x))*c['imax_A'])})
            training[f'{seed}/{count}'] = tr
    plt.figure()
    for i, trial in enumerate(trials):
        mean = trial['paired']['mean_T']*1e6
        lo, hi = np.array(trial['paired']['mean_bootstrap_95_T'])*1e6
        plt.errorbar(i, mean, yerr=[[mean-lo], [hi-mean]], fmt='o')
    plt.axhline(0, color='black'); plt.xlabel('predeclared trial index'); plt.ylabel('robust minus nominal RMS [microT]')
    plt.tight_layout(); plt.savefig(out/'paired_difference.png'); plt.close()
    data = {'config': cfg, 'phase1_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'source_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()),
            'python': platform.python_version(), 'units': 'm, A, T, rad',
            'peaks': peaks, 'trials': trials, 'scenarios': {'holdout': hr, 'training': training},
            'phase1_paired': paired_summary(phase1['holdout_rms_T']['matched_nominal'], phase1['holdout_rms_T']['robust']),
            'limitations': ['No global peak certificate', 'IID synthetic errors only',
                'Current budget matching unavailable', 'No independent convex dual certificate',
                'Magnitude, support, ridge and correlated stress sweeps not executed',
                'No tuning performed; no validation cohort required; holdout used only for locked comparisons',
                'No external code or confinement validation']}
    (out/'study.json').write_text(json.dumps(data, indent=2, allow_nan=False))
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/phase2_quick.json')
    parser.add_argument('--output', default='results/phase2')
    parser.add_argument('--phase1-input')
    args = parser.parse_args(); run(args.config, args.output, args.phase1_input)
