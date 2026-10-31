"""Read-only Phase 2D artifact investigation; requires Python 3.11, no third-party packages.

Never overwrites output. Keeps all differing JSON leaves (including metadata)
and uses independent Decimal direct RMS arithmetic rather than production code.
A completed investigation of disagreement exits 1; an incomplete one also fails.
"""
import argparse
import csv
from decimal import Decimal, localcontext
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import sys
import tempfile

WORKERS = ('phase2c-windows-reference', 'phase2c-linux-reference',
           'phase2c-linux-numpy-sensitivity', 'phase2c-linux-scipy-sensitivity')
RTOL, ATOL = 1e-11, 1e-13


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def invalid(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('Nonfinite JSON number: ' + value)
        return number
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      parse_constant=invalid, parse_float=finite_float)


def contained(root, name):
    name = name.replace('\\', '/')
    parts = PurePosixPath(name)
    if parts.is_absolute() or '..' in parts.parts or ':' in name:
        raise ValueError('Unsafe evidence path: ' + name)
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Missing/escaping evidence path: ' + name)
    return path


def verify_inventory(root, expected_count=247):
    with (root / 'sha256_inventory.csv').open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ['Path', 'SHA256', 'Bytes']:
            raise ValueError('Unknown inventory schema')
        rows = list(reader)
    if len(rows) != expected_count:
        raise ValueError('Inventory count mismatch')
    seen = set()
    for row in rows:
        path = contained(root, row['Path'])
        if path in seen:
            raise ValueError('Duplicate inventory entry')
        seen.add(path)
        if path.stat().st_size != int(row['Bytes']) or sha(path) != row['SHA256'].lower():
            raise ValueError('Inventory hash/length mismatch: ' + row['Path'])
    actual = {p.resolve() for p in root.rglob('*') if p.is_file()
              and p != root / 'sha256_inventory.csv'}
    if actual != seen:
        raise ValueError('Inventory does not cover exactly the supplied files')
    return {'entries': len(rows), 'sha256': sha(root / 'sha256_inventory.csv')}


def verify_manifest(root):
    manifest = load(root / 'manifest.json')
    expected = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
                and p.relative_to(root).as_posix() not in ('manifest.json', 'committed-reference-comparison.json')}
    if not manifest or manifest.keys() != expected:
        raise ValueError('Worker manifest completeness mismatch: ' + str(root))
    for name, digest in manifest.items():
        if sha(contained(root, name)) != digest:
            raise ValueError('Worker manifest mismatch: ' + name)


def differing_leaves(a, b, path=''):
    """No early stop, numerical rounding, ignored fields or approximate coordinates."""
    if type(a) is dict and type(b) is dict:
        for key in sorted(a.keys() | b.keys()):
            trail = path + '/' + key.replace('~', '~0').replace('/', '~1')
            if key not in a or key not in b:
                yield dict(path=trail, reason='missing-field', reference=a.get(key), observed=b.get(key))
            else:
                yield from differing_leaves(a[key], b[key], trail)
    elif type(a) is list and type(b) is list:
        if len(a) != len(b):
            yield dict(path=path, reason='dimensions', reference=len(a), observed=len(b))
        for i in range(max(len(a), len(b))):
            if i >= len(a) or i >= len(b):
                yield dict(path=f'{path}/{i}', reason='missing-element',
                           reference=a[i] if i < len(a) else None,
                           observed=b[i] if i < len(b) else None)
            else:
                yield from differing_leaves(a[i], b[i], f'{path}/{i}')
    elif type(a) is not type(b) or a != b:
        row = dict(path=path, reason='exact-value', reference=a, observed=b)
        if type(a) in (int, float) and type(b) in (int, float):
            if not math.isfinite(a) or not math.isfinite(b):
                row['reason'] = 'nonfinite'
            else:
                error = abs(a-b)
                threshold = ATOL + RTOL*abs(b) if type(a) is float else 0
                row.update(absolute_error=error, relative_error=error/abs(a) if a else None,
                           acceptance_threshold=threshold)
                row['reason'] = ('type' if type(a) is not type(b) else
                                 'outside-tolerance' if error > threshold else 'within-tolerance')
        yield row


