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

Phase 2 implementation and bounded studies are on `codex/phase2-peak-robustness-uq`.
Scientific status and unfinished milestones are recorded in
[Phase 2 execution status](docs/PHASE2_EXECUTION_STATUS.md). Peak observations are
lower bounds, with no global continuum certificate. To repeat the executed study
and its evidence checks using the existing Python 3.11 environment:

```powershell
.\.venv\Scripts\python.exe scripts/phase2_study.py
.\.venv\Scripts\python.exe scripts/phase2_training_audit.py
.\.venv\Scripts\python.exe scripts/phase2_failure_check.py
.\.venv\Scripts\python.exe scripts/phase2_verify.py
.\.venv\Scripts\python.exe scripts/phase2_gate.py --output results/phase2
.\.venv\Scripts\python.exe scripts/phase2_reports.py
```

Phase 1 artifacts remain under `results/quick`; new regression evidence is written
under `results/phase2/regression`. `configs/phase2_research.json` is an unexecuted
larger preset. Full repeats are stored in the ignored `results/reproduction/`.

Phase 2 cloud reproducibility is implemented in
[the dedicated workflow](.github/workflows/phase2-scientific-validation.yml).
Fast unit/saved-evidence checks run on Linux and Windows; the separate full Linux
job reruns the complete quick studies and independent gates on PRs targeting the
Phase 2 branch. See [CI methods](docs/PHASE2_CLOUD_CI_METHODS.md),
[local validation](docs/PHASE2_CLOUD_CI_VALIDATION.md) and
[execution status](docs/PHASE2_CLOUD_CI_EXECUTION_STATUS.md).
Remote CI remains pending until its actual runs are observed; a green run would
validate these bounded checks, while broader scientific validation remains PARTIAL.

Phase 2B adds an explicit `householder-v2` geometry and `dyadic-pattern-v2` finite
peak benchmark. Legacy APIs and all original numerical evidence are retained.
See [methods](docs/PHASE2B_METHODS.md), [local results](docs/PHASE2B_RESULTS.md),
[execution status](docs/PHASE2B_EXECUTION_STATUS.md) and
[limitations](docs/PHASE2B_LIMITATIONS.md). Reproduce into fresh output paths:

```powershell
.\.venv\Scripts\python.exe scripts/phase2b_verify.py --output results/ci/phase2b-run
.\.venv\Scripts\python.exe scripts/phase2b_investigate.py --output results/ci/phase2b-run/investigation --corrected results/ci/phase2b-run
.\.venv\Scripts\python.exe scripts/phase2b_finalize.py --output results/ci/phase2b-run
.\.venv\Scripts\python.exe scripts/phase2b_compare.py --current results/ci/phase2b-run
```

The dedicated Phase 2B PR workflow generates full Windows/Linux studies and
isolated library-sensitivity cohorts. Local success is not hosted CI success;
scientific status remains PARTIAL even after numerical agreement is observed.
