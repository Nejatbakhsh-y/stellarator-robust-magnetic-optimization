"""Refresh serialization provenance, only after non-numerical changes.

New scientific calculations require phase2_verify.py and full repeated studies.
"""
import json
import subprocess
import sys
from pathlib import Path
from stellarator_robust.evidence import file_hash

out = Path('results/phase2')
(out/'phase1_input.json').write_bytes(Path('results/quick/results.json').read_bytes())
result = subprocess.run([sys.executable, '-m', 'pytest', '-q'], capture_output=True, text=True)
commands = json.loads((out/'commands.json').read_text())
commands[0] = {'command': [sys.executable, '-m', 'pytest', '-q'], 'returncode': result.returncode,
               'stdout': result.stdout, 'stderr': result.stderr}
(out/'commands.json').write_text(json.dumps(commands, indent=2))
print(result.stdout, flush=True)
if result.returncode:
    raise SystemExit(result.returncode)
paths = list(Path('src').rglob('*.py'))+list(Path('tests').rglob('*.py'))
paths += list(Path('scripts').glob('*.py'))+list(Path('configs').glob('*.json'))
paths += [Path('.gitattributes')]
paths += [p for p in out.rglob('*') if p.is_file() and p.name not in ['manifest.json', 'gate.json']]
(out/'manifest.json').write_text(json.dumps({p.as_posix(): file_hash(p) for p in sorted(paths)}, indent=2))
print('Refreshed fingerprints and raw hashes; numerical records preserved')
