"""Reproducible synthetic experiments; write full precision machine-readable data."""
import csv
import json
import platform
import subprocess
import time
from pathlib import Path
import importlib.metadata
import numpy as np
from .model import benchmark, surface, response, field, clearance
from .optimize import baseline, sparse, deletion_path, robust
from .uncertainty import scenarios
from .validation import convergence
from .faults import outage_offsets


def metrics(A, b, w, I, bref, threshold):
    r = b+A@I
    rms = float(np.sqrt(w@(r*r)))
    return {"rms_T": rms, "max_T": float(max(abs(r))), "normalized_rms": rms/bref,
            "normalized_max": float(max(abs(r)))/bref, "active": int(sum(abs(I)>threshold)),
            "l1_A": float(sum(abs(I))), "l2_A": float(np.linalg.norm(I)), "peak_A": float(max(abs(I)))}


def run(config, output):
    start = time.perf_counter()
    c = json.loads(Path(config).read_text()); out = Path(output); out.mkdir(parents=True, exist_ok=True)
    if c['train_seed'] == c['holdout_seed']:
        raise ValueError('Train/holdout seeds must differ')
    imax, bref, ridge = c['imax_A'], c['bref_T'], c['ridge']
    p, n, w, coils, error, b = benchmark(c['nt'], c['np'], c['segments'], c['nphi'], c['ntheta'])
    A = response(p, n, coils); D, d = A*imax/bref, b/bref
    pv, nv, av = surface(1., .25, 2*c['nt'], 2*c['np'], .5); wv = av/av.sum()
    Av = response(pv, nv, coils); bv = np.sum(field(pv, error, 1500)*nv, axis=1)
    candidates = {"zero": np.zeros(len(coils))}; statuses = {}; pareto = []
    for name, reg in [('dense', ridge), ('unregularized', 0.)]:
        candidates[name], statuses[name] = baseline(D, d, w, reg)
    for penalty in c['l1_path']:
        x, status = sparse(D, d, w, penalty, ridge)
        support = np.flatnonzero(abs(x)*imax > c['active_threshold_A'])
        refit, _ = baseline(D, d, w, ridge, support)
        name = f'l1_{penalty:g}'; candidates[name] = refit; statuses[name] = status
        pareto.append({"method": "l1_refit", "parameter": penalty, **metrics(A, b, w, refit*imax, bref, c['active_threshold_A'])})
    path = deletion_path(D, d, w, ridge)
    for k, (x, removed) in enumerate(path):
        pareto.append({"method": "delete_refit", "parameter": k, "removed_next": removed,
                       **metrics(A, b, w, x*imax, bref, c['active_threshold_A'])})
    # Fixed half-array support budget: nominal and robust exactly share allowed coils.
    nominal = path[len(coils)//2][0]; support = np.flatnonzero(abs(nominal)>1e-12)
    candidates['matched_nominal'] = nominal
    trainA, trainoff, trainrec = scenarios(p, n, coils, c['train_scenarios'], c['train_seed'], imax=imax)
    candidates['robust'], statuses['robust'] = robust(trainA*imax/bref, (b+trainoff)/bref, w, support, ridge)
    holdA, holdoff, holdrec = scenarios(pv, nv, coils, c['holdout_scenarios'], c['holdout_seed'], imax=imax)
    summary, holdout, currents = {}, {}, {}
    for name, x in candidates.items():
        I = x*imax; currents[name] = I.tolist()
        losses = np.sqrt(np.sum(wv*(bv[None, :]+holdoff+np.einsum('smj,j->sm', holdA, I))**2, axis=1))
        holdout[name] = losses.tolist()
        actual = np.array([(1+np.array(rec['gain']))*I+np.array(rec['offset_A']) for rec in holdrec])
        summary[name] = {"nominal": metrics(A, b, w, I, bref, c['active_threshold_A']),
                         "fine_grid": metrics(Av, bv, wv, I, bref, c['active_threshold_A']),
                         "holdout": {"mean_T": float(losses.mean()), "median_T": float(np.median(losses)),
                                     "q90_T": float(np.quantile(losses, .9)), "q95_T": float(np.quantile(losses, .95)),
                                     "max_T": float(losses.max())},
                         "command_bound_violation_A": float(max(0, max(abs(I))-imax)),
                         "holdout_actual_bound_violation_A": float(max(0, np.max(abs(actual))-imax))}
    faults = []
    dense = candidates['dense']
    for failed in np.flatnonzero(abs(dense)*imax>c['active_threshold_A']):
        frozen = dense.copy(); frozen[failed] = 0
        recovered, status = baseline(D, d, w, ridge, np.delete(np.arange(len(coils)), failed))
        pre, loss, post = [metrics(Av, bv, wv, x*imax, bref, c['active_threshold_A'])['rms_T'] for x in [dense, frozen, recovered]]
        # Failed actual coil has neither gain nor additive offset.
        faultoff = outage_offsets(holdA, holdoff, holdrec, failed)
        held = {}
        for label, x in [('frozen', frozen), ('recovered', recovered)]:
            r = bv+faultoff+np.einsum('smj,j->sm', holdA, x*imax)
            held[label] = np.sqrt(np.sum(wv*r*r, axis=1)).tolist()
        faults.append({"failed": int(failed), "pre_T": pre, "frozen_T": loss, "recovered_T": post,
                       "fractional_recovery": (loss-post)/(loss-pre) if abs(loss-pre)>1e-15 else None,
                       "recovered_current_A": float(recovered[failed]*imax), "holdout_rms_T": held})
    s = np.linalg.svd(np.sqrt(w)[:, None]*D, compute_uv=False)
    metadata = {"config": c, "python": platform.python_version(),
                "packages": {p: importlib.metadata.version(p) for p in ['numpy', 'scipy', 'matplotlib', 'pytest']},
                "source_commit": subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                "source_dirty": bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()),
                "condition_number": float(s[0]/s[-1]), "rank": int(np.linalg.matrix_rank(D)),
                "clearance_sampled_m": min(clearance(pv, coil) for coil in coils+[error]),
                "elapsed_seconds": time.perf_counter()-start, "units": "m, A, T"}
    data = {"metadata": metadata, "summary": summary, "currents_A": currents,
            "holdout_rms_T": holdout, "solver_status": statuses, "pareto": pareto,
            "faults": faults, "convergence": convergence(),
            "scenarios": {"train": trainrec, "holdout": holdrec}}
    (out/'results.json').write_text(json.dumps(data, indent=2, allow_nan=False))
    keys = ['method', 'parameter', 'rms_T', 'active', 'l1_A', 'peak_A']
    with (out/'pareto.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore'); writer.writeheader(); writer.writerows(pareto)
    from .plotting import plots
    plots(out, data, p, coils, error, A, b, candidates, imax, c)
    return data
