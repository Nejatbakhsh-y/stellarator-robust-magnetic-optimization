"""Fail closed on incomplete workers or scientific differences; retain diagnostics."""
import argparse
import json
from pathlib import Path
from stellarator_robust.phase2c import pair, require_complete, load, sha, verify_manifest, ScientificMismatch, collector
from stellarator_robust.ci_evidence import compare

parser = argparse.ArgumentParser()
parser.add_argument('--reference', type=Path, default=Path('results/phase2c'))
parser.add_argument('--current', type=Path, required=True)
parser.add_argument('--output', type=Path, default=Path('results/ci/phase2c-comparison.json'))
args = parser.parse_args()
record = dict(status='FAIL', scientific_status='PARTIAL', comparisons={})
try:
    require_complete(args.reference); require_complete(args.current)
    verify_manifest(args.reference); verify_manifest(args.current)
    failures=[]
    try:
        record['comparisons']['numerical'] = pair(args.reference, args.current)
    except ScientificMismatch as exc:
        record['comparisons']['numerical'] = exc.report
        failures.extend(exc.report['failures'])
    compare = collector(failures)
    geometries = [load(root/'investigation/geometry.json') for root in (args.reference, args.current)]
    diagnostics = []
    for i, (a, b) in enumerate(zip(geometries[0]['coils'], geometries[1]['coils'])):
        diagnostics.append(dict(coil=i, reference_legacy_displacement_m=a.pop('legacy_indexed_vertex_displacement_m'),
                                current_legacy_displacement_m=b.pop('legacy_indexed_vertex_displacement_m'),
                                reason='legacy-v1 input geometry itself is platform-sensitive; raw values retained'))
    geometry_errors = []
    before_geometry=len(failures)
    compare(geometries[0], geometries[1], '/geometry', records=geometry_errors)
    record['comparisons']['geometry'] = dict(status='FAIL' if len(failures)>before_geometry else 'PASS', numeric_differences=geometry_errors,
                                             legacy_diagnostics=diagnostics)
    # Adaptive NM is retained as an investigation, not substituted for the new
    # finite-search benchmark. Its physical field values still face the same
    # numerical gates; its coordinates/counts are explicitly reported below.
    analyses = [load(root/'investigation/analysis.json') for root in (args.reference, args.current)]
    nm_diagnostics, nm_field_errors = [], []
    before_nm=len(failures)
    for method in analyses[0]['corrected_peak_sensitivity']:
        first, second = [a['corrected_peak_sensitivity'][method]['nelder_mead'] for a in analyses]
        if len(first['searches']) != len(second['searches']) or first['certificate'] is not False or second['certificate'] is not False:
            raise AssertionError('Diagnostic search structure/certificate mismatch')
        for i, (a, b) in enumerate(zip(first['searches'], second['searches'])):
            compare(a['sign'], b['sign'], '/NM/sign', exact=True)
            compare(a['field_T'], b['field_T'], f'/NM/{method}/{i}/field_T', records=nm_field_errors)
            nm_diagnostics.append(dict(method=method, search=i,
                reference_angles_rad=a['angles_rad'], current_angles_rad=b['angles_rad'],
                reference_nfev=a['nfev'], current_nfev=b['nfev'],
                reference_success=a['success'], current_success=b['success'],
                qualification='Adaptive trace/position estimates retained; no claim of exact coordinate reproduction or optimality. All primary finite-search coordinates remain strictly compared.'))
    record['comparisons']['diagnostic_NM'] = dict(field_status='FAIL' if len(failures)>before_nm else 'PASS', field_differences=nm_field_errors,
                                                retained_trace_and_coordinate_values=nm_diagnostics)
    record['failures']=failures
    if failures:
        raise AssertionError(str(len(failures))+' scientific differences; see complete inventory')
    record['status'] = 'PASS'
except Exception as exc:
    record['error'] = str(exc)
    raise
finally:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2)+'\n')
print('Phase 2C scientific and geometry comparison:', record['status'])
