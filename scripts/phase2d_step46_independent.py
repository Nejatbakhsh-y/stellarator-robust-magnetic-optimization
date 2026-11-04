"""Independent scalar diagnostics; exit 2 incomplete, 1 retained science FAIL.

Transport validation alone reuses STEP42. Arithmetic below calls no production
field, recovery, KKT or least-squares helper. Local seals are not GitHub origin.
"""
import argparse
from decimal import Decimal as D, localcontext
import hashlib
import json
from pathlib import Path
import sys

SOURCE = '3eabd1a98dad81493e664929890ba0effdd97a05'
RTOL, ATOL, GUARD = D('1e-11'), D('1e-13'), D('1e-15')


class MissingEvidenceError(Exception):
    """A required transport input is absent, rather than numerically invalid."""


def diagnostic_source_digest(path):
    """Fingerprint only these source bytes; None means unavailable, not sealed."""
    path = Path(path)
    if not path.is_file():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except FileNotFoundError:
        # The file may disappear between availability verification and reading.
        return None


def dec(x):
    if isinstance(x, bool):
        raise ValueError('Boolean scalar')
    z = D.from_float(x) if isinstance(x, float) else D(x)
    if not z.is_finite():
        raise ValueError('Nonfinite scalar')
    return z


def agrees(a, b):
    with localcontext() as c:
        c.prec = 90
        a, b = dec(a), dec(b)
        return abs(a-b) <= ATOL+RTOL*abs(b)


def ratio(values, digits=90):
    """B,L,P order; componentwise relative condition of the scalar quotient."""
    with localcontext() as c:
        c.prec = digits
        B, L, P = map(dec, values)
        g, n = L-B, L-P
        if abs(g) <= GUARD:
            raise ValueError('Original denominator guard')
        R = n/g
        grad = [n/g**2, (P-B)/g**2, -1/g]
        h = abs(g)*D('1e-20')
        fd = []
        for j in range(3):
            u, v = [B,L,P], [B,L,P]
            u[j] += h
            v[j] -= h
            f = lambda z: (z[1]-z[2])/(z[1]-z[0])
            fd.append((f(u)-f(v))/(2*h))
        return dict(ratio=str(R), rms_B_L_P=list(map(str, (B,L,P))),
                    gradient=list(map(str, grad)), finite_difference=list(map(str, fd)),
                    finite_difference_step=str(h), denominator_T=str(g),
                    absolute_condition=str(sum(abs(v*z) for v,z in zip((B,L,P),grad))),
                    relative_condition=None if R == 0 else str(sum(abs(v*z) for v,z in zip((B,L,P),grad))/abs(R)))


def forward(A, b, w, currents):
    """90-digit products/sums of exact input floats, including physical amps."""
    with localcontext() as c:
        c.prec = 90
        x = list(map(dec, currents))
        if not A or len(A) != len(b) or len(b) != len(w) or not x:
            raise ValueError('Field dimensions')
        fields = []
        for row, offset in zip(A,b):
            if len(row) != len(x):
                raise ValueError('Field dimensions')
            fields.append(dec(offset)+sum((dec(a)*v for a,v in zip(row,x)), D(0)))
        weights = list(map(dec,w))
        if any(v < 0 for v in weights) or sum(weights) <= 0:
            raise ValueError('Invalid weights')
        rms = sum((v*r*r for v,r in zip(weights,fields)),D(0)).sqrt()
        return fields, rms


def metric(A,b,w,dense,recovered,failed):
    frozen = list(dense)
    frozen[failed] = 0
    fields, norms = [], []
    for x in (dense,frozen,recovered):
        f, n = forward(A,b,w,x)
        fields.append(f)
        norms.append(n)
    return ratio(norms), fields


def certificate(M,y,x):
    """Direct residual gradient, exact-bound KKT and normal-map residual."""
    with localcontext() as c:
        c.prec = 90
        rows = [list(map(dec,row)) for row in M]
        xx, yy = list(map(dec,x)), list(map(dec,y))
        if not xx or len(rows) != len(yy) or any(len(r) != len(xx) for r in rows):
            raise ValueError('Least squares dimensions')
        r = [sum((a*v for a,v in zip(row,xx)),D(0))-b for row,b in zip(rows,yy)]
        g = [sum((row[j]*v for row,v in zip(rows,r)),D(0)) for j in range(len(xx))]
        k = [min(v,D(0)) if z == -1 else max(v,D(0)) if z == 1 else v for z,v in zip(xx,g)]
        projected = [z-max(D(-1),min(D(1),z-v)) for z,v in zip(xx,g)]
        return dict(objective=str(sum((v*v for v in r),D(0))/2),
                    gradient_max=str(max(map(abs,g))), kkt_max=str(max(map(abs,k))),
                    projected_gradient_max=str(max(map(abs,projected))),
                    bound_violation=str(max([D(0)]+[abs(v)-1 for v in xx])),
                    constraint_scope='Fixed support box only; no minimax epigraph captured')


