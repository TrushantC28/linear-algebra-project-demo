# Linear Algebra Library for Secure Computation — Working Prototype

**Group:** UGPCSE : 25  
**Deliverable:** Working Prototype (Modular Finite Field Linear Algebra & MPC)  
**Dependencies:** Python 3 Standard Library only (zero external numeric, MPC, or crypto dependencies)

---

## 1. Overview

This library implements a complete, layered pipeline for exact linear algebra over a finite prime field ($\mathbb{F}_p$) and simulated multi-party secure computation (MPC):

1. **Layer 1 (`prototype/field.py`)**: Finite Field Arithmetic ($\mathbb{F}_p$) with modular inversion via the Extended Euclidean Algorithm.
2. **Layer 2 (`prototype/vector.py`, `prototype/matrix.py`)**: Vector and Matrix core data structures with $O(n^3)$ matrix multiplication and dimension checks.
3. **Layer 3 (`prototype/linalg.py`)**: Exact linear algebra algorithms: Gaussian elimination, RREF, rank, determinant, and solving $Ax = b$ with singular matrix detection.
4. **Layer 4 (`prototype/secret_sharing.py`)**: Additive secret sharing (splitting & reconstruction of elements, vectors, and matrices).
5. **Layer 5 (`prototype/secure_ops.py`)**: Secure computation primitives (zero-communication addition, private inner product, and matrix product).
6. **Demo & Tests (`demo.py`, `prototype/tests/`)**: Narrated CLI walkthrough and 33 automated unit tests.

---

## 2. Quick Start & Commands

### A. Run the Narrated End-to-End Walkthrough

Run the default demonstration (uses prime $p = 997$ and $3$ parties):

```bash
python3 demo.py
```

