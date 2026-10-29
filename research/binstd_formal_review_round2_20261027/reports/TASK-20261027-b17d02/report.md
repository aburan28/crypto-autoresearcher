# Blind exact factor and Frobenius review

Task: `TASK-20261027-b17d02`. Conductor card: `T-617`.
Owned joint: `J2-blind-factor-and-frobenius`.
Verdict: **holds**, for the mathematical claims stated below.

The first intentional filesystem source read was exactly
`/var/tmp/binstd-round2-blind-20261027/statement.json`. Its SHA-256 was verified as
`2bbf336b088ff099546bcc3b5f3612f439ba2b7aa69a5007c6d02fcdb590f664` before any other
source access. No producer file, prior review, sibling report, Git history, PR,
repository instruction file, skill file, memory file, or search result was read.
The assigned mathematical instructions supplied in the parent message were used
without opening their named skill reference. The reviewer remains blind through
final delivery; there is no planned post-seal producer read.

## 1. Definitions and exact factor calculation

All coefficients are in F2. Let

```
f1 = X + 1
f8a = X^8 + X^5 + X^4 + X^3 + 1
f8b = X^8 + X^7 + X^6 + X^4 + X^2 + X + 1.
```

Polynomial coefficients were encoded as bits: bit i is the coefficient of X^i.
The respective masks are `0x3`, `0x139`, and `0x1d7`. Carryless multiplication
(XOR of shifts) gives

```
f8a * f8b = 1 + X + X^2 + ... + X^16 = 0x1ffff
f1 * f8a * f8b = X^17 + 1 = 0x20001.
```

The implementation then exhaustively divided each degree-eight polynomial by
every monic polynomial of degrees 1, 2, 3, and 4. There are
`2 + 4 + 8 + 16 = 30` such divisors per factor, including those with zero constant
coefficient. No candidate gave remainder zero for either factor. All 60 exact
remainder rows are in `raw_output.txt` and `results.json`.

This proves irreducibility: any nontrivial factorization of a degree-eight
polynomial has a positive-degree factor of degree at most four. Over F2 every
nonzero polynomial is monic, so the exhaustive list contains that factor. The
test does not presume a table of irreducibles or invoke a probabilistic test.

For completeness, f1 has degree one and is irreducible. These three factors are
distinct, so this is the complete irreducible factorization of X^17+1 over F2.
The derivative of X^17+1 is X^16, coprime to X^17+1, which also establishes that
the factorization is squarefree.

## 2. Canonical GF(2^17): abstract proof independent of any quotient

Let K be a field of characteristic two with exactly q = 2^17 = 131072 elements.
This is the property of canonical GF(2^17) used here. It contains the prime
subfield F2 and is a vector space of dimension 17 over F2: a finite vector
space of dimension d over F2 has 2^d elements.

Define F: K -> K by F(x) = x^2. Characteristic two gives
F(x+y) = x^2+y^2 and F(a*x) = a*F(x) for a in F2, so F is F2-linear.
Induction gives F^r(x) = x^(2^r), including F^0(x)=x.

Every nonzero x is in the multiplicative group K*, which has q-1 elements.
Lagrange's theorem therefore gives x^(q-1)=1. The equation x^q=x holds for
nonzero x and also for zero. Thus F^17 is the identity, and in particular F is
invertible with inverse F^16.

For any integer r with 1 <= r < 17, the nonzero polynomial
Y^(2^r)-Y has degree 2^r < q. A nonzero polynomial over a field has at most its
degree many distinct roots. It cannot vanish at all q elements of K.
Consequently F^r is not the identity. **The exact order of F is 17.** This
argument does not infer minimal polynomial from order.

Let p(T) = sum(i=0..r) a_i*T^i be a nonzero polynomial in F2[T], with a_r=1.
If r < 17, evaluation on F gives

```
p(F)(x) = sum(i=0..r) a_i * x^(2^i).
```

