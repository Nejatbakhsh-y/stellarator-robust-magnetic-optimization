"""STEP51 offline authenticated numerical investigation. Never executes ZIP code.

Transport/schema and Decimal QR/certificates explicitly reuse STEP38/40/46/50.
The Gauss-Legendre Biot-Savart integrator below is independent of production.
Exit 2 retains unresolved science; 1 denotes an unexpected execution error.
"""
import argparse
import contextlib
from decimal import Decimal as D, localcontext
import io
import json
import os
from pathlib import Path
import platform
import sys
import zipfile

sys.dont_write_bytecode = True
import phase2d_step50_reproduction as archive_tools

COHORTS = ('windows-reference', 'linux-reference', 'linux-numpy-sensitivity', 'linux-scipy-sensitivity')
FILES = ('solver-reproduction.json', 'field-validation.json', 'recovery-ratios.json',
         'causal-attribution.json', 'scientific-blockers.json')


def fingerprint(a):
    return archive_tools.digest(a.astype('<f8').tobytes())


def input_seals(members, name, raw):
    """Require original byte and semantic seals; missing seals are not a pass."""
    import phase2d_step38_verify as transport
    prefix = name.rpartition('/')[0]
    prefix = prefix+'/' if prefix else ''
    byte_record = prefix+'input-sha256.json'
    problem_record = prefix+'problem-sha256.json'
    if byte_record not in members or problem_record not in members:
        return dict(status='INCOMPLETE', reason='Missing original input or problem seal')
    expected = archive_tools.decode(members[byte_record])
    transport.frozen_seal(expected, {'inputs.json': archive_tools.digest(raw)})
    semantic = transport.fingerprint(transport.problem(archive_tools.decode(raw)))
    transport.frozen_seal(archive_tools.decode(members[problem_record]), {'sha256': semantic})
    return dict(status='VERIFIED', problem_sha256=semantic)


def comparison(a, b):
    import numpy as np
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        raise ValueError('Comparison shape mismatch')
    return dict(bitwise_identical=a.astype('<f8').tobytes() == b.astype('<f8').tobytes(),
                max_abs=float(np.max(np.abs(a-b))),
                original_tolerance_pass=bool(np.all(np.abs(a-b) <= 1e-13+1e-11*np.abs(b))))


def integrated_field(points, vertices, order=16):
    """Integrate dl cross r / |r|^3 on oriented saved polygon segments.

    Gauss nodes integrate segment interiors, independently of the production
    closed segment formula. No production response matrix is used here.
    """
    import numpy as np
    points, vertices = np.asarray(points, float), np.asarray(vertices, float)
    if points.ndim != 2 or points.shape[1] != 3 or vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) < 3:
        raise ValueError('Geometry dimensions')
    dl = np.roll(vertices, -1, axis=0)-vertices
    if np.any(np.linalg.norm(dl, axis=1) == 0):
        raise ValueError('Degenerate segment')
    nodes, weights = np.polynomial.legendre.leggauss(order)
    result = np.zeros_like(points)
    for node, weight in zip(nodes, weights):
        source = vertices+(node+1)*dl/2
        for start in range(0, len(points), 64):
            r = points[start:start+64, None, :]-source[None, :, :]
            norm = np.linalg.norm(r, axis=2)
            if np.any(norm == 0):
                raise ValueError('Singular field probe')
            result[start:start+64] += weight/2 * np.sum(np.cross(dl[None, :, :], r)/norm[:, :, None]**3, axis=1)
    return result*1e-7


