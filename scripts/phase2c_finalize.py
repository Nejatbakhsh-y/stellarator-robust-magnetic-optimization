"""Bind completed Phase 2C evidence and unchanged prior evidence to raw hashes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import gzip
from stellarator_robust.phase2c import require_complete, pair, preserve_previous, load, sha, verify_manifest
from stellarator_robust.evidence import file_hash

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=Path('results/phase2c'))
args = parser.parse_args(); out = args.output
record = require_complete(out)
pair(out, out/'repeat')  # Recheck actual separate repeated calculations, not self equality.
with gzip.open('results/phase2c/investigation/inventory.json.gz','rt') as f:
    if json.load(f)!=load('results/phase2c/history/inventory-initial.json'):
        raise AssertionError('Compressed inventory differs from immutable original')
previous = out/'source_fingerprints_at_run.json'
if not previous.exists():
    previous.write_bytes((out/'source_fingerprints.json').read_bytes())
original = load(previous)
calculation_files = ['src/stellarator_robust/model.py', 'src/stellarator_robust/peak.py',
                     'src/stellarator_robust/experiments.py', 'src/stellarator_robust/optimize.py',
                     'src/stellarator_robust/uncertainty.py', 'src/stellarator_robust/analysis.py',
                     'src/stellarator_robust/validation.py', 'scripts/phase2_study.py']
calculation_files += ['src/stellarator_robust/fault_metrics.py']
for name in calculation_files:
    if original[name] != file_hash(name):
        raise AssertionError('Calculation source changed; numerical rerun required: '+name)
with (out/'final-tests.log').open('w') as log:
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q'], stdout=log, stderr=subprocess.STDOUT)
if result.returncode:
    raise SystemExit(result.returncode)
with (out/'compilation.log').open('w') as log:
    compilation = subprocess.run([sys.executable, '-m', 'compileall', '-q', 'src', 'scripts', 'tests'], stdout=log, stderr=subprocess.STDOUT)
if compilation.returncode:
    raise SystemExit(compilation.returncode)
source = list(Path('src').rglob('*.py'))+list(Path('scripts').glob('*.py'))+list(Path('tests').glob('*.py'))+list(Path('configs').glob('*.json'))+[Path('.gitattributes')]
(out/'source_fingerprints.json').write_text(json.dumps({p.as_posix():file_hash(p) for p in sorted(source)}, indent=2)+'\n')
(out/'integrity.json').write_text(json.dumps(dict(status='PASS', study_sha256=record['study_sha256'],
    quick_sha256=record['quick_sha256'], final_pytest_returncode=0, legacy_evidence=preserve_previous(),
    compilation_returncode=0, compressed_inventory_matches_immutable_original=True,
    calculation_fingerprints_unchanged={name:original[name] for name in calculation_files},
    provenance_note='Final evidence-checker/source fingerprints refreshed after completed calculations; original at-run fingerprints preserved. Calculation source is identical.'), indent=2)+'\n')
paths = [p for p in out.rglob('*') if p.is_file() and p.relative_to(out).as_posix() not in ('manifest.json', 'committed-reference-comparison.json')]
(out/'manifest.json').write_text(json.dumps({p.relative_to(out).as_posix():sha(p) for p in sorted(paths)}, indent=2)+'\n')
verify_manifest(out)
print('Phase 2C complete evidence, source and preservation hashes PASS')
