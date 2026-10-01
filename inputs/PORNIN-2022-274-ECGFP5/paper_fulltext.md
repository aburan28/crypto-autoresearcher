<!--
Extracted from inputs/PORNIN-2022-274-ECGFP5/eprint-2022-274.pdf on 2026-09-20
by extract_text.py (pdfminer.six, LAParams line_margin=0.3, char_margin=2.0,
boxes_flow=0.5, detect_vertical=False). Derivative text under ePrint terms;
attribution to Thomas Pornin, EcGFp5: a Specialized Elliptic Curve, ePrint 2022/274.
NOT hand-cleaned.
-->

EcGFp5: a Specialized Elliptic Curve

Thomas Pornin

NCC Group, thomas.pornin@nccgroup.com

28 February, 2022

Abstract. We present here the design and implementation of ecGFp5, an elliptic
curve meant for a specific compute model in which operations modulo a given 64-bit
prime are especially efficient. This model is primarily intended for running operations
in a virtual machine that produces and verifies zero-knowledge STARK proofs. We
describe here the choice of a secure curve, amenable to safe cryptographic operations
such as digital signatures, that maps to such models, while still providing reasonable
performance on general purpose computers.

1 EcGFp5 Definition

Let p = 264 − 232 + 1. This is a 64-bit prime integer; computations modulo p can be relatively
efficiently implemented on a variety of platforms. It has high 2-adicity (p − 1 is a multiple of
a large power of 2, here 232) which makes it convenient for STARK proofs[4]. 32-bit integer
operations can also be expressed over GF (p) since, for instance, the product of two unsigned
32-bit integers is at most (232 − 1)2, which is lower than p. The Miden VM[13] is an open-
source implementation of a virtual machine whose internal opcodes work over elements of
GF (p) and can be used to generate and verify STARK proofs over arbitrary program execu-
tions. Miden is currently funded by Polygon for blockchain-related purposes, but it can be
used in a larger spectrum of situations. Moreover, other projects may want to use the same
modulus p, especially but not necessarily in conjunction with zero-knowledge proofs. For the
definition of ecGFp5, we consider the abstract and interesting problem of defining a secure
prime order group, based on an elliptic curve, amenable to cryptographic operations such
as digital signatures, and efficiently implementable in the compute model incarnated by the
Miden VM. In that model, all elementary operations in GF (p) have the same unit cost; this
includes additions, subtractions, multiplications, and, crucially, divisions.

5) = GF (p) [z]/(z

The chosen curve has the following parameters. We first define the finite field extension
5 − 3), i.e. the ring of polynomials (in the symbolic variable z) with
5−3.
5) can be represented as five elements of GF (p), corresponding to the

