"""Probe cancellation using exact binary64 inputs and 70-digit decimal arithmetic."""
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path
import numpy as np
from stellarator_robust.model import benchmark, response, surface, field
from stellarator_robust.optimize import baseline

q=json.loads(Path('results/phase2b/quick/results.json').read_text()); c=q['metadata']['config']
p,n,w,coils,error,b=benchmark(c['nt'],c['np'],c['segments'],c['nphi'],c['ntheta'],'householder-v2')
A=response(p,n,coils); D=A*c['imax_A']/c['bref_T']; d=b/c['bref_T']
pv,nv,av=surface(1.,.25,2*c['nt'],2*c['np'],.5); wv=av/av.sum()
Av=response(pv,nv,coils); bv=np.sum(field(pv,error,1500)*nv,axis=1)
dense,_=baseline(D,d,w,c['ridge']); out=[]
for failed in range(len(coils)):
    frozen=dense.copy(); frozen[failed]=0
    recovered,status=baseline(D,d,w,c['ridge'],np.delete(np.arange(len(coils)),failed))
    currents=[x*c['imax_A'] for x in (dense,frozen,recovered)]
    rr=[bv+Av@x for x in currents]; rms=[math.sqrt(math.fsum(float(ww)*float(y)*float(y) for ww,y in zip(wv,r))) for r in rr]
    def energy(i,j):
        delta=Av@(currents[i]-currents[j])
        return math.fsum(float(ww)*float(dd)*(2*float(y)+float(dd)) for ww,dd,y in zip(wv,delta,rr[j]))
    stable=energy(1,2)/energy(1,0)*(rms[1]+rms[0])/(rms[1]+rms[2])
    with localcontext() as ctx:
        ctx.prec=70
        dec=lambda v:Decimal.from_float(float(v))
        residuals=[[dec(bb)+sum((dec(aa)*dec(ii) for aa,ii in zip(row,x)),Decimal(0)) for bb,row in zip(bv,Av)] for x in currents]
        norms=[sum((dec(ww)*y*y for ww,y in zip(wv,r)),Decimal(0)).sqrt() for r in residuals]
        reference=float((norms[1]-norms[2])/(norms[1]-norms[0]))
    row=dict(failed=failed,naive=(rms[1]-rms[2])/(rms[1]-rms[0]),stable=stable,decimal_reference=reference,
             stable_error=abs(stable-reference),naive_error=abs((rms[1]-rms[2])/(rms[1]-rms[0])-reference),
             rms_T=rms,denominator_T=rms[1]-rms[0],subtraction_condition=(rms[1]+rms[0])/abs(rms[1]-rms[0]),
             recovered_currents_A=currents[2].tolist())
    out.append(row); print(failed,stable,reference,row['stable_error'],flush=True)
Path('results/phase2c/investigation/probe.json').write_text(json.dumps(dict(rows=out,dense_currents_A=currents[0].tolist()),indent=2)+'\n')
