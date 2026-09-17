"""Unit tests for Linear Algebra algorithms over F_p (Layer 3)."""

import unittest
from prototype.field import FieldElement
from prototype.vector import Vector
from prototype.matrix import Matrix
from prototype.linalg import (
    gaussian_elimination,
    rref,
    rank,
    determinant,
    solve,
    matrix_inverse,
    SingularMatrixError
)


class TestLinalg(unittest.TestCase):
    def setUp(self):
        self.p = 31

    def test_rref_and_rank(self):
        # Matrix with dependent rows: Row 2 = Row 0 + Row 1
        # [[1, 2, 3],
        #  [4, 5, 6],
        #  [5, 7, 9]] mod 31
        grid = [
            [1, 2, 3],
            [4, 5, 6],
            [5, 7, 9]
        ]
        A = Matrix.from_ints(grid, self.p)
        self.assertEqual(rank(A), 2)

        # Full rank 3x3
        I = Matrix.identity(3, self.p)
        self.assertEqual(rank(I), 3)

    def test_determinant(self):
        # 2x2 matrix: det([[3, 8], [4, 6]]) = 3*6 - 8*4 = 18 - 32 = -14 = 17 mod 31
        A = Matrix.from_ints([[3, 8], [4, 6]], self.p)
        det_A = determinant(A)
        self.assertEqual(det_A, FieldElement(17, self.p))

        # Singular matrix has determinant 0
        singular = Matrix.from_ints([[1, 2], [2, 4]], self.p)
        self.assertEqual(determinant(singular), FieldElement(0, self.p))

    def test_solve_linear_system(self):
        # Let's set up a known system:
        # A * x = b
        # A = [[2, 1], [5, 7]]
        # x_true = [3, 4]
        # b = A * x = [2*3 + 1*4, 5*3 + 7*4] = [10, 15 + 28 = 43 % 31 = 12]
        A = Matrix.from_ints([[2, 1], [5, 7]], self.p)
        b = Vector.from_ints([10, 12], self.p)

        x_sol = solve(A, b)
        self.assertEqual(x_sol.to_ints(), [3, 4])

        # Substitute back in: A * x_sol == b
        self.assertEqual(A.vector_mul(x_sol), b)

    def test_solve_3x3_system(self):
        # 3x3 system
        A = Matrix.from_ints([
            [1, 2, 3],
            [0, 1, 4],
            [5, 6, 0]
        ], self.p)
        x_true = Vector.from_ints([7, 11, 13], self.p)
        b = A.vector_mul(x_true)

        x_sol = solve(A, b)
        self.assertEqual(x_sol, x_true)
        self.assertEqual(A.vector_mul(x_sol), b)

    def test_singular_system_detection(self):
        # Singular matrix: rows are multiples
        A_singular = Matrix.from_ints([
            [1, 2, 3],
            [2, 4, 6],
            [1, 1, 1]
        ], self.p)
        b = Vector.from_ints([1, 2, 3], self.p)

        with self.assertRaises(SingularMatrixError):
            solve(A_singular, b)

    def test_matrix_inverse(self):
        A = Matrix.from_ints([
            [2, 1],
            [5, 7]
        ], self.p)
        A_inv = matrix_inverse(A)

        I = Matrix.identity(2, self.p)
        self.assertEqual(A @ A_inv, I)
        self.assertEqual(A_inv @ A, I)

    def test_singular_matrix_inverse_raises_error(self):
        A_singular = Matrix.from_ints([[1, 2], [2, 4]], self.p)
        with self.assertRaises(SingularMatrixError):
            matrix_inverse(A_singular)


if __name__ == "__main__":
    unittest.main()
