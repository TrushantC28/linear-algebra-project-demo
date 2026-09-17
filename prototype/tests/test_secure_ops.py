"""Unit tests for Secret Sharing and Secure Computation (Layers 4 & 5)."""

import unittest
from prototype.field import FieldElement
from prototype.vector import Vector
from prototype.matrix import Matrix
from prototype.secret_sharing import AdditiveSecretSharing
from prototype.secure_ops import (
    secure_add,
    secure_inner_product,
    secure_matrix_product,
    verify,
)


class TestSecureOps(unittest.TestCase):
    def setUp(self):
        self.p = 997

    def test_element_split_and_reconstruct(self):
        secret = FieldElement(742, self.p)
        for num_parties in [2, 3, 5]:
            shares = AdditiveSecretSharing.split_element(secret, num_parties)
            self.assertEqual(len(shares), num_parties)
            reconstructed = AdditiveSecretSharing.reconstruct_element(shares)
            self.assertEqual(reconstructed, secret)

    def test_vector_split_and_reconstruct(self):
        v = Vector.from_ints([12, 45, 89, 230], self.p)
        shares = AdditiveSecretSharing.split_vector(v, num_parties=3)
        self.assertEqual(len(shares), 3)
        reconstructed = AdditiveSecretSharing.reconstruct_vector(shares)
        self.assertEqual(reconstructed, v)

    def test_matrix_split_and_reconstruct(self):
        m = Matrix.from_ints([
            [1, 2, 3],
            [4, 5, 6]
        ], self.p)
        shares = AdditiveSecretSharing.split_matrix(m, num_parties=4)
        self.assertEqual(len(shares), 4)
        reconstructed = AdditiveSecretSharing.reconstruct_matrix(shares)
        self.assertEqual(reconstructed, m)

    def test_secure_vector_addition(self):
        v1 = Vector.from_ints([100, 200, 300], self.p)
        v2 = Vector.from_ints([50, 150, 250], self.p)
        expected_sum = v1 + v2

        shares_v1 = AdditiveSecretSharing.split_vector(v1, num_parties=3)
        shares_v2 = AdditiveSecretSharing.split_vector(v2, num_parties=3)

        sum_shares = secure_add(shares_v1, shares_v2)
        reconstructed_sum = AdditiveSecretSharing.reconstruct_vector(sum_shares)
        self.assertEqual(reconstructed_sum, expected_sum)

    def test_secure_inner_product_example_1(self):
        # Example 1
        u = Vector.from_ints([3, 7, 11], self.p)
        v = Vector.from_ints([5, 2, 9], self.p)
        expected_dot = u.dot(v)  # 3*5 + 7*2 + 11*9 = 15 + 14 + 99 = 128 mod 997

        shares_u = AdditiveSecretSharing.split_vector(u, num_parties=3)
        shares_v = AdditiveSecretSharing.split_vector(v, num_parties=3)

        result_shares = secure_inner_product(shares_u, shares_v)
        reconstructed_dot = AdditiveSecretSharing.reconstruct_element(result_shares)
        self.assertEqual(reconstructed_dot, expected_dot)
        self.assertTrue(verify("Inner Product 1", reconstructed_dot, expected_dot, verbose=False))

    def test_secure_inner_product_example_2(self):
        # Example 2 (orthogonal or larger components)
        u = Vector.from_ints([150, 420, 890, 312], self.p)
        v = Vector.from_ints([811, 23, 604, 55], self.p)
        expected_dot = u.dot(v)

        shares_u = AdditiveSecretSharing.split_vector(u, num_parties=4)
        shares_v = AdditiveSecretSharing.split_vector(v, num_parties=4)

        result_shares = secure_inner_product(shares_u, shares_v)
        reconstructed_dot = AdditiveSecretSharing.reconstruct_element(result_shares)
        self.assertEqual(reconstructed_dot, expected_dot)
        self.assertTrue(verify("Inner Product 2", reconstructed_dot, expected_dot, verbose=False))

    def test_secure_matrix_product(self):
        A = Matrix.from_ints([
            [12, 5],
            [3, 8]
        ], self.p)
        B = Matrix.from_ints([
            [7, 9],
            [4, 2]
        ], self.p)
        expected_product = A @ B

        shares_A = AdditiveSecretSharing.split_matrix(A, num_parties=3)
        shares_B = AdditiveSecretSharing.split_matrix(B, num_parties=3)

        product_shares = secure_matrix_product(shares_A, shares_B)
        reconstructed_product = AdditiveSecretSharing.reconstruct_matrix(product_shares)
        self.assertEqual(reconstructed_product, expected_product)


if __name__ == "__main__":
    unittest.main()
