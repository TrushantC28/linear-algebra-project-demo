"""Narrated End-to-End Walkthrough Demonstration.

Linear Algebra Library for Secure Computation — Working Prototype
Prepared for Group UGPCSE : 25

Follows PRD requirements D-1, D-2, D-3, and Section 11 Acceptance Criteria:
- Narrates each stage: Field Setup -> Vector/Matrix Ops -> Linear System Solve ->
  Secret Sharing -> Secure Addition -> Secure Inner Product -> Plaintext Verification.
- Sane defaults with optional CLI arguments (--prime, --parties, --explain).
- Explicitly calls out prototype boundaries and simplifications (PRD Section 9).
"""

import sys
import os
import argparse
from typing import Optional

# Ensure project root and prototype directory are in sys.path for direct execution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
for p in [current_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from field import FieldElement
    from vector import Vector
    from matrix import Matrix
    from linalg import (
        gaussian_elimination,
        rref,
        rank,
        determinant,
        solve,
        matrix_inverse,
        SingularMatrixError,
    )
    from secret_sharing import AdditiveSecretSharing
    from secure_ops import (
        secure_add,
        secure_inner_product,
        secure_matrix_product,
        verify,
        SIMPLIFIED_PROTOCOL_EXPLANATION,
    )
except ImportError:
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
        SingularMatrixError,
    )
    from prototype.secret_sharing import AdditiveSecretSharing
    from prototype.secure_ops import (
        secure_add,
        secure_inner_product,
        secure_matrix_product,
        verify,
        SIMPLIFIED_PROTOCOL_EXPLANATION,
    )



# ANSI Color formatting
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def header(title: str, step: Optional[int] = None) -> None:
    print()
    border = "=" * 76
    prefix = f"[Stage {step}] " if step is not None else ""
    print(f"{CYAN}{BOLD}{border}{RESET}")
    print(f"{CYAN}{BOLD}  {prefix}{title}{RESET}")
    print(f"{CYAN}{BOLD}{border}{RESET}")


def subheader(title: str) -> None:
    print(f"\n{BLUE}{BOLD}--- {title} ---{RESET}")


