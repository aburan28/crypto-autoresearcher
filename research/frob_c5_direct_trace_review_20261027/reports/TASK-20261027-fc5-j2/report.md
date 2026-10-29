# Independent blind J2 exact trace review

Task: `TASK-20261027-fc5-j2`; Conductor claim: `T-629`.

**Verdict: holds for the isolated five-term arithmetic claim in all three cells.** The deliberately incorrect four-term claim at q = 13 is rejected. This verdict concerns the mathematical input below and this reviewer's implementation. It does not judge producer fidelity, Lean compilation, archived Sage executable custody, performance, or official scientific status.

## Isolation and exact method

The first filesystem source read was exclusively `/var/tmp/frob-c5-blind-20261027/statement.json`. Its SHA-256 was checked before any arithmetic:

```text
17ba164feb8a59ba91346448befaf8ca56e8318de2cc53d6f950a377cbff45e2
```

No repository input, plan, producer code, producer report, producer replay, producer native output, Git history, PR, memory, search result, or sibling review was inspected. The reviewer wrote only into this review directory. Conductor help and the assigned task claim output were consulted for the explicitly requested coordination operation. The parent supplied only attestation field names, types, and the designated joint name after the first read; no producer mathematical output was supplied.

`exact_trace.py` uses Python integers, polynomial multiplication and reduction modulo the displayed monic polynomial and prime q, and Gaussian elimination over the prime field. It imports only standard-library modules, with no repository or third-party imports. This is a deterministic exact calculation over the three specified finite objects, not a scientific trial, benchmark, random sweep, Sage run, or Lean build.

For the five-term matrix, each basis vector e_j is independently raised to exponents 1, q, q², q³, q⁴ and summed in the quotient. For the Frobenius matrix, x^q is computed and the columns are built as 1, x^q, (x^q)², (x^q)³, (x^q)⁴. A separate matrix multiplication path produces I + F + F² + F³ + F⁴; all 25 entries agree with direct quotient exponentiation in every cell. The two assembly paths share this reviewer's polynomial arithmetic primitives. An additional symbolic check of the trace row uses Newton identities below.

All matrices below are printed as rows. Input and output coefficient vectors are columns in the ordered basis (1, x, x², x³, x⁴), and entries are least nonnegative residues modulo the relevant q. Full intermediate matrix powers and row reductions are preserved in `results.json` and `raw_output.json`.

## Complete exact matrices

### q = 11, g = x⁵ + 2x⁴ + 1

```text
F =
[1, 9, 10,  5,  1]
[0, 0,  4, 10, 10]
[0, 6,  1, 10,  3]
[0, 8,  3,  1,  4]
[0, 3,  3,  2,  8]

T = I + F + F² + F³ + F⁴ =
[5, 9, 4, 3, 5]
[0, 0, 0, 0, 0]
[0, 0, 0, 0, 0]
[0, 0, 0, 0, 0]
[0, 0, 0, 0, 0]
```

F has rank 5 and nullity 0. T has rank 1 and nullity 4, with image exactly F₁₁·1. Equivalently, its kernel is the four-dimensional set of coefficient vectors satisfying 5a₀ + 9a₁ + 4a₂ + 3a₃ + 5a₄ = 0 modulo 11.

### q = 13, g = x⁵ + 8x⁴ + 1

```text
F =
[1,  5,  7,  7, 6]
[0,  2,  4, 11, 1]
[0, 11, 10,  5, 0]
[0,  9,  4,  4, 6]
[0,  0,  0,  8, 9]

T = I + F + F² + F³ + F⁴ =
[5, 5, 12, 8, 1]
[0, 0,  0, 0, 0]
[0, 0,  0, 0, 0]
[0, 0,  0, 0, 0]
[0, 0,  0, 0, 0]
```

F has rank 5 and nullity 0. T has rank 1 and nullity 4, with image exactly F₁₃·1. Its kernel is given by 5a₀ + 5a₁ + 12a₂ + 8a₃ + a₄ = 0 modulo 13.

### q = 19, g = x⁵ + 3x⁴ + 1

```text
F =
[1,  7,  7,  8,  2]
[0, 15,  6, 14, 10]
[0, 14, 10,  0,  6]
[0, 11, 18, 16, 13]
[0,  9, 13, 13, 15]

T = I + F + F² + F³ + F⁴ =
[5, 16, 9, 11, 5]
[0,  0, 0,  0, 0]
[0,  0, 0,  0, 0]
[0,  0, 0,  0, 0]
[0,  0, 0,  0, 0]
```