def field_validation(a, vectors):
    import numpy as np
    records = {}
    for grid in ('', 'fine_'):
        points, normals = a[grid+'points'], a[grid+'normals']
        units = np.array([integrated_field(points, v, 16) for v in a['vertices']])
        finer = np.array([integrated_field(points, v, 32) for v in a['vertices']])
        disturbance = integrated_field(points, a['error_vertices'], 32)*1500
        projected = np.einsum('cpk,pk->pc', finer, normals)
        base = np.sum(disturbance*normals, axis=1)
        currents = {}
        for name, x in vectors.items():
            xyz = disturbance+np.einsum('c,cpk->pk', x, finer)
            normal = np.sum(xyz*normals, axis=1)
            currents[name] = dict(Bxyz_sha256=fingerprint(xyz),
                Bx_By_Bz_max_abs_T=np.max(np.abs(xyz), axis=0).tolist(),
                projected_vs_saved_matrix=comparison(normal, a[grid+'b']+a[grid+'A']@x))
        records[grid or 'training'] = dict(quadrature_16_vs_32=comparison(units, finer),
            response=comparison(projected, a[grid+'A']), disturbance=comparison(base, a[grid+'b']),
            unit_Bxyz_sha256=fingerprint(finer), currents=currents)
    return dict(status='EXECUTED_DIAGNOSTIC', grids=records,
        orientation='Saved vertex order; reversal tested separately',
        limitation='Quadrature convergence on saved polygons; smooth-coil segment-refinement and geometry generation not certified')


def numerical(raw):
    import numpy as np
    from scipy.optimize import lsq_linear
    import phase2d_step38_verify as transport
    import phase2d_step40_validation as schema
    import phase2d_step46_independent as scalar
    data = archive_tools.decode(raw)
    a = schema.reconstruct(data)
    vectors, solver, refs = {}, {}, {}
    scale = data['config']['imax_A']
    for case in ('dense', 'row3', 'row4'):
        support = data['cases'][case].get('support', list(range(24)))
        if case != 'dense' and data['cases'][case]['failed'] != {'row3': 3, 'row4': 6}[case]:
            raise ValueError('Fault identity')
        M, y = a[case+'_M'], a[case+'_y']
        rebuilt = np.vstack((np.sqrt(a['weights'])[:, None]*a['D'][:, support],
                             np.sqrt(data['config']['ridge'])*np.eye(len(support))))
        rebuilt_y = np.r_[-np.sqrt(a['weights'])*a['d'], np.zeros(len(support))]
        # Solve original binary64 M/y, never silently replace by regenerated M/y.
        fit = lsq_linear(M, y, bounds=(-1, 1), method='trf', lsq_solver='exact', tol=1e-12, max_iter=1000)
        fresh = np.zeros(24); fresh[support] = fit.x*scale
        vectors[case+'_saved'] = a[case+'_x']*scale
        vectors[case+'_fresh'] = fresh
        if case != 'dense':
            frozen = vectors['dense_saved'].copy()
            frozen[data['cases'][case]['failed']] = 0
            vectors[case+'_frozen_saved'] = frozen
            frozen_fresh = vectors['dense_fresh'].copy()
            frozen_fresh[data['cases'][case]['failed']] = 0
            vectors[case+'_frozen_fresh'] = frozen_fresh
        qr = {str(d): scalar.reference(M.tolist(), y.tolist(), d) for d in (60, 90)}
        if qr['90']['status'] == 'INTERIOR_REFERENCE':
            refs[case] = [D(0)]*24
            with localcontext() as ctx:
                ctx.prec = 90
                for j, value in zip(support, qr['90']['x']):
                    refs[case][j] = D(value)*D.from_float(float(scale))
        solver[case] = dict(M_sha256=fingerprint(M), y_sha256=fingerprint(y), support=support,
            failed=data['cases'][case].get('failed'), physical_scale_A=scale, normalized_bounds=[-1, 1],
            reconstruction_M=comparison(rebuilt, M), reconstruction_y=comparison(rebuilt_y, y),
            success=bool(fit.success), status=int(fit.status), nit=int(fit.nit), message=str(fit.message),
            fresh_x_sha256=fingerprint(fresh), fresh_x_A=fresh.tolist(),
            current_comparison=comparison(fresh, vectors[case+'_saved']),
            saved_certificate=scalar.certificate(M.tolist(), y.tolist(), a[case+'_x'][support].tolist()),
            fresh_certificate=scalar.certificate(M.tolist(), y.tolist(), fit.x.tolist()),
            singular_values=np.linalg.svd(M, compute_uv=False).tolist(), condition=float(np.linalg.cond(M)),
            high_precision=qr)
    recovery = {}
    for case in ('row3', 'row4'):
        failed = data['cases'][case]['failed']
        args = [a[k].tolist() for k in ('fine_A', 'fine_b', 'fine_weights')]
        old = [vectors['dense_saved'].tolist(), vectors[case+'_saved'].tolist()]
        new = [vectors['dense_fresh'].tolist(), vectors[case+'_fresh'].tolist()]
        record = scalar.intervention(*args, *old, *new, failed)
        with localcontext() as ctx:
            ctx.prec = 90
            u, v = record['reference'], record['candidate']
            record['numerator_delta_T'] = str((D(v['rms_B_L_P'][1])-D(v['rms_B_L_P'][2]))-(D(u['rms_B_L_P'][1])-D(u['rms_B_L_P'][2])))
            record['denominator_delta_T'] = str(D(v['denominator_T'])-D(u['denominator_T']))
        record['precision_60_saved'] = scalar.ratio([D(x) for x in record['reference']['rms_B_L_P']], 60)
        record['high_precision_solver_reference'] = (scalar.intervention(*args, *old, refs['dense'], refs[case], failed)
            if 'dense' in refs and case in refs else dict(status='INCOMPLETE', reason='No bounded high precision reference'))
        recovery[case] = record
    return dict(input_sha256=archive_tools.digest(raw),
        problem_sha256=transport.fingerprint(transport.problem(data)),
        arrays_sha256={k:fingerprint(v) for k,v in a.items()}, solver=solver), recovery, field_validation(a, vectors)