def reference(M,y,digits=90):
    """Scalar Decimal Householder QR, separately implemented from STEP40 MGS.

    No normal equations; an out-of-box solution is not a bounded reference.
    Precision convergence is empirical, not a rigorous interval certificate.
    """
    with localcontext() as c:
        c.prec = digits
        a, b = [list(map(dec,row)) for row in M], list(map(dec,y))
        m, n = len(a), len(a[0])
        if m < n or len(b) != m or any(len(row) != n for row in a):
            raise ValueError('QR dimensions')
        for j in range(n):
            v = [a[i][j] for i in range(j,m)]
            length = sum((z*z for z in v),D(0)).sqrt()
            if length == 0:
                return dict(status='NOT_CERTIFIED',reason='Rank deficient')
            v[0] += length if v[0] >= 0 else -length
            norm2 = sum((z*z for z in v),D(0))
            for k in range(j,n):
                factor = 2*sum((v[i-j]*a[i][k] for i in range(j,m)),D(0))/norm2
                for i in range(j,m):
                    a[i][k] -= factor*v[i-j]
            factor = 2*sum((v[i-j]*b[i] for i in range(j,m)),D(0))/norm2
            for i in range(j,m):
                b[i] -= factor*v[i-j]
        x = [D(0)]*n
        for j in reversed(range(n)):
            x[j] = (b[j]-sum((a[j][k]*x[k] for k in range(j+1,n)),D(0)))/a[j][j]
        return dict(status='INTERIOR_REFERENCE' if max(map(abs,x)) < 1 else 'NOT_CERTIFIED',
                    x=list(map(str,x)),certificate=certificate(M,y,x),digits=digits)


def intervention(A,b,w,dense,recovered,new_dense,new_recovered,failed):
    with localcontext() as c:
        c.prec = 90
        base, f = metric(A,b,w,dense,recovered,failed)
        candidate, ff = metric(A,b,w,new_dense,new_recovered,failed)
        changes = [D(v)-D(u) for u,v in zip(base['rms_B_L_P'],candidate['rms_B_L_P'])]
        linear = sum((D(g)*d for g,d in zip(base['gradient'],changes)),D(0))
        delta = D(candidate['ratio'])-D(base['ratio'])
        return dict(reference=base,candidate=candidate,delta_R=str(delta),
                    linearized_delta_R=str(linear),nonlinear_residual=str(delta-linear),
                    field_delta_max_T=str(max(abs(v-u) for row,rr in zip(f,ff) for u,v in zip(row,rr))),
                    current_delta_max_A=str(max(abs(dec(v)-dec(u)) for old,new in
                        ((dense,new_dense),(recovered,new_recovered)) for u,v in zip(old,new))),
                    pass_original_tolerance=agrees(candidate['ratio'],base['ratio']),
                    control='Identical A,b,w; currents alone changed')


