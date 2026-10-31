"""Independent, frozen-input diagnostics. No production model/solver is replaced."""
import hashlib
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path

VERSION = 'phase2d-frozen-field-and-lsq-v1'
RTOL, ATOL = 1e-11, 1e-13
SEALED_MANIFEST_SHA256 = 'd91d8add4c46ee29e1f954c5ad4bae4c870c2a10e371d0803d13d1829949c683'
SOURCE_PATHS = ('scripts/phase2d_frozen.py', 'src/stellarator_robust/frozen_diagnostics.py',
                'src/stellarator_robust/model.py', 'src/stellarator_robust/optimize.py',
                'src/stellarator_robust/fault_metrics.py', 'scripts/phase2d_investigate.py')


def source_hashes():
    return {name: sha(name) for name in SOURCE_PATHS}


def verify_contract(root, contract):
    manifest(root)
    if sha(Path(root)/'manifest.json') != SEALED_MANIFEST_SHA256:
        raise ValueError('Unrecognized sealed fixture fingerprint')
    if (contract.get('fixture_manifest_sha256') != SEALED_MANIFEST_SHA256
            or contract.get('sources') != source_hashes()):
        raise ValueError('Calculation source/fixture contract mismatch')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def invalid(value):
        raise ValueError('Nonfinite JSON: '+value)
    def number(value):
        x=float(value)
        if not math.isfinite(x): raise ValueError('Nonfinite JSON number')
        return x
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),parse_constant=invalid,parse_float=number)


def write_new(path,data):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(data,indent=2,allow_nan=False)+'\n')


def manifest(root):
    root=Path(root).resolve(); entries=load(root/'manifest.json')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix()!='manifest.json'}
    if not entries or entries.keys()!=actual: raise ValueError('Incomplete frozen manifest')
    for name,digest in entries.items():
        path=(root/name).resolve()
        if (Path(name).is_absolute() or '..' in Path(name).parts or ':' in name
                or not path.is_relative_to(root) or sha(path)!=digest):
            raise ValueError('Frozen input path/hash mismatch: '+name)
    cfg=load(root/'fixture.json')
    if (cfg['version']!=VERSION or cfg['rtol']!=RTOL or cfg['atol']!=ATOL
            or cfg['min_distance_m']!=1e-4 or cfg['ridge']!=1e-6
            or cfg['bounds']!=[-1.,1.] or cfg['solver_tol']!=1e-12
            or cfg['solver_max_iter']!=1000 or cfg['imax_A']!=3000.
            or cfg['bref_T']!=.001 or cfg['field_coefficient_T_m_per_A']!=1e-7
            or cfg['geometry_file']!='geometry.json' or cfg['fault_rows']!=[3,4]):
        raise ValueError('Unknown or changed benchmark settings')
    return cfg


def finite(value):
    if type(value) not in (int,float) or not math.isfinite(value):
        raise ValueError('Require a finite real scalar')
    return Decimal.from_float(float(value))


def _dot(a,b): return sum((x*y for x,y in zip(a,b)),Decimal(0))
def _cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def decimal_field(points,vertices,current=1.,precision=90,min_distance=1e-4):
    """Independent tangent/perpendicular finite-wire integral, not endpoint-cross code.

    Exact binary64 inputs; Decimal products and square roots at stated precision.
    The conventional coefficient is the exact recorded binary64 value 1e-7.
    Precision convergence is diagnostic, not an interval/continuum certificate.
    """
    if type(precision) is not int or precision<50: raise ValueError('Insufficient reference precision')
    if len(vertices)<8 or not points: raise ValueError('Invalid polygon/probes')
    if any(len(v)!=3 for v in [*vertices,*points]): raise ValueError('Expected 3-vectors')
    vv=[[finite(x) for x in v] for v in vertices]; pp=[[finite(x) for x in p] for p in points]
    with localcontext() as ctx:
        ctx.prec=precision
        coefficient=finite(1e-7)*finite(current); distance=finite(min_distance)
        if distance<=0: raise ValueError('Invalid clearance requirement')
        limit=distance**2
        result=[]
        for p in pp:
            total=[Decimal(0)]*3
            for a,b in zip(vv,vv[1:]+vv[:1]):
                d=[y-x for x,y in zip(a,b)]; length2=_dot(d,d)
                if not length2: raise ValueError('Degenerate wire segment')
                r=[x-y for x,y in zip(p,a)]; t=max(Decimal(0),min(Decimal(1),_dot(r,d)/length2))
                nearest=[x-t*y for x,y in zip(r,d)]
                if _dot(nearest,nearest)<=limit: raise ValueError('Evaluation point too close to filament')
                length=length2.sqrt(); e=[x/length for x in d]; z=_dot(e,r)
                perp=[x-z*y for x,y in zip(r,e)]; rho2=_dot(perp,perp)
                if not rho2: continue  # collinear beyond endpoints, already clearance-checked
                factor=coefficient/rho2*(z/(rho2+z*z).sqrt()-(z-length)/(rho2+(z-length)**2).sqrt())
                for j,value in enumerate(_cross(e,perp)): total[j]+=factor*value
            result.append([str(x) for x in total])
        return result


