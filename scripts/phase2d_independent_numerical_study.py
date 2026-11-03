"""Original-input numerical experiments, without modifying archived evidence.

Run with --archive-root STEP49 --output a-new-results/phase2d-directory.
Reuses the documented STEP51 integrator and STEP46 Decimal QR certificates;
these are independent of production, not new independent implementations.
Exit 1 is execution failure; exit 2 is completed but scientifically incomplete.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

import phase2d_step50_reproduction as archive


def now():
    return datetime.now(timezone.utc).isoformat()


def origin_contract(members, seal_name):
    """Diagnose origin-key seals; never search arbitrary matching bytes.

    A match proves the writer's local replay-member contract only. Capture/run,
    semantic problem seals and Git source identity require separate evidence.
    """
    from phase2d_step51_numerical import COHORTS
    mapping = archive.decode(members[seal_name])
    base = seal_name.rpartition('/')[0]
    prefix = base + '/' if base else ''
    rows = []
    for origin, expected in mapping.items():
        if origin not in COHORTS:
            continue
        interpreted = prefix + origin
        actual = interpreted + '/inputs.json'
        rows.append(dict(origin=origin, interpreted_member=interpreted,
            writer_member=actual, expected_sha256=expected,
            interpreted_exists=interpreted in members,
            writer_bytes_match=actual in members and archive.digest(members[actual]) == expected,
            association_scope='LOCAL_REPLAY_MEMBER_ONLY'))
    return rows


def precise_metric(A, b, w, dense, recovered, failed, digits):
    """Recompute every product, sum, RMS and quotient at requested precision."""
    from phase2d_step46_independent import dec, ratio
    with localcontext() as ctx:
        ctx.prec = digits
        frozen = list(dense)
        frozen[failed] = 0
        norms = []
        for currents in (dense, frozen, recovered):
            x = list(map(dec, currents))
            fields = [dec(offset) + sum((dec(v)*z for v, z in zip(row, x)), Decimal(0))
                      for row, offset in zip(A, b)]
            norms.append(sum((dec(weight)*v*v for weight, v in zip(w, fields)), Decimal(0)).sqrt())
        result = ratio(norms, digits)
        result['numerator_T'] = str(norms[1]-norms[2])
        return result


def study(raw, output):
    import numpy as np
    import phase2d_step40_validation as schema
    import phase2d_step46_independent as scalar
    import phase2d_step51_numerical as previous
    data = archive.decode(raw)
    arrays = schema.reconstruct(data)
    solver, recovery, fields = previous.numerical(raw)
    np.savez_compressed(output/'original-arrays.npz', **arrays)
    scale = data['config']['imax_A']
    dense = (arrays['dense_x']*scale).tolist()
    args = [arrays[k].tolist() for k in ('fine_A', 'fine_b', 'fine_weights')]
    measurements = {}
    for case in ('row3', 'row4'):
        failed = data['cases'][case]['failed']
        saved = (arrays[case+'_x']*scale).tolist()
        precision = {str(d): precise_metric(*args, dense, saved, failed, d) for d in (60, 90)}
        with localcontext() as ctx:
            ctx.prec = 90
            delta = abs(Decimal(precision['60']['ratio'])-Decimal(precision['90']['ratio']))
        probes = []
        for vector in ('dense', case):
            support = data['cases'][vector].get('support', list(range(24)))
            for j in support:
                for direction in (-np.inf, np.inf):
                    dd, rr = list(dense), list(saved)
                    target = dd if vector == 'dense' else rr
                    target[j] = float(np.nextafter(target[j], direction))
                    probes.append(dict(vector=vector, coordinate=j, direction=int(np.sign(direction)),
                        measurement=scalar.intervention(*args, dense, saved, dd, rr, failed)))
        measurements[case] = dict(precision=precision, precision_ratio_delta=str(delta),
            precision_stabilized=delta <= Decimal('1e-50'), one_ulp=probes)
    # Retain full independently integrated arrays, not merely aggregate maxima.
    generated = {}
    for prefix in ('', 'fine_'):
        points = arrays[prefix+'points']
        units16 = np.array([previous.integrated_field(points, v, 16) for v in arrays['vertices']])
        units32 = np.array([previous.integrated_field(points, v, 32) for v in arrays['vertices']])
        generated[prefix+'unit_Bxyz_16'] = units16
        generated[prefix+'unit_Bxyz_32'] = units32
        generated[prefix+'quadrature_residual'] = units32-units16
        generated[prefix+'disturbance_Bxyz'] = previous.integrated_field(points, arrays['error_vertices'], 32)*1500
        for case in ('dense', 'row3', 'row4'):
            for kind, x in (('saved', arrays[case+'_x']*scale),
                            ('fresh', np.array(solver['solver'][case]['fresh_x_A']))):
                xyz = generated[prefix+'disturbance_Bxyz'] + np.einsum('c,cpk->pk', x, units32)
                generated[prefix+case+'_'+kind+'_Bxyz'] = xyz
    np.savez_compressed(output/'independent-field-arrays.npz', **generated)
    return dict(solver=solver, recovery=recovery, precision_and_ulp=measurements,
        fields=fields, limitations=['Original replay field/result association remains incomplete',
        'Smooth-coil geometry regeneration/refinement not executed by this study',
        'Four controlled environments not reproduced',
        'Eight unique input/case pairs do not reproduce all historical failures'])


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--archive-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    root, output = args.archive_root.resolve(), args.output.resolve()
    repo = Path(__file__).resolve().parents[1]
    allowed = repo/'results'/'phase2d'
    if (output.exists() or not output.is_relative_to(allowed) or
            output.is_relative_to(root) or root.is_relative_to(output)):
        parser.error('Require fresh output under results/phase2d disjoint from originals')
    output.mkdir(parents=True)
    started = now()
    try:
        import phase2d_step51_numerical as previous
        manifest_raw = (root/'manifest.json').read_bytes()
        manifest = archive.decode(manifest_raw)
        records, contracts, cache = [], [], {}
        for run in manifest['runs']:
            for item in run['artifacts']:
                expected = item['github_sha256'].removeprefix('sha256:')
                if expected != item['verified_sha256']:
                    raise ValueError('Conflicting original archive seal')
                path = root/archive.safe(item['file'])
                if not path.resolve().is_relative_to(root):
                    raise ValueError('Archive root escape')
                members = archive.archive(path, expected)
                identity = dict(run_id=run['run_id'], artifact_id=item['id'], zip_sha256=expected)
                records.append(dict(**identity, sources=archive.source(members, run),
                    seals=archive.seals(members)))
                for name in members:
                    if name.endswith('input-sha256.json'):
                        contracts.append(dict(**identity, member=name, diagnosis=origin_contract(members, name)))
                    if name.split('/')[-1] != 'inputs.json':
                        continue
                    raw = members[name]
                    key = archive.digest(raw)
                    if key in cache or archive.decode(raw).get('schema') != 'production-upstream-v1':
                        continue
                    # Capture-local byte AND semantic seals are prerequisites.
                    seal = previous.input_seals(members, name, raw)
                    if seal['status'] != 'VERIFIED':
                        continue
                    destination = output/key
                    destination.mkdir()
                    result = study(raw, destination)
                    archive.write(destination/'measurements.json', result)
                    cache[key] = dict(**identity, member=name, input_seals=seal)
        report = dict(started=started, completed=now(), status='EXECUTED_WITH_UNRESOLVED_REQUIREMENTS',
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=repo, text=True).strip(),
            environment=previous.environment(), architecture=platform.machine(),
            dependencies={d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
            manifest_sha256=archive.digest(manifest_raw), archives=records, origin_contract=contracts,
            independently_recomputed_inputs=cache, scientific_acceptance='NOT ACCEPTED',
            production_acceptance='FAIL', root_cause='INCONCLUSIVE',
            recovery_ratio_validation='INCOMPLETE; historical FAIL retained',
            magnetic_field_validation='INCOMPLETE', four_environment_attribution='INCOMPLETE',
            original_criteria=dict(rtol=1e-11, atol=1e-13, guard_T=1e-15, refinement=1e-4),
            output_sha256={str(p.relative_to(output)):archive.digest(p.read_bytes())
                           for p in output.rglob('*') if p.is_file()})
        archive.write(output/'study.json', report)
        return 2
    except Exception as exc:
        archive.write(output/'execution-error.json', dict(started=started, completed=now(),
            status='UNEXPECTED_EXECUTION_FAILURE', error=repr(exc)))
        raise


if __name__ == '__main__':
    sys.exit(main())
