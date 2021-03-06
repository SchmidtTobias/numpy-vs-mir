import logging

import numpy as np
from numba import jit

from ..tools.apply_poisson import apply_poisson
from ..tools.util import timer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def GS_RB(
    F,
    U=None,
    h=None,
    max_iter=10_000_000,
    eps=1e-8,
    norm_iter=1000,
):
    """
    Solve AU = F, the poisson equation.

    @param F n vector
    @param h is distance between grid points | default is 1/N
    @return U n vector
    """
    if U is None:
        U = np.zeros_like(F)
    if h is None:
        h = 1 / (U.shape[0])

    h2 = h * h

    if len(F.shape) == 1:
        # do the sweep
        sweep = sweep_1D
    elif len(F.shape) == 2:
        # do the sweep
        sweep = sweep_2D
    elif len(F.shape) == 3:
        # Anzahl an Gauss-Seidel-Iterationen ausfuehren
        sweep = sweep_3D
    else:
        raise ValueError("Wrong Shape!!!")

    # a dirty hack that improves the speed,
    # maybe it is related that this memory is later reused in the sweeps
    # for the allocation of the lhs
    np.zeros_like(U)
    norm = 0.0  # declarate norm so we can output later
    it = 0
    # Anzahl an Gauss-Seidel-Iterationen ausfuehren
    while it < max_iter:
        it += 1
        # check sometimes if solutions converges
        if it % norm_iter == 0:
            norm = np.linalg.norm(F - apply_poisson(U, h))
            if norm <= eps:
                break

        # rote Halbiteration
        sweep(1, F, U, h2)
        # schwarze Halbiteration
        sweep(0, F, U, h2)

    logger.debug(f"converged after {it} iterations with {norm:.4} error")

    return U


# --- 1D Fall ---
@jit(nopython=True, fastmath=True)
def sweep_1D(color, F, U, h2):
    """
    Do the sweeps.

    @param color 1 = red 0 for black
    @param h2 is distance between grid points squared
    """
    n = F.shape[0]
    U[2 - color:n - 1:2] = (U[1 - color:n - 2:2] + U[3 - color::2] -
                            F[2 - color:n - 1:2] * h2) / (2.0)

# ----------------


# --- 2D Fall ---
@jit(nopython=True, fastmath=True)
def sweep_2D(color, F, U, h2):
    """
    Do the sweeps.

    @param color 1 = red 0 for black
    @param h2 is distance between grid points squared
    """
    m, n = F.shape

    U[1:m - 1:2, 1 + color:n - 1:2] = (
        U[0:m - 2:2, 1 + color:n - 1:2] +
        U[2::2, 1 + color:n - 1:2] +
        U[1:m - 1:2, color:n - 2:2] +
        U[1:m - 1:2, 2 + color::2] -
        F[1:m - 1:2, 1 + color:n - 1:2] * h2) / (4.0)
    U[2:m - 1:2, 2 - color:n - 1:2] = (
        U[1:m - 2:2, 2 - color:n - 1:2] +
        U[3::2, 2 - color:n - 1:2] +
        U[2:m - 1:2, 1 - color:n - 2:2] +
        U[2:m - 1:2, 3 - color::2] -
        F[2:m - 1:2, 2 - color:n - 1:2] * h2) / (4.0)

# ----------------


# --- 3D Fall ---
@jit(nopython=True, fastmath=True)
def sweep_3D(color, F, U, h2):
    """
    Do the sweeps.

    @param color 1 = red 0 for black
    @param h is distance between grid points
    """
    m, n, o = F.shape

    U[2:m - 1:2, 1:n - 1:2, 1 + color:o - 1:2] = (
        U[1:m - 2:2, 1:n - 1:2, 1 + color:o - 1:2] +
        U[3:m:2, 1:n - 1:2, 1 + color:o - 1:2] +
        U[2:m - 1:2, 0:n - 2:2, 1 + color:o - 1:2] +
        U[2:m - 1:2, 2:n:2, 1 + color:o - 1:2] +
        U[2:m - 1:2, 1:n - 1:2, color:o - 2:2] +
        U[2:m - 1:2, 1:n - 1:2, 2 + color:o:2] -
        F[2:m - 1:2, 1:n - 1:2, 1 + color:o - 1:2] * h2) / (6.0)

    U[1:m - 1:2, 1:n - 1:2, 2 - color:o - 1:2] = (
        U[0:m - 2:2, 1:n - 1:2, 2 - color:o - 1:2] +
        U[2:m:2, 1:n - 1:2, 2 - color:o - 1:2] +
        U[1:m - 1:2, 0:n - 2:2, 2 - color:o - 1:2] +
        U[1:m - 1:2, 2:n:2, 2 - color:o - 1:2] +
        U[1:m - 1:2, 1:n - 1:2, 1 - color:o - 2:2] +
        U[1:m - 1:2, 1:n - 1:2, 3 - color:o:2] -
        F[1:m - 1:2, 1:n - 1:2, 2 - color:o - 1:2] * h2) / (6.0)

    U[1:m - 1:2, 2:n - 1:2, 1 + color:o - 1:2] = (
        U[0:m - 2:2, 2:n - 1:2, 1 + color:o - 1:2] +
        U[2:m:2, 2:n - 1:2, 1 + color:o - 1:2] +
        U[1:m - 1:2, 1:n - 2:2, 1 + color:o - 1:2] +
        U[1:m - 1:2, 3:n:2, 1 + color:o - 1:2] +
        U[1:m - 1:2, 2:n - 1:2, color:o - 2:2] +
        U[1:m - 1:2, 2:n - 1:2, 2 + color:o:2] -
        F[1:m - 1:2, 2:n - 1:2, 1 + color:o - 1:2] * h2) / (6.0)

    U[2:m - 1:2, 2:n - 1:2, 2 - color:o - 1:2] = (
        U[1:m - 2:2, 2:n - 1:2, 2 - color:o - 1:2] +
        U[3:m:2, 2:n - 1:2, 2 - color:o - 1:2] +
        U[2:m - 1:2, 1:n - 2:2, 2 - color:o - 1:2] +
        U[2:m - 1:2, 3:n:2, 2 - color:o - 1:2] +
        U[2:m - 1:2, 2:n - 1:2, 1 - color:o - 2:2] +
        U[2:m - 1:2, 2:n - 1:2, 3 - color:o:2] -
        F[2:m - 1:2, 2:n - 1:2, 2 - color:o - 1:2] * h2) / (6.0)

# ----------------
