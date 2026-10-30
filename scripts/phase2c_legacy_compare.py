"""Grade unchanged Phase 2B scientific quantities; enumerate intentional metric changes."""
import argparse
import copy
import json
from pathlib import Path
from stellarator_robust.phase2c import collector, preserve_previous
from stellarator_robust.phase2b import load,sha
from stellarator_robust.ci_evidence import clearance_paths,compare_study

p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path('results/phase2c'))
args=p.parse_args(); root=args.root; failures=[]; compare=collector(failures)
a=load('results/phase2b/quick/results.json'); b=load(root/'quick/results.json')
out=dict(status='FAIL',quick_sha256=sha(root/'quick/results.json'),study_sha256=sha(root/'study/study.json'),
         preserved=preserve_previous(),intentional_fault_evaluation_changes=[],numeric_differences=[],excluded=[])
try:
    ma,mb=a.pop('metadata'),b.pop('metadata')
    assert mb['config'].pop('fault_metric_version')=='residual-energy-v3'
    compare(ma['config'],mb['config'],'/quick/config',exact=True)
    for key in ('units','condition_number','rank','clearance_sampled_m'):
        compare(ma[key],mb[key],'/quick/metadata/'+key,records=out['numeric_differences'])
    for key in ('source_commit','source_dirty','python','packages','elapsed_seconds'):
        out['excluded'].append(dict(path='/quick/metadata/'+key,reference=ma[key],current=mb[key]))
    for data in (a,b):
        for method,status in data['solver_status'].items():
            for key in ('seconds','iterations'):
                if key in status: out['excluded'].append(dict(path='/quick/solver_status/'+method+'/'+key,value=status.pop(key)))
    assert len(a['faults'])==len(b['faults'])
    for old,new in zip(a['faults'],b['faults']):
        evidence=new.pop('recovery_evidence')
        assert evidence['evaluation_version']=='residual-energy-v3'
        out['intentional_fault_evaluation_changes'].append(dict(failed=old['failed'],
            original=old.pop('fractional_recovery'),corrected=new.pop('fractional_recovery'),
            reason='Versioned algebraically equivalent energy-difference evaluation; original evidence not changed'))
    for data in (a,b):
        s=data.pop('scenarios')
        data['scenario_contract']=dict(holdout=s['holdout'],training={'quick':s['train']})
    paths=clearance_paths(a['scenario_contract'])
    assert paths==clearance_paths(b['scenario_contract'])
    compare(a.pop('scenario_contract'),b.pop('scenario_contract'),'/scenarios',exact=True,approximate_paths=paths,records=out['numeric_differences'])
    compare(a,b,'/quick',records=out['numeric_differences'])
    left=load('results/phase2b/study/study.json'); right=load(root/'study/study.json')
    record=load(root/'execution.json')
    assert left['phase1_sha256']==sha('results/phase2b/quick/results.json')
    assert right['phase1_sha256']==sha(root/'quick/results.json')
    assert (root/'study/phase1_input.json').read_bytes()==(root/'quick/results.json').read_bytes()
    assert left['config']['phase1_input']=='results/phase2b/quick/results.json'
    assert right['config']['phase1_input']=='results/phase2c/quick/results.json'
    left['phase1_sha256']=right['phase1_sha256']
    left['config']['phase1_input']=right['config']['phase1_input']
    result=compare_study(left,right,actual=record['study_runtime'],comparator=compare)
    result['status']='FAIL' if failures else 'PASS'; out['study']=result
    out['failures']=failures
    if failures: raise AssertionError('Unintended scientific changes')
    out['status']='PASS'
finally:
    (root/'legacy-scientific-comparison.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('Unchanged Phase 2B scientific outputs:',out['status'])
