# Tanja Lange, 'Attacking Elliptic Curve Challenges' 35-minute deck (server tallies dated 2010.09.07)

Derived text of inputs/BAILEY-2009-541-ECC2K130/lange-35minutes-talk.pdf (sha256 5a0dbb7a0f232bfeee249d3f80ac833b3141236b5fd4a2de0573beb3a959c26f) via PyMuPDF 1.28.2; 40 pages. See extract_text.py.


<!-- page 1 -->

Attacking Elliptic Curve Challenges
Daniel V. Bailey, Lejla Batina, Daniel J. Bernstein,
Peter Birkner, Joppe W. Bos, Hsieh-Chung Chen,
Chen-Mou Cheng, Gauthier van Damme,
Giacomo de Meulenaer, Luis Julian Dominguez Perez,
Junfeng Fan, Tim Güneysu, Frank Gürkaynak,
Thorsten Kleinjung, Tanja Lange, Nele Mentens,
Ruben Niederhagen, Christof Paar, Francesco Regazzoni,
Peter Schwabe, Leif Uhsadel, Anthony Van Herrewege,
Bo-Yin Yang,
and several individuals and institutions donating computer
time
2010.09.08


<!-- page 2 -->

The Certicom challenges
1997: Certicom announces several ECDLP prizes:
The Challenge is to compute the ECC private keys
from the given list of ECC public keys and associated
system parameters. This is the type of problem
facing an adversary who wishes to completely defeat
an elliptic curve cryptosystem.
Objectives stated by Certicom:
▶Increase community's understanding of ECDLP diculty.
▶Conrm theoretical comparisons of ECC and RSA.
▶Help users select suitable key sizes.
▶Compare ECDLP diculty for F2m and Fp.
▶Compare F2m ECDLP diculty for random and Koblitz.
▶Stimulate research in algorithmic number theory.


<!-- page 3 -->

The Certicom challenges, level 0: exercises
Estimated number
Bits
Name
of machine days
Prize
79
ECCp-79
146
book
79
ECC2-79
352
book
89
ECCp-89
4360
book
89
ECC2-89
11278
book
97
ECC2K-95
8637
$5000
97
ECCp-97
71982
$5000
97
ECC2-97
180448
$5000
Certicom believes that it is feasible that the 79-bit
exercises could be solved in a matter of hours, the
89-bit exercises could be solved in a matter of days,
and the 97-bit exercises in a matter of weeks using a
network of 3000 computers.


<!-- page 4 -->

The Certicom challenges, level 1
Estimated number
Bits
Name
of machine days
Prize
109
ECC2K-108
1300000
$10000
109
ECCp-109
9000000
$10000
109
ECC2-109
21000000
$10000
131
ECC2K-130
2700000000
$20000
131
ECCp-131
23000000000
$20000
131
ECC2-131
66000000000
$20000
The 109-bit Level I challenges are feasible using a
very large network of computers. The 131-bit Level I
challenges are expected to be infeasible against
realistic software and hardware attacks, unless of
course, a new algorithm for the ECDLP is discovered.


<!-- page 5 -->

The Certicom challenges, level 2
Estimated number
Bits
Name
of machine days
Prize
163
ECC2K-163
320000000000000
$30000
163
ECCp-163
2300000000000000
$30000
163
ECC2-163
6200000000000000
$30000
191
ECCp-191
48000000000000000000
$40000
191
ECC2-191
100000000000000000000
$40000
239
ECC2K-238
92000000000000000000000000
$50000
239
ECCp-239
1400000000000000000000000000
$50000
239
ECC2-238
2100000000000000000000000000
$50000
359
ECCp-359
≈∞
$100000
The Level II challenges are infeasible given today's
computer technology and knowledge.


<!-- page 6 -->

Broken challenges
1997: Baisley and Harley break ECCp-79.
1997: Harley et al. break ECC2-79.
1998: Harley et al. break ECCp-89.
1998: Harley et al. break ECC2-89.
1998: Harley et al. (1288 computers) break ECCp-97.
1998: Harley et al. (200 computers) break ECC2K-95.
1999: Harley et al. (740 computers) break ECC2-97.
2000: Harley et al. (9500 computers) break ECC2K-108.
2002: Monico et al. (10000 computers) break ECCp-109.
2004: Monico et al. (2600 computers) break ECC2-109.
Updated 2003 document cert_ecc_challenge.pdf still said
109-bit Level I challenges are feasible using a very large
network . . . 131-bit Level I challenges are expected to be
infeasible etc.


<!-- page 7 -->

