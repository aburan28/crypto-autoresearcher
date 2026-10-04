# Independent blind derivation for TASK-20260907-b27e3e

This note treats only the quantity statement supplied in
`coordination/experiment-reserve/BATCH-635652/blind-input.yaml`. It does not
compare the result with any producer amendment, design, implementation,
readiness note, archive narrative, or sibling review. Its owned-joint verdict
is **PASS**: the supplied quantities have canonical, implementable definitions
under the assumptions below. Whether a producer formula agrees with them is
**UNCHECKABLE** within this blind task and is left to the Coordinator.

## Assumptions and conventions

Let `p >= 5` be prime and let `s` be 2 or 3. Let `C` be the unique least
nonnegative representative of its class modulo `p^s`, so

\[
0 \le C < p^s.
\]

Every base-`p` digit is represented by the integer in `{0,...,p-1}`. For the
Teichmüller lift, `x` is likewise the canonical integer representative of a
residue in `F_p`. All lift congruences are taken in `Z/(p^s)`.

The primality assumption is not needed for ordinary positional digits; an
integer base at least two is enough there. Primality is needed for the stated
Teichmüller construction and uniqueness argument.

## Canonical base-p digits

There are unique digits `c_0,...,c_{s-1}` in `{0,...,p-1}` such that

\[
C=\sum_{k=0}^{s-1}c_kp^k.
\]

The direct formula is

\[
c_j=\left\lfloor\frac{C}{p^j}\right\rfloor\bmod p,
\qquad 0\le j<s,
\]

where `mod p` means the least nonnegative remainder. Equivalently, define

\[
q_0=C,\qquad c_j=q_j\bmod p,\qquad
q_{j+1}=\frac{q_j-c_j}{p}.
\]

Every quotient in this recursion is exact. Iterating gives

\[
q_j=\frac{C-\sum_{k<j}c_kp^k}{p^j},\qquad c_j=q_j\bmod p.
\]

Thus at precision three,

\[
c_0=C\bmod p,
\quad
c_1=\left(\frac{C-c_0}{p}\right)\bmod p,
\quad
c_2=\frac{C-c_0-pc_1}{p^2}.
\]

The final expression is already in `{0,...,p-1}` because `C<p^3`. The
subtraction of `p*c_1` is essential if `/p^2` denotes exact integer division.

Existence follows from repeated Euclidean division. For uniqueness, suppose
two allowed digit tuples reconstruct the same `C`. Reduction modulo `p` makes
their zeroth digits equal. Subtract that common digit and divide by `p`; the
same argument identifies the next digit, and induction identifies every digit.

### Known-false digit control

Take `p=5`, `s=3`, and `C=32`. Then

\[
32=2+1\cdot5+1\cdot25,
\]

so `(c_0,c_1,c_2)=(2,1,1)`. Removing only `c_0` before division by `p^2`
gives

\[
\frac{C-c_0}{p^2}=\frac{30}{25}=\frac65,
\]

which is not an integer. Consequently, a formula that uses this as an exact
integer quotient is false. This control does not refute
`floor((C-c_0)/p^2)`, which happens to equal `c_2` for nonnegative canonical
`C`; it refutes an unstated exact-divisibility claim. The unambiguous formulas
are `floor(C/p^2) mod p` and the recursive exact quotient above.

Canonical boundary checks are consistent:

- `C=0` has digits `(0,0,0)`.
- `C=p^3-1` has digits `(p-1,p-1,p-1)`.
- `C=p^2` at precision three has digits `(0,0,1)`.
- At precision two the canonical interval ends at `p^2-1`; `p^2` reduces to
  zero modulo `p^2`.

## Precision compatibility

If `C_3` is canonical modulo `p^3` and

\[
C_2=C_3\bmod p^2\in[0,p^2),
\]

then

\[
C_2=c_0+c_1p.
\]

Therefore the precision-two digits are exactly the first two
precision-three digits:

