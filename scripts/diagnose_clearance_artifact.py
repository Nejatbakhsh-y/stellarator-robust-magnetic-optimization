"""Diagnostic-only comparison and basis probe; never changes production geometry."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
import numpy as np
from stellarator_robust.model import circle, Coil, surface, clearance

parser = argparse.ArgumentParser()
parser.add_argument('--artifact', type=Path, required=True)
parser.add_argument('--output', type=Path, default=Path('results/ci/clearance-repair/diagnosis.json'))
args = parser.parse_args()
assert hashlib.sha256(args.artifact.read_bytes()).hexdigest() == 'befcc90ca3bc461e22b08e379bf1660bab93efe568dd18d8d6fae2fe272c6d14'
with zipfile.ZipFile(args.artifact) as archive:
    current = json.loads(archive.read('reproduction/cloud-work/results/phase2/study.json'))
reference_bytes = Path('results/phase2/study.json').read_bytes()
assert hashlib.sha256(reference_bytes).hexdigest() == '395027e9fdda163448789beda6b1c7eb7d1537d6024d0a0ee32790ddf53bb258'
reference = json.loads(reference_bytes)
record = dict(kind='diagnostic_not_a_passing_validation', material_differences=[],
              exact_input_changes=[], derived_clearance_differences=[])

def walk(a, b, path=''):
    if path in ('/source_commit', '/source_dirty', '/python') or (path.startswith('/trials/') and path.endswith('/solver/seconds')):
        return
    if isinstance(a, dict):
        assert a.keys() == b.keys(), path
        for key in a:
            walk(a[key], b[key], path+'/'+key)
    elif isinstance(a, list):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path+'/'+str(i))
    elif isinstance(a, float):
        error = abs(a-b)
        row = dict(path=path, reference=a, current=b, absolute_error=error,
                   relative_error=error/max(abs(a), 1e-300))
        if error and not np.isclose(a, b, rtol=1e-11, atol=1e-13):
            record['material_differences'].append(row)
        if path.startswith('/scenarios/') and path.endswith('/sampled_clearance_m') and error:
            record['derived_clearance_differences'].append(row)
        elif path.startswith('/scenarios/') and a != b:
            record['exact_input_changes'].append(row)
    elif type(a) is not type(b) or a != b:
        record['material_differences'].append(dict(path=path, reference=a, current=b))

walk(reference, current)
assert reference['config'] == current['config']
c = json.loads(Path('results/quick/results.json').read_text())['metadata']['config']
points, _, _ = surface(1., .25, 2*c['nt'], 2*c['np'], .5)
scenario = reference['scenarios']['holdout'][9]
assert scenario == {**current['scenarios']['holdout'][9], 'sampled_clearance_m': scenario['sampled_clearance_m']}
distances, geometry = [], []
for t in np.arange(c['ntheta'])*2*np.pi/c['ntheta']:
    for p in np.arange(c['nphi'])*2*np.pi/c['nphi']:
        center = np.array([(1+.65*np.cos(t))*np.cos(p), (1+.65*np.cos(t))*np.sin(p), .65*np.sin(t)])
        n = np.array([np.cos(t)*np.cos(p), np.cos(t)*np.sin(p), np.sin(t)])
        i = len(geometry)
        coil = circle(center, n, .16, 512)
        tr, rot = np.array(scenario['translation_m'][i]), np.array(scenario['rotation_rad'][i])
        distances.append(clearance(points, coil.moved(tr, rot)))
        geometry.append((center, n, tr, rot))
record['recomputed_windows_clearance'] = min(distances)
record['basis_diagnostics'] = []
for i, (center, normal, tr, rot) in enumerate(geometry):
    n = normal/np.linalg.norm(normal)
    axes = np.flatnonzero(abs(abs(n)-min(abs(n))) < 1e-15)
    if len(axes) < 2:
        continue
    for axis in axes:
        # Diagnostic-only alternate polygon phase; production geometry is untouched.
        u = np.cross(np.eye(3)[axis], n); u /= np.linalg.norm(u)
        v = np.cross(n, u)
        angles = np.arange(512)*2*np.pi/512
        alt = Coil(center+.16*(np.cos(angles)[:, None]*u+np.sin(angles)[:, None]*v))
        value = min(distances[:i]+[clearance(points, alt.moved(tr, rot))]+distances[i+1:])
        record['basis_diagnostics'].append(dict(coil_index=i, normal=n.tolist(),
            local_argmin_axis=int(np.argmin(abs(n))), diagnostic_axis=int(axis),
            global_sampled_clearance=value,
            error_to_linux=abs(value-current['scenarios']['holdout'][9]['sampled_clearance_m'])))
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(record, indent=2)+'\n')
print('Out-of-tolerance fields:', len(record['material_differences']))
print('Exact perturbation input changes:', len(record['exact_input_changes']))
print('First material fields:', json.dumps(record['material_differences'][:5], indent=2))
print('Best alternate basis match:', json.dumps(min(record['basis_diagnostics'], key=lambda r:r['error_to_linux']), indent=2))
