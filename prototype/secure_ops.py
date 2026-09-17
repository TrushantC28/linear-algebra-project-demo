"""Secure Computation Primitives over finite field F_p.

Satisfies Layer 5 requirements (M-1, M-2, M-3) and PRD Section 9 Item 4:
- Secure addition: local addition of shares with zero inter-party communication.
- Private inner product / matrix product: simplified protocol with explicit labeling
  explaining Beaver triples vs. simplified cross-term evaluation.
- Verification: assert secure computation result matches plaintext computation.
"""

from typing import List, Union, TypeVar, Tuple
from .field import FieldElement
from .vector import Vector
from .matrix import Matrix
from .secret_sharing import AdditiveSecretSharing

T = TypeVar("T", FieldElement, Vector, Matrix)

SIMPLIFIED_PROTOCOL_EXPLANATION = """
[MPC Simplification Notice - PRD Section 9, Item 4]
In textbook multi-party computation (e.g., SPDZ or Beaver-triple MPC), multiplying
secret-shared values requires pre-distributed correlated randomness (Beaver triples
[a], [b], [c] where c = a * b) and an interactive communication round where parties
open masked values (x - a) and (y - b) to evaluate cross-terms without revealing shares.

In this prototype, we simulate secure multiplication via local share products plus
an algebraic cross-term accumulator, returning fresh additive shares to the parties.
This preserves mathematical correctness and demonstrates the interface layering
without requiring an asynchronous networking stack or offline triple generation.
""".strip()


def secure_add(shares_a: List[T], shares_b: List[T], log_trace: bool = False) -> List[T]:
    """Secure addition of two secret-shared values (FieldElement, Vector, or Matrix).
    
    Each party i adds its local shares independently:
        share_result[i] = share_a[i] + share_b[i]
    Zero communication between parties is required.
    
    Complexity: O(n * size) where n is the number of parties.
    """
    if len(shares_a) != len(shares_b):
        raise ValueError(f"Mismatched number of party shares: {len(shares_a)} vs {len(shares_b)}")

    num_parties = len(shares_a)
    result_shares: List[T] = []

    for i in range(num_parties):
        # Strictly local computation: Party i touches ONLY party i's shares
        local_sum = shares_a[i] + shares_b[i]
        result_shares.append(local_sum)
        if log_trace:
            print(f"  [Party {i+1}/{num_parties}] Computed local addition without any network communication.")

    return result_shares


def secure_inner_product(
    shares_u: List[Vector],
    shares_v: List[Vector],
    log_trace: bool = False
) -> List[FieldElement]:
    """Computes a private inner product of two secret-shared vectors u and v.
    
    Algebraic Principle:
        u = sum_i(u_i) and v = sum_j(v_j)
        u . v = sum_i sum_j (u_i . v_j)
              = sum_i (u_i . v_i)   [Local diagonal products]
              + sum_{i != j} (u_i . v_j) [Cross-term products]

    Per PRD Section 9 Item 4, this prototype implements the simplified protocol
    where local products are evaluated by each party, cross-terms are aggregated,
    and fresh additive shares of the resulting scalar are distributed to all parties.
    
    Complexity: O(n^2 * d) field operations.
    Returns:
        List of n FieldElement shares whose sum equals u . v.
    """
    if len(shares_u) != len(shares_v):
        raise ValueError("Mismatched number of party shares for inner product.")

    num_parties = len(shares_u)
    p = shares_u[0].p

    # Step 1: Each party computes its local diagonal dot product: u_i . v_i
    local_dots: List[FieldElement] = []
    for i in range(num_parties):
        local_dot = shares_u[i].dot(shares_v[i])
        local_dots.append(local_dot)
        if log_trace:
            print(f"  [Party {i+1}/{num_parties}] Local product computed: u_{i+1} . v_{i+1} = {local_dot.value}")

    # Step 2: Cross-terms sum_{i != j} (u_i . v_j)
    cross_sum = FieldElement(0, p)
    cross_term_count = 0
    for i in range(num_parties):
        for j in range(num_parties):
            if i != j:
                cross_term = shares_u[i].dot(shares_v[j])
                cross_sum += cross_term
                cross_term_count += 1

    if log_trace:
        print(f"  [MPC Protocol] Aggregated {cross_term_count} pairwise cross-terms into fresh shares.")

    total_inner_prod = FieldElement(0, p)
    for ld in local_dots:
        total_inner_prod += ld
    total_inner_prod += cross_sum

    # Re-share result additively among parties
    return AdditiveSecretSharing.split_element(total_inner_prod, num_parties)


def secure_matrix_product(
    shares_A: List[Matrix],
    shares_B: List[Matrix],
    log_trace: bool = False
) -> List[Matrix]:
    """Computes a private matrix product A @ B using secret shares.
    
    Each entry (r, c) of the resulting matrix is computed as the secure inner
    product of row r of A and column c of B.
    
    Returns:
        List of n Matrix shares whose sum equals A @ B.
    """
    if len(shares_A) != len(shares_B):
        raise ValueError("Mismatched number of party shares for matrix product.")

    num_parties = len(shares_A)
    m = shares_A[0].num_rows
    k = shares_A[0].num_cols
    n = shares_B[0].num_cols
    p = shares_A[0].p

    if shares_B[0].num_rows != k:
        raise ValueError(f"Inner dimensions mismatch: {shares_A[0].shape} vs {shares_B[0].shape}")

    # Party grids for output shares
    party_grids: List[List[List[FieldElement]]] = [
        [[FieldElement(0, p) for _ in range(n)] for _ in range(m)]
        for _ in range(num_parties)
    ]

    for r in range(m):
        for c in range(n):
            # Extract row r shares from A and col c shares from B
            row_shares = [shares_A[i].row(r) for i in range(num_parties)]
            col_shares = [shares_B[i].col(c) for i in range(num_parties)]

            # Secure inner product produces n shares for cell (r, c)
            cell_shares = secure_inner_product(row_shares, col_shares, log_trace=False)
            for i in range(num_parties):
                party_grids[i][r][c] = cell_shares[i]

    if log_trace:
        print(f"  [MPC Matrix] Computed all {m}x{n} entries via secure row-column inner products.")

    return [Matrix(party_grids[i]) for i in range(num_parties)]


def verify(test_name: str, secure_reconstructed, plaintext_val, verbose: bool = True) -> bool:
    """Verifies that the result reconstructed from secure computation equals the plaintext value.
    
    Prints a clear, color-formatted PASS or FAIL status.
    """
    is_match = (secure_reconstructed == plaintext_val)
    if verbose:
        status = "\033[92m[PASS]\033[0m" if is_match else "\033[91m[FAIL]\033[0m"
        print(f"{status} {test_name}: Secure result matches plaintext.")
        if not is_match:
            print(f"       Expected: {plaintext_val}")
            print(f"       Got:      {secure_reconstructed}")
    return is_match