def vector_errors(reference,current):
    """Every component is graded; relative error at zero is explicitly undefined."""
    if len(reference)!=len(current): raise ValueError('Field dimensions differ')
    records=[]
    for i,(a,b) in enumerate(zip(reference,current)):
        if len(a)!=3 or len(b)!=3: raise ValueError('Field component dimensions')
        aa=[float(finite(x)) for x in a]; bb=[float(finite(x)) for x in b]
        errors=[abs(x-y) for x,y in zip(aa,bb)]
        threshold=[ATOL+RTOL*abs(x) for x in bb]
        norm=math.hypot(*aa)
        records.append(dict(point=i,reference_B_T=aa,current_B_T=bb,
            absolute_error_T=errors,relative_component_error=[err/abs(x) if x else None for x,err in zip(aa,errors)],
            vector_relative_error=math.hypot(*errors)/norm if norm else None,
            acceptance_threshold_T=threshold,passes=[x<=y for x,y in zip(errors,threshold)]))
    return records


def decimal_lsq(M,y,precision=90):
    """Independent high-precision normal equations with pivoted elimination.

    Only an interior solution is a bounded-solve reference. Normal-equation
    conditioning is squared; 90/120-digit agreement must be checked separately.
    """
    if precision<50 or not M or len(M)!=len(y) or not M[0]: raise ValueError('Invalid LSQ inputs')
    n=len(M[0])
    if any(len(row)!=n for row in M): raise ValueError('Ragged LSQ matrix')
    with localcontext() as ctx:
        ctx.prec=precision
        a=[[finite(x) for x in row] for row in M]; b=[finite(x) for x in y]
        H=[[sum((row[i]*row[j] for row in a),Decimal(0)) for j in range(n)] for i in range(n)]
        rhs=[sum((row[i]*v for row,v in zip(a,b)),Decimal(0)) for i in range(n)]
        for k in range(n):
            pivot=max(range(k,n),key=lambda i:abs(H[i][k]))
            if not H[pivot][k]: raise ValueError('Singular reference system')
            H[k],H[pivot]=H[pivot],H[k]; rhs[k],rhs[pivot]=rhs[pivot],rhs[k]
            for i in range(k+1,n):
                scale=H[i][k]/H[k][k]
                for j in range(k+1,n): H[i][j]-=scale*H[k][j]
                H[i][k]=Decimal(0); rhs[i]-=scale*rhs[k]
        x=[Decimal(0)]*n
        for i in range(n-1,-1,-1): x[i]=(rhs[i]-sum((H[i][j]*x[j] for j in range(i+1,n)),Decimal(0)))/H[i][i]
        residual=[_dot(row,x)-v for row,v in zip(a,b)]
        objective=sum((r*r for r in residual),Decimal(0))
        return dict(x=[str(v) for v in x],squared_augmented_residual=str(objective),
                    strictly_interior=all(abs(v)<1 for v in x),precision=precision)


def scalar_differences(a,b,path=''):
    """Complete fail-closed scientific comparison, including exact structure."""
    rows=[]
    if type(a) is dict and type(b) is dict:
        for k in sorted(a.keys()|b.keys()):
            if k not in a or k not in b: rows.append(dict(path=path+'/'+k,reason='missing-field'))
            else: rows+=scalar_differences(a[k],b[k],path+'/'+k)
    elif type(a) is list and type(b) is list:
        if len(a)!=len(b): rows.append(dict(path=path,reason='dimensions'))
        for i,(x,y) in enumerate(zip(a,b)): rows+=scalar_differences(x,y,path+'/'+str(i))
    elif type(a) is float and type(b) is float:
        finite(a);finite(b)
        error=abs(a-b)
        if error>ATOL+RTOL*abs(b): rows.append(dict(path=path,reference=a,current=b,absolute_error=error,reason='outside-tolerance'))
    elif type(a) is not type(b) or a!=b:
        rows.append(dict(path=path,reference=a,current=b,reason='exact-value'))
    return rows
