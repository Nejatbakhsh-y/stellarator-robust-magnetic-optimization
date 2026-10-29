"""Plots derived exclusively from recorded experiment arrays."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plots(out, data, points, coils, error, A, b, candidates, imax, c):
    plt.rcParams.update({'figure.dpi': 150, 'font.size': 10})
    def save(name):
        plt.tight_layout(); plt.savefig(out/f'{name}.png'); plt.close()
    fig = plt.figure(figsize=(8, 6)); ax = fig.add_subplot(projection='3d')
    ax.scatter(*points.T, s=2, alpha=.2)
    for coil in coils+[error]:
        v = np.vstack([coil.vertices, coil.vertices[0]])
        ax.plot(*v.T, color='red' if coil is error else 'blue', linewidth=.7)
    ax.set(xlabel='x [m]', ylabel='y [m]', zlabel='z [m]', title='Synthetic planar-coil benchmark')
    ax.set_box_aspect((1, 1, .6)); save('geometry')
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    limit = max(abs(b))*1e6
    for ax, name in zip(axes, ['zero', 'dense', 'robust']):
        r = (b+A@(candidates[name]*imax)).reshape(c['nt'], c['np'])*1e6
        im = ax.imshow(r, origin='lower', extent=[0, 360, 0, 360], aspect='auto', cmap='RdBu_r', vmin=-limit, vmax=limit)
        ax.set(title=name, xlabel='phi [deg]', ylabel='theta [deg]'); fig.colorbar(im, ax=ax, label='Bn [microtesla]')
    save('normal_field')
    rows = data['convergence']; plt.figure()
    plt.loglog([r['segments'] for r in rows], [r['max_relative_error'] for r in rows], 'o-')
    plt.xlabel('Polygon segment count'); plt.ylabel('Maximum relative axis error'); plt.grid(); save('convergence')
    plt.figure()
    for method in ['l1_refit', 'delete_refit']:
        rows = [r for r in data['pareto'] if r['method']==method]
        plt.scatter([r['active'] for r in rows], [r['rms_T']*1e6 for r in rows], label=method)
    dense = data['summary']['dense']['nominal']
    plt.scatter([dense['active']], [dense['rms_T']*1e6], marker='*', s=100, label='dense')
    plt.xlabel('Active coils (>1 A)'); plt.ylabel('Training RMS Bn [microtesla]'); plt.legend(); save('pareto')
    plt.figure()
    for method in ['l1_refit', 'delete_refit']:
        rows = [r for r in data['pareto'] if r['method']==method]
        plt.scatter([r['l1_A'] for r in rows], [r['rms_T']*1e6 for r in rows], label=method)
    plt.xlabel('Sum absolute commanded current [A]'); plt.ylabel('Training RMS Bn [microtesla]'); plt.legend(); save('current_tradeoff')
    plt.figure(figsize=(9, 4))
    for name in ['dense', 'matched_nominal', 'robust']:
        plt.plot(data['currents_A'][name], '.-', label=name)
    plt.xlabel('Coil index'); plt.ylabel('Commanded current [A]'); plt.legend(); save('currents')
    plt.figure()
    for name in ['dense', 'matched_nominal', 'robust']:
        values = np.sort(data['holdout_rms_T'][name])*1e6
        plt.plot(values, np.arange(1, len(values)+1)/len(values), label=name)
    plt.xlabel('Holdout RMS Bn [microtesla]'); plt.ylabel('Empirical cumulative probability'); plt.legend(); save('holdout')
    plt.figure(figsize=(9, 4))
    for key in ['pre_T', 'frozen_T', 'recovered_T']:
        plt.plot([f['failed'] for f in data['faults']], [f[key]*1e6 for f in data['faults']], '.-', label=key)
    plt.xlabel('Failed coil index'); plt.ylabel('Fine-grid RMS Bn [microtesla]'); plt.legend(); save('outages')