def run_demo(prime: int = 997, num_parties: int = 3, explain: bool = False) -> None:
    print(f"\n{MAGENTA}{BOLD}{'#' * 76}")
    print(f"#  LINEAR ALGEBRA LIBRARY FOR SECURE COMPUTATION — WORKING PROTOTYPE   #")
    print(f"#  Group UGPCSE : 25 | Python Standard Library Only (No External Libs) #")
    print(f"{'#' * 76}{RESET}")
    print(f"Configuration: Prime Field F_{prime} | Simulated Parties: {num_parties}\n")

    # =========================================================================
    # STAGE 1: FIELD ARITHMETIC (Layer 1)
    # =========================================================================
    header("Field Arithmetic (F_p) — Layer 1", step=1)
    print("Underlying field operations run over finite field F_p using exact integer modular arithmetic.")
    print(f"Active prime modulus p = {prime}.")

    a = FieldElement(385, prime)
    b = FieldElement(719, prime)
    print(f"\nCreated field elements:")
    print(f"  a = {a} (in F_{prime})")
    print(f"  b = {b} (in F_{prime})")

    add_res = a + b
    sub_res = a - b
    mul_res = a * b
    a_inv = a.inverse()
    ident = a * a_inv

    print(f"\nOperations:")
    print(f"  Addition:       a + b = ({a.value} + {b.value}) mod {prime} = {add_res}")
    print(f"  Subtraction:    a - b = ({a.value} - {b.value}) mod {prime} = {sub_res}")
    print(f"  Multiplication: a * b = ({a.value} * {b.value}) mod {prime} = {mul_res}")
    print(f"  Modular Inverse (Extended GCD): a^(-1) = {a_inv}")
    print(f"  Inversion Check: a * a^(-1) = {a.value} * {a_inv.value} mod {prime} = {ident} (Expected: 1)")
    assert ident == 1, "Field inversion verification failed!"

    print(f"\nTesting typed error handling for non-invertible zero (F-3):")
    zero = FieldElement(0, prime)
    try:
        zero.inverse()
        print("  Error: Zero inversion did not raise an exception!")
    except ZeroDivisionError as e:
        print(f"  {GREEN}[CORRECT]{RESET} Caught typed ZeroDivisionError on 0.inverse(): {DIM}{e}{RESET}")

    if explain:
        print(f"{DIM}Complexity: Add/Sub/Mul is O(1); Inverse via Extended GCD is O(log p).{RESET}")

    # =========================================================================
    # STAGE 2: VECTOR AND MATRIX ALGEBRA (Layer 2)
    # =========================================================================
    header("Vector and Matrix Algebra — Layer 2", step=2)
    print("Vectors and Matrices are built strictly from FieldElement instances.")

    u = Vector.from_ints([12, 45, 89], prime)
    v = Vector.from_ints([34, 78, 15], prime)
    print(f"\nVectors:")
    print(f"  u = {u}")
    print(f"  v = {v}")

    vec_add = u + v
    vec_dot = u.dot(v)
    # Plaintext calculation check: 12*34 + 45*78 + 89*15 = 408 + 3510 + 1335 = 5253 % 997 = 268
    print(f"  Vector Addition: u + v = {vec_add}")
    print(f"  Inner Product:   u . v = {vec_dot}")

    A = Matrix.from_ints([
        [2, 3, 1],
        [4, 1, 5],
        [3, 2, 4]
    ], prime)

    B = Matrix.from_ints([
        [5, 1],
        [2, 4],
        [3, 6]
    ], prime)

    print(f"\nMatrices:")
    print(f"  A (shape {A.shape}):\n{A}")
    print(f"  B (shape {B.shape}):\n{B}")

    C = A @ B
    print(f"\nMatrix Product C = A @ B (shape {C.shape}):\n{C}")
    print(f"  A Transpose A^T:\n{A.transpose()}")

    # Dimension mismatch check
    try:
        _ = B @ A
    except ValueError as e:
        print(f"\nDimension validation check: B @ A correctly rejected ({e})")

    # =========================================================================
    # STAGE 3: LINEAR ALGEBRA ALGORITHMS (Layer 3)
    # =========================================================================
    header("Linear Algebra Algorithms over F_p — Layer 3", step=3)
    print("Exact linear algebra over F_p using modular inverses (Gaussian elimination, determinant, solve).")

    A_det = determinant(A)
    A_rank = rank(A)
    print(f"\nProperties of Matrix A:")
    print(f"  Determinant: det(A) = {A_det}")
    print(f"  Matrix Rank: rank(A) = {A_rank} (Full rank = {A.num_rows})")

    subheader("Solving Linear System: A * x = b")
    # Choose true solution x_true
    x_true = Vector.from_ints([7, 13, 29], prime)
    # Compute RHS b = A * x_true
    b_rhs = A.vector_mul(x_true)
    print(f"Target RHS vector b = A * x_true = {b_rhs}")

    print(f"Solving for x using Gauss-Jordan elimination on augmented [A | b]...")
    x_solved = solve(A, b_rhs)
    print(f"Recovered solution:  x = {x_solved}")
    print(f"Expected solution:   x = {x_true}")

    # Back-substitution verification
    b_verify = A.vector_mul(x_solved)
    print(f"Back-substitution: A * x_solved = {b_verify}")
    assert x_solved == x_true, "Linear system solve produced incorrect vector!"
    print(f"{GREEN}[PASS]{RESET} Ax = b successfully solved and verified against original system.")

    subheader("Singular Matrix Detection (L-4)")
    # Construct a matrix with linearly dependent rows
    A_singular = Matrix.from_ints([
        [1, 2, 3],
        [2, 4, 6],  # Row 1 is 2 * Row 0
        [5, 1, 4]
    ], prime)
    print(f"Singular Matrix A_sing (det={determinant(A_singular)}, rank={rank(A_singular)}):\n{A_singular}")
    try:
        solve(A_singular, Vector.from_ints([1, 2, 3], prime))
    except SingularMatrixError as e:
        print(f"{GREEN}[CORRECT]{RESET} Detected singular system without crashing: {DIM}{e}{RESET}")

    # =========================================================================
    # STAGE 4: SECRET SHARING (Layer 4)
    # =========================================================================
    header("Additive Secret Sharing — Layer 4", step=4)
    print(f"Splitting vectors and matrices into {num_parties} additive shares mod {prime}.")
    print("Property: sum(shares) mod p == secret; any k < n shares reveal strictly 0 bits of information.")

    secret_vec = Vector.from_ints([105, 240, 680], prime)
    print(f"\nOriginal Secret Vector: {secret_vec}")

    shares = AdditiveSecretSharing.split_vector(secret_vec, num_parties=num_parties)
    for i, s in enumerate(shares):
        print(f"  Party {i+1} Share: {s} {DIM}(uniformly random individual share){RESET}")

    reconstructed_vec = AdditiveSecretSharing.reconstruct_vector(shares)
    print(f"\nReconstructed Vector:   {reconstructed_vec}")
    assert reconstructed_vec == secret_vec, "Vector reconstruction failed!"
    print(f"{GREEN}[PASS]{RESET} Vector successfully reconstructed from all {num_parties} shares.")

    print(f"\n{YELLOW}Single Share Distribution Note (S-3):{RESET}")
    print(AdditiveSecretSharing.privacy_guarantee_explanation())

    # =========================================================================
    # STAGE 5: SECURE COMPUTATION PRIMITIVES (Layer 5)
    # =========================================================================
    header("Secure Computation Primitives — Layer 5", step=5)
    print("Multi-party computation executed across parties held in single-process memory.")

    subheader("1. Secure Addition (Zero Communication — M-1)")
    vec_X = Vector.from_ints([200, 450, 700], prime)
    vec_Y = Vector.from_ints([150, 300, 120], prime)
    plaintext_sum = vec_X + vec_Y
    print(f"Plaintext input X: {vec_X}")
    print(f"Plaintext input Y: {vec_Y}")
    print(f"Expected Sum:      {plaintext_sum}")

    shares_X = AdditiveSecretSharing.split_vector(vec_X, num_parties)
    shares_Y = AdditiveSecretSharing.split_vector(vec_Y, num_parties)

    print("\nExecuting secure addition across parties:")
    sum_shares = secure_add(shares_X, shares_Y, log_trace=True)
    reconstructed_sum = AdditiveSecretSharing.reconstruct_vector(sum_shares)
    print(f"Reconstructed sum: {reconstructed_sum}")
    verify("Secure Addition", reconstructed_sum, plaintext_sum)

    subheader("2. Secure Private Inner Product (M-2)")
    print(f"{YELLOW}{SIMPLIFIED_PROTOCOL_EXPLANATION}{RESET}\n")

    vec_P = Vector.from_ints([42, 88, 19], prime)
    vec_Q = Vector.from_ints([17, 33, 91], prime)
    plaintext_dot = vec_P.dot(vec_Q)
    print(f"Vector P: {vec_P}")
    print(f"Vector Q: {vec_Q}")
    print(f"Plaintext inner product P . Q = {plaintext_dot}")

    shares_P = AdditiveSecretSharing.split_vector(vec_P, num_parties)
    shares_Q = AdditiveSecretSharing.split_vector(vec_Q, num_parties)

    print("\nExecuting secure inner product protocol:")
    secure_dot_shares = secure_inner_product(shares_P, shares_Q, log_trace=True)
    reconstructed_dot = AdditiveSecretSharing.reconstruct_element(secure_dot_shares)
    print(f"\nReconstructed inner product: {reconstructed_dot}")
    verify("Secure Inner Product", reconstructed_dot, plaintext_dot)

    subheader("3. Secure Matrix Product")
    mat_M1 = Matrix.from_ints([[3, 5], [7, 2]], prime)
    mat_M2 = Matrix.from_ints([[4, 1], [6, 8]], prime)
    plaintext_mat_prod = mat_M1 @ mat_M2

    shares_M1 = AdditiveSecretSharing.split_matrix(mat_M1, num_parties)
    shares_M2 = AdditiveSecretSharing.split_matrix(mat_M2, num_parties)

    secure_mat_shares = secure_matrix_product(shares_M1, shares_M2, log_trace=True)
    reconstructed_mat = AdditiveSecretSharing.reconstruct_matrix(secure_mat_shares)
    verify("Secure Matrix Product", reconstructed_mat, plaintext_mat_prod)

    # =========================================================================
    # STAGE 6: SUMMARY & ACCEPTANCE CRITERIA
    # =========================================================================
    header("Prototype Verification Summary", step=6)
    print(f"{GREEN}{BOLD}ALL PROTOTYPE CRITERIA MET AND VERIFIED:{RESET}")
    print(f"  {GREEN}✓{RESET} Layer 1: Finite Field Arithmetic (F_{prime}) with Extended GCD Inverse")
    print(f"  {GREEN}✓{RESET} Layer 2: Vector & Matrix Classes with dimension checks & O(n^3) matmul")
    print(f"  {GREEN}✓{RESET} Layer 3: Gaussian elimination, Rank, Determinant, and Ax=b solver")
    print(f"  {GREEN}✓{RESET} Layer 4: Additive secret sharing (split/reconstruct) across {num_parties} parties")
    print(f"  {GREEN}✓{RESET} Layer 5: Secure addition (zero-comm) & simplified secure inner product")
    print(f"  {GREEN}✓{RESET} Plaintext-vs-Secure equivalence verified for all operations")
    print(f"  {GREEN}✓{RESET} PRD Section 9 Prototype Limitations strictly respected\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Linear Algebra Library for Secure Computation — Working Prototype Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--prime", "-p",
        type=int,
        default=997,
        help="Prime modulus for finite field F_p (default: 997)",
    )
    parser.add_argument(
        "--parties", "-n",
        type=int,
        default=3,
        help="Number of simulated MPC parties (default: 3)",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Print detailed algorithmic complexity and security notes",
    )
    args = parser.parse_args()

    run_demo(prime=args.prime, num_parties=args.parties, explain=args.explain)


if __name__ == "__main__":
    main()