#### Expected Output:
```text
############################################################################
#  LINEAR ALGEBRA LIBRARY FOR SECURE COMPUTATION — WORKING PROTOTYPE   #
#  Group UGPCSE : 25 | Python Standard Library Only (No External Libs) #
############################################################################
Configuration: Prime Field F_997 | Simulated Parties: 3


============================================================================
  [Stage 1] Field Arithmetic (F_p) — Layer 1
============================================================================
Underlying field operations run over finite field F_p using exact integer modular arithmetic.
Active prime modulus p = 997.

Created field elements:
  a = 385 (in F_997)
  b = 719 (in F_997)

Operations:
  Addition:       a + b = (385 + 719) mod 997 = 107
  Subtraction:    a - b = (385 - 719) mod 997 = 663
  Multiplication: a * b = (385 * 719) mod 997 = 646
  Modular Inverse (Extended GCD): a^(-1) = 549
  Inversion Check: a * a^(-1) = 385 * 549 mod 997 = 1 (Expected: 1)

Testing typed error handling for non-invertible zero (F-3):
  [CORRECT] Caught typed ZeroDivisionError on 0.inverse(): Cannot invert 0: no modular inverse exists in F_997

============================================================================
  [Stage 2] Vector and Matrix Algebra — Layer 2
============================================================================
Vectors and Matrices are built strictly from FieldElement instances.

Vectors:
  u = [12, 45, 89]
  v = [34, 78, 15]
  Vector Addition: u + v = [46, 123, 104]
  Inner Product:   u . v = 268

Matrices:
  A (shape (3, 3)):
[
  [   2,    3,    1],
  [   4,    1,    5],
  [   3,    2,    4]
]
  B (shape (3, 2)):
[
  [   5,    1],
  [   2,    4],
  [   3,    6]
]

Matrix Product C = A @ B (shape (3, 2)):
[
  [  19,   20],
  [  37,   38],
  [  31,   35]
]
  A Transpose A^T:
[
  [   2,    4,    3],
  [   3,    1,    2],
  [   1,    5,    4]
]

Dimension validation check: B @ A correctly rejected (Matrix dimension mismatch for multiplication: cannot multiply (3x2) with (3x3). Inner dimensions must match.)

============================================================================
  [Stage 3] Linear Algebra Algorithms over F_p — Layer 3
============================================================================
Exact linear algebra over F_p using modular inverses (Gaussian elimination, determinant, solve).

Properties of Matrix A:
  Determinant: det(A) = 987
  Matrix Rank: rank(A) = 3 (Full rank = 3)

--- Solving Linear System: A * x = b ---
Target RHS vector b = A * x_true = [82, 186, 163]
Solving for x using Gauss-Jordan elimination on augmented [A | b]...
Recovered solution:  x = [7, 13, 29]
Expected solution:   x = [7, 13, 29]
Back-substitution: A * x_solved = [82, 186, 163]
[PASS] Ax = b successfully solved and verified against original system.

--- Singular Matrix Detection (L-4) ---
Singular Matrix A_sing (det=0, rank=2):
[
  [   1,    2,    3],
  [   2,    4,    6],
  [   5,    1,    4]
]
[CORRECT] Detected singular system without crashing: Matrix A is singular (rank=2 < 3) and has no unique solution.

============================================================================
  [Stage 4] Additive Secret Sharing — Layer 4
============================================================================
Splitting vectors and matrices into 3 additive shares mod 997.
Property: sum(shares) mod p == secret; any k < n shares reveal strictly 0 bits of information.

Original Secret Vector: [105, 240, 680]
  Party 1 Share: [720, 177, 583] (uniformly random individual share)
  Party 2 Share: [440, 765, 143] (uniformly random individual share)
  Party 3 Share: [939, 295, 951] (uniformly random individual share)

Reconstructed Vector:   [105, 240, 680]
[PASS] Vector successfully reconstructed from all 3 shares.

Single Share Distribution Note (S-3):
Privacy Property (Information-Theoretic Security):
Given a secret s in F_p shared among n parties, any subset of k < n shares
consists of k independent, identically distributed uniform random elements in F_p.
Because uniform distributions have maximum entropy and are statistically independent
of s, observing any k < n shares reveals exactly 0 bits of information about s.

============================================================================
  [Stage 5] Secure Computation Primitives — Layer 5
============================================================================
Multi-party computation executed across parties held in single-process memory.

--- 1. Secure Addition (Zero Communication — M-1) ---
Plaintext input X: [200, 450, 700]
Plaintext input Y: [150, 300, 120]
Expected Sum:      [350, 750, 820]

Executing secure addition across parties:
  [Party 1/3] Computed local addition without any network communication.
  [Party 2/3] Computed local addition without any network communication.
  [Party 3/3] Computed local addition without any network communication.
Reconstructed sum: [350, 750, 820]
[PASS] Secure Addition: Secure result matches plaintext.

--- 2. Secure Private Inner Product (M-2) ---
[MPC Simplification Notice - PRD Section 9, Item 4]
In textbook multi-party computation (e.g., SPDZ or Beaver-triple MPC), multiplying
secret-shared values requires pre-distributed correlated randomness (Beaver triples
[a], [b], [c] where c = a * b) and an interactive communication round where parties
open masked values (x - a) and (y - b) to evaluate cross-terms without revealing shares.

In this prototype, we simulate secure multiplication via local share products plus
an algebraic cross-term accumulator, returning fresh additive shares to the parties.
This preserves mathematical correctness and demonstrates the interface layering
without requiring an asynchronous networking stack or offline triple generation.

Vector P: [42, 88, 19]
Vector Q: [17, 33, 91]
Plaintext inner product P . Q = 362

Executing secure inner product protocol:
  [Party 1/3] Local product computed: u_1 . v_1 = 953
  [Party 2/3] Local product computed: u_2 . v_2 = 462
  [Party 3/3] Local product computed: u_3 . v_3 = 417
  [MPC Protocol] Aggregated 6 pairwise cross-terms into fresh shares.

Reconstructed inner product: 362
[PASS] Secure Inner Product: Secure result matches plaintext.

--- 3. Secure Matrix Product ---
  [MPC Matrix] Computed all 2x2 entries via secure row-column inner products.
[PASS] Secure Matrix Product: Secure result matches plaintext.

============================================================================
  [Stage 6] Prototype Verification Summary
============================================================================
ALL PROTOTYPE CRITERIA MET AND VERIFIED:
  ✓ Layer 1: Finite Field Arithmetic (F_997) with Extended GCD Inverse
  ✓ Layer 2: Vector & Matrix Classes with dimension checks & O(n^3) matmul
  ✓ Layer 3: Gaussian elimination, Rank, Determinant, and Ax=b solver
  ✓ Layer 4: Additive secret sharing (split/reconstruct) across 3 parties
  ✓ Layer 5: Secure addition (zero-comm) & simplified secure inner product
  ✓ Plaintext-vs-Secure equivalence verified for all operations
  ✓ PRD Section 9 Prototype Limitations strictly respected
```

