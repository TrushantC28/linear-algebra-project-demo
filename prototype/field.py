"""Finite Field Arithmetic (F_p).

Provides the FieldElement class for exact modular arithmetic over a finite prime field F_p.
Satisfies Layer 1 requirements (F-1 through F-5) of the PRD:
- FieldElement wrapping an integer value and prime modulus p.
- Addition, subtraction, multiplication, and modular inversion via the Extended Euclidean Algorithm.
- Typed ZeroDivisionError on inverting zero.
- Equality comparison.
- Operation complexity notes.
"""

from typing import Union, Tuple


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Computes the Extended Euclidean Algorithm: gcd(a, b) and coefficients x, y such that a*x + b*y = gcd(a, b).
    
    Complexity: O(log(min(a, b))) integer division steps.
    """
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    while b != 0:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0


class FieldElement:
    """Represents an element of a finite field F_p where p is prime.
    
    All arithmetic is performed modulo p.
    """
    __slots__ = ("value", "p")

    def __init__(self, value: int, p: int):
        if not isinstance(p, int) or p <= 1:
            raise ValueError(f"Modulus p must be an integer > 1, got {p}")
        self.p = p
        self.value = value % p

    def _ensure_compatible(self, other: Union["FieldElement", int]) -> "FieldElement":
        """Converts an integer to a compatible FieldElement or checks modulus match."""
        if isinstance(other, FieldElement):
            if self.p != other.p:
                raise ValueError(f"Field modulus mismatch: {self.p} vs {other.p}")
            return other
        elif isinstance(other, int):
            return FieldElement(other, self.p)
        return NotImplemented

    def inverse(self) -> "FieldElement":
        """Computes the multiplicative inverse x such that self * x == 1 (mod p).
        
        Uses the Extended Euclidean Algorithm.
        Complexity: O(log p) bit operations.
        Raises:
            ZeroDivisionError: If self.value == 0 (zero has no inverse in any field).
        """
        if self.value == 0:
            raise ZeroDivisionError(f"Cannot invert 0: no modular inverse exists in F_{self.p}")

        gcd, x, _ = extended_gcd(self.value, self.p)
        if gcd != 1:
            raise ValueError(f"Value {self.value} and modulus {self.p} are not coprime (gcd={gcd})")

        return FieldElement(x % self.p, self.p)

    def __add__(self, other: Union["FieldElement", int]) -> "FieldElement":
        comp = self._ensure_compatible(other)
        if comp is NotImplemented:
            return NotImplemented
        return FieldElement((self.value + comp.value) % self.p, self.p)

    def __radd__(self, other: int) -> "FieldElement":
        return self.__add__(other)

    def __sub__(self, other: Union["FieldElement", int]) -> "FieldElement":
        comp = self._ensure_compatible(other)
        if comp is NotImplemented:
            return NotImplemented
        return FieldElement((self.value - comp.value) % self.p, self.p)

    def __rsub__(self, other: int) -> "FieldElement":
        comp = self._ensure_compatible(other)
        if comp is NotImplemented:
            return NotImplemented
        return FieldElement((comp.value - self.value) % self.p, self.p)

    def __mul__(self, other: Union["FieldElement", int]) -> "FieldElement":
        comp = self._ensure_compatible(other)
        if comp is NotImplemented:
            return NotImplemented
        return FieldElement((self.value * comp.value) % self.p, self.p)

    def __rmul__(self, other: int) -> "FieldElement":
        return self.__mul__(other)

    def __truediv__(self, other: Union["FieldElement", int]) -> "FieldElement":
        comp = self._ensure_compatible(other)
        if comp is NotImplemented:
            return NotImplemented
        return self * comp.inverse()

    def __rtruediv__(self, other: int) -> "FieldElement":
        comp = self._ensure_compatible(other)
        if comp is NotImplemented:
            return NotImplemented
        return comp * self.inverse()

    def __neg__(self) -> "FieldElement":
        return FieldElement((-self.value) % self.p, self.p)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FieldElement):
            return self.p == other.p and self.value == other.value
        elif isinstance(other, int):
            return self.value == (other % self.p)
        return False

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"FieldElement({self.value}, p={self.p})"

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash((self.value, self.p))
