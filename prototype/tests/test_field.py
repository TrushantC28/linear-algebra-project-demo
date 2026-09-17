"""Unit tests for FieldElement (Layer 1)."""

import unittest
from prototype.field import FieldElement, extended_gcd


class TestFieldElement(unittest.TestCase):
    def setUp(self):
        self.p = 31  # Small prime for exhaustive testing of properties

    def test_extended_gcd(self):
        gcd, x, y = extended_gcd(30, 20)
        self.assertEqual(gcd, 10)
        self.assertEqual(30 * x + 20 * y, 10)

        gcd, x, y = extended_gcd(17, 31)
        self.assertEqual(gcd, 1)
        self.assertEqual((17 * x + 31 * y), 1)

    def test_basic_arithmetic(self):
        a = FieldElement(12, self.p)
        b = FieldElement(25, self.p)

        # Addition: (12 + 25) % 31 = 37 % 31 = 6
        self.assertEqual(a + b, FieldElement(6, self.p))
        # Subtraction: (12 - 25) % 31 = -13 % 31 = 18
        self.assertEqual(a - b, FieldElement(18, self.p))
        # Multiplication: (12 * 25) % 31 = 300 % 31 = 21
        self.assertEqual(a * b, FieldElement(21, self.p))
        # Negation: (-12) % 31 = 19
        self.assertEqual(-a, FieldElement(19, self.p))

    def test_commutativity_and_associativity(self):
        a = FieldElement(7, self.p)
        b = FieldElement(19, self.p)
        c = FieldElement(28, self.p)

        # Commutativity
        self.assertEqual(a + b, b + a)
        self.assertEqual(a * b, b * a)

        # Associativity
        self.assertEqual((a + b) + c, a + (b + c))
        self.assertEqual((a * b) * c, a * (b * c))

        # Distributivity
        self.assertEqual(a * (b + c), (a * b) + (a * c))

    def test_inverses_exhaustive(self):
        """Verify a * inverse(a) == 1 for all non-zero elements in F_31."""
        one = FieldElement(1, self.p)
        for val in range(1, self.p):
            elem = FieldElement(val, self.p)
            inv = elem.inverse()
            self.assertEqual(elem * inv, one, f"Failed inverse for {val} in F_{self.p}")
            self.assertEqual(inv * elem, one)

    def test_inverting_zero_raises_error(self):
        zero = FieldElement(0, self.p)
        with self.assertRaises(ZeroDivisionError):
            zero.inverse()

        with self.assertRaises(ZeroDivisionError):
            _ = FieldElement(5, self.p) / zero

    def test_division(self):
        a = FieldElement(15, self.p)
        b = FieldElement(4, self.p)
        div = a / b
        self.assertEqual(div * b, a)

    def test_modulus_mismatch(self):
        a = FieldElement(5, 31)
        b = FieldElement(5, 17)
        with self.assertRaises(ValueError):
            _ = a + b


if __name__ == "__main__":
    unittest.main()