The Certicom challenges ECC2-X
VAM1 research retreat in
Lausanne on SHARCS topics.
Decision to analyze the
Certicom challenges
ECC2K-130, ECC2-131,
ECC2K-163, ECC2-163.
Can we break ECC2K-130?
Infeasible sounds tempting.
Direct eects:
▶Certicom backpedals. Withdraws infeasible statement.
Instead says that ECC2K-130 may be within reach.


<!-- page 8 -->

The Certicom challenges ECC2-X
VAM1 research retreat in
Lausanne on SHARCS topics.
Decision to analyze the
Certicom challenges
ECC2K-130, ECC2-131,
ECC2K-163, ECC2-163.
Can we break ECC2K-130?
Infeasible sounds tempting.
Direct eects:
▶Certicom backpedals. Withdraws infeasible statement.
Instead says that ECC2K-130 may be within reach.
▶ECRYPT has several new research papers, starting with
paper at SHARCS The Certicom challenges ECC2-X.


<!-- page 9 -->

The target: ECC2K-130
The Koblitz curve y 2 + xy = x3 + 1 over
F2131 = F2[z]/(z131 + z13 + z2 + z + 1)
has 4ℓpoints, where ℓis the prime
680564733841876926932320129493409985129 ≈2129.
Certicom generated two random points on the curve
and multiplied them by 4, obtaining the following points P, Q:
x(P) = 05 1C99BFA6 F18DE467 C80C23B9 8C7994AA
y(P) = 04 2EA2D112 ECEC71FC F7E000D7 EFC978BD
x(Q) = 06 C997F3E7 F2C66A4A 5D2FDA13 756A37B1
y(Q) = 04 A38D1182 9D32D347 BD0C0F58 4D546E9A
The challenge:
Find an integer k ∈{0, 1, . . . , ℓ−1} such that [k]P = Q.
Worthy target:


<!-- page 10 -->

The target: ECC2K-130
The Koblitz curve y 2 + xy = x3 + 1 over
F2131 = F2[z]/(z131 + z13 + z2 + z + 1)
has 4ℓpoints, where ℓis the prime
680564733841876926932320129493409985129 ≈2129.
Certicom generated two random points on the curve
and multiplied them by 4, obtaining the following points P, Q:
x(P) = 05 1C99BFA6 F18DE467 C80C23B9 8C7994AA
y(P) = 04 2EA2D112 ECEC71FC F7E000D7 EFC978BD
x(Q) = 06 C997F3E7 F2C66A4A 5D2FDA13 756A37B1
y(Q) = 04 A38D1182 9D32D347 BD0C0F58 4D546E9A
The challenge:
Find an integer k ∈{0, 1, . . . , ℓ−1} such that [k]P = Q.
Worthy target: $ 20000 (but only CAD)


<!-- page 11 -->

The target: ECC2K-130
The Koblitz curve y 2 + xy = x3 + 1 over
F2131 = F2[z]/(z131 + z13 + z2 + z + 1)
has 4ℓpoints, where ℓis the prime
680564733841876926932320129493409985129 ≈2129.
Certicom generated two random points on the curve
and multiplied them by 4, obtaining the following points P, Q:
x(P) = 05 1C99BFA6 F18DE467 C80C23B9 8C7994AA
y(P) = 04 2EA2D112 ECEC71FC F7E000D7 EFC978BD
x(Q) = 06 C997F3E7 F2C66A4A 5D2FDA13 756A37B1
y(Q) = 04 A38D1182 9D32D347 BD0C0F58 4D546E9A
The challenge:
Find an integer k ∈{0, 1, . . . , ℓ−1} such that [k]P = Q.
Worthy target: 128-bit curves have been proposed for real
(RFID, TinyTate).


<!-- page 12 -->

Arithmetic on ECC2K-130
Elements of the Koblitz curve: a special point P∞, and each
(x1, y1) ∈F2131 × F2131 satisfying y 2
1 + x1y1 = x3
1 + 1.


<!-- page 13 -->

Arithmetic on ECC2K-130
Elements of the Koblitz curve: a special point P∞, and each
(x1, y1) ∈F2131 × F2131 satisfying y 2
1 + x1y1 = x3
1 + 1.
How to add P1, P2:
▶P1 + P∞= P∞+ P1 = P1; (x1, y1) + (x1, y1 + x1) = P∞.
▶If x1̸ = 0 the double [2](x1, y1) = (x3, y3) is given by
x3 = λ2 + λ, y3 = λ(x1 + x3) + y1 + x3, where λ = x1 + y1
x1
.
▶If x1̸ = x2 the sum (x1, y1) + (x2, y2) = (x3, y3) is given by
x3 = λ2+λ+x1+x2, y3 = λ(x1+x3)+y1+x3, where λ = y1 + y2
x1 + x2
.
Cost: 1I (inversion), 2M (multiplications), 1S (squaring).
▶For an overview of how to perform these operations in
other coordinate systems see the EFD:
http://hyperelliptic.org/EFD/


