"""Run pytest and save the actual return code and output for report generation."""
import json
import subprocess
import sys
from pathlib import Path

result = subprocess.run([sys.executable, '-m', 'pytest', '-q'], capture_output=True, text=True)
record = {'command': 'python -m pytest -q', 'returncode': result.returncode,
          'stdout': result.stdout, 'stderr': result.stderr}
Path('results/quick').mkdir(parents=True, exist_ok=True)
Path('results/quick/tests.json').write_text(json.dumps(record, indent=2))
print(result.stdout, end=''); print(result.stderr, end='', file=sys.stderr)
sys.exit(result.returncode)
