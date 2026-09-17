"""Linear Algebra Algorithms over a finite field F_p.

Satisfies Layer 3 requirements (L-1 through L-5) of the PRD:
- Gaussian elimination over F_p using modular inverses (no floats).
- Matrix rank derived from row-reduced form.
- Determinant for square matrices via elimination with sign tracking.
- Solving Ax = b for non-singular A with clear error reporting on singular systems.
- Matrix inverse via Gauss-Jordan elimination on [A | I].
"""

from typing import Tuple, List, Optional
from .field import FieldElement
from .vector import Vector
from .matrix import Matrix


class SingularMatrixError(ValueError):
    """Raised when an operation requires an invertible matrix but the matrix is singular."""
    pass


def gaussian_elimination(A: Matrix) -> Tuple[Matrix, int]:
    """Performs forward Gaussian elimination over F_p to convert A to upper-triangular form.
    
    Returns:
        (upper_triangular_matrix, row_swaps_count)
    Complexity:
        O(n^3) field operations for an n x n matrix.
    """
    m, n = A.shape
    p = A.p
    # Create mutable copy of rows as lists of FieldElements
    grid: List[List[FieldElement]] = [[A[r, c] for c in range(n)] for r in range(m)]
    row_swaps = 0
    pivot_row = 0

    for col in range(n):
        if pivot_row >= m:
            break

        # Find non-zero pivot entry in this column at or below pivot_row
        candidate = None
        for r in range(pivot_row, m):
            if grid[r][col].value != 0:
                candidate = r
                break

        if candidate is None:
            # All entries in this column from pivot_row downwards are zero
            continue

        # Swap rows if necessary
        if candidate != pivot_row:
            grid[pivot_row], grid[candidate] = grid[candidate], grid[pivot_row]
            row_swaps += 1

        # Eliminate entries below the pivot
        pivot_val = grid[pivot_row][col]
        pivot_inv = pivot_val.inverse()

        for r in range(pivot_row + 1, m):
            target_val = grid[r][col]
            if target_val.value != 0:
                factor = target_val * pivot_inv
                for c in range(col, n):
                    grid[r][c] = grid[r][c] - (factor * grid[pivot_row][c])

        pivot_row += 1

    return Matrix(grid), row_swaps


def rref(A: Matrix) -> Tuple[Matrix, List[int]]:
    """Computes the Reduced Row Echelon Form (RREF) of matrix A using Gauss-Jordan elimination over F_p.
    
    Returns:
        (rref_matrix, pivot_columns)
    Complexity:
        O(m * n * min(m, n)) field operations.
    """
    m, n = A.shape
    grid: List[List[FieldElement]] = [[A[r, c] for c in range(n)] for r in range(m)]
    pivot_cols: List[int] = []
    r = 0

    for c in range(n):
        if r >= m:
            break

        # Find pivot in column c from row r downwards
        pivot_idx = None
        for i in range(r, m):
            if grid[i][c].value != 0:
                pivot_idx = i
                break

        if pivot_idx is None:
            continue

        # Swap rows if needed
        if pivot_idx != r:
            grid[r], grid[pivot_idx] = grid[pivot_idx], grid[r]

        # Normalize pivot row so leading entry is 1
        lead_val = grid[r][c]
        lead_inv = lead_val.inverse()
        for j in range(c, n):
            grid[r][j] = grid[r][j] * lead_inv

        # Eliminate all other entries in column c (both above and below pivot)
        for i in range(m):
            if i != r and grid[i][c].value != 0:
                factor = grid[i][c]
                for j in range(c, n):
                    grid[i][j] = grid[i][j] - (factor * grid[r][j])

        pivot_cols.append(c)
        r += 1

    return Matrix(grid), pivot_cols


def rank(A: Matrix) -> int:
    """Computes the rank of matrix A over F_p.
    
    The rank is the number of pivot columns (or non-zero rows) in its RREF.
    Complexity: O(m * n * min(m, n)).
    """
    _, pivot_cols = rref(A)
    return len(pivot_cols)


