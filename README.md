# stellarator-robust-magnetic-optimization
Robust Optimization and Independent Validation of Planar-Coil Magnetic-Field Models

Independent, public, reduced-order research demonstration. Not affiliated with or validated by Thea Energy. Does not reproduce proprietary Eos or Helios geometry or establish plasma confinement performance.

This Python 3.11 package studies a **synthetic** toroidal boundary, 24 planar circular shaping coils and a separate nonzero disturbance coil. It implements bounded ridge least squares, box-constrained L1 selection with support refitting, optimize-then-delete, finite-scenario minimax optimization, paired uncertainty evaluation and static single-coil recovery.

From this checkout in Windows PowerShell, using the existing environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m stellarator_robust.cli validate
.\.venv\Scripts\python.exe -m stellarator_robust.cli run --config configs/quick.json --output results/quick
.\.venv\Scripts\python.exe scripts/check_outputs.py results/quick
.\.venv\Scripts\python.exe scripts/test_and_record.py
.\.venv\Scripts\python.exe scripts/audit_quick.py
.\.venv\Scripts\python.exe scripts/reproduce_check.py
.\.venv\Scripts\python.exe scripts/write_reports.py
```

On other platforms use the environment's `python` executable. Tested dependency versions are recorded in `requirements-tested.txt`; install those first for the tested environment. JSON configuration avoids a YAML dependency. `configs/research.json` is an opt-in larger study, whose completion status is tracked separately.

See [methods](docs/SCIENTIFIC_METHODS.md), [source verification](docs/SOURCE_VERIFICATION.md), [validation](docs/VALIDATION_REPORT.md), [results](docs/RESEARCH_REPORT.md), and [limitations](docs/LIMITATIONS.md). Figures and unrounded data are in `results/quick/`. The CLI validation subcommand checks analytical loop convergence; the full validation gate also requires pytest and the quick experiment/output checks.

The quick benchmark uses 512 polygon segments after a 256-segment refinement audit failed. See [the diagnosis](docs/REFINEMENT_DIAGNOSIS.md). Validation thresholds were retained and independent smooth-circle checks added. An executed run and all validation gates must succeed before reporting the checkpoint as verified.

No license has been selected; public availability does not itself grant an open-source license.