def units(path):
    # Unknown units stay explicit; field names alone cannot establish every unit.
    if 'fractional_recovery' in path:
        return 'dimensionless'
    for ending, unit in (('_T2', 'T^2'), ('_T_per_A', 'T/A'), ('_T', 'T'),
                         ('_A', 'A'), ('_m', 'm'), ('_rad', 'rad')):
        if any(part.endswith(ending) for part in path.split('/')):
            return unit
    if '/seconds' in path:
        return 's'
    return 'not established; review field definition'


def classify(path):
    if '/seconds' in path:
        return 'timing'
    if any('/' + key in path for key in ('metadata', 'environment', 'source_', 'python',
                                         'packages', 'sha256', 'legacy_evidence')):
        return 'metadata'
    return 'scientific-or-unclassified'  # Never excluded from the inventory/gates.


def decimal_inputs(data):
    def d(x):
        if type(x) not in (int, float) or not math.isfinite(x):
            raise ValueError('Invalid finite numeric reference input')
        return Decimal.from_float(float(x))
    A = [[d(x) for x in row] for row in data['response_T_per_A']]
    b = [d(x) for x in data['disturbance_T']]
    w = [d(x) for x in data['weights']]
    if not A or len(A) != len(b) or len(b) != len(w) or not A[0]:
        raise ValueError('Invalid reference dimensions')
    if any(len(row) != len(A[0]) for row in A) or min(w) < 0 or max(w) <= 0:
        raise ValueError('Invalid reference dimensions/weights')
    return A, b, w


def reference(data, currents, precision):
    """Direct high-precision RMS subtraction of exact recorded binary64 inputs."""
    A, b, w = data
    if len(currents) != 3 or any(len(c) != len(A[0]) for c in currents):
        raise ValueError('Invalid current dimensions')
    with localcontext() as ctx:
        ctx.prec = precision
        norms = []
        for current in currents:
            if any(not math.isfinite(x) for x in current):
                raise ValueError('Nonfinite current')
            c = [Decimal.from_float(float(x)) for x in current]
            residual = [bb + sum((a*x for a, x in zip(row, c)), Decimal(0))
                        for row, bb in zip(A, b)]
            norms.append(sum((ww*r*r for ww, r in zip(w, residual)), Decimal(0)).sqrt())
        den = norms[1]-norms[0]
        ratio = None if abs(den) <= Decimal('1e-15') else (norms[1]-norms[2])/den
        return dict(ratio=None if ratio is None else str(ratio),
                    rms_T=[str(v) for v in norms], denominator_T=str(den),
                    subtraction_condition=None if not den else str((norms[1]+norms[0])/abs(den)))


def fault_currents(q, row):
    f = q['faults'][row]
    before = q['currents_A']['dense']
    frozen = list(before)
    frozen[f['failed']] = 0.
    return [before, frozen, f['recovery_evidence']['recovered_currents_A']]