def environment():
    import numpy as np
    import scipy
    from threadpoolctl import threadpool_info
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        np.show_config(); scipy.show_config()
    return dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform(),
        BLAS_LAPACK=stream.getvalue(), threadpools=threadpool_info(),
        threads={k:os.getenv(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},
        solver_settings=dict(method='trf',lsq_solver='exact',tol=1e-12,max_iter=1000,bounds=[-1,1]))


def assess(root, manifest):
    archives, solves, ratios, fields, history, environments = [], [], [], [], [], []
    seen, paths, hashes = set(), set(), set()
    cache = {}
    for run in manifest['runs']:
        for item in run['artifacts']:
            identity = dict(run_id=run['run_id'], artifact_id=item['id'], name=item['name'])
            row = dict(**identity)
            try:
                expected = item['github_sha256'].removeprefix('sha256:')
                if item['id'] in seen or item['file'].casefold() in paths or expected in hashes:
                    raise ValueError('Duplicate archive identity')
                seen.add(item['id']); paths.add(item['file'].casefold()); hashes.add(expected)
                if expected != item['verified_sha256']:
                    raise ValueError('Conflicting STEP49 fingerprint')
                path = root/archive_tools.safe(item['file'])
                if not path.resolve().is_relative_to(root.resolve()):
                    raise ValueError('Archive root escape')
                members = archive_tools.archive(path, expected)
                row.update(status='AUTHENTICATED_TO_SUPPLIED_STEP49_MANIFEST', zip_sha256=expected,
                    internal_manifests=archive_tools.seals(members), sources=archive_tools.source(members, run),
                    members={k:archive_tools.digest(v) for k,v in members.items()})
                for name, raw in members.items():
                    if name.endswith('environment.json'):
                        environments.append(dict(**identity,path=name,sha256=archive_tools.digest(raw),original=archive_tools.decode(raw)))
                    if name.endswith('.json') and any(s in name.lower() for s in ('comparison','status','causal-attribution')):
                        history.append(dict(**identity,path=name,sha256=archive_tools.digest(raw),original=archive_tools.decode(raw)))
                    if name.split('/')[-1] not in ('inputs.json','sealed-inputs.json'):
                        continue
                    seal = archive_tools.digest(raw)
                    ref = dict(**identity,path=name,input_sha256=seal)
                    if archive_tools.decode(raw).get('schema') != 'production-upstream-v1':
                        solves.append(dict(**ref,status='INCOMPLETE',reason='Unsupported historical input schema'))
                        continue
                    seal_status = input_seals(members, name, raw)
                    ref['input_seals'] = seal_status
                    if seal_status['status'] != 'VERIFIED':
                        solves.append(dict(**ref,status='INCOMPLETE',reason=seal_status['reason']))
                        continue
                    if seal not in cache:
                        try:
                            cache[seal] = numerical(raw)
                        except (ValueError,KeyError,ImportError) as exc:
                            cache[seal] = (dict(status='INCOMPLETE',reason=str(exc)), {}, {})
                    solution, recovery, field = cache[seal]
                    solves.append(dict(**ref,calculation=solution))
                    ratios.append(dict(**ref,calculation=recovery))
                    fields.append(dict(**ref,calculation=field))
            except (OSError,ValueError,zipfile.BadZipFile) as exc:
                row.update(status='REJECTED_OR_MISSING',reason=str(exc))
            archives.append(row)
    return archives, solves, ratios, fields, history, environments


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    for name in ('archive-root','manifest','output'):
        parser.add_argument('--'+name,required=True,type=Path)
    args = parser.parse_args(argv)
    root, output = args.archive_root.resolve(), args.output.resolve()
    if output.exists() or root.is_relative_to(output) or output.is_relative_to(root) or args.manifest.resolve().is_relative_to(output):
        print('Require fresh disjoint output',file=sys.stderr)
        return 1
    output.mkdir(parents=True,exist_ok=False)
    try:
        raw = args.manifest.read_bytes()
        auth, solves, ratios, fields, history, envs = assess(root,archive_tools.decode(raw))
        blockers = ['Historical failed comparisons unresolved; retained separately by run/artifact/path',
            'Fresh controlled A/B/C/D environments unavailable; local runtime is not a substitute',
            'Smooth geometry regeneration and 1e-4 segment refinement not certified',
            'Full README research checkpoint gates not certified by this assessor',
            'Unique numerical library causal attribution not established']
        archive_tools.write(output/FILES[0],dict(archives=auth,inputs=solves,manifest_sha256=archive_tools.digest(raw)))
        archive_tools.write(output/FILES[1],dict(inputs=fields))
        archive_tools.write(output/FILES[2],dict(inputs=ratios,historical_cohorts=history))
        archive_tools.write(output/FILES[3],dict(local_environment=environment(),historical_environments=envs,
            controlled_configurations={k:dict(status='INCOMPLETE',reason='Original environment not freshly executed') for k in COHORTS},
            attribution='INCONCLUSIVE', identical_inputs='Group by exact input_sha256; different hashes are not identical inputs'))
        archive_tools.write(output/FILES[4],dict(blockers=blockers))
        archive_tools.write(output/'status.json',dict(assessment='COMPLETED_WITH_UNRESOLVED_REQUIREMENTS',
            scientific_comparison='FAIL',production_acceptance='FAIL',overall_scientific_status='INCOMPLETE',
            rtol=1e-11,atol=1e-13,refinement_limit=1e-4,denominator_guard_T=1e-15,exit_code=2,
            implementation_sha256=archive_tools.digest(Path(__file__).read_bytes()),
            output_sha256={n:archive_tools.digest((output/n).read_bytes()) for n in FILES}))
        return 2
    except Exception as exc:
        archive_tools.write(output/'status.json',dict(assessment='UNEXPECTED_EXECUTION_ERROR',error=repr(exc),exit_code=1))
        return 1


if __name__ == '__main__':
    sys.exit(main())