def investigate(path, digest):
    import numpy as np
    import scipy
    import platform
    from scipy.optimize import lsq_linear
    import phase2d_step42_replay as transport
    # Explicit reuse: strict file/problem/source seals and M/y reconstruction.
    try:
        data,a,identity = transport.load_capture(path,digest)
    except FileNotFoundError as exc:
        raise MissingEvidenceError('Required authenticated input file absent') from exc
    results, vectors, references = {}, {}, {}
    for case in ('dense','row3','row4'):
        M,y = a[case+'_M'],a[case+'_y']
        support = data['cases'][case].get('support',list(range(24)))
        fit = lsq_linear(M,y,method='trf',lsq_solver='exact',tol=1e-12,max_iter=1000,bounds=(-1,1))
        fresh = np.zeros(24)
        fresh[support] = fit.x*3000
        saved = a[case+'_x']*3000
        vectors[case] = (saved.tolist(),fresh.tolist())
        qr = {str(d):reference(M.tolist(),y.tolist(),d) for d in (60,90)}
        if qr['90']['status'] == 'INTERIOR_REFERENCE':
            with localcontext() as c:
                c.prec = 90
                ref = [D(0)]*24
                for j,v in zip(support,qr['90']['x']):
                    ref[j] = D(v)*3000
                references[case] = ref
        singular = np.linalg.svd(M,compute_uv=False)
        results[case] = dict(saved=certificate(M.tolist(),y.tolist(),a[case+'_x'][support].tolist()),
            fresh=certificate(M.tolist(),y.tolist(),fit.x.tolist()),success=bool(fit.success),
            optimality=float(fit.optimality),condition=float(singular[0]/singular[-1]),
            decimal_householder=qr,
            M_sha256=hashlib.sha256(M.astype('<f8').tobytes()).hexdigest(),
            y_sha256=hashlib.sha256(y.astype('<f8').tobytes()).hexdigest())
    recovery = {}
    for case in ('row3','row4'):
        A,b,w = (a[k].tolist() for k in ('fine_A','fine_b','fine_weights'))
        failed = data['cases'][case]['failed']
        if failed != {'row3':3,'row4':6}[case]:
            raise ValueError('Fault identity')
        recovery[case] = intervention(A,b,w,vectors['dense'][0],vectors[case][0],
                                      vectors['dense'][1],vectors[case][1],failed)
        perturb = list(vectors[case][0])
        j = data['cases'][case]['support'][0]
        perturb[j] = float(np.nextafter(perturb[j],np.inf))
        recovery[case]['one_ulp_current_probe'] = intervention(A,b,w,vectors['dense'][0],
            vectors[case][0],vectors['dense'][0],perturb,failed)
        if 'dense' in references and case in references:
            recovery[case]['independent_reference'] = intervention(A,b,w,vectors['dense'][0],
                vectors[case][0],references['dense'],references[case],failed)
        else:
            recovery[case]['independent_reference'] = dict(status='NOT_CERTIFIED')
        frozen = np.array(vectors['dense'][0]); frozen[failed] = 0
        norms = [float(np.sqrt(np.sum(a['fine_weights']*(a['fine_b']+a['fine_A']@x)**2)))
                 for x in (np.array(vectors['dense'][0]),frozen,np.array(vectors[case][0]))]
        binary_ratio = (norms[1]-norms[2])/(norms[1]-norms[0]) if abs(norms[1]-norms[0]) > 1e-15 else None
        recovery[case]['saved_current_binary64_ratio'] = binary_ratio
        recovery[case]['original_saved_result_ratio'] = 'MISSING_EVIDENCE: bind original result separately'
        with localcontext() as c:
            c.prec = 90
            recovery[case]['aggregate_binary64_evaluation_error'] = (None if binary_ratio is None else
                str(dec(binary_ratio)-D(recovery[case]['reference']['ratio'])))
    return dict(identity=identity,authentication='LOCAL_SEALS_ONLY',solver=results,recovery=recovery,
                environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform()),
                geometry_reconstruction='NOT_EXECUTED: saved field matrices held fixed')


def main(argv=None):
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--capture',type=Path)
    p.add_argument('--input-sha256')
    p.add_argument('--output',required=True,type=Path)
    args = p.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    out = args.output.resolve()
    if not out.is_relative_to(root/'results/phase2d') or out.exists():
        raise ValueError('Require new isolated results/phase2d output directory')
    if args.capture and (out.is_relative_to(args.capture.resolve()) or args.capture.resolve().is_relative_to(out)):
        raise ValueError('Input/output overlap')
    result = dict(source_commit=SOURCE,independent_calculation='INCOMPLETE',
                  artifact_authentication='MISSING_EVIDENCE',step32='FAIL',step33='FAIL',step45='FAIL',
                  recovery_ratio_validation='INCOMPLETE',numerical_root_cause='INCONCLUSIVE',
                  production_acceptance='FAIL',overall_scientific_status='PARTIAL')
    # Source identity is separate from scientific evidence and never authenticates
    # historical artifacts. Retain the manifest field with null when unavailable.
    source_digest = diagnostic_source_digest(__file__)
    incomplete = not args.capture or source_digest is None
    if args.capture:
        if not args.input_sha256 or len(args.input_sha256) != 64:
            raise ValueError('Explicit input SHA256 required')
        try:
            numerical = investigate(args.capture,args.input_sha256)
        except MissingEvidenceError:
            incomplete = True
        else:
            result['numerical'] = numerical
            if source_digest is not None:
                result['independent_calculation'] = 'EXECUTED_LOCAL_SEALED_INPUT'
                result['recovery_ratio_validation'] = 'PASS' if all(v['pass_original_tolerance'] for v in numerical['recovery'].values()) else 'FAIL'
    out.mkdir(parents=True)
    record = out/'assessment.json'
    record.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(dict(
        result_sha256=hashlib.sha256(record.read_bytes()).hexdigest(),
        diagnostic_source_sha256=source_digest),indent=2)+'\n',encoding='utf-8')
    return 2 if incomplete else 1


if __name__ == '__main__':
    sys.exit(main())
