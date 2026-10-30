"""Independent high-precision audit of every outage; no production metric helper."""
import argparse
import itertools
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path
import numpy as np
from stellarator_robust.model import benchmark, response, surface, field
from stellarator_robust.phase2b import load, sha, environment


def reference(A,b,w,currents,precision):
    with localcontext() as ctx:
        ctx.prec=precision
        dec=lambda x:Decimal.from_float(float(x))
        matrix=[[dec(x) for x in row] for row in A]
        bb=[dec(x) for x in b]; ww=[dec(x) for x in w]
        norms=[]; residuals=[]
        for cur in currents:
            cur=[dec(x) for x in cur]
            r=[v+sum((a*x for a,x in zip(row,cur)),Decimal(0)) for v,row in zip(bb,matrix)]
            residuals.append(r)
            norms.append(sum((weight*x*x for weight,x in zip(ww,r)),Decimal(0)).sqrt())
        denominator=norms[1]-norms[0]
        ratio=(norms[1]-norms[2])/denominator if abs(denominator)>Decimal('1e-15') else None
        return dict(ratio=None if ratio is None else str(ratio),rms_T=[str(x) for x in norms],
                    denominator_T=str(denominator),residual_T=[[float(x) for x in r] for r in residuals])


def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path('results/phase2c'))
    args=p.parse_args(); root=args.root; q=load(root/'quick/results.json'); c=q['metadata']['config']
    out=dict(status='FAIL',quick_sha256=sha(root/'quick/results.json'),environment=environment(),
             reference_scope='Decimal evaluation of exact binary64 matrix/field/weights/currents; not an exact-geometry or exact-optimizer certificate',checks={},faults=[])
    try:
        pt,nt,wt,coils,error,bt=benchmark(c['nt'],c['np'],c['segments'],c['nphi'],c['ntheta'],c['geometry_version'])
        train=response(pt,nt,coils)*c['imax_A']/c['bref_T']; target=bt/c['bref_T']
        pv,nv,av=surface(1.,.25,2*c['nt'],2*c['np'],.5); w=av/av.sum()
        A=response(pv,nv,coils); b=np.sum(field(pv,error,1500)*nv,axis=1)
        dense=np.array(q['currents_A']['dense']); checks=[]
        inputs=dict(response_T_per_A=A.tolist(),disturbance_T=b.tolist(),weights=w.tolist())
        (root/'fault-reference-inputs.json').write_text(json.dumps(inputs,allow_nan=False)+'\n')
        out['reference_inputs_sha256']=sha(root/'fault-reference-inputs.json')
        for row in q['faults']:
            ev=row['recovery_evidence']; frozen=dense.copy(); frozen[row['failed']]=0
            currents=[dense,frozen,np.array(ev['recovered_currents_A'])]
            x=currents[2]/c['imax_A']
            gradient=train.T@(wt*(target+train@x))+c['ridge']*x
            projected=x-np.clip(x-gradient,-1.,1.)
            projected[row['failed']]=0.
            first=reference(A,b,w,currents,60); second=reference(A,b,w,currents,90)
            ref=None if second['ratio'] is None else float(second['ratio'])
            value=row['fractional_recovery']
            agree=(value is None and ref is None) or (type(value) is float and ref is not None and math.isfinite(value) and abs(value-ref)<=1e-13+1e-11*abs(ref))
            converged=(first['ratio'] is None and ref is None) or (first['ratio'] is not None and abs(Decimal(first['ratio'])-Decimal(second['ratio']))<Decimal('1e-45'))
            residual_error=max(abs(a-bb) for key,rr in zip(('pre_residual_T','frozen_residual_T','recovered_residual_T'),second['residual_T']) for a,bb in zip(ev[key],rr))
            checks += [agree,converged,residual_error<1e-13,ev['solver_success'] is True,ev['recovered_currents_A'][row['failed']]==0.,max(abs(currents[2]))<=c['imax_A']]
            rms=[float(x) for x in second['rms_T']]; den=abs(float(second['denominator_T']))
            # Local input conditioning of the original RMS subtraction, not an error bound.
            naive=(row['frozen_T']-row['recovered_T'])/(row['frozen_T']-row['pre_T']) if abs(row['frozen_T']-row['pre_T'])>1e-15 else None
            ulp_values=[]
            for directions in itertools.product((-math.inf,math.inf),repeat=3):
                a,bb,cc=[math.nextafter(x,d) for x,d in zip((row['pre_T'],row['frozen_T'],row['recovered_T']),directions)]
                if abs(bb-a)>1e-15: ulp_values.append((bb-cc)/(bb-a))
            out['faults'].append(dict(failed=row['failed'],stable=value,legacy_evaluation=naive,
                decimal_60=first['ratio'],decimal_90=second['ratio'],reference_rms_T=second['rms_T'],
                denominator_T=second['denominator_T'],rms_subtraction_condition=(rms[0]+rms[1])/den if den else None,
                stable_absolute_error=None if ref is None or value is None else abs(value-ref),
                legacy_absolute_error=None if ref is None or naive is None else abs(naive-ref),
                one_ulp_naive_range=[min(ulp_values),max(ulp_values)] if ulp_values else None,
                residual_max_error_T=residual_error,reference_agreement=agree,precision_converged=converged))
            out['faults'][-1].update(projected_gradient_dimensionless=float(max(abs(projected))),
                training_ridge_objective=float(wt@((target+train@x)**2)+c['ridge']*(x@x)),
                optimizer_note='Diagnostic projected-gradient magnitude; solver settings unchanged. The failed coordinate is fixed and excluded from the free KKT components.')
        out['checks']=dict(all_faults_independently_verified=all(checks),expected_count=len(out['faults'])==len(q['faults']) and len(q['faults'])>0)
        if not all(out['checks'].values()): raise AssertionError('Independent fault audit failed')
        out['status']='PASS'
    finally:
        (root/'fault-audit.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('Independent 60/90-digit outage audit',out['status'],flush=True)


if __name__=='__main__': main()
