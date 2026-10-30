# Phase 2B methods and numerical contract

Benchmark version: phase2b-householder-v2-pattern-v2. This is an explicit new
benchmark, not a rewritten Phase 1/2 checkpoint. The legacy-v1 API remains the
default; configs/phase2b_quick.json and phase2b_study.json opt into the correction.
All original 38 result/audit/command/fingerprint files are preserved byte-for-byte
against base 72c70995b7e6c2f56ec6fad4fa07fd73930e3370 (with explicit historical
Phase 1 Git text-checkout filtering). Existing PRs #1–#3 are not modified or merged.

For unit normal n, choose s=+1 when n_z>=0, otherwise -1, including signed zero
in the positive hemisphere. Let a=-1/(s+n_z), b=n_x*n_y*a. The circle frame is
u=(1+s*n_x^2*a, s*b, -s*n_x), v=(b, s+n_y^2*a, -n_y).
Equivalently, with w=n+s*e_z, H=I-2*w*w^T/(w^T*w), R=H*diag(1,s,-s).
H is orthogonal with determinant -1; the diagonal factor also has determinant
-1. Thus R is orthogonal, det(R)=+1, and its third column is n: u cross v=n.
The denominator magnitude is at least one. Max-component scaling before norm
normalization avoids finite-vector overflow/underflow. No argmin among nearly
tied components is used. This convention was chosen algebraically, not fitted
to the historical Windows or Linux output.

There is a chart boundary at n_z=0; no global smooth frame over all normals is
claimed. The declared nominal benchmark has n_z exactly zero or approximately
+/-0.866, and the disturbance normal is away from the boundary. Manufacturing
rotations act on existing vertices, not by reselecting a frame. Signed-zero
handling is explicit. Tests check axis limits, poles, near-tied components,
extreme finite scales, orientation, winding, plane, radius and polygon perimeter.

Centers, radii, normal directions, current signs, 512 segments, torus dimensions,
current bounds, ridge objective, supports policy, uncertainty draws, seeds,
training counts, 64-scenario holdout and bootstrap settings are unchanged.
Polygon phase intentionally changes; a continuous circle is phase-invariant,
while a finite inscribed polygon is not. Both polygons lie within r*(1-cos(pi/N))
of the same circle, giving the conservative two-polygon Hausdorff upper bound
2*r*(1-cos(pi/N)). Indexed vertex displacement is not a physical coil translation.
Every coil's dimensional/phase comparison is retained in investigation/geometry.json.

The new peak contract uses the same nine grid/shift seeds for each of three
methods and both signs. It evaluates a fixed 24-level dyadic pattern with
initial step 0.2 rad and nine points per level (217 evaluations per signed seed).
Each move must improve signed field by more than 5e-14 T; canonical offset order
breaks near ties within this band. This decision resolution is half the unchanged
1e-13 T scientific absolute comparison tolerance. Coordinates, moves, counts,
fields, statuses and configuration of this finite benchmark remain compared at
the original 1e-11/1e-13 tolerances (exact integers/statuses). Completion means
completion of a finite budget, not a stationary-point or global certificate.
Exploration is bounded and every result is only an observed lower bound.

Legacy Nelder–Mead remains unchanged. Its xatol=1e-8 rad and dimensionless
fatol=1e-12 with 1 mT objective scaling imply a 1e-15 T function stopping test;
neither is a coordinate-error certificate. The investigation accounts for all
145 historical discrepancies: 97 coordinate, 46 algorithmic trace, and two
scientific dimensionless relative-error fields. All remain recorded as legacy
failures. Both candidate sets are evaluated on common geometry; finite-difference
signed Hessians at h=1e-4 and h=5e-5 rad give conditional quadratic position scales,
not interval bounds. The raw corrected-geometry NM traces and 20/28-level finite
searches are retained. NM physical field values and direct re-evaluations face
the original field tolerances; their adaptive coordinate/count differences are
reported explicitly, not misrepresented as reproduction of the new finite trace.

The separate quick and study repeats compare every scientific group. Runtime
Git HEAD/dirty flag/Python/packages are verified on their generating worker.
Phase 1 input-byte hashes are verified individually before exclusion from
cross-environment equality; their full scientific inputs remain compared.
Only quick solver iteration/timing traces are reported separately; success,
feasibility, all currents/losses/metrics and data structure remain graded.
Unknown metadata fails. Scenario inputs remain exact; derived clearance alone
uses the existing numeric tolerances. Each dataset has raw-byte manifests and
source fingerprints. Figure bytes are checked for integrity, not pixel equality
across OS font/rendering builds. Scientific data, including all new coordinates,
are not replaced by image comparisons.

Hosted CI runs full independent/repeated numerical pipelines on Windows and Linux
with NumPy 2.4.6/SciPy 1.17.1. Separate Linux cohorts vary NumPy alone to 2.3.5 and
SciPy alone to 1.16.3. These released CPython 3.11 packages are documented at
https://pypi.org/project/numpy/2.3.5/ and https://pypi.org/project/scipy/1.16.3/.
Actual imported versions are recorded and checked. No alternate dependencies
are installed into the development venv. All jobs use read-only repository
permissions, no persisted checkout credentials, 180-minute job limits and
always-attempted 14-day evidence uploads. No CI commit, push, secret upload or
pull_request_target is used. The final job compares independently generated
Windows/Linux bundles; unfinished or failed workers cannot pass the contract.