def write(path, data):
    """Publish complete JSON atomically and exclusively; never replace evidence."""
    payload = (json.dumps(data, indent=2, allow_nan=False)+'\n').encode('utf-8')
    fd, temporary = tempfile.mkstemp(prefix='.phase2d-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link publication fails if the destination exists, including races.
        # Unsupported filesystems fail closed rather than falling back to overwrite.
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def validate_output(root, out):
    """--output is a new directory, never a JSON filename or existing tree."""
    if out.exists():
        raise ValueError('Refusing to overwrite output: ' + str(out))
    if out.suffix:
        raise ValueError('--output requires a new directory without a file extension: ' + str(out))
    if out.resolve().is_relative_to(root.resolve()) or root.resolve().is_relative_to(out.resolve()):
        raise ValueError('Output and original evidence trees must be disjoint')


def investigate(root, out):
    validate_output(root, out)
    if sys.version_info[:2] != (3, 11):
        raise RuntimeError('Use the existing Python 3.11 project environment')
    integrity = verify_inventory(root)
    loaded = {}
    for worker in WORKERS:
        folder = root / worker
        verify_manifest(folder)
        loaded[worker] = {
            'q': load(folder / 'quick/results.json'),
            'input': decimal_inputs(load(folder / 'fault-reference-inputs.json')),
            'environment': load(folder / 'execution.json')['environment']}
    out.mkdir(parents=True)
    record = dict(status='RUNNING', scientific_status='PARTIAL', inventory=integrity,
                  environment=dict(python=sys.version, platform=platform.platform()),
                  provenance='User-supplied extraction; authenticated run identity is not established',
                  independent_audits=[], swap_experiments=[], inventory_summary=[])
    try:
        for left, right in itertools.combinations(WORKERS, 2):
            folders = [root / w for w in (left, right)]
            files = [{p.relative_to(f).as_posix() for p in f.rglob('*.json')} for f in folders]
            counts = {}; total = 0
            with gzip.open(out / f'{left}--{right}.jsonl.gz', 'wt', encoding='utf-8') as stream:
                for name in sorted(files[0] | files[1]):
                    if name not in files[0] or name not in files[1]:
                        rows = [dict(path='/' + name, reason='missing-file', reference=name in files[0], observed=name in files[1])]
                    else:
                        rows = differing_leaves(load(folders[0]/name), load(folders[1]/name), '/' + name)
                    for row in rows:
                        row.update(reference_worker=left, observed_worker=right,
                                   units=units(row['path']), category=classify(row['path']),
                                   reference_environment=loaded[left]['environment'],
                                   observed_environment=loaded[right]['environment'])
                        row['scientific_significance'] = ('Requires scientific assessment; not excluded'
                            if row['category'] == 'scientific-or-unclassified' else 'Retained diagnostic/provenance difference')
                        stream.write(json.dumps(row, allow_nan=False)+'\n')
                        total += 1
                        key = row['category'] + ':' + row['reason']
                        counts[key] = counts.get(key, 0)+1
            record['inventory_summary'].append(dict(reference=left, observed=right, differences=total, counts=counts))
        for worker in WORKERS:
            item = loaded[worker]; q = item['q']
            for i, f in enumerate(q['faults']):
                c = fault_currents(q, i)
                first, second = [reference(item['input'], c, p) for p in (60, 90)]
                with localcontext() as ctx:
                    ctx.prec = 100
                    converged = (first['ratio'] is None and second['ratio'] is None) or (
                        first['ratio'] is not None and second['ratio'] is not None and
                        abs(Decimal(first['ratio'])-Decimal(second['ratio'])) < Decimal('1e-45'))
                value = None if second['ratio'] is None else float(second['ratio'])
                saved = f['fractional_recovery']
                error = None if value is None or saved is None else abs(value-saved)
                agrees = (value is None and saved is None) or (error is not None and error <= ATOL+RTOL*abs(value))
                record['independent_audits'].append(dict(worker=worker, row=i, failed=f['failed'],
                    precision_60=first, precision_90=second, converged=converged,
                    saved=saved, absolute_error=error, agrees=agrees,
                    quick_sha256=sha(root/worker/'quick/results.json'),
                    input_sha256=sha(root/worker/'fault-reference-inputs.json')))
            print(worker, 'independent audits completed', flush=True)
        win = loaded[WORKERS[0]]
        for worker in WORKERS[1:]:
            other = loaded[worker]
            for i in (3, 4):
                # Hold every block fixed in turn; do not infer causal attribution from
                # the final scalar alone. Include coupled changes as a fourth case.
                for model_name, current_name in itertools.product(('windows', 'other'), repeat=2):
                    model = win if model_name == 'windows' else other
                    current = win if current_name == 'windows' else other
                    record['swap_experiments'].append(dict(worker=worker, row=i,
                        model=model_name, currents=current_name,
                        reference=reference(model['input'], fault_currents(current['q'], i), 90)))
        record['inventory_after'] = verify_inventory(root)
        if not all(a['agrees'] and a['converged'] for a in record['independent_audits']):
            raise AssertionError('Independent reference or precision agreement failed')
        record.update(status='INVESTIGATION_COMPLETE', numerical_status='NOT_CORRECTED',
                      limitation='Model/current swaps do not individually identify BLAS, geometry or solver causation')
    except Exception as exc:
        record.update(status='FAIL', error=str(exc))
        raise
    finally:
        write(out / 'reference-audit.json', record)
        paths = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'manifest.json')
        write(out / 'manifest.json', {p.relative_to(out).as_posix(): sha(p) for p in paths})
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=Path('results/ci/phase2d-inputs/run-41061184709'))
    parser.add_argument('--output', type=Path, required=True,
                        help='New output DIRECTORY without an extension; existing targets are refused')
    args = parser.parse_args()
    investigate(args.evidence, args.output)
    print('Investigation written; scientific discrepancies remain unresolved', flush=True)
    return 1  # No corrected/reproducible benchmark has been established.


if __name__ == '__main__':
    raise SystemExit(main())