\[
c_0^{(2)}=c_0^{(3)},\qquad c_1^{(2)}=c_1^{(3)}.
\]

The digit `c_2` is discarded; there is no precision-two value to compare it
with. More generally, reduction modulo `p^t` preserves precisely the digits
with indices below `t`.

## Teichmüller representative

For canonical `x` in `{0,...,p-1}`, define

\[
T_s(x)=x^{p^{s-1}}\bmod p^s,
\]

taking the least nonnegative representative when a concrete integer is
needed. For `x=0`, this is zero. For `x` nonzero, Euler's theorem gives

\[
x^{p^{s-1}(p-1)}\equiv1\pmod{p^s}.
\]

Hence

\[
T_s(x)^{p-1}\equiv1\pmod{p^s}
\quad\text{and}\quad
T_s(x)^p\equiv T_s(x)\pmod{p^s}.
\]

Because `p^{s-1}` is congruent to 1 modulo `p-1`, Fermat's theorem also gives

\[
T_s(x)\equiv x\pmod p.
\]

These statements are immediate for `x=0` as well.

To see uniqueness, let `f(X)=X^p-X`. Its derivative is

\[
f'(X)=pX^{p-1}-1\equiv-1\pmod p,
\]

which is a unit at every residue. Each root `x` of `f` modulo `p` therefore
has one lift through every higher power of `p`. Equivalently, if two roots
lifting the same `x` agree modulo `p^k`, write their difference as `p^k u`;
the first-order difference of `f` modulo `p^{k+1}` is `-p^k u`, forcing
`u=0 mod p`. Induction proves uniqueness modulo `p^s`.

Uniqueness also proves precision compatibility:

\[
T_3(x)\bmod p^2=T_2(x),
\]

because the reduction of `T_3(x)` has residue `x` and still satisfies the
fixed-point identity modulo `p^2`.

### Digit-level lift identities through precision three

Write

\[
T_3(x)=x+pa+p^2b,
\qquad a,b\in\{0,\ldots,p-1\},
\]

and set

\[
q=\frac{x^p-x}{p}.
\]

Fermat's theorem makes `q` an integer. Expanding the fixed-point equation
modulo `p^2` gives

\[
a\equiv q\pmod p.
\]

Choose `a=q mod p` canonically and put `r=(q-a)/p`. For `p>=5`, expansion
modulo `p^3` gives

\[
(x+pa+p^2b)^p
\equiv x^p+p^2x^{p-1}a\pmod{p^3}.
\]

Thus

\[
b\equiv r+x^{p-1}a\pmod p.
\]

These identities give the base-`p` digits of the lift directly. The
precision-two lift is `T_2(x)=x+pa`; precision three retains the same `x,a`
and adds `b`, making digit compatibility explicit.

For the fixed case `p=5,x=2`, one has

\[
q=(2^5-2)/5=6,\quad a=1,\quad r=1,\quad
b=1+2^4\cdot1=17\equiv2\pmod5.
\]

Therefore

\[
T_2(2)=7\pmod{25},\qquad T_3(2)=57\pmod{125},
\]

and the lift digits are `(2,1)` and `(2,1,2)` respectively. Indeed,
`57^2=-1 mod 125`, so `57^5=57 mod 125`, and `57 mod 25=7`.

### Known-false insufficient-lift control

At precision three, use only the precision-two exponent and set

\[
E=2^5\bmod125=32.
\]

This is an intentionally inconvenient control: it reduces to `2 mod 5`, and
it even behaves correctly modulo 25 because `32 mod 25=7`. Nevertheless,

\[
E^5\bmod125=57\ne32=E.
\]

Thus residue reduction and a precision-two check do not certify a
precision-three Teichmüller representative. The fixed-point identity must be
checked at the requested modulus. The control shows that exponent `p` is
insufficient in general for `s=3`; it does not say every residue fails under
that exponent.

## Synthetic arithmetic checks

