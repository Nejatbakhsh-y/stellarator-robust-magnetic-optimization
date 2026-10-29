"""Bounded, recorded rigid placement and command-to-actual current scenarios."""
import numpy as np
from .model import response, clearance


def scenarios(points, normals, coils, count, seed, translation=.003, rotation=.01,
              gain=.02, offset=2., imax=3000.):
    """Uniform independent component bounds; gain and additive offset applied once.

    Radial clearance certified with the torus signed-distance function (1-Lipschitz).
    This benchmark is fixed to R=1 m, a=.25 m; check whole segments via half-edge bound.
    """
    rng = np.random.default_rng(seed)
    matrices, offsets, records = [], [], []
    for _ in range(count):
        tr = rng.uniform(-translation, translation, (len(coils), 3))
        rot = rng.uniform(-rotation, rotation, (len(coils), 3))
        eps = rng.uniform(-gain, gain, len(coils))
        delta = rng.uniform(-offset, offset, len(coils))
        moved = [c.moved(t, r) for c, t, r in zip(coils, tr, rot)]
        for c in moved:
            v = c.vertices
            distance = np.sqrt((np.linalg.norm(v[:, :2], axis=1)-1)**2+v[:, 2]**2)-.25
            edge = np.max(np.linalg.norm(np.roll(v, -1, axis=0)-v, axis=1))
            if distance.min()-edge/2 < .05:
                raise ValueError("Scenario rejected: certified surface clearance below .05 m")
        A = response(points, normals, moved)
        matrices.append(A*(1+eps)[None, :])
        offsets.append(A@delta)
        records.append({"translation_m": tr.tolist(), "rotation_rad": rot.tolist(),
                        "gain": eps.tolist(), "offset_A": delta.tolist(),
                        "sampled_clearance_m": min(clearance(points, c) for c in moved)})
    return np.asarray(matrices), np.asarray(offsets), records
