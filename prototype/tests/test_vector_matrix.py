"""Unit tests for Vector and Matrix (Layer 2)."""

import unittest
from prototype.field import FieldElement
from prototype.vector import Vector
from prototype.matrix import Matrix


class TestVector(unittest.TestCase):
    def setUp(self):
        self.p = 31

    def test_construction_and_indexing(self):
        v = Vector.from_ints([1, 5, 30], self.p)
        self.assertEqual(len(v), 3)
        self.assertEqual(v[0], FieldElement(1, self.p))
        self.assertEqual(v[2], FieldElement(30, self.p))
        self.assertEqual(v.to_ints(), [1, 5, 30])

    def test_addition_and_subtraction(self):
        # [3, 10, 25] + [5, 22, 10] = [8, 32%31, 35%31] = [8, 1, 4]
        v1 = Vector.from_ints([3, 10, 25], self.p)
        v2 = Vector.from_ints([5, 22, 10], self.p)
        v_sum = v1 + v2
        self.assertEqual(v_sum.to_ints(), [8, 1, 4])

        v_sub = v1 - v2
        # [3-5, 10-22, 25-10] mod 31 = [-2, -12, 15] mod 31 = [29, 19, 15]
        self.assertEqual(v_sub.to_ints(), [29, 19, 15])

    def test_scalar_multiplication(self):
        v = Vector.from_ints([2, 5, 11], self.p)
        v_scaled = v * 4
        # [8, 20, 44%31=13]
        self.assertEqual(v_scaled.to_ints(), [8, 20, 13])
        self.assertEqual(3 * v, Vector.from_ints([6, 15, 2], self.p))

    def test_dot_product(self):
        # [1, 2, 3] . [4, 5, 6] = 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32 = 1 mod 31
        v1 = Vector.from_ints([1, 2, 3], self.p)
        v2 = Vector.from_ints([4, 5, 6], self.p)
        self.assertEqual(v1.dot(v2), FieldElement(1, self.p))

    def test_dimension_mismatch(self):
        v1 = Vector.from_ints([1, 2], self.p)
        v2 = Vector.from_ints([1, 2, 3], self.p)
        with self.assertRaises(ValueError):
            _ = v1 + v2
        with self.assertRaises(ValueError):
            _ = v1.dot(v2)


class TestMatrix(unittest.TestCase):
    def setUp(self):
        self.p = 31

    def test_construction_and_indexing(self):
        grid = [
            [1, 2, 3],
            [4, 5, 6]
        ]
        m = Matrix.from_ints(grid, self.p)
        self.assertEqual(m.shape, (2, 3))
        self.assertEqual(m[0, 1], FieldElement(2, self.p))
        self.assertEqual(m[1, 2], FieldElement(6, self.p))
        self.assertEqual(m[0].to_ints(), [1, 2, 3])

    def test_addition_and_subtraction(self):
        m1 = Matrix.from_ints([[1, 2], [3, 4]], self.p)
        m2 = Matrix.from_ints([[5, 6], [7, 8]], self.p)
        res = m1 + m2
        self.assertEqual(res.to_ints(), [[6, 8], [10, 12]])

    def test_transpose_and_involution(self):
        grid = [
            [1, 2, 3],
            [4, 5, 6]
        ]
        m = Matrix.from_ints(grid, self.p)
        t = m.transpose()
        self.assertEqual(t.shape, (3, 2))
        self.assertEqual(t.to_ints(), [[1, 4], [2, 5], [3, 6]])
        # Transpose-of-transpose property: (A^T)^T == A
        self.assertEqual(t.transpose(), m)

    def test_multiplication_hand_computed(self):
        # A: (2x3), B: (3x2)
        # A = [[1, 2, 3], [4, 5, 6]]
        # B = [[7, 8], [9, 1], [2, 3]]
        # Row 0, Col 0: 1*7 + 2*9 + 3*2 = 7 + 18 + 6 = 31 = 0 mod 31
        # Row 0, Col 1: 1*8 + 2*1 + 3*3 = 8 + 2 + 9 = 19 mod 31
        # Row 1, Col 0: 4*7 + 5*9 + 6*2 = 28 + 45 + 12 = 85 = 23 mod 31 (85 = 2*31 + 23)
        # Row 1, Col 1: 4*8 + 5*1 + 6*3 = 32 + 5 + 18 = 55 = 24 mod 31 (55 = 1*31 + 24)
        A = Matrix.from_ints([[1, 2, 3], [4, 5, 6]], self.p)
        B = Matrix.from_ints([[7, 8], [9, 1], [2, 3]], self.p)
        C = A @ B
        self.assertEqual(C.shape, (2, 2))
        self.assertEqual(C.to_ints(), [[0, 19], [23, 24]])

    def test_identity_multiplication(self):
        A = Matrix.from_ints([[12, 17], [5, 23]], self.p)
        I = Matrix.identity(2, self.p)
        self.assertEqual(A @ I, A)
        self.assertEqual(I @ A, A)

    def test_matrix_vector_multiplication(self):
        A = Matrix.from_ints([[1, 2], [3, 4]], self.p)
        x = Vector.from_ints([5, 6], self.p)
        # [1*5 + 2*6, 3*5 + 4*6] = [17, 39%31=8]
        b = A.vector_mul(x)
        self.assertEqual(b.to_ints(), [17, 8])

    def test_dimension_mismatch_error(self):
        A = Matrix.from_ints([[1, 2, 3], [4, 5, 6]], self.p)  # 2x3
        B = Matrix.from_ints([[1, 2], [3, 4]], self.p)          # 2x2
        with self.assertRaises(ValueError):
            _ = A + B
        with self.assertRaises(ValueError):
            _ = A @ B


if __name__ == "__main__":
    unittest.main()