<!-- page 14 -->

Koblitz curves  the Frobenius endomorphism
▶In 1991 Koblitz pointed out that scalar multiplications
[m]P can be computed faster on curves
Ea : y 2 + xy = x3 + ax2 + 1,
where a is restricted to {0, 1}.
▶The main observation is that if (x1, y1) ∈Ea(F2n) then
also the point σ(P) = (x2
1, y 2
1) is in Ea(F2n) and these
points are related by
σ2(P) + [µ]σ(P) + [2]P = P∞,
where µ = 1 for a = 0 and µ = −1 for a = 1. The map σ
extends the Frobenius automorphism of F2n to Ea(F2n)
and is thus called the Frobenius endomorphism of Ea.


<!-- page 15 -->

The most important ECDL algorithms
No known index-calculus attack applies to ECC2K-130.
But can still use generic attacks that work in any group:
▶The PohligHellman attack reduces the hardness of the
ECDLP to the hardness of the ECDLP in the largest
subgroup of prime order: in this case order ℓ.
▶The Baby-Step Giant-Step attack nds the logarithm in
√
ℓsteps and
√
ℓstorage by comparing Q −[jt]P (the
giant steps) to a sorted list of all [i]P (the baby steps),
where 0 ≤i, j ≤⌈
√
ℓ⌉and t = ⌈
√
ℓ⌉.
▶Pollard's rho and kangaroo methods also use O(
√
ℓ) steps
but require constant memorymuch less expensive! The
kangaroo method would be faster if the logarithm were
known to lie in a short interval; for us rho is best.
▶Multiple-target attacks: not relevant here.


<!-- page 16 -->

Pollard's rho method
Make a pseudo-random walk in ⟨P⟩, where the next step
depends on current point: Pi+1 = f (Pi).
Birthday paradox: Randomly choosing from ℓelements picks
one element twice after about
p
πℓ/2 draws.
The walk has now entered a cycle.
Cycle-nding algorithm (e.g., Floyd) quickly detects this.


<!-- page 17 -->

Pollard's rho method
Make a pseudo-random walk in ⟨P⟩, where the next step
depends on current point: Pi+1 = f (Pi).
Birthday paradox: Randomly choosing from ℓelements picks
one element twice after about
p
πℓ/2 draws.
The walk has now entered a cycle.
Cycle-nding algorithm (e.g., Floyd) quickly detects this.
Assume that for each point we know ai, bi ∈Z/ℓZ so that
Pi = [ai]P + [bi]Q. Then Pi = Pj means that
[ai]P + [bi]Q = [aj]P + [bj]Q
so
[bi −bj]Q = [aj −ai]P.
If bi̸ = bj the ECDLP is solved: k = (aj −ai)/(bi −bj).


<!-- page 18 -->

Pollard's rho method
Make a pseudo-random walk in ⟨P⟩, where the next step
depends on current point: Pi+1 = f (Pi).
Birthday paradox: Randomly choosing from ℓelements picks
one element twice after about
p
πℓ/2 draws.
The walk has now entered a cycle.
Cycle-nding algorithm (e.g., Floyd) quickly detects this.
Assume that for each point we know ai, bi ∈Z/ℓZ so that
Pi = [ai]P + [bi]Q. Then Pi = Pj means that
[ai]P + [bi]Q = [aj]P + [bj]Q
so
[bi −bj]Q = [aj −ai]P.
If bi̸ = bj the ECDLP is solved: k = (aj −ai)/(bi −bj).
e.g. Adding walk: Start with P0 = P and put
f (Pi) = Pi + [cr]P + [dr]Q where r = h(Pi).


<!-- page 19 -->

A rho within a random walk on 1024 elements
Method is called rho method because of the shape.


<!-- page 20 -->

Parallel collision search
Running Pollard's rho method on N computers gives speedup
of ≈
√
N from increased likelihood of nding collision.
Want better way to spread computation across clients.
Want to nd collisions between walks on dierent machines,
without frequent synchronization!


<!-- page 21 -->

Parallel collision search
Running Pollard's rho method on N computers gives speedup
of ≈
√
N from increased likelihood of nding collision.
Want better way to spread computation across clients.
Want to nd collisions between walks on dierent machines,
without frequent synchronization!
Perform walks with dierent starting points but same update
function on all computers. If same point is found on two
dierent computers also the following steps will be the same.
Terminate each walk once it hits a distinguished point.
Attacker chooses denition of distinguished points;
can be more or less frequent. Do not wait for cycle.
Collect all distinguished points in central database.
Expect collision within O(
√
ℓ/N) iterations. Speedup ≈N.


