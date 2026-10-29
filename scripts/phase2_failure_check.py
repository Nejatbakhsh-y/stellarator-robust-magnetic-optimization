"""Demonstrate that missing evidence and a changed hash cannot produce a pass."""
import hashlib
import json
import subprocess
import sys
from contextlib import nullcontext
from pathlib import Path

root = Path('results/reproduction'); root.mkdir(parents=True, exist_ok=True)
with nullcontext(str(root/'gate-negative')) as temp:
    path = Path(temp)
    path.mkdir(parents=True, exist_ok=True)
    (path/'study.json').write_text('{}')
    (path/'manifest.json').write_text(json.dumps({'src/stellarator_robust/peak.py': '0'*64}))
    command = [sys.executable, 'scripts/phase2_gate.py', '--output', str(path)]
    result = subprocess.run(command, text=True, capture_output=True)
    gate = json.loads((path/'gate.json').read_text())
    passed = (result.returncode == 1 and gate['software_status'] == 'FAIL'
              and 'manifest completeness' in gate['failed_checks']
              and 'hash src/stellarator_robust/peak.py' in gate['failed_checks'])
    record = {'status': 'PASS' if passed else 'FAIL', 'expected_child_returncode': 1,
              'actual_child_returncode': result.returncode, 'rejected_evidence': gate,
              'stdout': result.stdout, 'stderr': result.stderr,
              'study_sha256': hashlib.sha256(Path('results/phase2/study.json').read_bytes()).hexdigest()}
    Path('results/phase2/failure_sensitivity.json').write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))
    raise SystemExit(0 if passed else 1)
