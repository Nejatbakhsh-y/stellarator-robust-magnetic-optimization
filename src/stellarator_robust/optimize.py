"""Dimensionless current x=I/Imax and field residual/Bref optimization."""
import time
import numpy as np
from scipy.optimize import lsq_linear, minimize


def baseline(A, b, w, ridge=1e-6, support=None):
    start = time.perf_counter()
    support = np.arange(A.shape[1]) if support is None else np.asarray(support, dtype=int)
    x = np.zeros(A.shape[1])
    if len(support):
        M = np.vstack([np.sqrt(w)[:, None]*A[:, support], np.sqrt(ridge)*np.eye(len(support))])
        y = np.r_[-np.sqrt(w)*b, np.zeros(len(support))]
        fit = lsq_linear(M, y, bounds=(-1, 1), tol=1e-12, max_iter=1000)
        if not fit.success:
            raise RuntimeError(f"Bounded least squares failed: {fit.message}")
        x[support] = fit.x
    return x, {"success": True, "seconds": time.perf_counter()-start}


def sparse(A, b, w, penalty, ridge=1e-6, tol=1e-8, maxiter=30000):
    """FISTA with L1 proximal map and box projection; gradient-map stopping."""
    M, y = np.sqrt(w)[:, None]*A, np.sqrt(w)*b
    H, g = M.T@M + ridge*np.eye(A.shape[1]), M.T@y
    L = np.linalg.norm(H, 2)
    x = np.zeros(A.shape[1]); z = x.copy(); t = 1.
    def prox(v):
        return np.clip(np.sign(v)*np.maximum(abs(v)-penalty/L, 0), -1, 1)
    for k in range(maxiter):
        new = prox(z-(H@z+g)/L)
        tn = (1+np.sqrt(1+4*t*t))/2
        z = new + (t-1)/tn*(new-x)
        x, t = new, tn
        residual = np.max(abs(x-prox(x-(H@x+g)/L)))
        if residual < tol:
            return x, {"iterations": k+1, "gradient_map_step": float(residual), "success": True}
    raise RuntimeError("FISTA did not converge")


def deletion_path(A, b, w, ridge=1e-6):
    support = np.arange(A.shape[1]); rows = []
    while len(support):
        x, _ = baseline(A, b, w, ridge, support)
        removed = int(support[np.argmin(abs(x[support]))])
        rows.append((x, removed))
        support = support[support != removed]
    return rows


def robust(As, bs, w, support, ridge=1e-6):
    """Convex finite-scenario minimax epigraph via SLSQP, with analytic Jacobians."""
    start = time.perf_counter()
    support = np.asarray(support)
    M = As[:, :, support]*np.sqrt(w)[None, :, None]
    y = bs*np.sqrt(w)[None, :]
    def losses(x):
        r = np.einsum('smj,j->sm', M, x)+y
        return np.sum(r*r, axis=1), 2*np.einsum('smj,sm->sj', M, r)
    def obj(z):
        return z[-1]+ridge*(z[:-1]@z[:-1])
    def jac(z):
        return np.r_[2*ridge*z[:-1], 1.]
    z = np.r_[np.zeros(len(support)), max(losses(np.zeros(len(support)))[0])]
    fit = minimize(obj, z, jac=jac, bounds=[(-1, 1)]*len(support)+[(0, None)],
                   constraints={"type": "ineq", "fun": lambda z: z[-1]-losses(z[:-1])[0],
                                "jac": lambda z: np.column_stack([-losses(z[:-1])[1], np.ones(len(As))])},
                   method="SLSQP", options={"ftol": 1e-12, "maxiter": 2000})
    violation = max(0., float(max(losses(fit.x[:-1])[0])-fit.x[-1]))
    if not fit.success or violation > 1e-8:
        raise RuntimeError(f"Robust optimization failed: {fit.message}, violation={violation}")
    x = np.zeros(As.shape[2]); x[support] = fit.x[:-1]
    return x, {"success": bool(fit.success), "message": fit.message, "violation": violation,
               "iterations": fit.nit, "epigraph": float(fit.x[-1]), "seconds": time.perf_counter()-start}