<!-- page 22 -->

Short walks ending in distinguished points
Blue and orange paths found the same distinguished point!


<!-- page 23 -->

Equivalence classes
P and −P have same x-coordinate. Search for x-coordinate
collision. Search space for collisions is only ℓ/2; this gives
factor
√
2 speedup . . . provided that f (Pi) = f (−Pi).
Solution: f (Pi) = |Pi| + [cr]P + [dr]Q where r = h(|Pi|).
Dene |Pi| as, e.g., lexicographic minimum of Pi, −Pi.


<!-- page 24 -->

Equivalence classes
P and −P have same x-coordinate. Search for x-coordinate
collision. Search space for collisions is only ℓ/2; this gives
factor
√
2 speedup . . . provided that f (Pi) = f (−Pi).
Solution: f (Pi) = |Pi| + [cr]P + [dr]Q where r = h(|Pi|).
Dene |Pi| as, e.g., lexicographic minimum of Pi, −Pi.
Problem: this walk can run into fruitless cycles!
If there are S dierent steps [cr]P + [dr]Q then with
probability 1/(2S) the following happens for some step:
Pi+2 = Pi+1 + [cr]P + [dr]Q
= −(Pi + [cr]P + [dr]Q) + [cr]P + [dr]Q = −Pi,
i.e. |Pi| = |Pi+2|. Get |Pi+3| = |Pi+1|, |Pi+4| = |Pi|, etc.
Can detect and x, but requires attention.


<!-- page 25 -->

Equivalence classes for Koblitz curves
More savings: P and σi(P) have x(σj(P)) = x(P)2j.
Reduce number of iterations by another factor √n by
considering equivalence classes under Frobenius and ±.
Need to ensure that the iteration function satises
f (Pi) = f (±σj(Pi)) for any j.


<!-- page 26 -->

Equivalence classes for Koblitz curves
More savings: P and σi(P) have x(σj(P)) = x(P)2j.
Reduce number of iterations by another factor √n by
considering equivalence classes under Frobenius and ±.
Need to ensure that the iteration function satises
f (Pi) = f (±σj(Pi)) for any j.
Could again dene adding walk starting from |Pi|.
Redene |Pi| as canonical representative of class containing
Pi: e.g., lexicographic minimum of Pi, −Pi, σ(Pi), etc.
Iterations now involve many squarings,
but squarings are not so expensive in characteristic 2.


<!-- page 27 -->

Our choice of iteration function
In normal basis, x(P) and x(P)2j have same Hamming weight
HW(x(P)). Convenient to use this to determine iteration.
Our iteration functionnote that HW(x(P)) is always even:
Pi+1 = Pi + σj(Pi),
where j = (HW(x(P))/2 mod 8) + 3.
Iteration consists of
▶computing the Hamming weight HW(x(P)) of the
normal-basis representation of x(P);
▶checking for distinguished points (is HW(x(P)) ≤34?);
▶computing j and P + σj(P).
Choice of j avoids short, fruitless cycles.


<!-- page 28 -->

Some highlights
▶Detailed analysis of randomness of iteration function.
▶Could increase randomness of the walk but then iteration
function gets slower. Optimized:
time per iteration × # iterations
▶Do not remember multiset of j's; instead recompute this
from seed when collision is found (cheaper, less storage).
▶Comparative study of normal basis and polynomial basis
representation; new: optimal polynomial bases.
▶For Cell processor (chip in PlayStation 3) erce battle
between bitsliced and non-bitsliced implementation.
Result: much faster implementation! (Bitsliced won.)
▶Assembly language for GPUs and qhasm version. Get
control over powerful beast.
▶FPGA implementation of Shokrollahi multiplier: big
speed-up, useful also for constructive ECC.


<!-- page 29 -->

Faster implementations
500
750
1000
1500
2000
3000
4000
October 2009
March 2010
now
GTX 295
graphics card
FPGA
(RIVYERA
has 128!)
Cell in
PlayStation
Core 2 CPU
Number of cards or chips needed for 68 · 109 iterations/second.


<!-- page 30 -->

Overall speedup
E.g. 2466 Cell CPUs for a year: i.e., 900000 machine days.
Recall Certicom's estimate: 2700000000 machine days.


<!-- page 31 -->

Overall speedup
E.g. 2466 Cell CPUs for a year: i.e., 900000 machine days.
Recall Certicom's estimate: 2700000000 machine days.
That's unfair! Computers ten years ago were very slow!