GF (p
coefficients in GF (p), and all operations performed modulo the irreducible polynomial z
Every element of GF (p
five coefficients of a polynomial of degree at most 4.

We define, over GF (p

5), an elliptic curve of equation:

2 = x(x

2 + 2x + 263z)

y

This is a double-odd curve[16], with equation constants a = 2 and b = 263z; its order is

2n for the 319-bit prime integer:

n = 106799351671714695104148491657179270274505774058

1727230159139685185762082554198619328292418486241

EcGFp5 is then formally defined as the group G of points of that curve which are not points
of n-torsion. The neutral element of the group is the point N = (0, 0) (the only point of
order 2 on the curve). The sum in the group of two elements P and Q is defined as the curve
point P + Q + N . As explained in [16], this yields a group with the proper characteristics for
defining cryptographic operations such as digital signatures or key exchange:

– The group G has prime order n.
– Elements of G can be uniquely encoded into a field element; the decoding process is
unambiguous and inherently verifies that the provided encoding was valid and canonical.

– Group operations can be computed with efficient complete formulas.

Several systems of coordinates can be used. In general, it is recommended to use (x, u)
coordinates, in which u = x/y for element (x, y) (for the neutral N , we use u = 0). If both
x and u are expressed as fractions (denoted X /Z and U /T , respectively), then general point
addition formulas have a cost of 10 multiplications in the field (denoted 10M), and specialized
formulas for sequences of doublings have a per-doubling cost of 2M+5S (two multiplications
and five squarings in the field). As will be detailed in the next sections, though, within the
target compute model, it is in fact more efficient to switch to affine Weierstraß coordinates
and formulas.

In the next sections, we will:

– justify the choice of a degree-5 field extension;
– describe the implementation of field and curve operations in the target compute model

(thereafter called “in-VM”);

– formalize the choice criteria for the curve parameters;
– provide some details on the implementation of the curve when not working in the VM

(i.e. the “out-of-VM” situation).

A copy of this paper, a test implementation in Python that emulates the VM model to

measure costs, and a reference implementation in Rust, are provided at:

https://github.com/pornin/ecgfp5/

2 Choice of Field

Since p is a 64-bit integer, we need to work in a field extension GF (pk) in order to have a field
large enough to obtain a curve with adequate security. We aim at the usual “128-bit security”
level. For such a level, we need a field with at least a 256-bit order, hence k ≥ 4. Robustness
of elliptic curve discrete logarithm in extension fields has been studied in various articles. A
rough summary is the following:

– If the extension degree k is composite, then Weil descent attacks may apply, using a tower
of field extensions to turn the problem into a discrete logarithm in a higher genus curve
on a smaller field[9,3]. To avoid such issues, a prime degree is highly recommended. Diem
showed that if k is prime and not lower than 11, then such attacks cannot work[6].

– A related attack using Gröbner bases was described by Gaudry[8]; its complexity was

further analyzed by Joux and Vitse, along with some possible variants[12].

2

For performance reasons, we would like to have k as small as possible; k = 11 would lead
to a 704-bit field where computations would be too expensive. Using k = 4 would allow the
3/2) ≈ 296. Though
known attacks on quartic extension fields[3], with complexity about O(p
this value is quite larger than what can practically be implemented, it still falls short of the
expected “128-bit” level. Thus, we need at least k = 5.

With k = 5, Gaudry’s attack entails computing about p

2−2/5 ≈ 2102.4 systems of polyno-
mial equations, and obtaining a Gröbner basis for each of them. Each system would contain
5 equations with 5 unknowns, and a total degree 2k−1 = 16; it is expected that obtaining the
3), with k the number
basis will require using the FGLM algorithm[7] with complexity O(kD
of unknowns (here, k = 5) and D the degree of the underlying ideal, which should be close to
2k(k−1) = 220. The involved matrix should be mostly empty and a lower complexity might be
2) ≈ 240.
achieved, but even with very optimistic assumptions, it is unlikely to go below O(D
This leads to a total theoretical complexity of at least 2142, well beyond the target 128-bit level.
2) for some constant C that depends on k, again above
Joux and Vitse’s variant has cost O(Cp
the 128-bit level.

We can thus claim that a degree-5 extension field, GF (p

5), is sufficient to achieve 128-bit

security against all known attacks on discrete logarithm on elliptic curves.

All finite fields with the same cardinality are isomorphic to each other; we can thus choose
whatever definition of that field provides the best performance. Field extensions of degree k
are classically defined as the quotient of the ring of polynomials in the base field, by a given
unitary irreducible polynomial M of degree k. Since multiplications in the extension field
will involve reductions modulo M, performance should be best if using an M of minimal
Hamming weight, and with non-zero coefficients as close to 1 or -1 as possible; moreover,
5 − c for some constant c makes the Frobenius operator especially
a modulus with format z
inexpensive. Among polynomials in GF (p) [z], none of the following polynomials happens
5 ± 2. The next best choices are
to be irreducible: z
5 − 3 and z
z

5 + 3, which are both irreducible; we thus choose M = z

5 ± zi ± 1 for any i ∈ [1; 4], z

5 ± 1, z

5 − 3.

5, z

3 In-VM Implementation

3.1 VM Opcodes

We assume here that the following opcodes are offered by the target compute model, and all
have cost exactly 1 cycle:

– add, sub, mul and div perform respectively addition, subtraction, multiplication and
division in GF (p). Division fails if the divisor is zero; it is up to the caller to make sure
that this situation does not happen. Negation has a specific opcode (neg) but could also
be implemented with a subtraction from zero.

– and, or, xor and not perform operations on Boolean values. A “true” is represented as
the GF (p) element 1, while a “false” is 0. Any other value triggers a failure. Opcodes
eq and neq compare two GF (p) elements and return such Boolean value if the two
operands, are, respectively, equal to each other, or different from each other.

– select applied on three values x, y and c returns x if c = 0, or y if c = 1. The control

value c must have a Boolean 0-or-1 value.

3

– add32, sub32, mul32, div32, shl32, shr32, and gte32 implement operations on
32-bit values (for addition, subtraction, multiplication, division, shift left, shift right,
and greater-or-equal comparisons, respectively). Addition and subtraction are computed
modulo 232 and have carry/borrow support for both input and output. Multiplication
yields a 64-bit output (which always fits in a GF (p) element). Shifts and comparisons
operate on unsigned values; the left shift truncates its output to 32 bits. Moreover, shift
counts must be fixed constants. All 32-bit opcodes assume that the operands are in the
proper range (0 to 232 − 1).

The names above do not exactly match the names used by the Miden VM assembly spe-
cification[14]; for instance, what we call here add32 is known as u32addc.unsafe in the
specification document.

The compute model should be understood as a general circuit emulation in which only
arithmetic gates have a cost, while data routing is free, provided that it can be resolved stat-
ically. In the context of a VM executing a program consisting of opcodes, this means that
function calls, loop control, reading from memory and writing to memory are all free (their
cost is zero); however, this does not extend to data-dependent conditional jumps, and array
accesses at data-dependent indexes. These operations are possible in Miden but very expen-
sive; in the context of this paper, we simply consider them to be forbidden. In a sense, we use
a compute model which is close to constant-time implementations, although for different
reasons.

3.2 Field Operations

An element x of GF (p
2 + x3z
x2z
tion in GF (p

3 + x4z

5) is represented as five coefficients x0 to x4, such that x = x0 + x1z +
4. Addition and subtraction are simply done coefficient-wise; thus, an addi-

5) boils down to five add opcodes, for a cost of 5.

Multiplication. Multiplication in GF (p
way:

5) (d ← a + b) can be done in a straightforward

d0 ← a0b0 + 3(a1b4 + a2b3 + a3b2 + a4b1)
d1 ← a0b1 + a1b0 + 3(a2b4 + a3b3 + a4b2)
d2 ← a0b2 + a1b1 + a2b0 + 3(a3b4 + a4b3)
d3 ← a0b3 + a1b2 + a2b1 + a3b0 + 3a4b4
d4 ← a0b4 + a1b3 + a2b2 + a3b1 + a4b0

5 − 3. Any con-
The multiplications by 3 come from the reduction modulo the polynomial z
stant in GF (p) other than 3 would yield the same overall cost, except 0, 1 or −1, which would
5 − 1 are not irreducible, and do not yield a
be cheaper; however, polynomials z
proper field.

5 + 1 and z

5, z

Overall multiplication cost is 49. Other techniques such as Karatsuba or Toom-Cook may
reduce the number of multiplications, but at the cost of a higher number of additions and
subtractions; in our compute model, these do not seem to provide overall cost reductions.

Squaring can be done with lower cost since, for instance, product a0b1 and a1b0 yield the

same value when a = b. The cost of a squaring operation is then 34.

4

Inversion in GF (p

Inversion.
described by Itoh and Tsujii[11]. Define the integer r = 1 + p + p
holds:

5) can be computed very efficiently thanks to a method first
4. The following

2 + p

3 + p

p
Therefore, for any non-zero x in GF (p

5 − 1 = (p − 1)r
5), we have:

5−1 = 1 = (xr)p−1
Thus, xr is a root of the polynomial X p−1 − 1. Since the roots of that polynomial are exactly
5). We can
the non-zero elements of GF (p), this implies that xr ∈ GF (p) for any x in GF (p
thus write the inverse of x as:

xp

1

x

=

xr−1
xr

which can be computed as the product of xr−1 (an element of GF (p
(an element of GF (p)).

5)) by the inverse of xr

Values xr−1 and xr can furthermore be computed with appropriate use of the Frobenius
5); this is a field automorphism, i.e. ϕ1 (x + y) =

operator. Define ϕ1(x) = xp for any x ∈ GF (p
ϕ1(x) + ϕ1(y), and ϕ1(xy) = ϕ1(x)ϕ1 (y) for any x and y. Thus, if x = (cid:205)

i xizi, then:

ϕ1(x) =

=

4
(cid:213)

i=0
4
(cid:213)

i=0

ϕ1 (xi)zpi

xi (3 (cid:98)pi/5(cid:99))zpi mod 5

which boils down to multiplying each coefficient by a precomputed constant, and possibly
reordering them. In our case, p = 1 mod 5, which means that zpi mod 5 = zi, and there is no
reordering; also, one of the five precomputed constants is 30 = 1. The cost of the Frobenius
operator is thus only 4 cycles. We similarly define ϕ2 (x) = ϕ1(ϕ1 (x)), which is also computed
in cost 4 (we will also call ϕ2 a “Frobenius operator”).
With the Frobenius operator, we compute xr−1 as:

xr−1 = xp+p

2+p

4

3+p

= ϕ1 (x)ϕ1(ϕ1 (x))ϕ2 (ϕ1(x)ϕ1 (ϕ1(x)))

5). Once xr−1 is ob-
which entails three Frobenius operators and two multiplications in GF (p
tained, xr is computed by multiplying that value with x; since xr is known to be in GF (p), we
only need to compute the first coefficient, with cost 10.

Inversion in GF (p) has cost 1 (this is a single div opcode); however, we have to add a
small corrective action to avoid a division by zero, in case the input x was equal to zero: before
inverting y = xr, we compare it with zero (eq opcode), then add the Boolean result (a GF (p)
element with value 0 or 1) to y. Thus, if x = 0, we end up inverting y(cid:48) = 1 instead of y = 0,
and the division opcode does not fail. This corrective action has cost 2.

Final multiplication of xr−1 by the resulting x−r is done in five mul opcodes. The overall
5) is 128 cycles (it would be 126 if the div opcode tolerated a divisor
cost of inversion in GF (p
equal to 0). Note that if x = 0, the inversion process described above does not fail; instead, it
returns 0. This is a feature; it simplifies some operations later on.

General division is the combination of a multiplication and an inversion, with cost 177.

5

Legendre Symbol. We define the Legendre symbol of x as the value x (p
to 0 if x = 0, to 1 if x is a non-zero quadratic residue, or −1 if x is not a square in GF (p
Again using the value r = 1 + p + p

4, we find that:

5−1)/2; it is equal
5).

2 + p

3 + p

x (p

5−1)/2 = (xr) (p−1)/2

5) is equal to the Legendre symbol of xr in GF (p). As
Thus, the Legendre symbol of x ∈ GF (p
in the case of inversion, the computation of xr is efficient. In GF (p), we note that (p − 1)/2 =
263 − 231, leading to the following process:

1. y ← xr (result is in GF (p))
2. y31 ← y
3. y63 ← y
4. t ← y63/y31 (one div opcode)

231 (with 31 mul opcodes)
31 (with 32 mul opcodes)

232

The overall cost is 186.

Square Root. We can use, again, the Frobenius operator to speed up square roots, by
noticing that, for x ≠ 0 in GF (p

5):

√

x =

=

(cid:114)

xr
xr−1
√
xr
x (r−1)/2

since r − 1 = p + p

2 + p

3 + p

4, which is an even integer. We can compute x (r−1)/2 as:

x (r−1)/2 = xp(1+p

2) (p+1)/2

= ϕ1 (x (p+1)/2

ϕ2 (x (p+1)/2))

263+1/x

231, allowing the computation of that value with 63 squar-
We can write x (p+1)/2 = x
5). Once we obtained x (p+1)/2, we use it to
ings, one multiplication and one inversion in GF (p
compute x (r−1)/2 as shown above, with two Frobenius operators and one multiplication. We
can furthermore derive xr from x (r−1)/2 with a squaring (to get xr−1) then a multiplication by
x; the latter only needs to compute the lowest coefficient, since xr ∈ GF (p).

At that point, we have to compute the square root of y = xr in GF (p). Moduli with
high 2-arity are known to be inconvenient for computing square roots. We use the following
process, which really is the Tonelli-Shanks algorithm, specialized to our compute model in
which data-dependent conditional jumps are forbidden, but multiplications are inexpensive:

1. Let n = 32 and q = 232 − 1, so that q is odd and p = q2n + 1. Let g be a primitive 2n-th
root of unity in GF (p) (we can use g = 7q mod p, since 7 is a non-QR in GF (p)). We
precompute values gi = g

2i for i = 0 to n − 1.

2. (u, v) ← (y(q+1)/2
3. For i = n − 1 down to 1:

, yq)

(a) w ← v

2i−1 (with i − 1 squarings)

6

(b) If w = −1 mod p, then: (u, v) ← (ugn−i−1, vgn−i) (the new (u, v) are always com-
puted, but kept with select opcodes only if an eq opcode declares that the com-
puted w is indeed equal to −1)

4. If v = 0 or 1, then y was indeed a square, and u contains one of its square roots. Otherwise,
y was not a square, and thus x was not a square either; in that case, we arrange to set v to
zero (e.g. with an extra select).

The algorithm above entails (n − 1)(n − 2)/2 = 450 squarings, and some other operations,
for a total of 659 cycles for the square root in GF (p). Combined with the computations of
5)
x (r−1)/2 and xr, and finally putting together the values, we compute a square root in GF (p
in a total of 3261 cycles. The routine returns two values, the square root itself, and a Boolean
value reporting the success of the process; if the input value was not a square, the returned
“square root” is zero, and the Boolean is zero.

Cost Summary. We obtain the following costs for in-VM operations in GF (p

5):

Operation
addition
subtraction
multiplication
squaring
inversion
division
Legendre symbol
square root

Cost (cycles)
5
5
49
34
128
177
186
3261

5) are quite inexpensive: the cost of an
An important point here is that inversions in GF (p
inversion is only about 2.57 times the cost of a multiplication. This is not the usual situa-
tion when dealing with elliptic curve implementations; it impacts the strategy we will use, in
particular the point addition formulas.

3.3 Curve Formulas

5) are quite efficient (their cost is lower than three times the cost of
Since inversions in GF (p
5)), the most efficient formulas for computing point additions and
a multiplication in GF (p
doublings are obtained by working with the short Weierstraß equation and affine coordinates.
5) can be expressed as a short Weierstraß curve with
Moreover, any elliptic curve over GF (p
a suitable change of variable; thus, no curve type will be any better or worse than any other,
efficiency-wise, for in-VM computations.

2 + ax +
Change of Variable. A double-odd curve such as ecGFp5 has equation y
b) for two constants a and b (for ecGFp5, a = 2 and b = 263z). It can be converted to the
short Weierstraß equation:

2 = x(x

with constants:

2 = X

3 + AX + B

Y

A = (3b − a
B = a(2a

2)/3
2 − 9b)/27

7

using the following change of variable:

(X, Y ) = (x +

a

3 , y)

This change of variable is very inexpensive: it suffices to add a single constant to the x coordi-
nate. Moreover, that constant is in GF (p) for ecGFp5, leading to an addition in a single cycle
in the VM.

EcGFp5, however, is not exactly the elliptic curve with equation y

2 +ax +b), but a
subset thereof, consisting of (exactly) the points which are not the double of any other point.
In order to perform computations on the short Weierstraß curve, we also need to map into the
subgroup of points of n-torsion on the short Weierstraß curve, which entails adding the point
2).
N . This can be done while still on the original equation, since (x, y) + N = (b/x, −by/x
Another method, which is even simpler, is to combine the addition of N with the decoding
process. Given an encoded point w (nominally equal to y/x for the ecGFp5 element (x, y)),
compute the following:

2 = x(x

2 − a
2 − 4b

1. e ← w
2. Δ ← e
3. (x1, x2) ← ((e +

√

√

Δ)/2) (if Δ is not a square, then either w = 0, in which
case the point is N and should be decoded as the point-at-infinity in the short Weierstraß
curve; or w ≠ 0, and there is no solution, w is not a validly encoded point)

Δ)/2, (e −

4. If x1 is a quadratic residue, then set x = x1; otherwise, set x = x2
5. Return (X, Y ) = (x + a/3, −wx)

Step 4 is where processing diverges from normal decoding in double-odd curves, where
we would have chosen the x value which is not a quadratic residue instead. This decoding
process works because a given w = y/x value is shared by two points on the curve, P + N
(which is in ecGFp5) and −P (which is in the subgroup of points of n-torsion); here, we
simply use the latter, and take the negation into account by computing y = −wx instead of
y = wx.

It shall be noted that if w = 0, then the decoding above computes Δ = a

2 − 4b, which
is not a quadratic residue. Moreover, in that case, the “point-at-infinity” should be returned,
and that point does not have defined (X, Y ) coordinates. In a practical implementation, a
point in affine coordinates on the short Weierstraß curve really is a set of three values: the co-
5), and a Boolean flag I which, when non-zero, indicates
ordinates X and Y , which are in GF (p
that the point is the point-at-infinity, and the values of X and Y should be ignored.

Point Addition. The sum of two points (X1, Y1) and (X2, Y2) is the point (X3, Y3) with:

λ =

X3 = λ

Y2 − Y1
X2 − X1
2 − X1 − X2

Y3 = λ(X1 − X3) − Y1

Famously, these formulas are not complete; if X1 = X2 then either Y1 = −Y2, in which case
the sum is the point-at-infinity (sum of a point and its opposite); or Y1 = Y2, which means

8

that the point is added to itself, and λ must instead be computed as:

λ =

3X

2

1 + A
2Y1

A complete routine that supports all cases looks like this:

1. Inputs are points (X1, Y1) (with infinity flag I1) and (X2, Y2) (with flag I2).
2. Compare X1 with X2, yielding a Boolean sx with value 1 if they are equal, 0 otherwise.
This entails five eq opcodes, and four and opcodes, for a cost of 9. Similarly, compare Y1
with Y2, yielding sy.

3. Set λ0 to Y2 −Y1 if sx = 1, or to 3X

1 +A if sx = 0 (both values are computed, and select

2

opcodes are used to keep the right one, depending on the value of sx).

2 − X1 − X2

4. Set λ1 to X2 − X1 if sx = 1, or to 2Y1 if sx = 0.
5. λ ← λ0/λ1
6. X3 ← λ
7. Y3 ← λ(X1 − X3) − Y1
8. I3 ← sx and sy
9. If I1 ≠ 0, then replace (X3, Y3, I3) with (X2, Y2, I2)
10. If I2 ≠ 0, then replace (X3, Y3, I3) with (X1, Y1, I1)

This routine handles all edge cases (point doublings, point-at-infinity as input or output
operand) with a fixed cost of 387 cycles in the VM. This cost is about 7.9 times the cost of a
single multiplication: this is faster than the best know curve point adding formulas that do
not involve any inversion.

Optimizations are possible in some cases:

– When it is a priori known that the addition is not an edge case, then we can avoid in par-
ticular the squaring involved in computing λ0 for a point doubling, and all the select
opcodes, leading to a routine with cost 290.

– For explicit point doublings, the select opcodes can also be skipped, since the double
of a non-infinity n-torsion point cannot be the point-at-infinity; we can simply keep the
infinity flag unchanged, and apply the doubling formulas on the coordinates. This leads
a point doubling in 326 cycles.

Point Multiplication.
v, the following process can be used:

In the specific case of the multiplication of a point P by a scalar

1. Reduce the scalar v modulo n, then add n to get a value k in the n to 2n − 1 range.
2. Split the scalar into chunks (cid:100)321/w(cid:101) of w bits, for a given window width w (experimen-
tally, w = 4 seems to be the best choice here). Each chunk ci yields a signed digit di with
the following:
(a) Initialize a carry m to 0.
(b) For each chunk ci (in least-to-most significant order), add m to the value of ci. If
m + ci ≤ 2w−1, then set di to that value, and set m to zero; otherwise, set di to
m + ci − 2w, and set m to 1.

9

All digits are between −2w−1 + 1 and +2w−1; moreover, with the chosen parameters, it can
be shown that the top digit is necessarily greater than or equal to 1. Since the VM works
with unsigned 32-bit integers (mapped to GF (p) elements), the sign and absolute value
of each digit may be returned separately.

3. Fill an array W with points iP for i = 1 to 2w−1. This is called the “window”. For an
index value d between −2w−1 and +2w−1, the point dP can be recovered with a lookup
process (detailed below).

4. For all digits di, starting with the second-to-top digit down to d0:

(a) Multiply Q by 2w with w successive doublings.
(b) Lookup point diP from the window, and add it to Q.
It can be shown that in this process, if input P was not the point-at-infinity, then for all
digits except the last two (d1 and d0), the addition of the looked-up point diP to the current
Q cannot be an edge case of the point addition formulas; thus, each of these additions can
be the specialized routine with cost 290; only the last two iterations need to use the generic
routine with cost 387.

All these operations, including the building of the window, can be performed assuming
that the input P is not the point-at-infinity; it suffices to combine (with a Boolean or) the
initial flag IP with the current flag IQ to obtain a proper result even in case the input P is the
point-at-infinity. Note that window building can then use the specialized point addition, and
the infinity flag of each window element needs not be stored.

The window lookup for digit value d is done as follows:

1. Initialize variables X and Y to copies of XP and YP.
2. For indices i = 2 to 2w−1, replace X and Y with the coordinates of iP (from the window)

if and only if |d| = i.

3. If d < 0, then replace Y with −Y .
4. Set the flag I to 1 if d = 0, or to 0 otherwise.

Lookup cost increases with window size, with an overhead of 11 cycles per extra point.

Overall cost of the point multiplication function, including the addition of n to v and

the split into digits, and the building of the window, was measured to be 138482 cycles.

Key Pair and Signature Generation. A special case of point multiplication is when
the point to multiply is the conventional generator point G. This is the main curve operation
in public/private key pair generation, as well as signature generation. In that case:

– The window can be precomputed.
– Since there is no cost for window building, a larger window may offer better perfor-

mance, although lookup costs will dominate with large windows.

– Several windows for precomputed multiples of G may be used conjointly, in order to
reduce the number of loop iterations and doubles. For instance, with 8 windows for all
240iG (with i = 0 to 7), 7/8th of the point doublings can be avoided, leading to a con-
siderable speed-up.

There are many possible trade-offs between window size, number of windows, and code
size. When generating or verifying STARK proofs, the whole implementation can be con-
ceptually unrolled, and large tables of constants used; other situations might call for more
compact implementations.

10

Signature Verification. Verification of a Schnorr signature entails checking that dG +
eQ = R for some scalars d and e (obtained from the signature itself, and some hashing),
conventional generator G, public key Q, and the point R whose encoding is the first half
of the signature. In general, there are many optimizations that can be applied on signature
verification:

– The size of the two scalars can be about halved by using the Antipa et al method[1],

usually with Lagrange’s algorithm for lattice reduction[15].

– Scalar representation as signed digits can use the w-NAF representation, in which most
digits are zero and all the non-zero digits are odd, leading to fewer and faster window
lookups.

– Several verifications can be performed simultaneously with a randomized batch verifica-

tion process, allowing important cost sharings.

Unfortunately, most of these optimizations require conditional execution of some kind,
depending on the involved data. This is usually not a problem (signature verification nomi-
nally happens only over public data), but in the VM compute model, conditional execution
is quite inconvenient.

Computation of dP + eQ for two points P and Q, and two scalars d and e, can still use
Straus’s algorithm[18] (often known in cryptography as “Shamir’s trick”) to mutualize point
doublings, i.e. perform about 320 doublings in total, instead of 640 as would be obtained
with two separate point multiplication operations.

4 Curve Parameters Selection

As we saw in section 3.3, in-VM curve operations will preferably use a short Weierstraß equa-
tion and affine formulas. Any elliptic curve is amenable to such a representation; moreover,
the specific values of the Weierstraß constants A and B have little to no incidence on in-VM
5) as part of the doubling formulas, and
performance: A is only used in an addition over GF (p
B is not used at all in the formulas. Thus, the in-VM compute model does not imply any con-
straint on the curve equation type we will use. We are free to select a curve type that favours
out-of-VM performance, as long as it provides the required security characteristics.

For proper security in arbitrary protocols, we need a prime-order group with a unique,

canonical and verifiable encoding[5]. In practice, this restricts our choice to the following:

– A curve with a prime order. This requires using the generic short Weierstraß equation.
Encoding output consists of the x coordinate, along with a single “sign” bit for y to des-
ignate which square root of y

2 is intended.

– A double-odd curve[16], with order 2n for a prime n. An element of the prime order

group is encoded as a single field element.

– A Montgomery or twisted Edwards curve, of order 4n or 8n for a prime n, along with

the Decaf/Ristretto encoding process[10,2].

All three kinds offer division-less complete formulas for safe out-of-VM processing. The
formulas for prime-order short Weierstraß curves[17] are somewhat slower than for the other
two (12M for general addition, 8M+3S for doubling). Twisted Edwards curves have the fastest
general addition formulas (8M), and point doubling with cost 4M+4S (an alternate choice

11

of representation called “inverted coordinates” offers addition in 9M+1S and doubling in
3M+4S). However, double-odd curves have better doubling formulas (2M+5S per-doubling
overhead); the encoding/decoding process of double-odd curves is also somewhat simpler
than that of Decaf/Ristretto, and allows for efficient validation that a point is decodable and
canonical (with only a Legendre symbol). We will thus choose a double-odd curve.

There are several representations for double-odd curves; in general, it is recommended
to use fractional (x, u) coordinates, for which complete formulas are known. A point is rep-
resented as a quadruplet (X :Z:U :T ), which is such that x = X /Z and u = x/y = U /T .
Point addition formulas on that representation entail some multiplications by the equation
2)/(2b − a) and β = (a − 2)/(2b − a).
constants a and b, and also the constants α = (4b − a
Choosing a = 2 implies that α = 2 and β = 0, which is convenient.

If a = 2, which is an element of GF (p) (the base field), we must choose b outside of
5),
GF (p); otherwise, the curve over the base field would be a subgroup of the curve over GF (p
and it would not be possible to obtain total curve order 2n for a prime n. To speed up multi-
plications by b, we will still want to use a constant b equal to bizi for some i ∈ [1; 4], and bi
as small as possible as an integer (in absolute value). We thus use the following search process:

1. c ← 1
2. For i = 1 to 4:
(a) If curve y
(b) If curve y

3. c ← c + 1
4. Loop to step 2.

2 = x(x
2 = x(x

2 + 2x + czi) has order 2n with n prime, then return b = czi.
2 + 2x − czi) has order 2n with n prime, then return b = −czi.

2 + ax + b) may be double-odd (i.e.
As explained in [16], a curve of equation y
2 − 4b is a quadratic residue; this gives a
order 2n for an odd integer n) only if neither b nor a
fast test that allows skipping most of the expensive point counting operations in the process
described above.

2 = x(x

Using the process above, the first usable curve is obtained for b = 263z. This yields the

curve whose parameters were given in section 1.

While the curve selection process is not known to induce any bias or select a curve with
uncommon properties, we still checked that its embedding degree is large. For a curve defined
over a finite field GF (q) and with a subgroup of prime order n (that does not divide q), the
embedding degree is the smallest integer e > 0 such that n divides qe − 1 (or, said otherwise,
e is the multiplicative order of q modulo n). If e is very small, then the Weil, Tate and similar
pairings can be computed, reducing the discrete logarithm in the curve into the discrete log-
arithm over the multiplicative group of invertible elements in GF (qe). A randomly selected
curve should have a very large embedding degree e (about the same size as n); a low embedding
degree does not necessarily imply a weakness (except if e is so small that the discrete logarithm
in GF (qe) can be computed more efficiently than in the curve itself), but it would hint at
some unexpected internal structure. In the case of ecGFp5, we checked that e = (n − 1)/5,
i.e. a 317-bit integer, close to the size of n itself, as is expected of a randomly selected curve.
To perform this check, notice that e is necessarily a divisor of n − 1; thus, we can factor n − 1
to try all values (n − 1)/r for any prime r that divides n − 1. The factorization of n − 1 is:

n − 1 = 25 · 5 · 163 · 769 · 1059871

· 253243826720162431254857814100127

· 198400523053184002814403536918162724916343842520561

12

5 Out-of-VM Implementation

EcGFp5 was designed to match the abilities of the target VM compute model, not the abili-
ties of any specific concrete CPU such as modern x86 or ARM. Out-of-VM performance is
thus expected to be lower than what is usually expected from fast elliptic curves with 128-bit
security, for two reasons:

– Operations in GF (p) have some overhead. The specific value of p = 264 − 232 + 1 allows
for some fast reduction techniques, but fast reduction is still more expensive than no
reduction at all.

– GF (p

5) is a 320-bit field, 1.25 times larger than a 256-bit field. Point multiplication has
a cost cubic in the size of the field (with commonly used field sizes); thus, as a very rough
approximation, we should expect a cost factor 1.253 ≈ 1.95 compared to a usual curve
with 128-bit security.

We implemented ecGFp5 in the Rust programming language. The implementation is
constant-time and efficient; it is nonetheless fully portable (it uses only the core library; it
includes no inline assembly, no architecture-specific intrinsics, and no unsafe code). We still
achieve the following performance on an Intel i5-8259U “Coffee Lake” CPU (using Rust
compiler version 1.57.0, with extra flags “-C target-cpu=native” to allow the compiler to use
opcodes available on that CPU, in particular mulx):

Operation
GF (p) addition
GF (p) subtraction
GF (p) multiplication
GF (p) inversion
GF (p) Legendre symbol
GF (p) square root
GF (p
GF (p
GF (p
GF (p
GF (p
GF (p
GF (p
ecGFp5 point addition
ecGFp5 point doubling
ecGFp5 point doubling ×5
ecGFp5 point multiplication
ecGFp5 generator multiplication
ecGFp5 mul+add verification

5) addition
5) subtraction
5) multiplication
5) squaring
5) inversion
5) Legendre symbol
5) square root

Cost (cycles)
4.02
3.02
10.18
737.39
714.20
5430.19
8.80
5.78
94.03
68.63
1069.75
1042.20
12410.38
1328.50
985.37
3971.39
363168.03
109516.20
336952.88

In this table, an average per-operation time is reported for a long sequence of dependent
operations: the output of each operation is used as part of the input to the next one. When
some operations do not depend on each other, they may be run concurrently by the CPU to
some extent; this is how, for instance, a subtraction in GF (p) costs 3 cycles, but a subtraction
in GF (p

5) can be done in less than 6 cycles instead of 15.

13

“Point doubling ×5” means five successive point doublings. The fractional (x, u) formu-
las on double-odd curves include optimizations for long sequences of successive doublings,
for a cost of 2M+1S+j(2M+5S) for j doublings; this is why that sequence cost is only about
four times the cost of a single doubling, instead of five times.

5.1 Field Operations

There are several possible representations of integers modulo p. In our implementation, we
chose to use Montgomery representation: an element x ∈ GF (p) is represented as 264
x mod p,
normalized as an integer in the [0; p − 1] range. This representation is coupled with Mont-
gomery multiplication, which, given x and y in GF (p), computes xy/264 mod p. Hence, the
Montgomery multiplication of 264
xy, which is the Montgomery rep-
resentation of the product xy. The cornerstone of this support is the reduction function,
p = 2128 − 296 + 264) returns x/264 mod p.
which, given a 128-bit input x (lower than 264
This reduction is implemented in Rust as follows:

y yields 264

x and 264

const fn montyred(x: u128) -> u64 {

let xl = x as u64;
let xh = (x >> 64) as u64;
let (a, e) = xl.overflowing_add(xl << 32);
let b = a.wrapping_sub(a >> 32).wrapping_sub(e as u64);
let (r, c) = xh.overflowing_sub(b);
r.wrapping_sub(0u32.wrapping_sub(c as u32) as u64)

}

This reduction works as follows:

– The input x is split into two 32-bit words and one 64-bit word: x = x0+232

x2 with
x0 and x1 being unsigned 32-bit integers, and x2 being 64-bit. Note that the assumption
on the range of the function input implies that x2 < p.

x1+264

– The third function line adds 232

x0 to 232

x1 + x0, with a carry in e. We thus obtain:

a = −264

e + 232 (x0 + x1) + x0

– On the fourth line, we compute:

b = −264

e + 232(x0 + x1) + x0 + 232

e − (x0 + x1) − e

= 232 (x0 + x1) − x1 − ep
= 232

x0 + (232 − 1)x1 − ep

If x0 + x1 < 232, then e = 0 and this value is bounded as:

0 ≤ b = 232

x0 + (232 − 1)x1 = x0 + (232 − 1)(x0 + x1) ≤ 232 − 1 + (232 − 1)2

< p

Otherwise, if x0 + x1 ≥ 232, then e = 1, and:

0 = 264 − (232 − 1) − p ≤ b = 232 (x0 + x1) − x1 − p ≤ 232 (233 − 2) − 1 − p < p

In both cases, the computed value indeed fits in the variable b without truncation, and
we know that b < p.

14

– Since 1 = 232 − 264 mod p, we know that:

x0 + 232

x0 − 264
x0 − 296

x0 + 264
x1 = 232
= 264
x0 − 264
= −264(232 (x0 + x1) − x1) mod p
= −264

x1 − 296
x0 + 264

b mod p

x1 mod p
x1 − 296

x1 mod p

Therefore, x/264 = x2 − b mod p. At that point, we have both x2 (in xh) and b (in b),
and both are in the [0; p − 1] range; thus, we only have to do a single subtraction, and
potentially add back p if this subtraction yields a negative result. This is what is done in
the last two lines of the function. Specifically, a subtraction is done with result in r and
borrow flag in c. If the borrow is 1, then we subtract it from zero with a 32-bit wrapping
operation, which then yields 232 − 1 = −p mod 264. We then subtract that value from
r, which is equivalent to adding p (modulo 264). It is easily seen that if there were no
borrow (c is zero), then the last line does not change the value of r. In both cases, the
correctly reduced output value is computed.

Using Montgomery representation has the benefit of producing strictly normalized val-
ues in the [0; p − 1] range, which allows fast subtractions and additions. Subtraction modulo
p is implemented just like the last two lines of the reduction function, described above; it has
an expected latency of 3 cycles, which is corroborated by the benchmarks.

Montgomery multiplication is a 64×64 → 128 multiplication followed by Montgomery
reduction. On recent Intel x86 CPUs, this multiplication uses the mulx opcode, which yields
the low half of the result in 3 cycles (4 cycles for the upper half). Following operations involved
in the Rust code above, we may expect that an optimal implementation will yield the result in
a total of 10 cycles (assuming that all non-compute data movements are “free”, as well as the
zero-extension of a 32-bit value to 64 bits); again, this is what we achieve in the benchmarks.
5), it is beneficial to mutualize Montgomery
reductions. For instance, the computation of the low coefficient of a product is performed as
follows:

For multiplications and squarings in GF (p

fn mul_to_k0(&self, rhs: &Self) -> GFp {

let pp0 = (self.0[0].0 as u128) * (rhs.0[0].0 as u128);
let pp1 = (self.0[1].0 as u128) * (rhs.0[4].0 as u128);
let pp2 = (self.0[2].0 as u128) * (rhs.0[3].0 as u128);
let pp3 = (self.0[3].0 as u128) * (rhs.0[2].0 as u128);
let pp4 = (self.0[4].0 as u128) * (rhs.0[1].0 as u128);
let zhi = (pp0 >> 64) + 3 * ((pp1 >> 64)

+ (pp2 >> 64) + (pp3 >> 64) + (pp4 >> 64));

let zlo = ((pp0 as u64) as u128) + 3 * (

((pp1 as u64) as u128)
+ ((pp2 as u64) as u128)
+ ((pp3 as u64) as u128)
+ ((pp4 as u64) as u128));

GFp(GFp::montyred(zlo + (zhi << 32) - zhi))

}

15

We recognize the five products (for a0b0, a1b4,...), each yielding a 128-bit output. The
full linear combination could be up to 132 bits in length, which exceeds what can be stored
in a u128 variable. To keep to sizes for which Rust has portable types, and to avoid some
contention on carry flags, we do the linear combination twice, on the low and high halves
separately; the final expression which assembles zlo and zhi is a partial reduction (using the
fact that 264 = 232 − 1 mod p) which outputs a value that fits on 100 bits, well in range of
the Montgomery reduction function.

For inversions, Legendre symbols and square roots, methods described in section 3.2 still
apply, but since divisions in GF (p) are much more expensive than multiplications (in out-
5) are not as fast as inside the VM. We obtain an
of-VM architectures), inversions in GF (p
5), which is very fast com-
inversion in about 11.4 times the cost of a multiplication in GF (p
pared with the situation in prime fields, but still not fast enough to contemplate use of affine
coordinates on the short Weierstraß curve.

5.2 Curve Operations

Using fractional (x, u) coordinates, we obtain generic point addition in 10M, and generic
point doubling in 4M+5S; however, some optimizations can be applied to sequences of dou-
blings, making it worthwhile to organize operations such that doublings happen in such long
sequences.

We use window optimizations, similar to in-VM operations (see section 3.3). Inversions in
5) are fast enough to allow normalization of window points to affine coordinates; mixed
GF (p
addition (addition between a point in fractional (x, u) and a point in affine (x, u) coordinates)
has cost 8M instead of 10M. Conversion of t points from fractional to affine coordinates in-
volves inverting 2t field elements, which can be done in a single inversion and 3(2t − 1) mul-
5) (using Montgomery’s trick of computing 1/u and 1/v as (1/uv)v and
tiplications in GF (p
(1/uv)u, respectively, and applying it recursively). With a 5-bit window, 64 point additions
5), while the normaliza-
are needed, and using affine points saves 128 multiplications in GF (p
tion involves one inversion and 93 extra multiplications, making the operation worthwhile.
Moreover, using affine coordinates for window points makes these points smaller in RAM,
which speeds up constant-time window lookups. It is expected that the optimal window size
will be 4 or 5 bits, depending on the target architecture; on the test x86 system, 5-bit windows
seem slightly better.

For the special case of multiplying the conventional generator, multiple windows can be
used (in our implementation, eight windows are used, for G, 240
G,...) and they are
precomputed, thereby avoiding the cost of conversion to affine coordinates. This operation
is used when generating a new key pair, and when producing a Schnorr signature.

G, 280

For signature verification, we apply the Antipa et al optimization[1] with Lagrange’s lat-
tice reduction algorithm[15]; the latter algorithm is implemented in about 20400 cycles on
average. Verification is nominally on public values, and thus needs not be constant-time; we
use direct array accesses for lookups. However, we do not use w-NAF representation of scalars,
because a regular addition schedule favours long sequences of sequential doublings, for which
performance is better than isolated doublings.

16

6 Conclusion

We presented an elliptic curve designed for a specific compute model. Although we use the
Miden VM as a representative of that model, we expect this curve to be generally useful for
other projects related to zero-knowledge proofs; curve design and implementation is also an
interesting problem in its own right. As a general-purpose curve, ecGFp5 performance is not
on par with the fastest standard curves (e.g. Curve25519), but is still decent enough: a single
core on a laptop computer or a smartphone can generate or verify thousands of signatures
per second.

Acknowledgements

We thank Bobbin Threadbare and Hamish Ivey-Law for providing the target context and
5), and Pierrick Gaudry for point-
useful discussions on optimized implementations in GF (p
ers and explanations on the fine details of curve attacks in extension fields. Paul Bottinelli,
Marie-Sarah Lacharité, Giacomo Pope and Javed Samuel reviewed this manuscript.

References

1. A. Antipa, D. Brown, R. Gallant, R. Lambert, R. Struik and S. Vanstone, Accelerated Veriﬁcation
of ECDSA signatures, Selected Areas in Cryptography - SAC 2005, Lecture Notes in Computer
Science, vol 3897, pp. 307-318, 2005.

2. T. Arcieri, I. Lovecruft and H. de Valence, The Ristretto Group,

https://ristretto.group/

3. S. Arita, K. Matsuo, K. Nagao and M. Shimura, A Weil Descent Attack against Elliptic Curve Cryp-
tosystems over Quartic Extension Fields, IEICE Transactions on Fundamentals of Electronics, Com-
munications and Computer Sciences, vol. E89-A, issue. 5, 2006.

4. E. Ben-Sasson, I. Bentov, Y. Horesh and M. Riabzev, Scalable, transparent, and post-quantum secure

computational integrity,
https://eprint.iacr.org/2018/046

5. C. Cremers and D. Jackson, Prime, Order Please! Revisiting Small Subgroup and Invalid Curve At-
tacks on Protocols using Diﬃe-Hellman, IEEE 32nd Computer Security Foundations Symposium
(CSF), 2019.

6. C. Diem, The GHS attack in odd characteristic, Journal of the Ramanujan Mathematical Society,

vol. 18, issue 1, pp. 1-32, 2003.

7. J.-C. Faugère, P. Gianni, D. Lazard and T. Mora, Eﬃcient Computation of Zero-dimensional Gröb-
ner Bases by Change of Ordering, Journal of Symbolic Computation, vol. 16, issue 4, pp. 329-344,
1993.

8. P. Gaudry, Index calculus for abelian varieties of small dimension and the elliptic curve discrete log-

arithm problem, Journal of Symbolic Computation, vol. 44, issue 12, pp. 1690-1702, 2009.

9. P. Gaudry, F. Hess and N. Smart, Constructive and destructive facets of Weil descent on elliptic curves,

Journal of Cryptology, vol. 15, issue 1, pp. 19-46, 2002.

10. M. Hamburg, Decaf: Eliminating cofactors through point compression, Advances in Cryptology -

CRYPTO 2015, Lecture Notes in Computer Science, vol. 9215, pp. 705-723, 2015.

11. T. Itoh and S. Tsujii, A Fast Algorithm for Computing Multiplicative Inverses in GF (2m) Using

Normal Bases, Information and Computation, vol. 78, pp. 171-177, 1988.

17

12. A. Joux and V. Vitse, Elliptic curve discrete logarithm problem over small degree extension ﬁelds. Ap-
, Journal of Cryptology, vol. 26, issue 1, pp. 119-

plication to the static Diﬃe-Hellman problem on F5

q

143, 2013.
13. Polygon Miden,

https://github.com/maticnetwork/miden

14. Miden Assembly,

version 0.2, accessed on 2022-02-21,

https://hackmd.io/YDbjUVHTRn64F4LPelC-NA

15. T. Pornin, Optimized Lattice Basis Reduction In Dimension 2, and Fast Schnorr and EdDSA Sig-

nature Veriﬁcation,
https://eprint.iacr.org/2020/454

16. T. Pornin, Double-Odd Elliptic Curves,

https://eprint.iacr.org/2020/1558

17. J. Renes, C. Costello and L. Batina, Complete addition formulas for prime order elliptic curves, Ad-
vances in Cryptology – Eurocrypt 2016, Lecture Notes in Computer Science, vol. 9665, pp. 403-
428, 2016.

18. E. Straus, Addition chains of vectors (problem 5125), American Mathematical Monthly, vol. 70,

pp. 806-808, 1964.

18

