# CSIDH-512 class-group order N and factorization — independently obtained and cross-verified

Required artifact per specification.yaml required_artifacts[1]: "The independently
obtained CSIDH-512 class-group order N and its full prime factorization, with
the primality-check method and result for each factor, and citations to both
independent sources."

## Primary citation (inputs.class_group_order_source)

Beullens, Kleinjung, Vercauteren, "CSI-FiSh: Efficient Isogeny based Signatures
through Class Group Computations", IACR ePrint 2019/498. Retrieved live via
`curl` (HTTP 200) from `https://eprint.iacr.org/2019/498.pdf` this run (see
`command.txt`; local copy not committed — retrieval is reproducible from the
cited URL and this exact command).

**Section 3 ("Class group computation"), page 8**, displayed equation:

> #Cl(O_{Q(sqrt(-p))}) = 37 × 1407181 × 51593604295295867744293584889
>                          × 31599414504681995853008278745587832204909

immediately followed by (same page):

> "The class group of the order O therefore has cardinality
> 3 · #Cl(O_{Q(sqrt(-p))}) which is approximately equal to 2^257.136."

So the CSIDH-512 class-group order (of the *order* O, i.e. Cl(O), which is
what CSIDH itself acts by — see Section 2.1 of the same paper, p.4: "we get
#Cl(O) = 3#Cl(O_{Q(sqrt(-p))})") is:

```
N = 3 x 37 x 1407181 x 51593604295295867744293584889
      x 31599414504681995853008278745587832204909
  = 254652442229484275177030186010639202161620514305486423592570860975597611726191
```

Bit length: 258. log2(N) = 257.1369928597118, matching the paper's own stated
"approximately equal to 2^257.136" (Section 3, p.8) to the precision the paper
itself gives.

Also stated by the same paper, **Section 3, p.8** ("Final computations"):
"This class group turns out to be cyclic and the class number is not
divisible by 3." — wait, this sentence appears in the paragraph *preceding*
the factorization display and refers to the *maximal-order* class group
Cl(O_{Q(sqrt(-p))}) (the one NOT divisible by 3); the suborder class group
Cl(O) is exactly 3x that one, per the immediately following sentence quoted
above. Both class groups are stated cyclic. This full context is preserved
here to avoid a misleading partial quotation.

## Second, independently obtained citation (inputs.second_independent_citation)

The CSI-FiSh reference implementation's own parameter file:
`https://github.com/KULeuven-COSIC/CSI-FiSh`, file
`classgroup_data/class number`. Retrieved this run via `git clone` (see
`command.txt`); the repository's own `README.md` states: "This folder
contains the class number, discrete logarithms and a HKZ reduced basis of
the relation lattice" — the repository is referenced by the CSI-FiSh paper's
own reference [2] ("Ward Beullens. CSI-FiSh: github repository available at
https://github.com/KULeuven-COSIC/CSI-FiSh, 2019").

Content of `classgroup_data/class number`:

```
254652442229484275177030186010639202161620514305486423592570860975597611726191
```

## Cross-citation consistency control (per amendments/v1.yaml, renamed from
"Cross-source agreement control")

Per the amendment's scope disclosure: this control checks that the same
number was transcribed identically across two of the same authors' own
publications describing the same underlying computation, **not** an
independent mathematical re-derivation of N by a second, differently-computed
source. Both sources here (the CSI-FiSh paper itself and its own reference
implementation's parameter file) originate from the same 2019 record
computation by the same three authors — this is the example source the
specification's own `inputs.second_independent_citation` field names, and no
stronger, genuinely-differently-computed second source was located within
budget.

Result: **EXACT AGREEMENT** between the two citations. See
`verify_class_group_order.py` / `stdout.log` for the executed check.

## Factorization-integrity control

Every prime factor was independently primality-checked (Miller-Rabin via
`sympy.isprime`, a deterministic strong probable-prime test at these sizes),
and the product of the five stated factors was verified to equal the stated
N exactly:

| factor | prime? |
|---|---|
| 3 | True |
| 37 | True |
| 1407181 | True |
| 51593604295295867744293584889 | True |
| 31599414504681995853008278745587832204909 | True |

Product of all five factors = N (exact match to both citations above).

## Known-answer control (harness sanity check)

Before touching the CSIDH-512-scale value, the same primality-check-and-
product-reconciliation procedure was run on a small imaginary-quadratic
discriminant with a textbook-known class number: Q(sqrt(-23)) has class
number h(-23) = 3 (a standard tabulated fact for a small imaginary quadratic
discriminant; class number tables for |discriminant| < 100 are found in any
standard computational number theory reference, e.g. Cohen's "A Course in
Computational Algebraic Number Theory"). Verified: 3 is prime, product of
factors [3] = 3, matches the tabulated class number exactly. See
`stdout.log` for the executed check. PASSED before the CSIDH-512-scale check
was trusted.

## class_group_order_match (primary metric)

**TRUE.** Both citations agree exactly on N; every stated factor is prime;
the product of the stated factors equals N; the known-answer control on the
verification method itself passed first.
