# Product Requirement Document
## Linear Algebra Library for Secure Computation — Working Prototype

**Document type:** Prototype PRD (build handoff for a coding agent)
**Project:** Development of a Linear Algebra Library for Secure Computation
**Prepared for:** Group UGPCSE : 25
**Status:** Draft v1.0

---

## 1. Purpose of This Document

This PRD is **not** the spec for the final, three-worklet academic deliverable. It is a
scoped-down spec for a **single working prototype** that walks end-to-end through the whole
pipeline — field arithmetic → vector/matrix algebra → linear-algebra algorithms →
secret sharing → secure computation — so the team can see and demo how the pieces fit
together *before* committing to the full, polished implementation.

Hand this document to a coding agent as the build brief. Section 9 ("Prototype
Limitations") is deliberately explicit and should be treated as binding — the agent
should not "improve" the prototype past these boundaries without being asked.

---

## 2. Background

The parent project builds a reusable vector/matrix library whose arithmetic runs over a
finite field (mod a prime) instead of floating point, so it can support secure
multi-party computation (MPC). It is split into three cumulative worklets:

| Worklet | Focus |
|---|---|
| 1 | Field arithmetic, and the Vector / Matrix core types |
| 2 | Linear-algebra algorithms over the field (Gaussian elimination, rank, determinant, solving `Ax = b`) |
| 3 | Secure-computation primitives (additive secret sharing, secure addition, private inner/matrix product) |

No numeric libraries (NumPy, BLAS/LAPACK), no MPC frameworks, no databases, and no web
frameworks are allowed anywhere in the real deliverable — every algorithm is
hand-written. The prototype inherits this same constraint, since its whole point is to
prove the *real* design works, not to fake it with a library.

---

## 3. Goal of the Prototype

Build a small, runnable Python program that **demonstrates the entire pipeline working
together on toy-sized inputs**, so the team can:

- Confirm the Field → Vector → Matrix → Algorithm → Secret-Share → Secure-Op layering
  actually composes the way the design assumes it will.
- Catch interface mismatches between what will become Worklet 1, 2, and 3 before the
  real worklets are built in parallel by different sub-teams.
- Have a runnable script the whole group can point to during the week-3 design review
  to explain the plan.

This is explicitly a **proof-of-concept**, not production code, not the final
submission, and not optimized.

---

## 4. Non-Goals

- This is **not** a performance-tuned or production-hardened library.
- This is **not** a real, network-based, multi-party MPC system.
- This is **not** the final three-worklet deliverable — it is a throwaway or
  lightly-reusable scaffold that the real worklets may partially borrow code from.
- This does **not** need to handle every edge case, malicious input, or adversarial
  actor — see Section 9.

---

## 5. Target User of the Prototype

The four members of Group UGPCSE : 25 (and their reviewer), running the prototype
locally from the command line to see a worked example end-to-end. No external users,
no deployment, no UI beyond a CLI/script output.

---

## 6. Functional Requirements

### 6.1 Layer 1 — Field Arithmetic (`FieldElement`)

| ID | Requirement |
|---|---|
| F-1 | A `FieldElement` type wrapping an integer value and a shared prime modulus `p`. |
| F-2 | Support `add`, `sub`, `mul`, and modular `inverse` (extended Euclidean algorithm). |
| F-3 | Raise a clear, typed error when inverting `0` (no inverse exists). |
| F-4 | Support equality comparison between two `FieldElement`s. |
| F-5 | `p` is fixed at program start for a given run (a small prime, e.g. in the 10–10,000 range, is sufficient for the prototype). |

### 6.2 Layer 2 — Vector and Matrix

| ID | Requirement |
|---|---|
| V-1 | `Vector`: ordered list of `FieldElement`s; supports construction from a plain list of ints, indexing, length, addition, scalar multiplication, dot product, equality. |
| V-2 | `Matrix`: 2-D array of `FieldElement`s (rows of `Vector`); supports construction from a nested list of ints, indexing by `(row, col)`, dimensions, addition, scalar multiplication, transpose, equality. |
| V-3 | `Matrix` multiplication (standard `O(n³)`), raising a clear error on dimension mismatch. |
| V-4 | A short, printed complexity note (in code comments or a `--explain` flag) for each operation — this is a design-understanding aid, not a benchmarking suite. |

### 6.3 Layer 3 — Linear-Algebra Algorithms

| ID | Requirement |
|---|---|
| L-1 | Gaussian elimination over the field (row reduction using field arithmetic, not floats). |
| L-2 | Rank of a matrix, derived from the row-reduced form. |
| L-3 | Determinant, for square matrices, via elimination. |
| L-4 | Solve `Ax = b` for a square, non-singular `A`; detect and clearly report the singular case rather than crashing. |
| L-5 | (Prototype-only, optional) Matrix inverse via Gauss-Jordan, only if time allows — not required for the demo to succeed. |

### 6.4 Layer 4 — Secret Sharing

| ID | Requirement |
|---|---|
| S-1 | Split a `FieldElement` (or a `Vector`/`Matrix` of them) into `n` additive shares such that summing all shares mod `p` reconstructs the original value. |
| S-2 | Reconstruct the original value from the full set of shares. |
| S-3 | Demonstrate that a single share reveals nothing (e.g. print that a lone share is uniformly distributed / could correspond to any original value) — a comment/explanation is sufficient for the prototype; no formal proof needed. |
| S-4 | The prototype simulates all parties **in a single process** (e.g. as Python lists/objects held together) — no real network communication is required. |

### 6.5 Layer 5 — Secure Computation Primitives

| ID | Requirement |
|---|---|
| M-1 | Secure addition: add two secret-shared values by adding shares locally, with no communication between "parties" — the prototype should make this "no communication" property visible (e.g. a log line showing each party only touches its own share). |
| M-2 | A private inner product / matrix product protocol built using shares of two vectors/matrices — the prototype may use a simplified protocol (e.g. Beaver-triple-free, direct multiply-and-reveal-partial-sums) as long as it is clearly labeled as a simplification (see Section 9). |
| M-3 | Verification step: compute the same inner/matrix product in plaintext and assert it equals the result recovered from the secure computation, printing a pass/fail. |

### 6.6 Demo / Orchestration

| ID | Requirement |
|---|---|
| D-1 | A single entry-point script (e.g. `demo.py`) that runs a scripted end-to-end walkthrough: create a field → build vectors/matrices → run one linear-algebra example (solve `Ax = b`) → secret-share a vector → run secure addition → run a private inner product → verify against plaintext → print a summary. |
| D-2 | All output should be printed in a readable, narrated way (short labeled print statements), since the point of the prototype is to *show* the pipeline working, not just return exit code 0. |
| D-3 | The demo should run with no arguments needed (sane defaults for `p` and example vectors/matrices baked in), plus optional flags to vary the prime or input size if easy to add. |

---

## 7. Non-Functional Requirements

- **Language:** Python 3 (standard library only — no NumPy, no third-party MPC or
  crypto libraries).
- **No external numeric/algebra libraries** — this is a hard constraint carried over
  from the real project, since the whole point is to prove the team's own algorithms
  work.
- **Readability over performance:** the prototype should favor clear, well-commented
  code over speed. Small inputs (vectors/matrices up to roughly 5×5, primes up to a
  few thousand) are all that's needed.
- **Testable:** each layer should have a handful of `unittest` (or `pytest`) tests
  proving basic correctness (see Section 10) — not exhaustive coverage, just enough to
  trust the demo's output.
- **Single machine, single process:** no deployment, no persistence, no concurrency
  requirements.

---

## 8. Suggested Architecture

```
prototype/
├── field.py            # FieldElement
├── vector.py           # Vector
├── matrix.py           # Matrix
├── linalg.py           # Gaussian elimination, rank, determinant, solve
├── secret_sharing.py   # split / reconstruct
├── secure_ops.py       # secure add, secure inner/matrix product, verification
├── demo.py             # single entry point, runs the full walkthrough
└── tests/
    ├── test_field.py
    ├── test_vector_matrix.py
    ├── test_linalg.py
    └── test_secure_ops.py
```

Each module should only depend on the ones above it in this list (`field.py` has no
dependencies; `demo.py` may import everything). This mirrors — and is meant to
pressure-test — the real Worklet 1 → 2 → 3 layering.

---

## 9. Prototype Limitations (must be respected)

This section exists to stop the prototype from quietly turning into a second, competing
"real" implementation. The agent building this should treat every item below as an
explicit boundary, not an oversight to fix:

1. **Not a real MPC protocol.** All "parties" run in the same Python process and share
   memory. There is no network layer, no message passing, and no protection against a
   party peeking at another party's in-memory share. This is fine for demonstrating the
   *math*, but it is not a security guarantee of any kind.
2. **Semi-honest only, and only conceptually.** The secure computation primitives assume
   all parties follow the protocol correctly. There is no defense against a malicious or
   cheating party, and the prototype does not need to detect or resist one.
3. **Small scale only.** Primes and matrix/vector sizes are toy-sized, chosen for
   clarity, not for the security margins a real deployment would need. Do not attempt to
   benchmark this at production scale.
4. **Simplified secure multiplication protocol.** A textbook private inner/matrix product
   typically needs correlated randomness (e.g. Beaver triples) to stay secure across
   more than one round. The prototype may use a simplified, clearly-labeled version that
   demonstrates the *idea* (local computation on shares + a minimal reveal step) without
   implementing the full cryptographic protocol. This must be called out in code comments
   and in the demo's printed output, not silently glossed over.
5. **No input validation hardening.** Basic errors (dimension mismatch, inverting 0,
   singular systems) should be handled cleanly, but the prototype does not need to guard
   against adversarial or malformed input beyond what's needed for the demo to run
   reliably.
6. **No persistence, no UI, no config system.** A single script with sane hardcoded
   defaults is sufficient; do not build a CLI framework, config files, or a web/GUI
   front end.
7. **Not a drop-in replacement for the real worklets.** Code here may be reused as a
   starting point once the real Worklet 1/2/3 teams begin, but the prototype's job ends
   once it has proven the design — it is not expected to survive unchanged into the
   final submission.

If the agent building this finds itself adding retry logic, concurrency, network
sockets, cryptographic randomness sourcing, or performance optimization, that is a
signal it has drifted outside the prototype's scope — it should stop and flag this
rather than continue.

---

## 10. Testing Requirements (lightweight)

- **Field:** associativity/commutativity of `add`/`mul` for a few sample values;
  `a * inverse(a) == 1` for all non-zero `a` in a small field; inverting `0` raises an
  error.
- **Vector/Matrix:** a couple of hand-computed addition/multiplication examples;
  transpose-of-transpose returns the original; dimension-mismatch raises an error.
- **Linalg:** solve a small, known `Ax = b` system and check the returned `x` by
  substituting back in; a deliberately singular system is detected and reported, not
  silently miscomputed.
- **Secure ops:** shares reconstruct to the original value; a secure inner product on
  shares matches the plaintext inner product for at least two example vectors.

Tests should run with a single command (e.g. `python -m unittest discover tests`).

---

## 11. Acceptance Criteria for the Prototype

The prototype is "done" when:

- [ ] `python demo.py` runs with no errors and no external dependencies beyond the
      Python standard library.
- [ ] The demo's printed output narrates each stage: field setup → vector/matrix ops →
      solving a linear system → secret sharing → secure addition → secure inner
      product → plaintext-vs-secure verification (pass/fail clearly shown).
- [ ] All items in Section 10 pass.
- [ ] Every simplification made relative to a "real" implementation is called out
      either in a code comment or in the demo's printed output (see Section 9, item 4
      in particular).
- [ ] The module boundaries in Section 8 are respected, so the prototype visibly
      mirrors the intended Worklet 1 → 2 → 3 layering.

---

## 12. Suggested Build Order (for the agent)

1. `field.py` + its tests.
2. `vector.py`, `matrix.py` + their tests (depends on `field.py`).
3. `linalg.py` + its tests (depends on `matrix.py`).
4. `secret_sharing.py` + its tests (depends on `field.py`, and `vector.py`/`matrix.py`
   for sharing whole vectors/matrices).
5. `secure_ops.py` + its tests (depends on `secret_sharing.py`).
6. `demo.py`, wiring all of the above into one narrated end-to-end run.

Each step should be independently runnable and tested before moving to the next, so
that a broken later layer never masks a bug in an earlier one.

---

## 13. Out of Scope / Future Work (post-prototype)

Once the prototype has validated the design, the *real* work — building out the full
Worklet 1, 2, and 3 deliverables with proper interface contracts, complexity
documentation, complete test suites, and (for Worklet 3) an honest treatment of the
security assumptions — proceeds separately per the project's own execution plan
(joint design weeks, biweekly worklet reviews, and final integration). This prototype
is an input to that process, not a substitute for it.