Exactly one Python process executed 15 fixed logical checks, with no rerun, no
parameter sweep, no curve generation, and no scientific run. It reported
`real 0.11`, `user 0.03`, and `sys 0.01` seconds. All checks passed. The exact
program passed to `/usr/bin/time -p python3 -c` was:

```python
from fractions import Fraction
count = 0

def check(label, condition, detail):
    global count
    count += 1
    if not condition:
        raise AssertionError(f"{label}: {detail}")
    print(f"PASS {count:02d} {label}: {detail}")

def digits(p, s, C):
    assert 0 <= C < p**s
    return tuple((C // (p**j)) % p for j in range(s))

def reconstruct(p, ds):
    return sum(d * p**j for j, d in enumerate(ds))

def teich(p, s, x):
    return pow(x, p**(s-1), p**s)

check("digits-p5-C32", digits(5,3,32) == (2,1,1) and reconstruct(5,digits(5,3,32)) == 32, str(digits(5,3,32)))
check("digits-zero-boundary", digits(5,3,0) == (0,0,0), str(digits(5,3,0)))
check("digits-upper-boundary", digits(5,3,124) == (4,4,4) and reconstruct(5,digits(5,3,124)) == 124, str(digits(5,3,124)))
check("digits-p2-boundary-in-p3", digits(5,3,25) == (0,0,1), str(digits(5,3,25)))
check("digits-upper-p2", digits(5,2,24) == (4,4), str(digits(5,2,24)))
check("precision-32", digits(5,2,32 % 25) == digits(5,3,32)[:2], f"{digits(5,2,32%25)}={digits(5,3,32)[:2]}")
check("precision-124", digits(5,2,124 % 25) == digits(5,3,124)[:2], f"{digits(5,2,124%25)}={digits(5,3,124)[:2]}")
check("known-false-digit-exact-division", (32-2) % 25 != 0 and Fraction(32-2,25) == Fraction(6,5), f"remainder={(32-2)%25}, quotient={Fraction(30,25)}")
T2 = teich(5,2,2)
T3 = teich(5,3,2)
check("teich-p2-x2", T2 == 7 and T2 % 5 == 2 and pow(T2,5,25) == T2, f"T2={T2}")
check("teich-p3-x2", T3 == 57 and T3 % 5 == 2 and pow(T3,5,125) == T3, f"T3={T3}")
check("teich-precision", T3 % 25 == T2, f"{T3%25}={T2}")
check("teich-digits-compatible", digits(5,3,T3) == (2,1,2) and digits(5,3,T3)[:2] == digits(5,2,T2), f"{digits(5,3,T3)} -> {digits(5,2,T2)}")
T0 = teich(5,3,0)
check("teich-zero", T0 == 0 and pow(T0,5,125) == T0, f"T0={T0}")
E = pow(2,5,125)
check("insufficient-lift-passes-p2", E == 32 and E % 5 == 2 and pow(E,5,25) == E % 25, f"E={E}, E^5 mod25={pow(E,5,25)}")
check("known-false-insufficient-p3", pow(E,5,125) == 57 and pow(E,5,125) != E, f"E={E}, E^5 mod125={pow(E,5,125)}")
print(f"SUMMARY fixed_checks={count} failures=0 processes=1")
```

The observed summary was:

```text
SUMMARY fixed_checks=15 failures=0 processes=1
```

These fixed arithmetic witnesses establish only that the displayed identities
and counterexamples evaluate as stated on the declared hand cases. They are not
scientific experiments, empirical panels, performance measurements, RUN
records, or evidence about any hypothesis.

## Blindness and handoff boundary

No path under the plan's `blind_from` list was read. No sibling report was
read. No producer artifact, status record, queue, experiment, ledger state, or
source file was edited. The only generated artifacts are this note and the
adjacent `review.yaml`. There was no commit or push. Both remain pending the
Coordinator archive task `TASK-20260907-0cbf2c` and Coordinator adjudication.