The right side is a nonzero ordinary polynomial in x: its exponents 2^i are
distinct, and its highest coefficient is one. Its degree is 2^r, strictly less
than q. The root bound again shows that it cannot vanish on all K. Hence no
nonzero polynomial of degree below 17 annihilates F.

The monic polynomial T^17+1 does annihilate F, since F^17 is the identity and
the characteristic is two. Therefore **the minimal polynomial of F over F2 is
exactly T^17+1**. One can use the definition as the monic annihilator of least
degree; uniqueness follows because subtracting two monic least-degree
annihilators would produce a smaller-degree annihilator. No normal basis
theorem, characteristic-polynomial assumption, or archived runner is needed.

The factorization proved in Section 1 consequently factors this canonical
minimal polynomial into degrees 1, 8, and 8.

## 3. Optional archived quotient: independent calculation and required bridge

The only archived datum provided was the modulus mask 131081 = `0x20009`, namely
g(X) = X^17+X^3+1. Exhaustive polynomial division tested every monic polynomial
of degrees 1 through 8, a total of 510 candidates, with no zero remainder.
Every reducible degree-17 polynomial would have a factor of degree at most
eight, so g is irreducible. The quotient A = F2[X]/(g) is therefore a field,
with 2^17 residue classes represented uniquely by polynomials of degree < 17.

Writing alpha for the residue class of X, the coordinate basis is
(1, alpha, ..., alpha^16). The independently calculated squaring matrix has
the following columns, encoded as 17-bit integers in that basis:

```
[1, 4, 16, 64, 256, 1024, 4096, 16384, 65536,
 18, 72, 288, 1152, 4608, 18432, 73728, 32786]
```

Each column is the exact remainder of X^(2j) modulo g for j=0,...,16.
Successive exact matrix multiplication finds the first positive identity power
at exponent 17. Independently, Gaussian elimination on flattened matrices
I,F,F^2,... finds ranks 1,2,...,17 through exponent 16. The first dependence,
at exponent 17, is exactly I+F^17=0. Thus this concrete quotient map also has
order 17 and minimal polynomial T^17+1.

An additional explicit basis certificate is the Frobenius orbit of alpha+1,
whose coordinate mask is 3:

```
[3, 5, 17, 257, 65537, 32787, 73989, 102915,
 107653, 127563, 126661, 109433, 42593, 75355,
 33549, 8259, 517]
```

Its 17 vectors have rank 17 by exact F2 elimination and the next iterate is 3.
This is a concrete normal basis certificate; no normal basis existence theorem
was assumed to find it.

**Required bridge to an archived runner:** establish that its represented
states and operations implement A with this modulus and coordinate convention,
and that its claimed Frobenius operation is squaring in A. In particular, give
a bijective F2-linear representation map rho from A to the runner state space
and verify `runner_F(rho(a)) = rho(a^2)` for every a (or prove sufficient
linearity and verify all basis vectors). Any different bit or basis ordering
must be accounted for in rho.

To transport the canonical theorem literally, take an F2-field isomorphism
iota: K -> A. The uniqueness theorem for finite fields of a given cardinality
supplies such an abstract isomorphism; it fixes F2 and obeys
iota(x^2)=iota(x)^2. Then `rho ∘ iota` conjugates canonical Frobenius to the
runner map. Conjugacy preserves the exact order and every annihilating
polynomial, hence the minimal polynomial. Alternatively, a verified concrete
matrix equality with the matrix above suffices for the runner's linear-map
claims, without selecting a canonical-field isomorphism.

The supplied modulus and this calculation do not prove that actual runner code
uses those operations. No runner code was read. The representation bridge and
any executable or formal implementation claim remain unverified in this joint.

## 4. Required false controls

The same exhaustive divisor checker rejects irreducibility of X^8+1. Its
divisors among degrees 1 through 4 have masks `[3, 5, 15, 17]`, corresponding to
X+1, X^2+1, X^3+X^2+X+1, and X^4+1. Carryless multiplication independently
confirms `(X+1)^8 = X^8+1`. The deliberately false irreducibility assertion was
caught and recorded as an expected assertion failure.

