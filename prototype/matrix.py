"""Matrix data structure over a finite field F_p.

Satisfies Layer 2 requirements (V-2, V-3, V-4) of the PRD:
- 2-D array of FieldElements composed of rows of Vectors.
- Construction from nested lists of ints or list of Vectors.
- Indexing by (row, col) or row index.
- Dimensions (num_rows, num_cols, shape).
- Addition, subtraction, scalar multiplication, transpose, equality.
- Standard O(n^3) matrix multiplication with dimension checks.
- Matrix-vector multiplication A * x.
- Operation complexity notes in docstrings.
"""

from typing import List, Tuple, Union, Iterator
from .field import FieldElement
from .vector import Vector


class Matrix:
    """Represents a 2-D matrix of elements in a finite field F_p."""

    def __init__(self, rows: Union[List[Vector], List[List[FieldElement]]]):
        if not rows:
            raise ValueError("Matrix must contain at least one row.")

        vector_rows: List[Vector] = []
        for i, row in enumerate(rows):
            if isinstance(row, Vector):
                vector_rows.append(row)
            elif isinstance(row, list):
                vector_rows.append(Vector(row))
            else:
                raise TypeError(f"Row {i} must be a Vector or List[FieldElement], got {type(row).__name__}")

        num_cols = len(vector_rows[0])
        p = vector_rows[0].p
        for i, row in enumerate(vector_rows):
            if len(row) != num_cols:
                raise ValueError(f"Inconsistent row dimensions: row 0 has length {num_cols}, row {i} has length {len(row)}")
            if row.p != p:
                raise ValueError(f"Inconsistent field moduli: row 0 has p={p}, row {i} has p={row.p}")

        self._rows: List[Vector] = vector_rows
        self._p: int = p

    @classmethod
    def from_ints(cls, grid: List[List[int]], p: int) -> "Matrix":
        """Factory method to construct a Matrix from a 2-D nested list of integers mod p.
        
        Complexity: O(m * n) conversions for an m x n matrix.
        """
        if not grid or not grid[0]:
            raise ValueError("Grid must be non-empty.")
        return cls([Vector.from_ints(row, p) for row in grid])

    @classmethod
    def identity(cls, n: int, p: int) -> "Matrix":
        """Constructs an n x n identity matrix I_n over F_p.
        
        Complexity: O(n^2).
        """
        if n <= 0:
            raise ValueError("Identity dimension must be positive.")
        grid = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        return cls.from_ints(grid, p)

    @classmethod
    def zeros(cls, rows: int, cols: int, p: int) -> "Matrix":
        """Constructs a rows x cols zero matrix over F_p.
        
        Complexity: O(rows * cols).
        """
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        return cls.from_ints(grid, p)

    @property
    def p(self) -> int:
        """Prime modulus p of the underlying field."""
        return self._p

    @property
    def num_rows(self) -> int:
        """Number of rows (m). Complexity: O(1)."""
        return len(self._rows)

    @property
    def num_cols(self) -> int:
        """Number of columns (n). Complexity: O(1)."""
        return len(self._rows[0])

    @property
    def shape(self) -> Tuple[int, int]:
        """Matrix dimensions (m, n). Complexity: O(1)."""
        return (self.num_rows, self.num_cols)

    def row(self, r: int) -> Vector:
        """Returns row r as a Vector. Complexity: O(1)."""
        return self._rows[r]

    def col(self, c: int) -> Vector:
        """Returns column c as a Vector. Complexity: O(m)."""
        if c < 0 or c >= self.num_cols:
            raise IndexError(f"Column index {c} out of range for matrix with {self.num_cols} columns")
        return Vector([self._rows[r][c] for r in range(self.num_rows)])

    def __getitem__(self, key: Union[Tuple[int, int], int]) -> Union[FieldElement, Vector]:
        """Index by (row, col) to get a FieldElement, or by row integer to get a Vector row.
        
        Complexity: O(1).
        """
        if isinstance(key, tuple):
            r, c = key
            return self._rows[r][c]
        elif isinstance(key, int):
            return self._rows[key]
        raise TypeError(f"Matrix indices must be integers or (row, col) tuples, not {type(key).__name__}")

    def __len__(self) -> int:
        """Number of rows. Complexity: O(1)."""
        return self.num_rows

    def __iter__(self) -> Iterator[Vector]:
        """Iterate over rows as Vectors."""
        return iter(self._rows)

    def to_ints(self) -> List[List[int]]:
        """Returns 2-D list of plain integers."""
        return [row.to_ints() for row in self._rows]

    def transpose(self) -> "Matrix":
        """Computes the matrix transpose A^T.
        
        Complexity: O(m * n) copy operations where shape is (m, n).
        """
        transposed_grid = [
            [self._rows[r][c] for r in range(self.num_rows)]
            for c in range(self.num_cols)
        ]
        return Matrix(transposed_grid)

    def __add__(self, other: "Matrix") -> "Matrix":
        """Matrix addition A + B in F_p.
        
        Complexity: O(m * n) field additions.
        Raises:
            ValueError: If dimensions mismatch.
        """
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.shape != other.shape:
            raise ValueError(f"Matrix dimension mismatch for addition: {self.shape} vs {other.shape}")
        if self.p != other.p:
            raise ValueError(f"Field modulus mismatch: p={self.p} vs p={other.p}")
        return Matrix([r1 + r2 for r1, r2 in zip(self._rows, other._rows)])

    def __sub__(self, other: "Matrix") -> "Matrix":
        """Matrix subtraction A - B in F_p.
        
        Complexity: O(m * n) field subtractions.
        """
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.shape != other.shape:
            raise ValueError(f"Matrix dimension mismatch for subtraction: {self.shape} vs {other.shape}")
        if self.p != other.p:
            raise ValueError(f"Field modulus mismatch: p={self.p} vs p={other.p}")
        return Matrix([r1 - r2 for r1, r2 in zip(self._rows, other._rows)])

    def __neg__(self) -> "Matrix":
        """Matrix negation -A in F_p. Complexity: O(m * n)."""
        return Matrix([-row for row in self._rows])

    def __mul__(self, scalar: Union[FieldElement, int]) -> "Matrix":
        """Scalar-matrix multiplication A * c in F_p.
        
        Complexity: O(m * n) field multiplications.
        """
        if isinstance(scalar, (FieldElement, int)):
            return Matrix([row * scalar for row in self._rows])
        return NotImplemented

    def __rmul__(self, scalar: Union[FieldElement, int]) -> "Matrix":
        """Scalar-matrix multiplication c * A in F_p."""
        return self.__mul__(scalar)

    def matmul(self, other: "Matrix") -> "Matrix":
        """Standard matrix multiplication A @ B.
        
        For A of size (m x k) and B of size (k x n), result is (m x n).
        Complexity: O(m * k * n) field multiplications and additions (standard O(n^3) for square matrices).
        Raises:
            ValueError: If inner dimensions mismatch (A.num_cols != B.num_rows).
        """
        if not isinstance(other, Matrix):
            raise TypeError(f"Cannot matrix multiply with non-Matrix type {type(other).__name__}")
        if self.num_cols != other.num_rows:
            raise ValueError(
                f"Matrix dimension mismatch for multiplication: cannot multiply ({self.num_rows}x{self.num_cols}) "
                f"with ({other.num_rows}x{other.num_cols}). Inner dimensions must match."
            )
        if self.p != other.p:
            raise ValueError(f"Field modulus mismatch: p={self.p} vs p={other.p}")

        m = self.num_rows
        k = self.num_cols
        n = other.num_cols

        result_grid: List[List[FieldElement]] = []
        for r in range(m):
            result_row: List[FieldElement] = []
            for c in range(n):
                acc = FieldElement(0, self.p)
                for idx in range(k):
                    acc += (self._rows[r][idx] * other._rows[idx][c])
                result_row.append(acc)
            result_grid.append(result_row)

        return Matrix(result_grid)

    def __matmul__(self, other: "Matrix") -> "Matrix":
        return self.matmul(other)

    def vector_mul(self, vec: Vector) -> Vector:
        """Matrix-vector multiplication A * x.
        
        Complexity: O(m * n) operations for m x n matrix and n-vector.
        Raises:
            ValueError: If self.num_cols != len(vec).
        """
        if not isinstance(vec, Vector):
            raise TypeError(f"Expected Vector, got {type(vec).__name__}")
        if self.num_cols != len(vec):
            raise ValueError(f"Dimension mismatch for matrix-vector multiplication: {self.shape} and vector len {len(vec)}")
        if self.p != vec.p:
            raise ValueError(f"Field modulus mismatch: p={self.p} vs p={vec.p}")

        return Vector([self._rows[r].dot(vec) for r in range(self.num_rows)])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix):
            return False
        if self.shape != other.shape or self.p != other.p:
            return False
        return self._rows == other._rows

    def __repr__(self) -> str:
        return f"Matrix({self.to_ints()}, p={self.p})"

    def __str__(self) -> str:
        row_strs = ["  [" + ", ".join(f"{el.value:>4}" for el in r) + "]" for r in self._rows]
        return "[\n" + ",\n".join(row_strs) + "\n]"