---

### B. Run with Custom Parameters & Explanations

You can vary the prime modulus, number of simulated MPC parties, and view algorithmic complexity notes:

```bash
python3 demo.py --prime 1009 --parties 4 --explain
```

- `--prime <P>`: Specify prime modulus $p$ (e.g., $31, 997, 1009$).
- `--parties <N>`: Set number of simulated parties (e.g., $2, 3, 4, 5$).
- `--explain`: Include time complexity and theoretical security explanations.

---

### C. Run the Unit Tests

Execute the 33 automated unit tests:

```bash
python3 -m unittest discover -s prototype/tests -p "test_*.py"
```

#### Expected Output:
```text
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.003s

OK
```

---

## 3. End-User Library Guide (How to Use in Code)

You can import and use any layer directly in your own Python scripts.

### 1. Field Arithmetic (`FieldElement`)

```python
from prototype.field import FieldElement

p = 997  # Prime modulus

# Create field elements
a = FieldElement(385, p)
b = FieldElement(719, p)

# Arithmetic
c = a + b       # (385 + 719) mod 997 == 107
d = a * b       # (385 * 719) mod 997 == 646

# Modular Inversion via Extended Euclidean Algorithm
inv_a = a.inverse()  # 549
assert a * inv_a == 1

# Inverting zero raises a typed ZeroDivisionError
try:
    FieldElement(0, p).inverse()
except ZeroDivisionError as e:
    print("Cannot invert 0:", e)
```

---

### 2. Vectors and Matrices (`Vector`, `Matrix`)

```python
from prototype.vector import Vector
from prototype.matrix import Matrix

p = 997

# Build vectors from integers
u = Vector.from_ints([1, 2, 3], p)
v = Vector.from_ints([4, 5, 6], p)

# Vector operations
w = u + v            # [5, 7, 9]
dot_val = u.dot(v)   # 1*4 + 2*5 + 3*6 = 32
scaled = 5 * u       # [5, 10, 15]

# Build matrices
A = Matrix.from_ints([
    [2, 1],
    [5, 7]
], p)

B = Matrix.from_ints([
    [3, 4],
    [1, 2]
], p)

# Matrix multiplication (O(n^3)) and transpose
C = A @ B
A_T = A.transpose()

# Matrix-vector multiplication
x = Vector.from_ints([3, 4], p)
b = A.vector_mul(x)
```

---

### 3. Linear Algebra Algorithms (`linalg`)

```python
from prototype.linalg import (
    determinant,
    rank,
    solve,
    matrix_inverse,
    SingularMatrixError
)
from prototype.matrix import Matrix
from prototype.vector import Vector

p = 997

A = Matrix.from_ints([
    [2, 3, 1],
    [4, 1, 5],
    [3, 2, 4]
], p)

# Properties
det = determinant(A)  # 987
rk = rank(A)          # 3

# Solve Ax = b
b = Vector.from_ints([82, 186, 163], p)
x = solve(A, b)
print("Solution x:", x)  # [7, 13, 29]

# Matrix inverse via Gauss-Jordan
A_inv = matrix_inverse(A)
assert A @ A_inv == Matrix.identity(3, p)

# Singular system detection
singular_A = Matrix.from_ints([[1, 2], [2, 4]], p)
try:
    solve(singular_A, Vector.from_ints([1, 2], p))
except SingularMatrixError as e:
    print("Caught singular system:", e)
```

