"""Exhaustive diagnostic inventory; never converts a failed comparison to PASS."""
import argparse
import itertools
import json
import math
import gzip
from pathlib import Path
from stellarator_robust.phase2b import load, sha, verify_manifest, require_complete


def inventory(a, b, path=''):
    rows = []
    def add(reason):
        row = dict(path=path, reason=reason, reference=a, current=b)
        if type(a) is float and type(b) is float and math.isfinite(a) and math.isfinite(b):
            row.update(absolute_error=abs(a-b), permitted_error=1e-13+1e-11*abs(b))
        rows.append(row)
    if type(a) is not type(b):
        add('type'); return rows
    if isinstance(a, dict):
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                rows.append(dict(path=path+'/'+key, reason='missing-field'))
            else:
                rows += inventory(a[key], b[key], path+'/'+key)
    elif isinstance(a, list):
        if len(a) != len(b): add('dimensions')
        for i, (x, y) in enumerate(zip(a, b)):
            rows += inventory(x, y, path+'/'+str(i))
    elif type(a) is float:
        if not math.isfinite(a) or not math.isfinite(b): add('nonfinite')
        elif a != b:
            add('outside-tolerance' if abs(a-b) > 1e-13+1e-11*abs(b) else 'within-tolerance')
    elif a != b:
        add('exact-value')
    return rows


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--artifacts', type=Path, default=Path('results/ci/phase2c-failures'))
    p.add_argument('--output', type=Path, default=Path('results/phase2c/investigation/inventory.json.gz'))
    args = p.parse_args()
    roots = [Path('results/phase2b')] + sorted(x for x in args.artifacts.glob('phase2b-*')
                                             if x.is_dir() and (x/'execution.json').exists())
    assert len(roots) == 5
    records = []
    for root in roots:
        verify_manifest(root); require_complete(root)
    for a, b in itertools.combinations(roots, 2):
        groups = {}
        for name, file in [('quick', 'quick/results.json'), ('study', 'study/study.json'),
                           ('geometry', 'investigation/geometry.json'), ('analysis', 'investigation/analysis.json')]:
            rows = inventory(load(a/file), load(b/file), '/'+name)
            groups[name] = dict(differences=rows, total_differing_leaves=len(rows),
                                outside_tolerance=sum(r['reason']=='outside-tolerance' for r in rows))
        records.append(dict(reference=str(a), current=str(b), groups=groups))
    result = dict(status='DIAGNOSTIC_ONLY', run_id=41044895641, comparisons=records,
                  note='Includes every raw differing leaf, including provenance and adaptive diagnostics; no first-error stop or failed-field exclusion.',
                  artifacts={x.name:sha(x) for x in sorted(args.artifacts.glob('*.zip'))})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(filename=str(args.output),mode='wb',mtime=0) as f:
        f.write((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    summary=[]
    for r in records:
        primary={k:[x for x in v['differences'] if x['reason'] not in ('within-tolerance',)
                    and '/metadata/' not in x['path'] and '/solver/' not in x['path']
                    and '/solver_status/' not in x['path'] and 'source_' not in x['path']
                    and not x['path'].endswith('/python') and not x['path'].endswith('/phase1_sha256')]
                 for k,v in r['groups'].items() if k in ('quick','study')}
        summary.append(dict(reference=r['reference'],current=r['current'],primary=primary))
    args.output.with_name('inventory-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    for r in records:
        print(r['current'], {k:v['outside_tolerance'] for k,v in r['groups'].items()})
