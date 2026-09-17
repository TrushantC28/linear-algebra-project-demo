"""Vector data structure over a finite field F_p.

Satisfies Layer 2 requirements (V-1, V-4) of the PRD:
- Ordered sequence of FieldElements with identical modulus p.
- Construction from plain integers or FieldElements.
- Vector addition, scalar multiplication, dot product, equality.
- Explicit dimension mismatch checking.
- Operation complexity notes in docstrings.
"""

from typing import List, Union, Iterator
from .field import FieldElement


class Vector:
    """Represents a vector of elements in a finite field F_p."""

    def __init__(self, elements: List[FieldElement]):
        if not elements:
            raise ValueError("Vector must have at least one element.")
        p = elements[0].p
        for i, el in enumerate(elements):
            if not isinstance(el, FieldElement):
                raise TypeError(f"Element at index {i} must be a FieldElement, got {type(el).__name__}")
            if el.p != p:
                raise ValueError(f"Inconsistent field moduli in vector: element 0 has p={p}, element {i} has p={el.p}")
        self._elements: List[FieldElement] = list(elements)
        self._p: int = p

    @classmethod
    def from_ints(cls, values: List[int], p: int) -> "Vector":
        """Factory method to construct a Vector from plain Python integers mod p.
        
        Complexity: O(n) conversions where n = len(values).
        """
        return cls([FieldElement(v, p) for v in values])

    @property
    def p(self) -> int:
        """The prime modulus p of the field."""
        return self._p

    def __len__(self) -> int:
        """Length (dimension) of the vector. Complexity: O(1)."""
        return len(self._elements)

    def __getitem__(self, index: int) -> FieldElement:
        """Access element at given index. Complexity: O(1)."""
        return self._elements[index]

    def __iter__(self) -> Iterator[FieldElement]:
        """Iterate over elements."""
        return iter(self._elements)

    def to_ints(self) -> List[int]:
        """Returns plain integer representation of the vector components."""
        return [e.value for e in self._elements]

    def __add__(self, other: "Vector") -> "Vector":
        """Component-wise addition of two vectors in F_p.
        
        Complexity: O(n) field additions.
        Raises:
            ValueError: If vector dimensions or field moduli mismatch.
        """
        if not isinstance(other, Vector):
            return NotImplemented
        if len(self) != len(other):
            raise ValueError(f"Vector dimension mismatch for addition: {len(self)} vs {len(other)}")
        if self.p != other.p:
            raise ValueError(f"Field modulus mismatch: p={self.p} vs p={other.p}")
        return Vector([a + b for a, b in zip(self._elements, other._elements)])

    def __sub__(self, other: "Vector") -> "Vector":
        """Component-wise subtraction of two vectors in F_p.
        
        Complexity: O(n) field subtractions.
        """
        if not isinstance(other, Vector):
            return NotImplemented
        if len(self) != len(other):
            raise ValueError(f"Vector dimension mismatch for subtraction: {len(self)} vs {len(other)}")
        if self.p != other.p:
            raise ValueError(f"Field modulus mismatch: p={self.p} vs p={other.p}")
        return Vector([a - b for a, b in zip(self._elements, other._elements)])

    def __neg__(self) -> "Vector":
        """Unary negation of vector elements in F_p. Complexity: O(n)."""
        return Vector([-el for el in self._elements])

    def __mul__(self, scalar: Union[FieldElement, int]) -> "Vector":
        """Scalar multiplication v * c where c in F_p.
        
        Complexity: O(n) field multiplications.
        """
        if isinstance(scalar, (FieldElement, int)):
            return Vector([el * scalar for el in self._elements])
        return NotImplemented

    def __rmul__(self, scalar: Union[FieldElement, int]) -> "Vector":
        """Scalar multiplication c * v where c in F_p.
        
        Complexity: O(n) field multiplications.
        """
        return self.__mul__(scalar)

    def dot(self, other: "Vector") -> FieldElement:
        """Computes the inner product (dot product) of two vectors: sum(u_i * v_i) mod p.
        
        Complexity: O(n) field multiplications and O(n) field additions.
        Raises:
            ValueError: If vector dimensions or field moduli mismatch.
        """
        if not isinstance(other, Vector):
            raise TypeError(f"Cannot compute dot product with non-Vector type {type(other).__name__}")
        if len(self) != len(other):
            raise ValueError(f"Vector dimension mismatch for dot product: {len(self)} vs {len(other)}")
        if self.p != other.p:
            raise ValueError(f"Field modulus mismatch: p={self.p} vs p={other.p}")

        acc = FieldElement(0, self.p)
        for a, b in zip(self._elements, other._elements):
            acc += (a * b)
        return acc

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return False
        if len(self) != len(other) or self.p != other.p:
            return False
        return self._elements == other._elements

    def __repr__(self) -> str:
        return f"Vector({[e.value for e in self._elements]}, p={self.p})"

    def __str__(self) -> str:
        return f"[{', '.join(str(e.value) for e in self._elements)}]"
