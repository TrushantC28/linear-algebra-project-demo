"""Additive Secret Sharing over finite field F_p.

Satisfies Layer 4 requirements (S-1 through S-4) of the PRD:
- Split a FieldElement, Vector, or Matrix into n additive shares such that
  sum(shares) mod p == secret.
- Reconstruct the original value from the full set of shares.
- Privacy explanation: Any subset of < n shares is uniformly distributed across F_p,
  revealing strictly zero information about the secret.
- Single-process simulation of parties.
"""

import secrets
from typing import List, Optional, Union
from .field import FieldElement
from .vector import Vector
from .matrix import Matrix


class AdditiveSecretSharing:
    """Provides additive secret sharing primitives for FieldElements, Vectors, and Matrices."""

    @staticmethod
    def split_element(secret: FieldElement, num_parties: int) -> List[FieldElement]:
        """Splits a FieldElement into n additive shares.
        
        Let s be the secret in F_p. We generate n-1 independent uniform random values
        s_1, s_2, ..., s_{n-1} in F_p, and set s_n = (s - sum_{i=1}^{n-1} s_i) mod p.
        Then sum_{i=1}^n s_i = s (mod p).
        
        Complexity: O(n) field additions.
        Privacy:
            Since s_1, ..., s_{n-1} are drawn uniformly at random, any subset of
            k < n shares has a joint distribution identical to k independent uniform
            field elements, completely independent of the secret value s.
        """
        if num_parties < 2:
            raise ValueError(f"Number of parties must be at least 2, got {num_parties}")

        p = secret.p
        random_shares: List[FieldElement] = []
        running_sum = FieldElement(0, p)

        for _ in range(num_parties - 1):
            rand_val = secrets.randbelow(p)
            share = FieldElement(rand_val, p)
            random_shares.append(share)
            running_sum += share

        final_share = secret - running_sum
        return random_shares + [final_share]

    @staticmethod
    def reconstruct_element(shares: List[FieldElement]) -> FieldElement:
        """Reconstructs the original secret by summing all shares mod p.
        
        Complexity: O(n) field additions.
        """
        if not shares:
            raise ValueError("Shares list must not be empty.")
        p = shares[0].p
        acc = FieldElement(0, p)
        for share in shares:
            if share.p != p:
                raise ValueError("All shares must belong to the same field.")
            acc += share
        return acc

    @staticmethod
    def split_vector(secret: Vector, num_parties: int) -> List[Vector]:
        """Splits a Vector of length d into n additive Vector shares.
        
        Party i receives a Vector whose j-th coordinate is party i's share of secret[j].
        Complexity: O(n * d).
        """
        if num_parties < 2:
            raise ValueError(f"Number of parties must be at least 2, got {num_parties}")

        p = secret.p
        dim = len(secret)
        # party_vectors[party_idx][coord_idx]
        party_elements: List[List[FieldElement]] = [[] for _ in range(num_parties)]

        for el in secret:
            el_shares = AdditiveSecretSharing.split_element(el, num_parties)
            for party_idx, share in enumerate(el_shares):
                party_elements[party_idx].append(share)

        return [Vector(party_elements[i]) for i in range(num_parties)]

    @staticmethod
    def reconstruct_vector(shares: List[Vector]) -> Vector:
        """Reconstructs the original Vector by summing all Vector shares component-wise.
        
        Complexity: O(n * d).
        """
        if not shares:
            raise ValueError("Shares list must not be empty.")
        dim = len(shares[0])
        p = shares[0].p

        reconstructed_elements: List[FieldElement] = []
        for j in range(dim):
            coord_shares = [party_vec[j] for party_vec in shares]
            reconstructed_elements.append(AdditiveSecretSharing.reconstruct_element(coord_shares))

        return Vector(reconstructed_elements)

    @staticmethod
    def split_matrix(secret: Matrix, num_parties: int) -> List[Matrix]:
        """Splits an m x n Matrix into k additive Matrix shares.
        
        Party i receives an m x n Matrix of shares.
        Complexity: O(k * m * n).
        """
        if num_parties < 2:
            raise ValueError(f"Number of parties must be at least 2, got {num_parties}")

        rows, cols = secret.shape
        p = secret.p

        # party_grids[party_idx][r][c]
        party_grids: List[List[List[FieldElement]]] = [
            [[FieldElement(0, p) for _ in range(cols)] for _ in range(rows)]
            for _ in range(num_parties)
        ]

        for r in range(rows):
            for c in range(cols):
                el_shares = AdditiveSecretSharing.split_element(secret[r, c], num_parties)
                for party_idx, share in enumerate(el_shares):
                    party_grids[party_idx][r][c] = share

        return [Matrix(party_grids[i]) for i in range(num_parties)]

    @staticmethod
    def reconstruct_matrix(shares: List[Matrix]) -> Matrix:
        """Reconstructs the original Matrix by summing all Matrix shares element-wise.
        
        Complexity: O(k * m * n).
        """
        if not shares:
            raise ValueError("Shares list must not be empty.")
        rows, cols = shares[0].shape
        p = shares[0].p

        reconstructed_grid: List[List[FieldElement]] = []
        for r in range(rows):
            reconstructed_row: List[FieldElement] = []
            for c in range(cols):
                cell_shares = [party_mat[r, c] for party_mat in shares]
                reconstructed_row.append(AdditiveSecretSharing.reconstruct_element(cell_shares))
            reconstructed_grid.append(reconstructed_row)

        return Matrix(reconstructed_grid)

    @staticmethod
    def privacy_guarantee_explanation() -> str:
        """Explains why additive secret sharing provides perfect information-theoretic secrecy."""
        return (
            "Privacy Property (Information-Theoretic Security):\n"
            "Given a secret s in F_p shared among n parties, any subset of k < n shares\n"
            "consists of k independent, identically distributed uniform random elements in F_p.\n"
            "Because uniform distributions have maximum entropy and are statistically independent\n"
            "of s, observing any k < n shares reveals exactly 0 bits of information about s."
        )
