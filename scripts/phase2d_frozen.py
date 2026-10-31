"""Seal once on Windows; compare identical bytes on four numerical cohorts.

This is an investigation subbenchmark, never a production reproducibility claim.
All outputs must be fresh. No production source or historical evidence is edited.
"""
import argparse
import contextlib
import hashlib
import io
import inspect
import itertools
import json
import math
import platform
import shutil
import sys
import subprocess
from decimal import Decimal, localcontext
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import lsq_linear
from stellarator_robust import frozen_diagnostics as fd
from stellarator_robust.model import Coil,field,benchmark,response
from stellarator_robust.fault_metrics import stable_recovery
from phase2d_investigate import decimal_inputs,reference,fault_currents,differing_leaves


def environment():
    config=io.StringIO()
    with contextlib.redirect_stdout(config):
        np.show_config(); scipy.show_config()
    return dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                source_dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),
                build_and_blas=config.getvalue())


def seal(source,out):
    cfg=fd.manifest(source)
    if (platform.system()!='Windows' or sys.version_info[:2]!=(3,11)
            or np.__version__!='2.4.6' or scipy.__version__!='1.17.1'):
        raise ValueError('Seal on the designated Windows Python 3.11 reference cohort')
    if out.exists() or out.resolve().is_relative_to(source.resolve()): raise ValueError('Fresh disjoint output required')
    shutil.copytree(source,out,ignore=shutil.ignore_patterns('manifest.json'))
    data=fd.load(source/cfg['workers'][0]/'model.json')
    A=np.array(data['response_T_per_A']); b=np.array(data['disturbance_T']); w=np.array(data['weights'])
    D=A*cfg['imax_A']/cfg['bref_T']; d=b/cfg['bref_T']; problems={}
    for failed in (None,3,6):
        support=[j for j in range(A.shape[1]) if j!=failed]
        M=np.vstack([np.sqrt(w)[:,None]*D[:,support],np.sqrt(cfg['ridge'])*np.eye(len(support))])
        y=np.r_[-np.sqrt(w)*d,np.zeros(len(support))]
        problems['dense' if failed is None else 'failed_'+str(failed)]=dict(support=support,M=M.tolist(),y=y.tolist())
    fd.write_new(out/'solver-inputs.json',problems)
    fd.write_new(out/'seal.json',dict(version=fd.VERSION,source_manifest_sha256=fd.sha(source/'manifest.json'),
        environment=environment(),scope='Fine-grid diagnostic M/y assembled once; all cohorts consume identical bytes'))
    fd.write_new(out/'manifest.json',{p.relative_to(out).as_posix():fd.sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    fd.manifest(out)
    print('Sealed immutable shared inputs',fd.sha(out/'manifest.json'),flush=True)


def prepare(source, out):
    """Distribute existing audited bytes; never reassemble numerical inputs."""
    contract=dict(fixture_manifest_sha256=fd.SEALED_MANIFEST_SHA256,
                  sources=fd.source_hashes(), source_environment=environment())
    fd.verify_contract(source, contract)
    contract['bounded_problem']=bounded_problem(fd.load(source/'solver-inputs.json')['dense'])
    if out.exists(): raise ValueError('Fresh output required')
    out.mkdir(parents=True)
    shutil.copytree(source, out/'fixture')
    fd.write_new(out/'contract.json', contract)


def bounded_problem(problem):
    """Separate one-actuator disturbance cancellation at the original current cap.

    Keep M, ridge rows and bounds unchanged. Scale only the physical disturbance
    RHS by an exact power of two, chosen once from the frozen one-column system.
    This stress case is not the historical production objective or fixture solve.
    """
    column=0
    M=np.asarray(problem['M'],dtype=float)[:,column:column+1]
    y=np.asarray(problem['y'],dtype=float)
    unbounded=float((M[:,0]@y)/(M[:,0]@M[:,0]))
    if not math.isfinite(unbounded) or unbounded==0: raise ValueError('Invalid bounded diagnostic')
    scale=2.**max(0,math.ceil(math.log2(2./abs(unbounded))))
    y=y*scale
    exact=float(np.clip(unbounded*scale,-1.,1.))
    return dict(M=M.tolist(),y=y.tolist(),support=[problem['support'][column]],
                disturbance_scale=scale,analytic_clipped_solution=exact)


def bounded_diagnostic(problem, cfg):
    M=np.asarray(problem['M']); y=np.asarray(problem['y'])
    result=solve(M,y,cfg)
    exact=problem['analytic_clipped_solution']
    residual=M[:,0]*exact-y
    expected_cost=float(residual@residual)/2
    passed=(result['success'] and result['nit']>0 and abs(result['active_mask'][0])==1
            and not fd.scalar_differences([exact,expected_cost],[result['x'][0],result['cost']]))
    return dict(scope='Separate single-actuator amplified-disturbance stress diagnostic',
                support=problem['support'],disturbance_scale=problem['disturbance_scale'],M=M.tolist(),y=y.tolist(),
                matrix_sha256=hashlib.sha256(M.astype('<f8').tobytes()).hexdigest(),
                rhs_sha256=hashlib.sha256(y.astype('<f8').tobytes()).hexdigest(),
                analytic_clipped_solution=exact,analytic_cost=expected_cost,result=result,passed=passed)


def solve(M,y,cfg):
    """Observe the existing SciPy call; verbose logging does not alter settings."""
    calls=[]; original=np.linalg.lstsq; log=io.StringIO()
    def observe(a,b,*args,**kwargs):
        matrix_sha=hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
        rhs_sha=hashlib.sha256(np.asarray(b,dtype='<f8').tobytes()).hexdigest()
        result=original(a,b,*args,**kwargs)
        calls.append(dict(matrix_sha256=matrix_sha,rhs_sha256=rhs_sha,
                          rcond=kwargs.get('rcond',args[0] if args else None),
                          x=result[0].tolist(),residuals=result[1].tolist(),rank=int(result[2]),singular_values=result[3].tolist()))
        return result
    np.linalg.lstsq=observe
    try:
        with contextlib.redirect_stdout(log):
            fit=lsq_linear(M,y,bounds=tuple(cfg['bounds']),tol=cfg['solver_tol'],max_iter=cfg['solver_max_iter'],verbose=2)
    finally:
        np.linalg.lstsq=original
    source=Path(inspect.getsourcefile(inspect.unwrap(lsq_linear)))
    def plain(value):
        if isinstance(value,np.ndarray):return value.tolist()
        if isinstance(value,np.generic):return value.item()
        if isinstance(value,(tuple,list)):return [plain(x) for x in value]
        return value
    return dict(x=fit.x.tolist(),cost=float(fit.cost),optimality=float(fit.optimality),
        status=int(fit.status),nit=int(fit.nit),success=bool(fit.success),message=str(fit.message),
        active_mask=fit.active_mask.tolist(),initial_lstsq_calls=calls,verbose_trace=log.getvalue(),
        public_unbounded_initialization=plain(fit.unbounded_sol),
        scipy_lsq_source_sha256=fd.sha(source),
        trajectory_scope=('No bounded iterations: accepted unconstrained initialization' if fit.nit==0 else
                          'Verbose iteration table retained; per-iterate vectors unavailable from this public API'))


def run(root,out,cohort,contract_path,contract_sha256):
    cfg=fd.manifest(root)
    if fd.sha(contract_path)!=contract_sha256: raise ValueError('Execution contract fingerprint mismatch')
    contract=fd.load(contract_path)
    fd.verify_contract(root,contract)
    if out.exists() or out.resolve().is_relative_to(root.resolve()): raise ValueError('Fresh disjoint output required')
    if sys.version_info[:2]!=(3,11): raise ValueError('Python 3.11 required')
    expected={'windows-reference':('Windows','2.4.6','1.17.1'),
              'linux-reference':('Linux','2.4.6','1.17.1'),
              'linux-numpy-sensitivity':('Linux','2.3.5','1.17.1'),
              'linux-scipy-sensitivity':('Linux','2.4.6','1.16.3')}
    if (platform.system(),np.__version__,scipy.__version__)!=expected[cohort]:
        raise ValueError('Actual numerical environment does not match named cohort')
    out.mkdir(parents=True)
    report=dict(status='FAIL',completed=False,scientific_status='PARTIAL',version=fd.VERSION,cohort=cohort,
                fixture_manifest_sha256=fd.sha(root/'manifest.json'),environment=environment(),
                calculation_sources=fd.source_hashes(), execution_contract=contract,
                primary={},diagnostics={},local_checks={})
    try:
        geometry=fd.load(root/cfg['geometry_file'])
        if len(geometry['coils'])!=25 or any(len(c['vertices'])!=512 for c in geometry['coils']):
            raise ValueError('Wrong frozen benchmark geometry')
        coils=[Coil(np.array(c['vertices'])) for c in geometry['coils']]; points=np.array(cfg['points_m'])
        production=[]; precise=[]; reference_checks=[]; differences=[]
        for i,c in enumerate(coils):
            prod=field(points,c,current=1.,min_distance=cfg['min_distance_m']).tolist()
            low=fd.decimal_field(cfg['points_m'],c.vertices.tolist(),precision=80)
            high=fd.decimal_field(cfg['points_m'],c.vertices.tolist(),precision=110)
            with localcontext() as ctx:
                ctx.prec=130
                converged=all(abs(Decimal(a)-Decimal(b))<Decimal('1e-60') for r,s in zip(low,high) for a,b in zip(r,s))
            ref=[[float(x) for x in row] for row in high]
            err=fd.vector_errors(ref,prod)
            differences.append(dict(coil=i,errors=err)); reference_checks.append(converged)
            production.append(prod); precise.append(high)
        report['primary']['unit_coil_B_T']=production
        report['primary']['decimal_unit_coil_B_T']=precise
        report['diagnostics']['unit_component_errors']=differences
        q=fd.load(root/cfg['workers'][0]/'quick.json'); cases={}
        for name in ('dense','matched_nominal','robust'):
            cases[name]=q['currents_A'][name]+[1500.]
        for row in cfg['fault_rows']:
            for label,cur in zip(('pre','frozen','recovered'),fault_currents(q,row)):
                cases['row_'+str(row)+'_'+label]=cur+[1500.]
        if any(len(cur)!=25 for cur in cases.values()):raise ValueError('Invalid frozen current dimensions')
        bits=lambda value:hashlib.sha256(np.asarray(value,dtype='<f8').tobytes()).hexdigest()
        report['primary']['frozen_input_binary64']=dict(points=bits(cfg['points_m']),
            vertices=bits([c.vertices.tolist() for c in coils]),currents={name:bits(cur) for name,cur in cases.items()},solver_inputs={})
        totals={}; total_checks=[]
        for name,currents in cases.items():
            # Direct current evaluation includes production coefficient rounding.
            per=[field(points,c,current=amp).tolist() for c,amp in zip(coils,currents)]
            compensated=[[math.fsum(p[i][j] for p in per) for j in range(3)] for i in range(len(points))]
            unit_scaled=[[math.fsum(float(amp)*production[k][i][j] for k,amp in enumerate(currents)) for j in range(3)] for i in range(len(points))]
            with localcontext() as ctx:
                ctx.prec=110
                exact=[[float(sum((Decimal(precise[k][i][j])*fd.finite(amp) for k,amp in enumerate(currents)),Decimal(0))) for j in range(3)] for i in range(len(points))]
            errors=fd.vector_errors(exact,compensated)
            scaled_errors=fd.vector_errors(exact,unit_scaled)
            total_checks.extend(x for r in errors for x in r['passes'])
            total_checks.extend(x for r in scaled_errors for x in r['passes'])
            totals[name]=dict(currents_A=currents,direct_fsum_B_T=compensated,unit_scaled_fsum_B_T=unit_scaled)
            report['diagnostics'].setdefault('total_field_errors',{})[name]=dict(direct_current=errors,unit_scaled=scaled_errors)
        report['primary']['fixed_current_totals']=totals
        report['local_checks']['field_reference_converged']=all(reference_checks)
        report['local_checks']['raw_components_match_independent_reference']=all(x for c in differences for r in c['errors'] for x in r['passes']) and all(total_checks)
        problems=fd.load(root/'solver-inputs.json'); solved={}; solver_checks=[]
        for name,p in problems.items():
            M=np.array(p['M']); y=np.array(p['y']); result=solve(M,y,cfg)
            report['primary']['frozen_input_binary64']['solver_inputs'][name]=dict(M=bits(p['M']),y=bits(p['y']))
            low=fd.decimal_lsq(p['M'],p['y'],90); high=fd.decimal_lsq(p['M'],p['y'],120)
            with localcontext() as ctx:
                ctx.prec=140
                converge=all(abs(Decimal(a)-Decimal(b))<Decimal('1e-60') for a,b in zip(low['x'],high['x']))
            current=[0.]*24; ref=[0.]*24
            with localcontext() as ctx:
                ctx.prec=130
                for j,x,r in zip(p['support'],result['x'],high['x']):
                    current[j]=x*cfg['imax_A'];ref[j]=float(Decimal(r)*fd.finite(cfg['imax_A']))
            errors=fd.scalar_differences(ref,current,'/current_A')
            objective_errors=fd.scalar_differences(float(high['squared_augmented_residual']),2*result['cost'],'/objective')
            solver_checks += [converge,high['strictly_interior'],result['success'],not errors,not objective_errors]
            solved[name]=dict(current_A=current,squared_augmented_residual=2*result['cost'])
            report['diagnostics'].setdefault('frozen_solver',{})[name]=dict(result=result,
                reference_90=low,reference_120=high,reference_precision_converged=converge,current_errors=errors,objective_errors=objective_errors)
        report['primary']['frozen_solver']=solved
        report['local_checks']['frozen_solutions_match_interior_reference']=all(solver_checks)
        bounded=bounded_diagnostic(contract['bounded_problem'],cfg)
        report['diagnostics']['bounded_iteration_stress']=bounded
        report['local_checks']['separate_bounded_iteration_control']=bounded['passed']
        # Native regeneration is an attribution control, never confused with frozen inputs.
        p,n,w,cc,ee,b=benchmark(10,24,512,8,3,'householder-v2')
        A=response(p,n,cc); D=A*cfg['imax_A']/cfg['bref_T']; d=b/cfg['bref_T']
        native={}
        archived=fd.load(root/('phase2c-'+cohort)/'quick.json')
        for failed in (None,3,6):
            support=[j for j in range(24) if j!=failed]
            M=np.vstack([np.sqrt(w)[:,None]*D[:,support],np.sqrt(cfg['ridge'])*np.eye(len(support))]); y=np.r_[-np.sqrt(w)*d,np.zeros(len(support))]
            result=solve(M,y,cfg); full=np.zeros(24);full[support]=np.array(result['x'])*cfg['imax_A']
            saved=archived['currents_A']['dense'] if failed is None else next(r['recovery_evidence']['recovered_currents_A'] for r in archived['faults'] if r['failed']==failed)
            native['dense' if failed is None else 'failed_'+str(failed)]=dict(result=result,
                current_A=full.tolist(),archived_current_A=saved,archived_differences=fd.scalar_differences(saved,full.tolist()),M=M.tolist(),y=y.tolist())
        report['diagnostics']['native_training']=dict(points_m=p.tolist(),normals=n.tolist(),weights=w.tolist(),
            coil_vertices_m=[c.vertices.tolist() for c in cc]+[ee.vertices.tolist()],
            cartesian_unit_coil_B_T=[field(p,c).tolist() for c in cc+[ee]],
            response_T_per_A=A.tolist(),disturbance_T=b.tolist(),solves=native)
        # Retain the two original failures and all four model/current combinations.
        audits=[]; swaps=[]; metric_checks=[]
        loaded={worker:(fd.load(root/worker/'quick.json'),fd.load(root/worker/'model.json')) for worker in cfg['workers']}
        for worker,(quick,model) in loaded.items():
            for row in cfg['fault_rows']:
                cur=fault_currents(quick,row)
                low=reference(decimal_inputs(model),cur,80); high=reference(decimal_inputs(model),cur,110)
                stable=stable_recovery(model['response_T_per_A'],model['disturbance_T'],model['weights'],*cur)['fractional_recovery']
                target=float(high['ratio'])
                with localcontext() as ctx:
                    ctx.prec=130
                    converge=abs(Decimal(low['ratio'])-Decimal(high['ratio']))<Decimal('1e-60')
                error=abs(stable-target); agree=error<=fd.ATOL+fd.RTOL*abs(target)
                metric_checks += [converge,agree]
                audits.append(dict(worker=worker,row=row,failed_coil=quick['faults'][row]['failed'],
                    saved=quick['faults'][row]['fractional_recovery'],compensated=stable,reference_80=low,reference_110=high,
                    precision_converged=converge,absolute_error=error,within_gate=agree))
        win=loaded[cfg['workers'][0]]
        for worker in cfg['workers'][1:]:
            for row in cfg['fault_rows']:
                for m,c in itertools.product((0,1),repeat=2):
                    model=(win,loaded[worker])[m][1]; quick=(win,loaded[worker])[c][0]
                    swaps.append(dict(worker=worker,row=row,other_model=bool(m),other_currents=bool(c),
                        reference_110=reference(decimal_inputs(model),fault_currents(quick,row),110)))
        report['diagnostics']['original_recovery_audits']=audits;report['diagnostics']['original_swaps']=swaps
        report['local_checks']['recorded_metric_arithmetic_agrees_with_independent_reference']=all(metric_checks)
        fd.manifest(root)
        report['completed']=True
        report['status']='FIXED_INPUT_SUBBENCHMARK_PASS' if all(report['local_checks'].values()) else 'FAIL'
    except Exception as exc:
        report['error']=str(exc)
        raise
    finally:
        fd.write_new(out/'record.json',report)
        fd.write_new(out/'sources.json',fd.source_hashes())
        fd.write_new(out/'manifest.json',{p.relative_to(out).as_posix():fd.sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    return 0 if report['status']=='FIXED_INPUT_SUBBENCHMARK_PASS' else 1


def verify_evidence(root):
    entries=fd.load(root/'manifest.json')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix()!='manifest.json'}
    if not entries or entries.keys()!=actual or not {'record.json','sources.json'}<=entries.keys():
        raise ValueError('Incomplete worker manifest')
    for name,digest in entries.items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or fd.sha(path)!=digest: raise ValueError('Worker hash/path mismatch')
    return fd.load(root/'record.json')


def compare(left,right,out):
    if out.exists(): raise ValueError('Refusing to replace comparison')
    records=[]
    for root in (left,right):
        record=verify_evidence(root)
        if record['version']!=fd.VERSION: raise ValueError('Unknown diagnostic worker version')
        if 'calculation_sources' in record and fd.load(root/'sources.json')!=record['calculation_sources']:
            raise ValueError('Worker calculation sources disagree with manifest sources')
        records.append(record)
    same_inputs=records[0]['fixture_manifest_sha256']==records[1]['fixture_manifest_sha256']
    same_sources=(records[0].get('calculation_sources')==records[1].get('calculation_sources')==fd.source_hashes())
    same_contract=(records[0].get('execution_contract')==records[1].get('execution_contract')
                   and records[0].get('execution_contract',{}).get('sources')==fd.source_hashes())
    pinned_inputs=all(r['fixture_manifest_sha256']==fd.SEALED_MANIFEST_SHA256 for r in records)
    reference_cohort=records[0].get('cohort')=='windows-reference'
    current_cohort=records[1].get('cohort') in {'linux-reference','linux-numpy-sensitivity','linux-scipy-sensitivity'}
    same_commit=(records[0].get('environment',{}).get('source_commit') is not None
                 and records[0].get('environment',{}).get('source_commit')==records[1].get('environment',{}).get('source_commit'))
    failures=fd.scalar_differences(records[0]['primary'],records[1]['primary'])
    raw=list(differing_leaves(records[0],records[1]))
    out.parent.mkdir(parents=True,exist_ok=True)
    checks={'field_reference_converged','raw_components_match_independent_reference',
            'frozen_solutions_match_interior_reference','recorded_metric_arithmetic_agrees_with_independent_reference',
            'separate_bounded_iteration_control'}
    fields={'unit_coil_B_T','decimal_unit_coil_B_T','fixed_current_totals','frozen_solver','frozen_input_binary64'}
    workers_complete=all(r['completed'] is True and r['status']=='FIXED_INPUT_SUBBENCHMARK_PASS'
        and r['local_checks'].keys()==checks and all(x is True for x in r['local_checks'].values())
        and r['primary'].keys()==fields for r in records)
    failed=(bool(failures) or not same_inputs or not pinned_inputs or not same_sources or not same_contract
            or not reference_cohort or not current_cohort or not same_commit or not workers_complete)
    fd.write_new(out,dict(status='FAIL' if failed else 'FIXED_INPUT_SUBBENCHMARK_PASS',scientific_status='PARTIAL',
        identical_input_bytes=same_inputs,pinned_inputs=pinned_inputs,identical_calculation_sources=same_sources,
        identical_execution_contract=same_contract,
        expected_cohort_pair=reference_cohort and current_cohort,identical_checkout_commit=same_commit,
        worker_statuses=[r['status'] for r in records],workers_completed=[r['completed'] for r in records],
        version=fd.VERSION,fixture_manifest_sha256=records[0]['fixture_manifest_sha256'],failures=failures,
        all_raw_differences=raw,scope='All raw differences retained. Only common-input primary field/current/objective quantities determine this subbenchmark gate; native replay, traces, archived failures and environment remain explicit diagnostics. No full production reproducibility claim.'))
    return 1 if failed else 0


def main():
    p=argparse.ArgumentParser(description=__doc__); s=p.add_subparsers(dest='command',required=True)
    sealp=s.add_parser('seal');sealp.add_argument('--source',type=Path,default=Path('benchmarks/phase2d-frozen-v1'));sealp.add_argument('--output',type=Path,required=True)
    prep=s.add_parser('prepare');prep.add_argument('--source',type=Path,default=Path('benchmarks/phase2d-sealed-v1'));prep.add_argument('--output',type=Path,required=True)
    runp=s.add_parser('run');runp.add_argument('--fixture',type=Path,required=True);runp.add_argument('--output',type=Path,required=True)
    runp.add_argument('--cohort',choices=['windows-reference','linux-reference','linux-numpy-sensitivity','linux-scipy-sensitivity'],required=True)
    runp.add_argument('--contract',type=Path,required=True)
    runp.add_argument('--contract-sha256',required=True)
    cmp=s.add_parser('compare');cmp.add_argument('--reference',type=Path,required=True);cmp.add_argument('--current',type=Path,required=True);cmp.add_argument('--output',type=Path,required=True)
    verify=s.add_parser('verify-evidence');verify.add_argument('--root',type=Path,required=True)
    args=p.parse_args()
    if args.command=='seal':seal(args.source,args.output);return 0
    if args.command=='prepare':prepare(args.source,args.output);return 0
    if args.command=='verify-evidence':verify_evidence(args.root);print('Worker manifest verified; no scientific execution implied');return 0
    if args.command=='run':return run(args.fixture,args.output,args.cohort,args.contract,args.contract_sha256)
    try:
        return compare(args.reference,args.current,args.output)
    except Exception as exc:
        if args.output.exists(): raise
        args.output.parent.mkdir(parents=True,exist_ok=True)
        fd.write_new(args.output,dict(status='FAIL',scientific_status='PARTIAL',
            error=str(exc),reason='Missing, tampered or incomplete comparison evidence'))
        return 1


if __name__=='__main__': raise SystemExit(main())
