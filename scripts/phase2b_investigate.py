"""Preserved trace investigation and independent geometry/conditioning audit."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np
from stellarator_robust.model import benchmark, deterministic_frame, clearance
from stellarator_robust.peak import normal_field, local_extrema, lattice_extrema
from stellarator_robust.phase2b import environment, sha, load

parser = argparse.ArgumentParser()
parser.add_argument('--archive', type=Path)
parser.add_argument('--output', type=Path, default=Path('results/phase2b/investigation'))
parser.add_argument('--corrected', type=Path)
args = parser.parse_args(); out = args.output; out.mkdir(parents=True, exist_ok=True)
history = Path('results/phase2b/history')
if args.archive:
    digest = sha(args.archive)
    assert digest == 'befcc90ca3bc461e22b08e379bf1660bab93efe568dd18d8d6fae2fe272c6d14'
    with zipfile.ZipFile(args.archive) as archive:
        raw = archive.read('reproduction/cloud-work/results/phase2/study.json')
        execution = json.loads(archive.read('ci/phase2-cloud/full/execution.json'))
    history.mkdir(parents=True, exist_ok=True)
    (history/'linux-v1-study.json').write_bytes(raw)
    (history/'provenance.json').write_text(json.dumps(dict(artifact_sha256=digest,
        linux_study_sha256=hashlib.sha256(raw).hexdigest(), run_id=40977794679,
        artifact_id=12944135712, environment=execution), indent=2)+'\n')
original = load('results/phase2/study.json'); linux = load(history/'linux-v1-study.json')
provenance = load(history/'provenance.json')
assert sha(history/'linux-v1-study.json') == provenance['linux_study_sha256']
quick = load('results/quick/results.json'); c = quick['metadata']['config']
_, _, _, legacy, error, _ = benchmark(3, 3, 512, c['nphi'], c['ntheta'])
_, _, _, corrected, corrected_error, _ = benchmark(3, 3, 512, c['nphi'], c['ntheta'], 'householder-v2')
trace = []
def walk(a, b, path):
    if isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a: walk(a[key], b[key], path+'/'+key)
    elif isinstance(a, list):
        assert len(a) == len(b)
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, path+'/'+str(i))
    elif isinstance(a, float):
        if not np.isclose(a, b, rtol=1e-11, atol=1e-13):
            trace.append(dict(path=path, reference=a, current=b, absolute_error=abs(a-b), category='scientific_coordinate' if '/angles_rad/' in path else 'scientific_value'))
    elif type(a) is not type(b) or a != b:
        trace.append(dict(path=path, reference=a, current=b, category='algorithmic_trace'))
for name in original['peaks']:
    walk(original['peaks'][name], linux['peaks'][name], '/peaks/'+name)
assert len(trace) == 145
conditioning = []
for name, peak in original['peaks'].items():
    currents = quick['currents_A'][name]
    evaluate = lambda x: normal_field(x, legacy, currents, error)
    rows = peak['search']['searches']; other = linux['peaks'][name]['search']['searches']
    fields_a = evaluate(np.array([r['angles_rad'] for r in rows]))
    fields_b = evaluate(np.array([r['angles_rad'] for r in other]))
    for i, (a, b, fa, fb) in enumerate(zip(rows, other, fields_a, fields_b)):
        angle = np.array(a['angles_rad']); curvatures = []
        for h in (1e-4, 5e-5):
            offsets = np.array([[0, 0], [h, 0], [-h, 0], [0, h], [0, -h], [h, h], [h, -h], [-h, h], [-h, -h]])
            f = evaluate(angle+offsets)
            H = np.array([[(f[1]-2*f[0]+f[2])/h**2, (f[5]-f[6]-f[7]+f[8])/(4*h*h)],
                          [(f[5]-f[6]-f[7]+f[8])/(4*h*h), (f[3]-2*f[0]+f[4])/h**2]])
            curvatures.append(np.linalg.eigvalsh(-a['sign']*H).tolist())
        smallest = curvatures[-1][0]
        conditioning.append(dict(method=name, search=i,
            periodic_angle_difference_rad=np.arctan2(np.sin(angle-b['angles_rad']), np.cos(angle-b['angles_rad'])).tolist(),
            saved_field_difference_T=abs(a['field_T']-b['field_T']),
            common_geometry_field_difference_T=abs(float(fa-fb)),
            reference_nfev=a['nfev'], linux_nfev=b['nfev'],
            signed_curvature_eigenvalues_T_per_rad2=curvatures,
            conditional_quadratic_position_scale_rad=float(np.sqrt(2e-15/smallest)) if smallest > 0 else None,
            qualification='Local finite differences; not an interval bound or coordinate certificate'))
expected = []
for t in np.arange(c['ntheta'])*2*np.pi/c['ntheta']:
    for p in np.arange(c['nphi'])*2*np.pi/c['nphi']:
        expected.append((np.array([(1+.65*np.cos(t))*np.cos(p), (1+.65*np.cos(t))*np.sin(p), .65*np.sin(t)]),
                         np.array([np.cos(t)*np.cos(p), np.cos(t)*np.sin(p), np.sin(t)]), .16))
expected.append((np.array([1.6, .25, .35]), np.array([1., .2, .4]), .22))
geometry = []
for i, (old, new, (declared_center, declared_normal, declared_radius)) in enumerate(zip(legacy+[error], corrected+[corrected_error], expected)):
    # Antipodal vertices recover the exact regular-polygon center without a
    # 512-term accumulation of its large translation. Record ordinary-mean
    # disagreement separately rather than misclassifying it as nonplanarity.
    center = (new.vertices[0]+new.vertices[len(new.vertices)//2])/2
    centroid_reduction_error = float(np.linalg.norm(new.vertices.mean(axis=0)-center))
    r = new.vertices-center
    normal = np.cross(r[0], r[len(r)//4]); normal /= np.linalg.norm(normal)
    radius = np.linalg.norm(r, axis=1)
    declared_normal /= np.linalg.norm(declared_normal)
    assert np.max(abs(center-declared_center)) < 1e-14
    assert np.max(abs(radius-declared_radius)) < 1e-14
    assert np.max(abs(normal-declared_normal)) < 1e-14
    assert np.max(abs(radius-radius.mean())) < 1e-14
    assert np.max(abs(r@normal)) < 1e-14
    assert np.sum(np.cross(r, np.roll(r, -1, axis=0))@normal) > 0
    geometry.append(dict(coil=i, vertices=new.vertices.tolist(), center=center.tolist(),
        radius_m=float(radius.mean()), normal=normal.tolist(), segments=len(r),
        ordinary_centroid_reduction_error_m=centroid_reduction_error,
        legacy_indexed_vertex_displacement_m=float(np.max(np.linalg.norm(new.vertices-old.vertices, axis=1))),
        polygon_to_polygon_Hausdorff_upper_m=float(2*radius.mean()*(1-np.cos(np.pi/len(r))))))
(out/'geometry.json').write_text(json.dumps(dict(version='householder-v2', coils=geometry), indent=2)+'\n')
points, _, _ = __import__('stellarator_robust.model', fromlist=['surface']).surface(1., .25, 20, 48, .5)
scenario = original['scenarios']['holdout'][9]
new_clearance = min(clearance(points, coil.moved(np.array(tr), np.array(rot)))
                    for coil, tr, rot in zip(corrected, scenario['translation_m'], scenario['rotation_rad']))
report = dict(kind='scientific_investigation_not_legacy_revalidation', environment=environment(),
              legacy_status='FAIL_RETAINED', legacy_trace_discrepancies=trace, conditioning=conditioning,
              original_Windows_clearance_m=scenario['sampled_clearance_m'],
              original_Linux_clearance_m=linux['scenarios']['holdout'][9]['sampled_clearance_m'],
              new_geometry_clearance_m=new_clearance,
              old_optimizer_settings=dict(method='Nelder-Mead', xatol_rad=1e-8, fatol_dimensionless=1e-12,
                                          objective_scale_T=1e-3, effective_fatol_T=1e-15),
              version_sensitivity='Original NumPy/SciPy versions match; platform effects remain. Hosted prior-version jobs provide controlled sensitivity data.')
if args.corrected:
    q = load(args.corrected/'quick/results.json'); d = load(args.corrected/'study/study.json')
    comparisons = {}
    for name, peak in d['peaks'].items():
        evaluate = lambda x: normal_field(x, corrected, q['currents_A'][name], corrected_error)
        seeds = [r['angles_rad'] for r in peak['grids']]
        nm = local_extrema(evaluate, seeds, 120, 240)
        variants = {str(levels): lattice_extrema(evaluate, seeds, levels=levels) for levels in (20, 28)}
        for search in [nm, *variants.values(), peak['search']]:
            assert search['certificate'] is False
            for row in search['searches']:
                assert abs(float(evaluate(np.array([row['angles_rad']]))[0])-row['field_T']) < 1e-13
        comparisons[name] = dict(nelder_mead=nm, finite_refinements=variants,
            baseline_finite=peak['search'],
            best_field_gap_to_NM_T=abs(abs(nm['best']['field_T'])-abs(peak['search']['best']['field_T'])))
    report['corrected_peak_sensitivity'] = comparisons
(out/'analysis.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
print('Accounted for all', len(trace), 'historical trace discrepancies; legacy failure retained')
print('Version 2 geometry invariants passed; scenario 9 clearance:', new_clearance)
