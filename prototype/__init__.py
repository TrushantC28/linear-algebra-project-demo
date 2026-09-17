"""Linear Algebra Library for Secure Computation - Prototype Package."""

from .field import FieldElement, extended_gcd
from .vector import Vector
from .matrix import Matrix
from .linalg import (
    gaussian_elimination,
    rref,
    rank,
    determinant,
    solve,
    matrix_inverse,
    SingularMatrixError,
)
from .secret_sharing import AdditiveSecretSharing
from .secure_ops import (
    secure_add,
    secure_inner_product,
    secure_matrix_product,
    verify,
    SIMPLIFIED_PROTOCOL_EXPLANATION,
)

__all__ = [
    "FieldElement",
    "extended_gcd",
    "Vector",
    "Matrix",
    "gaussian_elimination",
    "rref",
    "rank",
    "determinant",
    "solve",
    "matrix_inverse",
    "SingularMatrixError",
    "AdditiveSecretSharing",
    "secure_add",
    "secure_inner_product",
    "secure_matrix_product",
    "verify",
    "SIMPLIFIED_PROTOCOL_EXPLANATION",
]