def determinant(A: Matrix) -> FieldElement:
    """Computes the determinant of a square matrix A over F_p via Gaussian elimination.
    
    det(A) = (-1)^(row_swaps) * product(diagonal_entries)
    Complexity: O(n^3) field operations.
    Raises:
        ValueError: If matrix is not square.
    """
    if A.num_rows != A.num_cols:
        raise ValueError(f"Determinant is only defined for square matrices, got shape {A.shape}")

    n = A.num_rows
    p = A.p
    upper_tri, row_swaps = gaussian_elimination(A)

    det = FieldElement(1, p)
    for i in range(n):
        det = det * upper_tri[i, i]

    if row_swaps % 2 == 1:
        det = -det

    return det


def solve(A: Matrix, b: Vector) -> Vector:
    """Solves the linear system Ax = b over F_p for square, non-singular A.
    
    Uses Gauss-Jordan elimination on the augmented matrix [A | b].
    Complexity: O(n^3) field operations.
    Returns:
        Vector x satisfying Ax = b.
    Raises:
        ValueError: If dimensions mismatch.
        SingularMatrixError: If A is singular (det(A) == 0 or rank(A) < n).
    """
    if A.num_rows != A.num_cols:
        raise ValueError(f"Matrix A must be square to solve uniquely, got shape {A.shape}")
    if A.num_rows != len(b):
        raise ValueError(f"Dimension mismatch between matrix A ({A.shape}) and vector b (len={len(b)})")
    if A.p != b.p:
        raise ValueError(f"Modulus mismatch: A has p={A.p}, b has p={b.p}")

    n = A.num_rows
    p = A.p

    # Form augmented matrix [A | b] of size n x (n + 1)
    aug_grid: List[List[FieldElement]] = [
        [A[r, c] for c in range(n)] + [b[r]] for r in range(n)
    ]
    aug_matrix = Matrix(aug_grid)

    reduced_aug, pivot_cols = rref(aug_matrix)

    # Check for singularity: rank of A must be n, and pivot cols must be exactly [0, 1, ..., n-1]
    if len(pivot_cols) < n or any(pivot_cols[i] != i for i in range(n)):
        raise SingularMatrixError(
            f"Matrix A is singular (rank={len(pivot_cols)} < {n}) and has no unique solution."
        )

    # Extract solution vector x from the last column
    sol_elements = [reduced_aug[i, n] for i in range(n)]
    return Vector(sol_elements)


def matrix_inverse(A: Matrix) -> Matrix:
    """Computes the multiplicative inverse A^(-1) of a square matrix A over F_p via Gauss-Jordan elimination on [A | I].
    
    Complexity: O(n^3) field operations.
    Raises:
        ValueError: If A is not square.
        SingularMatrixError: If A is singular (not invertible).
    """
    if A.num_rows != A.num_cols:
        raise ValueError(f"Only square matrices can be inverted, got shape {A.shape}")

    n = A.num_rows
    p = A.p

    # Form augmented matrix [A | I_n] of size n x 2n
    aug_grid: List[List[FieldElement]] = []
    for r in range(n):
        row_elems = [A[r, c] for c in range(n)]
        identity_part = [FieldElement(1 if c == r else 0, p) for c in range(n)]
        aug_grid.append(row_elems + identity_part)

    aug_matrix = Matrix(aug_grid)
    reduced_aug, pivot_cols = rref(aug_matrix)

    # Left side must be identity matrix (pivots at 0, 1, ..., n-1)
    if len(pivot_cols) < n or any(pivot_cols[i] != i for i in range(n)):
        raise SingularMatrixError(f"Matrix is singular over F_{p} and has no inverse.")

    # Extract right side n x n
    inv_grid: List[List[FieldElement]] = [
        [reduced_aug[r, n + c] for c in range(n)] for r in range(n)
    ]
    return Matrix(inv_grid)