F has rank 5 and nullity 0. T has rank 1 and nullity 4, with image exactly F₁₉·1. Its kernel is given by 5a₀ + 16a₁ + 9a₂ + 11a₃ + 5a₄ = 0 modulo 19.

In all three cases the lower four rows of T are zero, so the image is contained in the constant line. Its (0,0) entry is 5, which is nonzero for each prime here, so the image equals that line. The exact matrix calculations also give F⁵ = I in all three cases.

For g = x⁵ + cx⁴ + 1, Newton identities give the first four power sums of its roots as −c, c², −c³, c⁴. After identifying the irreducible quotient with its field extension, the five-term trace row therefore equals (5, −c, c², −c³, c⁴). These three substitutions reproduce the rows (5,9,4,3,5), (5,5,12,8,1), and (5,16,9,11,5) above.

## Wrong-length control at q = 13

Replacing five terms by four gives the following direct matrix, which also agrees with the independently assembled four-term matrix sum:

```text
T₄ = I + F + F² + F³ =
[4,  1, 10,  9, 0]
[0,  1,  4,  2, 0]
[0,  9, 11, 12, 4]
[0, 11,  8,  8, 5]
[0,  9,  3,  3, 7]
```

T₄ has rank 5 and nullity 0. Its image is the whole five-dimensional quotient, so it is not contained in the base-field line. A concrete witness is

```text
T₄(x) = 1 + x + 9x² + 11x³ + 9x⁴  (mod 13, g).
```

This control fails the rank-1, nullity-4, and base-field-image claims. Merely checking agreement between direct summation and a matrix polynomial would not reject it: the correct four-term direct and matrix constructions agree, while their rank and image differ from the asserted five-term properties.

The full rank also follows from the checked five-term relations. Since 5 is invertible modulo 13, the space decomposes as the constant line plus ker(T). On the constant line, T₄ = T − F⁴ acts by 4. On ker(T), it acts by −F⁴, which is invertible because F⁵ = I. Both restrictions are invertible.

## Exactly where irreducibility is used

No irreducibility assumption is needed to define the quotient, its displayed basis, multiplication, q-power map, direct sum, or matrix polynomial. The quotient by any monic degree-five polynomial has this five-dimensional vector-space basis. For prime q, the q-power map is linear over F_q on any commutative F_q algebra. Thus direct summation and I + F + F² + F³ + F⁴ describe the same operator without assuming g irreducible.

The ranks, nullities, image statements, F⁵ = I, and wrong-length failure reported here follow from exact matrix computations and also do not require assuming irreducibility. A general monic degree-five quotient need not have these same rank, image, or period properties.

Irreducibility is needed to identify this quotient as the degree-five field extension F_(q⁵) and to invoke its standard field-trace and Frobenius fixed-field theorems directly. In that field, Frobenius has order five, its fixed field is F_q, and the five-term sum is the field trace. This establishes the familiar abstract explanation for the constant image; 5 ≠ 0 then proves surjectivity onto that line. The identification with field trace in the Newton-identity check above uses this field interpretation.

Irreducibility was checked independently, rather than assumed. For degree five (a prime), the exact finite-field criterion is

```text
x^(q^5) − x = 0 modulo g,
gcd(g, x^q − x) = 1.
```

For each of the three inputs, the first remainder is [0,0,0,0,0] and the monic gcd is [1]. These conditions imply irreducibility because x^(q⁵)−x is squarefree and its irreducible factors have degrees dividing five; the gcd condition excludes degree-one factors. Degree five then forces a single irreducible factor of degree five.

## Reproduction, artifacts, and boundaries

`commands.md` records the source reads, coordination calls, calculation command, output inspection, and seal procedure. `runtime.json` records Python 3.9.25 and the local execution environment. The exact arithmetic run completed in approximately 0.027 seconds; this is provenance for one local invocation and supports no performance comparison. `raw_output.json` preserves complete stdout, and `results.json` contains the structured mathematical result. `review_attestation.yaml` records the joint verdict and source isolation. `SHA256SUMS` seals every review artifact other than the manifest itself, plus the isolated input. The manifest is verified after creation, and its own hash is delivered separately.

The assignment cited frozen plan commit `dd4afa8950`; the reviewer did not inspect or verify that commit. No scientific status was changed. No Sage, Lean, EKS, PR operation, Git operation, or commit was performed. The parent may assess fidelity to any producer artifact only after this sealed blind review is delivered; this review supplies no such assessment.
