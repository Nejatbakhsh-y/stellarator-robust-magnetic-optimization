"""Planar polygons and exact straight-segment Biot–Savart integration."""
from dataclasses import dataclass
import numpy as np
from scipy.spatial.transform import Rotation

MU0 = 4e-7 * np.pi  # conventional approximation, H/m


@dataclass
class Coil:
    """Closed polygon; vertices in metres, positive current follows vertex order."""
    vertices: np.ndarray

    def moved(self, translation: np.ndarray, rotation: np.ndarray) -> "Coil":
        center = self.vertices.mean(axis=0)
        return Coil((self.vertices - center) @ Rotation.from_rotvec(rotation).as_matrix().T
                    + center + translation)


def circle(center, normal, radius: float, segments: int = 128) -> Coil:
    if radius <= 0 or segments < 8:
        raise ValueError("Positive radius and at least eight segments required")
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    helper = np.eye(3)[np.argmin(abs(n))]
    u = np.cross(helper, n)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    t = np.arange(segments) * 2 * np.pi / segments
    return Coil(np.asarray(center) + radius * (np.cos(t)[:, None] * u + np.sin(t)[:, None] * v))


def surface(R: float, a: float, nt: int, np_: int, shift: float = 0):
    if not R > a > 0 or min(nt, np_) < 3:
        raise ValueError("Require R > a > 0 and periodic grids >= 3")
    t, p = np.meshgrid((np.arange(nt) + shift) * 2*np.pi/nt,
                       (np.arange(np_) + shift) * 2*np.pi/np_, indexing="ij")
    normals = np.stack([np.cos(t)*np.cos(p), np.cos(t)*np.sin(p), np.sin(t)], -1)
    xyz = np.stack([(R+a*np.cos(t))*np.cos(p), (R+a*np.cos(t))*np.sin(p), a*np.sin(t)], -1)
    area = (a*(R+a*np.cos(t)) * (2*np.pi/nt)*(2*np.pi/np_)).ravel()
    return xyz.reshape(-1, 3), normals.reshape(-1, 3), area


def clearance(points: np.ndarray, coil: Coil) -> float:
    """Exact minimum distance from sampled points to polygon segments."""
    start = coil.vertices
    d = np.roll(start, -1, axis=0) - start
    r = points[:, None, :] - start
    t = np.clip(np.sum(r*d, axis=-1)/np.sum(d*d, axis=-1), 0, 1)
    return float(np.min(np.linalg.norm(r-t[..., None]*d, axis=-1)))


def field(points: np.ndarray, coil: Coil, current: float = 1., min_distance: float = 1e-4) -> np.ndarray:
    """Analytic segment integral; bounded point batches; reject near wires."""
    points = np.asarray(points, dtype=float)
    out = np.empty_like(points)
    a = coil.vertices
    b = np.roll(a, -1, axis=0)
    for lo in range(0, len(points), 128):
        p = points[lo:lo+128]
        if clearance(p, coil) <= min_distance:
            raise ValueError("Evaluation point too close to filament")
        r1, r2 = p[:, None, :] - a, p[:, None, :] - b
        n1, n2 = np.linalg.norm(r1, axis=-1), np.linalg.norm(r2, axis=-1)
        cross = np.cross(r1, r2)
        denom = n1*n2*(n1*n2 + np.sum(r1*r2, axis=-1))
        # Collinear points beyond endpoints have exactly zero field.
        factor = np.divide(n1+n2, denom, out=np.zeros_like(denom), where=denom > 0)
        out[lo:lo+128] = MU0*current/(4*np.pi) * np.sum(cross*factor[..., None], axis=1)
    if not np.all(np.isfinite(out)):
        raise ValueError("Nonfinite field")
    return out


def response(points, normals, coils):
    return np.column_stack([np.sum(field(points, c)*normals, axis=1) for c in coils])


def benchmark(nt=8, np_=16, segments=64, nphi=8, ntheta=3):
    points, normals, area = surface(1., .25, nt, np_)
    coils = []
    for t in np.arange(ntheta)*2*np.pi/ntheta:
        for p in np.arange(nphi)*2*np.pi/nphi:
            center = [(1+.65*np.cos(t))*np.cos(p), (1+.65*np.cos(t))*np.sin(p), .65*np.sin(t)]
            n = [np.cos(t)*np.cos(p), np.cos(t)*np.sin(p), np.sin(t)]
            coils.append(circle(center, n, .16, segments))
    error = circle([1.6, .25, .35], [1., .2, .4], .22, segments)
    b = np.sum(field(points, error, 1500.)*normals, axis=1)
    return points, normals, area/area.sum(), coils, error, b