<!-- page 32 -->

Overall speedup
E.g. 2466 Cell CPUs for a year: i.e., 900000 machine days.
Recall Certicom's estimate: 2700000000 machine days.
That's unfair! Computers ten years ago were very slow!
Indeed, Certicom's machine was a 100MHz Pentium.
Today's Cell has several cores, each running at 3.2GHz.
Scale by counting cycles . . . and we're still 15× faster.


<!-- page 33 -->

Overall speedup
E.g. 2466 Cell CPUs for a year: i.e., 900000 machine days.
Recall Certicom's estimate: 2700000000 machine days.
That's unfair! Computers ten years ago were very slow!
Indeed, Certicom's machine was a 100MHz Pentium.
Today's Cell has several cores, each running at 3.2GHz.
Scale by counting cycles . . . and we're still 15× faster.
Computers ten years ago didn't do much work per cycle!


<!-- page 34 -->

Overall speedup
E.g. 2466 Cell CPUs for a year: i.e., 900000 machine days.
Recall Certicom's estimate: 2700000000 machine days.
That's unfair! Computers ten years ago were very slow!
Indeed, Certicom's machine was a 100MHz Pentium.
Today's Cell has several cores, each running at 3.2GHz.
Scale by counting cycles . . . and we're still 15× faster.
Computers ten years ago didn't do much work per cycle!
True for the Pentium . . . but not for Harley's Alpha,
which had 64-bit registers, 4 instructions/cycle, etc.
Harley's ECC2K-108 software uses 1651 Alpha cycles/iteration.
We ran the same software on a Core 2: 1800 cycles/iteration.
We also wrote our own polynomial-basis ECC2K-108 software:
on the same Core 2, fewer than 500 cycles/iteration.


<!-- page 35 -->

Running the attack
Is ECC2K-130 feasible for a serious attacker? Obviously.


<!-- page 36 -->

Running the attack
Is ECC2K-130 feasible for a serious attacker? Obviously.
Is ECC2K-130 feasible for a big public Internet project? Yes.


<!-- page 37 -->

Running the attack
Is ECC2K-130 feasible for a serious attacker? Obviously.
Is ECC2K-130 feasible for a big public Internet project? Yes.
Is ECC2K-130 feasible for us? We think so.
To prove it we're running the attack.


<!-- page 38 -->

Running the attack
Is ECC2K-130 feasible for a serious attacker? Obviously.
Is ECC2K-130 feasible for a big public Internet project? Yes.
Is ECC2K-130 feasible for us? We think so.
To prove it we're running the attack.
Eight central servers receive points, pre-sort the points into
8192 RAM buers, ush the buers to 8192 disk les.
Periodically read each le into RAM, sort, nd collisions.
Also double-check random samples for validity.
Several sites contribute points, including several clusters. E.g.
test runs on rst generation of PRACE clusters
http://www.prace-project.eu
Each packet is encrypted, authenticated, veried, decrypted
using http://nacl.cace-project.eu; costs 16 bytes.
Total block cost: 1090-byte IP packet plus 66-byte ack.


<!-- page 39 -->

Reports so far (2010.09.07 tallies from servers)
▶from site c: 21820833792 bytes; GPUs, Core 2
▶from site L: 17830614016 bytes; Opteron
▶from site ℓ: 14669790208 bytes; Cell (PS3), Core 2
▶from site d: 3939812352 bytes
▶from site e: 3839403008 bytes; GPUs, Core 2
▶from site j: 3605491712 bytes; Cell blade
▶from site t: 3505213440 bytes; Core 2, Phenom II, GPUs
▶from site G: 3476676608 bytes
▶from site p: 3038750720 bytes
▶from site z: 1732281344 bytes
▶from site B: 1604201472 bytes
▶from site b: 507629568 bytes
▶from site a: 117901312 bytes
▶from site n: 86499328 bytes
Top priority: Get RIVYERA (128 FPGAs) running!


<!-- page 40 -->

Get more details, and watch our progress!
http://ecc-challenge.info
https://twitter.com/ECCchallenge
Papers and preprints:
▶The Certicom challenges ECC2-X (SHARCS 2009)
▶ECC2K-130 on Cell CPUs (AFRICACRYPT 2010)
▶Type-II optimal polynomial bases (WAIFI 2010)
▶Breaking elliptic curve cryptosystems using
recongurable hardware (FPL 2010)
▶ECC2K-130 on NVIDIA GPUs
▶Usable assembly language for GPUs
▶The whole attack in progress: Breaking ECC2K-130

