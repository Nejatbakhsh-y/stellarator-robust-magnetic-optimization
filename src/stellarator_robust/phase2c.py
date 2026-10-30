"""Phase 2C benchmark contract; original Phase 2B defaults remain intact."""
from pathlib import Path
import subprocess
import math
from .phase2b import (pair as old_pair, preserve_legacy, sha, load, environment,
                     attest, require_complete as previous_complete, verify_manifest)
from .ci_evidence import compare, compare_study

VERSION = 'phase2c-householder-v2-pattern-v2-energy-v3'
BASE = '74fddfe3a2a7cf95ee334f8bc1ec7757ef22c379'
INVENTORY_SHA256='0af5f1618a7e0722a015bdd3388da69d52fe95e3c386e4f3eb95bdadbfee899a'
ARTIFACTS={
    'phase2b-windows-reference.zip':'53a3878f7535bc798636027f734bc511aa9c44f744edb842f4f162f00631be82',
    'phase2b-linux-reference.zip':'3e5103fd3cc8242ad551d14149866b28e54ac852e853864c65be9f702462dea8',
    'phase2b-linux-numpy-sensitivity.zip':'e2f3efbbd7690ef03de89463307a925ad3aa004293d770f91a4fe57367d26fcd',
    'phase2b-linux-scipy-sensitivity.zip':'43348ecaa87d8126a25fae9374c0a8f18d823e09ae73aeb3d49066283ddf0e13',
    'phase2b-cross-platform.zip':'59850854fed914ecddc2466e1606c88867d28066e9f04120ab1911ea9a495c83',
}


def preserve_previous():
    hashes = preserve_legacy()
    for name in subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
                                         'results/phase2b'], text=True).splitlines():
        if subprocess.check_output(['git', 'show', BASE+':'+name]) != Path(name).read_bytes():
            raise AssertionError('Phase 2B evidence changed: '+name)
        hashes[name] = sha(name)
    for name,digest in ARTIFACTS.items():
        path='results/phase2c/history/'+name
        if sha(path)!=digest: raise AssertionError('Failure artifact changed: '+name)
        hashes[path]=digest
    for name in ('history/inventory-initial.json','investigation/inventory.json'):
        path='results/phase2c/'+name
        if sha(path)!=INVENTORY_SHA256: raise AssertionError('Initial inventory changed: '+name)
        hashes[path]=INVENTORY_SHA256
    return hashes


def require_complete(root):
    record=previous_complete(root)
    audit=load(Path(root)/'fault-audit.json')
    legacy=load(Path(root)/'legacy-scientific-comparison.json')
    if (legacy['status']!='PASS' or legacy['quick_sha256']!=record['quick_sha256']
            or legacy['study_sha256']!=record['study_sha256']):
        raise AssertionError('Unchanged scientific output comparison failed')
    if (record['benchmark_version']!=VERSION or audit['status']!='PASS'
            or audit['quick_sha256']!=record['quick_sha256']
            or not audit['checks'] or not all(audit['checks'].values())):
        raise AssertionError('Independent fault metric audit/link failed')
    if sha(Path(root)/'fault-reference-inputs.json')!=audit['reference_inputs_sha256']:
        raise AssertionError('Independent fault reference input hash mismatch')
    faults=load(Path(root)/'quick/results.json')['faults']
    if [x['failed'] for x in faults]!=[x['failed'] for x in audit['faults']] or not faults:
        raise AssertionError('Independent fault audit coverage mismatch')
    for row,checked in zip(faults,audit['faults']):
        ev=row['recovery_evidence']; value=row['fractional_recovery']
        if (ev['fractional_recovery']!=value or not ev['solver_success']
                or checked['stable']!=value or checked['reference_agreement'] is not True
                or checked['precision_converged'] is not True):
            raise AssertionError('Invalid independent fault audit')
        if value is not None:
            ref=float(checked['decimal_90'])
            if type(value) is not float or not math.isfinite(value) or not math.isfinite(ref) or abs(value-ref)>1e-13+1e-11*abs(ref):
                raise AssertionError('Independent fault reference mismatch')
    return record


class ScientificMismatch(AssertionError):
    def __init__(self, report):
        self.report = report
        super().__init__(str(len(report['failures']))+' scientific comparison failures')


def collector(failures):
    """Traverse all comparable leaves while preserving the original comparator."""
    def collect(a,b,trail='',records=None,exact=False,approximate_paths=frozenset()):
        if type(a) is dict and type(b) is dict and a.keys()==b.keys():
            for k in a: collect(a[k],b[k],trail+'/'+k,records,exact,approximate_paths)
        elif type(a) is list and type(b) is list and len(a)==len(b):
            for i,(x,y) in enumerate(zip(a,b)): collect(x,y,trail+'/'+str(i),records,exact,approximate_paths)
        else:
            try: compare(a,b,trail,records,exact,approximate_paths)
            except AssertionError as exc:
                failures.append(dict(path=trail,reference=a,current=b,error=str(exc)))
    return collect


def pair(left,right):
    for root in (Path(left),Path(right)):
        c=load(root/'quick/results.json')['metadata']['config']
        if c.get('fault_metric_version') != 'residual-energy-v3':
            raise AssertionError('Wrong fault metric benchmark')
        for row in load(root/'quick/results.json')['faults']:
            if row['recovery_evidence']['evaluation_version']!='residual-energy-v3':
                raise AssertionError('Missing versioned recovery evidence')
    failures=[]; collect=collector(failures)
    def study(a,b,actual):
        before=len(failures)
        report=compare_study(a,b,actual=actual,comparator=collect)
        report['status']='FAIL' if len(failures)>before else 'PASS'
        return report
    result=old_pair(left,right,version=VERSION,comparator=collect,study_comparator=study)
    result['failures']=failures
    result['status']='FAIL' if failures else 'PASS'
    if failures: raise ScientificMismatch(result)
    return result