---

### 4. Additive Secret Sharing (`AdditiveSecretSharing`)

```python
from prototype.secret_sharing import AdditiveSecretSharing
from prototype.vector import Vector

p = 997
num_parties = 3

secret_vector = Vector.from_ints([105, 240, 680], p)

# Split into 3 additive shares
shares = AdditiveSecretSharing.split_vector(secret_vector, num_parties=3)

# Each share is an independent Vector held by a party
for i, party_share in enumerate(shares):
    print(f"Party {i+1} share:", party_share)

# Reconstruct back
reconstructed = AdditiveSecretSharing.reconstruct_vector(shares)
assert reconstructed == secret_vector
```

---

### 5. Secure Multi-Party Computation (`secure_ops`)

```python
from prototype.secret_sharing import AdditiveSecretSharing
from prototype.secure_ops import secure_add, secure_inner_product, verify
from prototype.vector import Vector

p = 997
num_parties = 3

u = Vector.from_ints([42, 88, 19], p)
v = Vector.from_ints([17, 33, 91], p)

# Step 1: Input owners secret-share their vectors among parties
shares_u = AdditiveSecretSharing.split_vector(u, num_parties)
shares_v = AdditiveSecretSharing.split_vector(v, num_parties)

# Step 2: Secure Addition (Purely local - zero communication)
sum_shares = secure_add(shares_u, shares_v)
reconstructed_sum = AdditiveSecretSharing.reconstruct_vector(sum_shares)
verify("Secure Addition", reconstructed_sum, u + v)

# Step 3: Secure Inner Product (Simplified MPC protocol)
dot_shares = secure_inner_product(shares_u, shares_v)
reconstructed_dot = AdditiveSecretSharing.reconstruct_element(dot_shares)
verify("Secure Inner Product", reconstructed_dot, u.dot(v))
```

---

## 4. Architecture & Module Structure

```
linear-algebra-project-demo/
├── demo.py                        # Root convenience entry point
├── README.md                      # Documentation, usage guide & expected outputs
├── PRD.md                         # Product Requirement Document
└── prototype/
    ├── __init__.py                # Package exports
    ├── field.py                   # Layer 1: FieldElement, extended_gcd
    ├── vector.py                  # Layer 2: Vector over F_p
    ├── matrix.py                  # Layer 2: Matrix over F_p
    ├── linalg.py                  # Layer 3: Gaussian elimination, rank, det, solve, inverse
    ├── secret_sharing.py          # Layer 4: AdditiveSecretSharing
    ├── secure_ops.py              # Layer 5: secure_add, secure_inner_product, secure_matrix_product
    ├── demo.py                    # Narrated CLI walkthrough runner
    └── tests/
        ├── __init__.py
        ├── test_field.py          # FieldElement unit tests
        ├── test_vector_matrix.py  # Vector & Matrix unit tests
        ├── test_linalg.py         # Linear algebra algorithm unit tests
        └── test_secure_ops.py     # Secret sharing & secure ops unit tests
```

---

## 5. Prototype Boundaries & Limitations (PRD Section 9)

Per the build brief, the following intentional boundaries are maintained:

1. **Simulated Parties:** All parties run within a single Python process in shared memory. No network sockets or concurrency.
2. **Semi-Honest Model:** Assumes parties correctly follow the protocol (no malicious adversary detection).
3. **Simplified Private Multiplication Protocol:** Standard production MPC requires pre-distributed Beaver triples $[a], [b], [c]$. This prototype evaluates cross-terms algebraically and re-shares the result additively to demonstrate mathematical composition without offline triple generation overhead.
4. **No External Libraries:** Pure Python 3 standard library throughout.