For GF(2), squaring is the identity, with the 1x1 matrix `[1]`. The same matrix
routines return exact order 1 and minimal polynomial T+1. Deliberately false
assertions of order 17 and minimal polynomial T^17+1 both fail as expected.
Nevertheless T^17+1 annihilates this identity map. Thus a check of that one
annihilator, or of F^17=I alone, would accept the wrong-degree control and cannot
establish the requested exact order or minimal polynomial.

No required false control escaped rejection, and there was no unexpected
arithmetic failure. The initial bare conductor invocation failed because the
executable was absent from the non-login shell PATH; the coordinator supplied
its absolute path and the claim then succeeded.

## 5. Theorems, assumptions, trust, and scope

The mathematical derivations rely on the following explicit facts:

1. F2 is a field; polynomial degree is additive under nonzero products; the
   polynomial division algorithm over a field gives unique remainders.
2. A nontrivial product of total degree n has a factor of degree at most
   floor(n/2). Exhausting all monic possibilities therefore certifies the
   irreducibility checks in this report.
3. A quotient of F2[X] by an irreducible polynomial is a field; unique reduced
   representatives give cardinality 2^n for a degree-n modulus.
4. A finite field K of characteristic two and cardinality 2^17 is the subject of
   the canonical claim. Standard finite-field existence provides such K;
   Section 3 also gives an explicit construction independently. No particular
   source-level definition of a canonical field was inspected.
5. The characteristic-two binomial identity, basic exponent rules, and
   Lagrange's theorem for the multiplicative group yield F^17=I.
6. The field polynomial root bound establishes exact order and rules out every
   smaller-degree annihilator. This applies to all coefficients in F2, not just
   a selected list of candidate polynomials.
7. A finite vector space over F2 of dimension d has 2^d elements. Elementary
   Gaussian elimination over F2 computes rank and exact linear dependence.
8. The minimal polynomial is the unique monic annihilator of least degree.
   Matrix flattening is injective and F2-linear, so its power dependence test
   computes that polynomial for the concrete matrix. Cayley-Hamilton would
   guarantee a dependence by the matrix dimension, but the observed dependence
   here is explicit and the canonical proof does not require that theorem.
9. For the proposed canonical-to-runner bridge only: finite fields of the same
   cardinality are isomorphic, field homomorphisms commute with squaring, and
   linear conjugacy preserves polynomial identities and map order. The actual
   runner representation still needs its own proof.

Executable evidence trusts Python integer operations, this independent script,
and the local execution environment. The program uses only Python's standard
library, exact integers, exhaustive finite loops, and deterministic Gaussian
elimination. It does not use floats, randomness, network data, producer code,
Lean output, symbolic algebra packages, or precomputed irreducibility tables.
The Python code is not a formal proof artifact. Its exhaustive division rows
and matrix certificates permit independent reimplementation and review.

This review establishes the supplied mathematical statements and the
independently constructed quotient calculation. It makes no assertion about
producer theorem fidelity, Lean compilation, repository integration, performance,
security strength, a production runner, or official scientific status.

## 6. Artifacts and source boundary

- `check_exact.py`: independent, deterministic checker.
- `raw_output.txt`: complete stdout of the final successful invocation, including
  every divisor/remainder row and all expected false-control assertion failures.
- `results.json`: exact structured results, including divisor rows and certificates.
- `commands.md`: actual verification commands and relevant control-plane outputs.
- `runtime.json`: interpreter and platform details.
- `review_attestation.yaml`: joint verdict, input hash, boundary declarations,
  source list, and artifact hashes.
- `seal.sha256`: final hashes of the report, attestation, and supporting artifacts.

The sole external mathematical source was the isolated statement. The complete
intentional read set also includes this reviewer's own script and artifacts,
enumerated in the attestation. Task instructions, coordinator messages supplying
the conductor executable path and lease reminder, and direct conductor/clock
tool output were operational context. They supplied no producer proof or result.
The reviewer performed no PR, commit, experiment launch, heavy Lean build, or
scientific status change. The conductor claim is released after sealing.
