# A New Approach to Generic Lower Bounds: Classical/Quantum MDL, Quantum Factoring, and More

Minki Hhan, arXiv:2402.11269v1 (submitted 2024-02-17; CC BY 4.0).

Derived text of inputs/HHAN-2024-2402.11269/hhan-2024-2402.11269v1.pdf (sha256 eb5df4bea59017d7f9b395ecc3722a8d460ba6e1f5c15961042167e0b348638c) via pypdf 6.19.0. Equations are fragmentary; see extract_text.py.


<!-- page 1 -->

arXiv:2402.11269v1  [quant-ph]  17 Feb 2024
A New Approach to Generic Lower Bounds:
Classical/Quantum MDL, Quantum Factoring, and More
Minki Hhan*
February 20, 2024
Abstract
This paper studies the limitations of the generic approache s to solving cryptographic problems in clas-
sical and quantum settings in various models.
• In the classical generic group model (GGM), we ﬁnd simple al ternative proofs for the lower bounds
of variants of the discrete logarithm (DL) problem: the mult iple-instance DL and one-more DL prob-
lems (and their mixture). We also re-prove the unknown-order GGM lower bounds, such as the order
ﬁnding, root extraction, and repeated squaring.
• In the quantum generic group model (QGGM), we study the comp lexity of variants of the discrete
logarithm. We prove the logarithm DL lower bound in the QGGM e ven for the composite order
setting. We also prove an asymptotically tight lower bound f or the multiple-instance DL problem.
Both results resolve the open problems suggested in a recent work by Hhan, Yamakawa, and Yun.
• In the quantum generic ring model we newly suggested, we giv e the logarithmic lower bound for the
order-ﬁnding algorithms, an important step for Shor’s algo rithm. We also give a logarithmic lower
bound for a certain generic factoring algorithm outputting relatively small integers, which includes
a modiﬁed version of Regev’s algorithm.
• Finally , we prove a lower bound for the basic index calculus method for solving the DL problem in a
new idealized group model regarding smooth numbers.
The quantum lower bounds in both models allow certain (diffe rent) types of classical preprocessing.
All of the proofs are signiﬁcantly simpler than the previous proofs and are through a single tool, the so-
called compression lemma, along with linear algebra tools. Our use of this lemma may be of independent
interest.
*E-mail:minkihhan@gmail.com. KIAS
1

<!-- page 2 -->

Contents
1 Introduction 3
1.1 Our Results . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2 Compression Lemmas 6
3 Lower Bounds in the Classical Generic Group Model 7
3.1 Generic Group Model . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
3.1.1 V ariations: Maintaining Polynomials . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
3.2 The Discrete Logarithm Problem and Friends . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
3.3 Oracle Problems in the GGM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
4 Lower Bounds in the Unknown-order GGM 12
4.1 Order-ﬁnding in the Unknown-order GGM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
4.2 Root Extraction and Repeated Squaring Problems . . . . . . . . . . . . . . . . . . . . . . . . . 14
5 Lower Bounds in the Quantum GGM 14
5.1 Quantum Generic Group Models . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
5.1.1 Basic Quantum Generic Group Model . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
5.1.2 QGGM with Coherent Indices . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
5.1.3 Quantum Generic Group Algorithm with Classical Prepr ocessing . . . . . . . . . . . . 16
5.2 Discrete Logarithms in the QGGM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
5.3 Unknown-order QGGM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
6 Lower Bounds in the Quantum Generic Ring Model 19
6.1 Quantum Generic Ring Model . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
6.1.1 Quantum Generic Ring Algorithm with Classical Prepro cessing . . . . . . . . . . . . . 21
6.2 Lower Bounds in the QGRM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
7 Lower Bounds for Index Calculus Algorithms 22
7.1 Smooth Generic Group Model . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
7.1.1 Polynomial Representations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
7.2 The Discrete Logarithm Problem in the SGGM . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
A Missing Proofs 28
A.1 Missing proofs in the GGM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
A.2 A QGGM lemma . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29
B An Alternative Proof for the MDL Lower Bound 29
C Equivalence between GGMs 30
C.1 Lower bounds in the Random Representation GGM . . . . . . . . . . . . . . . . . . . . . . . . 32
2

<!-- page 3 -->

1 Introduction
What is the source of the generic hardness of some cryptograp hic problems?
The generic group models (GGM) [ Nec94, Sho97, Mau05] are the most successful and inﬂuential ideal-
ized models in cryptography . In this model, the group operations can be carried out by making queries to a
group oracle, and any other use of the particular features of the group is not allowed. Despite its restricted
nature, many important algorithms, such as Pohlig-Hellman [PH78] or Pollard’s rho algorithm [ Pol78], are
encompassed by the class of generic group algorithms. Despi te some criticisms [ Den02, KM06] and non-
generic algorithms, e.g., index-calculus, the GGM plays an important test bed for cryptographic protocols,
and the security proofs in the GGM provide a sanity check guar anteeing that there are no simple attacks.
The proofs in the GGM become more meaningful in the elliptic- curve groups.
The GGM is especially promising because of its simple securi ty proofs; most of the security proofs in the
GGM heavily rely on the Schwartz-Zippel (SZ) lemma that is al ready used in [ Sho97]. This lemma roughly
states that for a non-zero multivariate linear polynomial P over Zp for a prime p, the probability that a
random element becomes a root of P is 1/p. This provides a meaningful limitation for generic algorit hms
obtaining a single piece of information and is used to prove t he generic lower bounds for the discrete log-
arithm (DL) problem and computational/decisional Difﬁe-H ellman (C/DDH) problems, as well as many
cryptographic applications.
W e face hurdles in proving the generic security when we sligh tly tweak the model or problems. If
we consider the unknown-order groups, the lower bounds for v arious problems can be proven with rel-
atively small efforts, including the order-ﬁnding problem [Sut07] or the root extraction problems [ DK02].
When we consider the problems where enormous amounts of info rmation can be obtained, the security
proofs based on the SZ lemma do not work. T o remedy this, other idealized problems (e.g., the search-
by-hyperplane/surfaces) [ Yun15, AGK20, AHP23] are suggested or seemingly involved techniques (e.g.,
compression lemmas or pre-sampling) are used [ CK18, CDG18] in the proofs. In the quantum setting, the
rigorous proofs are rather complicated and pass through the classical lower bounds [ HYY23].
Extensions beyond the group structures [ BL96, BV98, AM09, JS13, YYHK20] become much more com-
plicated. In many cases, there is some evidence that the unco nditional lower bounds unlikely exist, and
the proofs are done through the reduction between the proble ms. T o our knowledge, there are no known
unconditional lower bounds, even in the idealized models.
This state of affairs makes the genuine source of the generic hardness elusive and asks for case-by-case
studies for each model. In particular, the unconditional lo wer bounds in idealized settings are only known
for the generic group models.
1.1 Our Results
W e provide a uniﬁed way to prove the old and new hardness proof s in the various idealized models: the
known/unknown-order classical generic groups, quantum ge neric groups, quantum generic rings, and the
new group model embracing index calculus.
Our main technical lemma is, along with some linear algebraic observations, (variants of) the compression
lemma, which roughly asserts that there is no way to compress n-bit strings to strings less than n-bit. This
lemma is occasionally used in proving the time-space tradeo ff lower bounds [ DTT10, NABT15, DGK17,
CK18, HXY19, CLQ19], and introduces a highly involved proof. Our proofs are sig niﬁcantly simpler, as
shown in this section. Roughly , we compress the problem inst ances along with some relevant randomness
into the information that generic algorithms can obtain; th e decoding simulates the generic algorithm using
the encoding, without accessing the oracles, but still recovers the problem insta nces. This gives some clues
that the generic hardness is from the limited way of obtainin g information on generic algorithms.
This paper mainly focuses on the abstract model of Maurer [ Mau05]. In this model, the group (or ring)
elements are stored in element wires, and they can be accessed only by the group operation ga tes or the
equality gates.
3

<!-- page 4 -->

The Known-order GGM Lower Bounds Let us begin with the lower bound of folklore for the DL problem
(Theorem 3.3). Let G≃ Zp be the underlying group of prime order p. In this problem, the algorithm A is
given (g, gx) and is asked to ﬁnd x. Suppose that A solves the DL problem with almost certainty with T
group operations. W e also associate a polynomial aX + b to the group element gax+b. It is not hard to argue
that (slightly modiﬁed)A ﬁnds two equal group elements with different polynomials.
W e use this algorithm to compressx∈ [p]. Among T group elements, there are T 2 possibilities for a pair
of equal group elements. In other words, we can encode the dis crete logarithm x in T 2 possible collisions,
and the compression lemma says that log T 2 = 2 log T≥ log p for the high success probability . This implies
that T≥
√
|G| as in the previous proofs.
W e proceed to the MDL problem (Theorem 3.4). Suppose that the algorithmA with T group operations
is given (g, gx1, ..., gxm) and is asked to ﬁnd x = ( x1, ..., xm). As before, we can assume that A ﬁnds m
collisions. W e can encode x using the information of the collisions, which requires
log
({T
2
)
m
)
≈ m log eT 2
2m
bits. T o solve the MDL problem with certainty , it must be larg er than m log|G|, which is the information
that x possesses, implying that T≥√mp. Previously , this bound was ﬁrst proven in [ Yun15] and required
an involved argument regarding the related problem called t he search-by-hyperplane-queries (SHQ). W e
note that we have another simple proof for this lower bound solely based on the linear- algebra reasoning
in Theorem B.1.
The same proof strategy easily extends to the other problems . This includes the gap-DL and gap-
CDH problems ( Theorems 3.5 and 3.6) and the one-more DL problem (OM-DL) ( Theorem 3.7) that was
ﬁrst proven recently [ BFP21] (and was falsely proven in [ CDG18]). W e actually prove the lower bounds
for a much more general problem, where the adversary is asked to ﬁnd the n-more DL solutions than its
queries to the DL oracles; n = 1 corresponds to the OM-DL problem.
The Unknown-order GGM Lower Bounds W e also consider the unknown-order GGM. In Section 4, we
show that the same strategy can prove the lower bounds for the order-ﬁnding in the prime-order group
(Theorem 4.1) that is shown in [ Sut07] and in the RSA group ( Theorem 4.2). W e also prove the hardness of
the root extraction (Theorem 4.3), which was proven in [ DK02], and the repeated squaring ( Theorem 4.4) in
the unknown-order GGM. W e stress that we do not consider the ring operations. Thus, its implications are
limited to the group setting.
W e sketch the proof for the order-ﬁnding problem. In this mod el, the generic algorithm can compute
gx±y for given gx, gy as in the previous GGM, but does not know the order of the under lying group. There-
fore, the corresponding polynomials have a bounded coefﬁci ent after T group operations, so the number
of their prime factors is bounded. It turns out that each equa lity gate can contain T prime divisors. The en-
coding contains the equality gate that speciﬁes the order, a nd the index of its divisors. The length becomes
3 log T to compress log|G|-bit order, giving the T≥|G| 1/3 bound.
The Quantum GGM Lower Bounds W e prove the quantum lower bounds for solving the DL problem
(Theorem 5.2) and variants in the quantum GGM (QGGM). This direction was s uggested in [ HYY23], and
the authors gave the lower bounds for the DL and C/DDH problem s in the QGGM.
The proof strategy is different from the classical lower bou nds. Instead of the one-shot encoding as
in the classical setting, we need an interactive version of t he compression lemma ( Corollary 2.3) proven
in [ HNR18]. This roughly states that if Alice wants to send an n-bit message to Bob, Alice needs to send
n-bit anyway , regardless of the amounts of Bob’s messages to A lice and the number of rounds.
In the QGGM, the algorithm can make group operations coheren tly . Given a generic algorithm, we
construct the interactive protocol between Alice and Bob, w here Alice holds all the group elements, and
Bob holds the other registers. Bob runs the DL algorithm, and whenever it needs to make a quantum
group operation, he sends the relevant registers to Alice; A lice applies the group operations and returns
4

<!-- page 5 -->

the relevant registers to Bob. For simplicity , we assume tha t the indices for the target group elements are
classical. In this setting, Alice sends two bits (or one qubi t) to delegate the group operation Bob requested.
If the algorithm makes Q group operations, the interactive version of the compressi on lemmas proves
2Q≥ log|G|, recovering the previous lower bound; actually , with a better constant than the previous bound
4Q≥ log|G|.
If we allow the indices to be quantum, delegating quantum gro up operations requires more communi-
cation to include them. The lower bound becomes Q = Ω(log|G|/ log ℓ) for the length of indices ℓ. The same
strategy naturally extends to the MDL problem (Theorem 5.3) in the QGGM, proving Q = Ω(m log G/ log ℓ.)
Our proof equally works for the composite order DL problems and holds even regarding the classical pre-
processing. The composite order DL lower bound and MDL lower bound in the QGGM resolves the open
problems asked in [ HYY23], where the matching algorithms were suggested. In fact, ou r lower bound
implies that the number of quantumly accessible indices is a n important measure, while the previous re-
sults only consider the memory-bounded setting, which natu rally bounds the number of quantum indices.
Also, our lower bound implies that the speed-up for the MDL pr oblem beyond Shor in terms of the group
operation complexity requires a large quantum data structu re.
W e also prove the QGGM variant for the order-ﬁnding problems (Theorem 5.4), showing the order-
ﬁnding in the QGGM requires Ω(log|G|) quantum group operations, even with classical preprocessi ng.
The Quantum Generic Ring Model and Lower Bounds W e study a quantum variant of the generic ring
model [AM09, JS13], which we call the quantum generic ring model (QGRM). In thi s model, the algorithm
has oracle access to the ring elements as in the GGM. However, we do not give the explicit value of N to
the algorithm because we aim for the unconditional lower bou nds in the idealized model. If the algorithm
knows N , we cannot rule out the direct use of N , and the proof must be through reductions as in [ AM09].
W e prove that the logarithmic lower bound for the QGRM order ﬁ nding algorithm in the ring isomor-
phic to ZN where N is a product of two safe primes ( Theorem 6.1). The order (or period) ﬁnding problem
is a major subroutine in Shor’s factoring algorithm [ Sho99].
Note that a recent work of Regev [ Reg23] solves the integer factorization with a different method. In
this approach, small integers are extensively used, taking advantage of the fact that small integer arith-
metic operations are faster than large integer operations, giving an improved algorithm with better circuit
complexity .
W e observe that this advantage results in a modiﬁed algorith m that outputs a plain integer with a non-
trivial common factor with N of relatively small size. W e consider the generic algorithm s that output such
an integer to solve the integer factoring that can be compute d without modulus reductions—this must be
done in plain because QGRM algorithms do not know N . W e prove that if the output is relatively small,
the logarithmic ring operation lower bound holds for factor ing (Theorem 6.2). Intriguingly , the output of
Shor’s algorithm with this modiﬁcation is too large to apply this lower bound.
These results give the ﬁrst evidence that the quantum factor ing algorithm needs a logarithmic number
of group operations. Our result extends to the straight-lin e classical preprocessing that reﬂects the real
world better.
Beyond GGMs: Index Calculus Finally , we study the idealized group model, called the smoo th GGM,
beyond the generic groups, encompassing the index calculus method. This model provides the abstraction
for the notion of smooth elements and efﬁcient factoring for the smooth integers.
W e prove that the DL algorithm must make exp
(
C
√
log|G| log log|G|
)
group operations for some con-
stant C > 0 in the SGGM ( Theorem 7.1), giving some evidence that going beyond this bound require s a
new idea, as the ones in the number ﬁeld sieves.
W e do not claim this lower bound provides new insights or stro ng evidence for the index calculus. W e
believe that the ideas used in the proof for the SGGM lower bou nd must have been observed and used
in the development of the index calculus, especially for opt imization. Still, our result shows that a proper
5

<!-- page 6 -->

abstraction of the generic approaches, where only limited o perations are used, can indeed prove that these
approaches cannot go further; asking for new ideas.
Notations. For a positive integer N , a ﬁnite cyclic group of order N is denoted by ZN , identiﬁed by
{0, 1, ..., N− 1} with the natural group operation, and [N ] :={1, ..., N}.
2 Compression Lemmas
This section presents our main lemmas, which are usually cal led the compression lemma. The classical
compression lemma is stated as follows.
Lemma 2.1. LetM, R be ﬁnite sets. Let Encode :M× R→ {0, 1}m and Decode :{0, 1}m× R→ Mbe
deterministic algorithms. For ǫ∈ (0, 1], if
Pr
r←R,x←M
[Decode(Encode(x, r), r) = x]≥ ǫ,
then we have m≥ log|M| + log ǫ.
This is a direct corollary of the following quantum interact ive version of the compression lemma. Pre-
cisely , the classical one-way protocol with the preshared entanglement∑
r∈R|r, r⟩ corresponds to the above
lemma.
Lemma 2.2 ([HNR18, Theorem 1.2]) . Consider an interactive protocol between Alice and Bob, who share an arbi-
trarily entangled state and communicate through classical channels. Alice wants to send a uniformly random element
in a ﬁnite set M to Bob. Suppose that the probability that Bob correctly reco vers x with probability ǫ∈ (0, 1], and
Alice sends m bits to Bob total over all rounds. Then it holds that m≥ log|M| + log ǫ, regardless of the number of
bits sent by Bob to Alice.
In general, if Alice sends a classical string in [Mi] to Bob as the i-th round message for i∈ [k] where k is the
maximum number of rounds, then it holds that
log
( k∏
i=1
Mi
)
≥ log|M| + log ǫ.
The original theorem in [ HNR18, Theorem 1.2] mainly concerns the case of M ={0, 1}n and the bit-
strings as messages. This generalization is straightforwa rd.1 The quantum communication version can be
derived using quantum teleportation (See also [ NS06, Theorem 2]).
Corollary 2.3. In the same setting as the above lemma, if Alice and Bob can com municate through quantum chan-
nels, the bounds become
m≥ log|M| + log ǫ
2 , and log
( k∏
i=1
Mi
)
≥ log|M| + log ǫ
2 ,
respectively, where Alice sends one qudit of dimension Mi in the i-th round. When Alice additionally sends c classical
bits, the bounds become
2m + c≥ log|M| + log ǫ, and 2 log
( k∏
i=1
Mi
)
+ c≥ log|M| + log ǫ.
W e give some remarks. The above lemmas consider the average- case probability for input x, while the
previous (both classical and quantum) versions [ GT00, DTT10, NS06] consider the case that the success
probability is at least ǫ for any input x. This caused a signiﬁcant loss in the resulting security in t he ﬁrst
AI-QROM bound [HXY19], or call for the random-self-reducibility in the preprocessing DL security [CK18].
Thanks to this average-case feature, we exclude the random- self-reducibility in the proofs.
1Roughly , the choice ofM = {0, 1}n is only used at the end of the proof where the probability that input to Alice is x is 1/2n, and
modifying it to 1/|M| sufﬁces to prove our theorem. The non-bit-string is slightl y involved, but changing the appropriate set sufﬁces.
6

<!-- page 7 -->

3 Lower Bounds in the Classical Generic Group Model
3.1 Generic Group Model
W e ﬁrst deﬁne the generic group model (GGM) of Maurer [Mau05], also known as the type-safe model [Zha22].
Let N be the known prime order 2 of our interested ﬁnite cyclic groupG∼= ZN with a generator g. A generic
algorithmA in this model is given by a circuit with the following feature s:
• There are two types of wires: bit wires and (group) element w ires. Bit wires take a bit in {0, 1},
whereas element wires take an element in ZN∪{⊥} . For an element wire containing x, we write gx
to denote this wire to distinguish it from a bit string.
• There are bit gates that map bits to bits, which cannot take e lement wires as input.
• There are three special gates called element gates that can access the element wires as follows:
Labeling Gate. It takes⌈log2 N⌉ bit wires and interprets them as an element in x∈ ZN as input, and
outputs an element wire gx. If there is no corresponding element x∈ ZN to the input wires, it
outputs an element wire containing⊥.
Group Operation Gate. It takes two element wires containing gx, gy and a single bit wire containing
b as input. If both gx, gy are not⊥, it outputs an element wire containing gx+by.3 Otherwise, it
outputs an element wire containing⊥.
Equality Gate. It takes two element wires as input. If both wires contain the same element gx⁄=⊥, it
outputs a bit wire containing 1. In all other cases including ⊥ inputs, the output is 0.
An algorithmA in this model is called a GGM algorithm and is usually denoted byAG. The cost metric
for the algorithms, denoted by the group operation complexity , counts the number of labeling and group
operation gates used in the circuit, and all other gates are c onsidered free.
W e assume that the element gates have some orders so they can b e applied sequentially (along with
required bit gates). 4 W e also assume that GGM algorithms never make two equality ga tes with the same
input wires. This ensures that for a GGM algorithm taking m element wires as input and with the group
operation complexity T , the number of group operation gates T , the number of equality gates less than or
equal to
{m+T
2
)
. W e further assume that the description of the GGM algorithm contains the order of the
element gates so that they can be applied in order (ignoring b it gates).
Remark 1 (Relations to the other generic group models.) . A different model for generic group algorithms is
suggested by Shoup [Sho97]. The results for known-order GGM algorithms in this paper c an be extended to
Shoup’s generic group model. This is because this paper focu ses on the cryptographic assumptions that can
be described as a single-stage game, where the generic equiv alence between two models is known [ Zha22].
W e place the detailed theorem with the proof in Appendix C for completeness. W e note that our proof can
be extended to the Shoup-style GGM directly , as shown in Appendix C.1. However, this makes the proof
involved, and the main body focuses on the Maurer-style mode l for a simpler exposition.
3.1.1 V ariations: Maintaining Polynomials
Before proceeding to the classical lower bounds in the gener ic group model, we give a variation of GGM
algorithms, which maintains the polynomials representing the elements and information that it achieved.
W e assume that the input to the GGM algorithm is speciﬁed by po lynomials P1, ..., Pm ∈ ZN [X1, ..., Xt]
for some formal variables X1, ..., Xt corresponding to the hidden values. For example, in the disc rete log-
arithm problem, X1 speciﬁes the problem instance gx, and the input is speciﬁed by P1 = 1 , P2 = X1. W e
2W e can extend to the composite-order setting easily .
3One may deﬁne this gate differently , e.g., (gx, gy, a, b) ↦→gax+by, but it does not make any change to our result.
4Given the circuit, such an order can be found using the breadt h-ﬁrst search.
7

<!-- page 8 -->

occasionally identify a polynomial P = a1X1 + ... + atXt + b as a vector (b, a1, ..., at)∈ Zt+1
N (recall N is
prime, which makes Zt+1
N a vector space.) especially when we discuss the linear algeb ra notions.
Given the polynomial representations of inputs, we maintai n a listP of a pair of the element wire and
polynomial called the polynomial list and a counter c, and it behaves as follows.
• As an initialization, set P as an empty list. For each input element wire w containing a group element
corresponding Pi for i∈ [m], store (w, Pi) in the i-th row ofP. Set c← m.
• For a labeling gate in the circuit of A with input representing a∈ ZN and output element wire w, set
c← c + 1, and store (w, Pc := a) in the c-th row ofP.
• For a group operation gate with two element wires w1, w2 and a bit wire containing b as input and
output wire w appears, ﬁnd i, j≤ c such that i, j-th rows of P are w1, w2. Set c← c + 1, compute
Pc := Pi + (−1)bPj, and store (w, Pc) in the c-th row ofP.
The equality gates are dealt with differently , by maintaining the zero setsZ that is initialized as an empty
set. For an equality gate eq with two input element wires w1, w2 and output 1 (i.e., they are equal), we ﬁnd
i, j-th rows ofP containing w1, w2 and call g by collision; since no two equality gates have the same inputs,
we also call (i, j) as a collision ambiguously . W e process each collision as fol lows. W e do nothing for the
equality gates outputting 0.
• If Pi = Pj as a polynomial over ZN , then the collision is called trivial, and do nothing.
• If an equality query ﬁnds a nontrivial collision (i, j), then write |Z| = z andZ ={Qi}i∈[z], check if
there exists a = (a1, ..., az)∈ Zz
N such that
Pi− Pj = a1Q1 + ... + azQz (1)
holds as a polynomial. If there is no such a, updatesZ←Z∪{ Pi− Pj}. W e call the collision (i, j)
informative, and otherwise predictable.
Note that the notion of informative collisions is similar to the useful queries in [ Yun15] in the search-by-
hyperplane problem, but our deﬁnition is purely linear-alg ebraic and direct. It just says that the new infor-
mative collision must not be included in the span of the previ ous collisions.
The informative collisions are sufﬁcient for describing th e behavior of the GGM algorithm, as shown in
the following lemma, proved in Appendix A.1.
Lemma 3.1. LetA be a GGM algorithm. Given a description of the circuit for A and the zero set Z for the given
input, the polynomial list of A right before its termination can be computed without using t he element gates, i.e.,
computed by a Boolean circuit.
The following auxiliary lemma is a generalization of the Sch wartz-Zippel lemma, which could be of
independent interest. It gives another alternative proof f or the MDL lower bound presented in Appendix B
with its proof.
Lemma 3.2. Suppose the hidden variables x1, ..., xt are uniform in ZN , and the group elements during the execution
of the algorithm always correspond to the linear polynomial s in ZN [X1, ..., Xt]. For any equality gate for wi, wj, the
probability that it induces an informative collision is at m ost 1/N.
3.2 The Discrete Logarithm Problem and Friends
W e ﬁrst prove the following well-known generic lower bound f or the DL problem.
Problem 1. A discrete logarithm (DL) problem for a cyclic group G of order p with a generator g asks to
ﬁnd x given (g, gx) for uniformly random x∈{ 0, ..., p− 1}. An m-multiple DL ( m-MDL) problem asks to
ﬁnd x = ( x1, ..., xm) given (g, gx1, ..., gxm) for uniformly random x∈{ 0, ..., p− 1}m. In the (Q)GGM, the
group is ﬁxed a priori, and the inputs are stored in the elemen t registers.
8

<!-- page 9 -->

Theorem 3.3. LetG be a cyclic group of prime order. Let ADL be a DL algorithm in the GGM having at most T
group operation gates, then the following holds:
Pr
ADL,x
[
AG
DL(g, gx)→ x
]
= O
( T 2
|G|
)
.
Proof. Let p = |G| and ǫ be the success probability of ADL. W e make the following modiﬁcations: For
z←AG
DL(g, gx), we let the algorithm make the labeling gate on input z and apply the equality gate on input
(gz, gx) to ﬁnd a collision at the end, so that A always ﬁnds an informative collision with probability at
least ǫ. Including this procedure, we assume that the algorithm mak es C = T + 1 group operations. The
algorithmADL may be randomized by taking a random string r as a seed.
Now , we construct a pair of encoding and decoding protocols f orM = [ p] and a set R of seed r. For
x∈ [p], the protocols are deﬁned as follows.
Encode(x, r): It runsAG
DL(g, gx) with randomness r and outputs the equality gate c with input (i, j) that is
the lexicographically ﬁrst informative collision, i.e., f or any other informative collision (i′, j′), it holds
that i < i′, or i = i′ and j < j′. If there is no informative collision, it outputs a special s ymbol c =⊥.
Decode(c, r): If c =⊥, it outputs a random value in [p]. Otherwise, it constructs a sub-circuitA′
DL ofADL by
cutting out the gates after the equality gate c corresponding to the ﬁrst informative collision (i, j). W e
associate the group element gax+b with a polynomial aX + b∈ Zp[X]. By Lemma 3.1, the correspond-
ing polynomials Pi = aiX + bi and Pj = ajX + bj can be computed without using the element wires.
Then it returns z =−(bi− bj)/(ai− aj) mod p as an output.
W e prove this protocol is correct with a probability of at lea st ǫ, or wheneverADL ﬁnds x. In this case,
the encoder ﬁnds a collision c with input (i, j), which is informative only when
(aix + bi = ajx + bj mod p)∧ ((ai, bi)⁄= (aj , bj)) ⇐⇒ x =− bi− bj
ai− aj
mod p.
Thus, given c⁄=⊥, the decoder always ﬁnds the correct answer x, i.e., the protocol succeeds with probability
at least ǫ.
Now we compute the encoding length of the protocol. Since ADL obtains at most C + 2 group elements
including inputs, the encoding spaceC has the cardinality
{C+2
2
)
+ 1≤ (T + 3)2/2. By Lemma 2.1, we have
the following inequality
log ǫ + log|G|≤ log|C|≤ log
( (T + 3)2
2
)
=⇒ ǫ = O
( T 2
|G|
)
which concludes the proof.
It can easily be extended to the multiple-instance DL proble m with small adjustments. For a positive
integer m, we write gx to denote (gx1, ..., gxm).
Theorem 3.4. LetG be a cyclic group of prime order. Let Am-MDL be an m-MDL algorithm in the GGM having at
most T group operation gates. It holds that:
Pr
Am-MDL,x
[
AG
m-MDL(g, gx)→ x
]
= O
(( e(T + 2m + 1)2
2m|G|
)m)
.
Proof. Let p =|G| and ǫ be the success probability of Am-MDL. With a similar modiﬁcation, we assume that
Am-MDL ﬁnds at least m informative collisions with probability at least ǫ using C = T + m group operation
complexity . W e associate a group element ga1x1+...+amxm+b with a polynomial a1X1 + ... + amXm + b∈
Zp[X1, ..., Xm]. W e additionally need the following result from linear algebra.
9

<!-- page 10 -->

Fact 1. Given m informative collisions, there is a polynomial time algorit hm to ﬁnd the unique assignments
(X1, ..., Xm) = ( x1, ..., xm) making the given collisions informative.
The proof can be found in Appendix A.1.
Am-MDL may be randomized using a random seed r. W e construct encoding and decoding protocols for
M = [p]m and a set R of the seed r. For input x∈ Zm
p , the protocols are deﬁned as follows.
Encode(x, r): It runsAG
m-MDL(g, gx) with randomness r and collects the lexicographically ﬁrst m informative
collision gates ck with input (ik, jk) for k ∈ [m]. If m informative collisions are found during the
execution, it outputs c = (c1, ..., cm). Otherwise, it outputs a symbol⊥.
Decode(c, r): If c =⊥, it outputs a random value in [p]m. Otherwise, it parses c = (c1, ..., cm) and constructs
a sub-circuit A′
m-MDL ofAm-MDL by cutting out the gates after the m-th informative collision gate
(corresponding to cm). By Lemma 3.1, it recovers the polynomial list. Using c and Fact 1, it ﬁnds and
outputs the assignment z = (z1, ..., zm) of (X1, ..., Xm).
It is obvious that ifAm-MDL ﬁnds x = ( x1, ..., xm) then the decoder correctly recovers x, which happens
with probability at least ǫ. W e focus on the encoding size below . Let B =
{C+m+1
2
)
be the upper bound of
the number of equality queries. The bit-length for describi ng the m informative collision (or⊥) is less than
log
({B
m
)
+ 1
)
, which is bounded by
log
(B + 1
m
)
≤ m log
( e(B + 1)
m
)
≤ m log
( e(T + 2m + 1)2
2m
)
,
where we use B + 1≤ (C+m+1)2
2 ≤ (T +2m+1)2
2 . By Lemma 2.1, we have
log ǫ + m log|G|≤ log|C|≤ m log
( e(T + 2m + 1)2
2m
)
which can be rewritten as follows
ǫ = O
(( e(T + 2m + 1)2
2m|G|
)m)
,
as we desired.
3.3 Oracle Problems in the GGM
This section extends the lower bounds relative to the oracle . W e ﬁrst consider the following problems.
Problem 2. In the gap DL (gap-DL) problem, the adversary is given (g, gx) as input and is asked to ﬁnd
x, having access to the decisional Difﬁe-Hellman (DDH) oracl e: ODDH : ( gx, gy, gz)↦→δxy,z . In the gap
computational Difﬁe-Hellman (gap-CDH) problem, the adversary is given (g, gx, gy) and is asked to output
gxy with the DDH oracle access.
Theorem 3.5. LetG be a cyclic group. Let AGap-DL be a gap-DL algorithm in the GGM having at most T group
operation gates and making TDDH queries to the DDH oracle, then the following holds:
Pr
AGap-DL,x
[
AG,ODDH
Gap-DL (g, gx)→ x
]
= O
( T 2 + TDDH
|G|
)
.
Proof sketch. W e extend the notion of collisions to include the DDH oracle a nswers that output 1. By a
similar modiﬁcation as the previous section, we can assume that the algorithm ﬁnds at least one informative
collision. If it is an answer from the DDH oracle, then it spec iﬁes the equation (aX + b)(cX + d) = eX + f
for some a, b, c, d, e, f. It has at most two solutions; thus, the encoding includes on e more bit to specify the
correct solution. The number of collisions is bounded by
{T +3
2
)
+ TDDH. The other parts of the proof are
identical.
10

<!-- page 11 -->

Theorem 3.6. LetG be a cyclic group. Let AGap-CDH be a gap-CDH algorithm in the GGM having at most T group
operation gates and making TDDH queries to the DDH oracle, then the following holds:
Pr
AGap-CDH,x
[
AG,ODDH
Gap-CDH(g, gx, gy)→ gxy
]
= O
( T 2 + TDDH
|G|
)
.
The proof is almost identical and placed in Appendix A.1.
Problem 3. In the one-more-DL ( OM-DL) problem, the adversary is given access to the challenge ora cle
OChal that outputs gxi for an unknown xi and to the DL oracle ODL : gx↦→x. The number of DL oracle
queries q must be less than the number of challenge queries t. The adversary aims to ﬁnd all answers to the
challenges. More generally , in the n-out-of-m-more-DL ((n, m)-M-DL) problem, it must hold that t = q + m,
and the adversary needs to ﬁnd q + n solutions to the challenges among q + m challenges.
Theorem 3.7. LetG be a cyclic group. LetA(m,n)-M-DL be an n-out-of-m-more-DL algorithm in the GGM having at
most T group operation gates and making q queries to the DL oracle, then the following holds:
Pr
A(n,m)-M-DL,x
[
AG,OChal,ODL
(n,m)-M-DL(g) solves (n, m)-M-DL
]
= O
(( e(T + m + n + 1)2
|G|
)n)
.
In particular, the advantage against OM-DL is O
(
T 2
|G|
)
.
Proof. Suppose that the t = m + q challenges are gx1, ..., gxt. W e construct an encoding for x = ( x1, ..., xt).
W e assume that the algorithm is deterministic. Regarding in formative collisions, we include the DL oracle
answers as the collision. If the DL oracle outputs z for input gP , we regard P− z as a collision. Since the
algorithm ﬁnds n + q solutions, it must ﬁnd n + q informative collisions (including the DL oracle outputs).
W e assume that the algorithm never queries to the DL oracle that the answer induces a trivial collision. This
means there are n informative collisions that are not from the DL oracle queri es.
W e need the following simple fact from linear algebra.
Fact 2. Given a linear independent linear equations over b variables for a < b . There are b− a variables
such that the linear equations are still independent after ﬁ xing them to some values.
The procedures are as follows.
Encode(x): It runs AG,OChal,ODL
m-M-DL (g) and collects the lexicographically ﬁrst t informative collisions, which
could be the equality gate or the DL oracle answer. If n + q informative collisions are found dur-
ing the execution, it outputs c = ( c1, ..., cn) that denote the informative equality gates and the DL
oracle answers z = ( z1, ..., zq). By Fact 2, there are m− n xi’s such that revealing them does not hurt
the linear independence of the informative collisions. Fin ally , thosexi’s, denoted by w become a part
of the encoding. Otherwise, it outputs a symbol ⊥.
Decode(c, z, w): It runsAG,OChal,ODL
m-M-DL (g) to recover n + q informative collisions. Given these equations, the
decoder can recognize the indices for w. It recovers w, and plugs them in the informative collisions.
The informative collisions become n + q linear equations over n + q variables, so that it can recover x.
The length of the encoding is bounded by
log
({T +m+n
2
)
n
)
+ q log|G| + (m− n) log|G| + O(1)
which must be larger than (m + q) log|G| + log ǫ for the success probability ǫ by Lemma 2.1. This gives
n log
( e(T + 2m + 1)2
2n
)
≥ n log|G| + log ǫ
11

<!-- page 12 -->

which implies
ǫ = O
(( e(T + m + n + 1)2
|G|
)n)
,
concluding the proof.
Remark 2. Extending the results to high-degree variants like m-CDH problems is not trivial. W e believe
with some algebraic geometry reasoning like Bézout theorem , as in [ AGK20], the high-degree variants can
be proven in essentially the same way .
4 Lower Bounds in the Unknown-order GGM
W e extend the generic group to the unknown-order setting. As the order is unknown, we should consider
the distribution of the order.
LetG be a cyclic group of order N , where the distribution of N will be speciﬁed later. W e assume that
N is unknown to the algorithm except for its bit length. The oth er interface of the generic algorithms is
identical to the (known-order) GGM. In particular, the assu mption that the group operation only allows to
compute (gx, gy)↦→gx+y is important. 5 Note that the algorithm cannot extract any information from the
element wire containing⊥; for example, the equality gate involving ⊥ always outputs 0.
Remark 3. W e found that the known equivalence proof between the generi c group models does not ex-
tend to the unknown-order group setting. Therefore, we incl ude the random-representation GGM proof
at Appendix C.1.
Polynomial Representations As in the known-order GGM, we give the polynomial representa tions for
each group element. However, as the group order is unknown, we choose the polynomials from Z[X1, ..., Xt]
without modulus for the formal variables X1, ..., Xt corresponding to the hidden values. In particular, if the
algorithm takes no input, the representations could be in ju st Z without formal variables.
W e extend the notion of informative collisions appropriate ly . W e maintain the zero setZ and process
each collision (i, j) with inputs corresponding to polynomials Pi, Pj (i.e., the equality gate outputting 1) as
follows:
• If Pi = Pj as a polynomial, then the collision is called trivial, and do nothing.
• If an equality query ﬁnds a nontrivial collision (i, j), then check if Pi− Pj is included in Z-span ofZ;
recall the we only checked ZN -span in the known-order case. If it is not true, updateZ←Z∪{ Pi−Pj}.
W e call the collision(i, j) informative, and otherwise predictable.
4.1 Order-ﬁnding in the Unknown-order GGM
W e consider the following problem.
Problem 4. LetD(n)
prime be a uniform distribution over the set of n-bit primes. An order-ﬁnding problem over
D(n)
prime in the GGM is deﬁned as follows. First, a random N is sampled from D(n)
prime. The adversary in the
unknown-order GGM for the groupGN of order N is asked to output N . A product-order-ﬁnding problem
overD(n)
prime is similarly deﬁned, but the two distinct primes p, q are sampled and N := pq.
This problem is studied in [ Sut07] in detail. In particular, the generic order-ﬁnding algori thm with
the O(
√
N/ log log N ) group operation complexity suggested in [ Sut07, Section 4], and the lower bound of
Ω(N 1/3) (for the prime-order case) is proven in the same thesis. W e re prove this bound using our method.
5This was also used in the related works [ DK02, Sut07] in the unknown-order GGM.
12

<!-- page 13 -->

Theorem 4.1. LetAord be an order-ﬁnding algorithm over D(n)
prime in the GGM with the group operation complexity
T . It holds that
Pr
Aord,N
[
AGN
ord (g)→ N
]
= O
( T 3
2n
)
.
In particular, any generic order-ﬁnding algorithm with a co nstant success probability must make Ω
{
N 1/3)
group
operations.
Proof. Let ǫ be the success probability ofAord. For simplicity , we assume thatAord is deterministic.
W e consider the integer representations corresponding to the elements ofAord because of the unknown
order and no indeterminate value. In this case, an informati ve collision (i, j) must specify two integers
xi, xj such that xi− xj is a multiple of the order N . The integer x appearing in this list must satisfy
|x|≤ 2T N
because a group operation only increases the number twice. T his gives that the number of n-bit primes
divisors of x− y for some x, y appearing in the list is bounded by
log2n (2T N ) = O
( T
log N
)
.
W e consider the following modiﬁcation: If Aord outputs z, we let the algorithm make the labeling gate
on inputs z, 0 and apply the equality gate on input (g0, gz) to ﬁnd a collision at the end with probability at
least ǫ.
Now , we construct the following encoding-decoding pair.
Encode(N ): It runsAGN
ord (g) and computes the equality gate c with input (i, j) that is the lexicographically
ﬁrst informative collision. Let xi, xj be the corresponding integer representations. It factoriz es xi− xj
and lets p1, ..., pK be the n-bit prime divisors. It outputs (c, ℓ) where pℓ = N if exists. Otherwise, it
outputs a special symbol c =⊥.
Decode(c, ℓ): If c =⊥, it outputs a random sample from D(n)
prime. Otherwise, it recovers xi, xj , computes and
outputs the ℓ-th prime factor N′.
The correctness is analogous. The size of the encoding is log
{T
2
)
+ log( K) + O(1), and we have K =
O(T /log N ). This gives
log
(T
2
)
+ log(K) + O(1)≥ log
( 2n
n
)
+ O(1) + log ǫ =⇒ ǫ = O
( T 3
N
)
applying Lemma 2.1 and 2n−1≤ N≤ 2n.
W e can prove the analogous result for the product of two prime s. The proof is essentially identical,
except that we need to encode two prime factors using two info rmative collisions.
Theorem 4.2. LetAord be a product-order-ﬁnding algorithm over D(n)
prime in the GGM with the group operation
complexity T . It holds that
Pr
Aord,p,q
[
AGpq
ord (g)→ pq
]
= O
( T 4
22n
)
.
In particular, any generic order-ﬁnding algorithm with a co nstant success probability must make Ω
{
N 1/4)
group
operations for N = pq.
13

<!-- page 14 -->

4.2 Root Extraction and Repeated Squaring Problems
W e prove similar lower bounds for the (strong) root extracti on and the repeated squaring in the unknown-
order GGM.
Theorem 4.3. LetA be an algorithm in the GGM with the group operation complexit y T . Suppose that N is sampled
fromD(n)
prime. It holds that
Pr
A,N,x
[
gey = gx :AGN (g, gx)→ (e, gy)
]
= O
( T 3
2n
)
.
Proof sketch. If there is an informative collision when running A, we can apply the same encoding as in the
previous section. W e show that if the algorithm ﬁnds the root gy, then it ﬁnds an informative collision.
Suppose that there is no informative collision during the ex ecution for given input (g, gx). Then, the
polynomial corresponding to gy must be Y = aX + b∈ Z[X]. The correctness implies that eax + eb =
x mod N. T o do so, either N|ea− 1, N|eb or x = eb/(ea− 1) mod N must hold. The ﬁrst case implies that
N|b (otherwise ea− 1 is not divided by N ), and since|b||≤ 2T N, this event only happens with probability
at most O(T n/2n). The second case holds with probability 1/N. In other words, except this probability , the
algorithm ﬁnds an informative collision.
Theorem 4.4. LetA be an algorithm in the GGM with the group operation complexit y T . Suppose that N is sampled
fromD(n)
prime. Let t > T be a positive integer. It holds that
Pr
A,N,x
[
AGN (g)→ g2t]
= O
( (T + t)3
2n
)
.
Proof sketch. If the algorithmA outputs h, we can compute g2t
using t group operations and check if h =
g2t
. Also, the integer representation corresponding to h must be smaller than 2T , thus it should be the
informative collision. Using this, we can construct an enco ding algorithm for N as in the previous section,
proving the desired result.
5 Lower Bounds in the Quantum GGM
5.1 Quantum Generic Group Models
5.1.1 Basic Quantum Generic Group Model
W e deﬁne the quantum generic group model (QGGM) extending th e model in Section 3.1, following the
formalization in [HYY23]. LetG be a cyclic group of order N with a generator g. A quantum generic group
algorithmA works similarly to a generic group algorithm but is deﬁned on the registers holding qubits or
superpositions of elements.
W e ﬁrst consider a rudimentary model, denoted by the basic QGGM, where group operations only work
on two a priori ﬁxed registers. As we look for the logarithmic lower bounds, we do not allow the quantum
labeling gate and give a quantum inversion gate as a unit. An a lgorithm in the basic QGGM is deﬁned as
follows.
• There are two registers: qubit and element registers holdi ng superpositions of some information.
Qubit registers take a set of bits{0, 1} as the computational basis. In contrast, element registers take a
set of elements x∈G∪{⊥} as the computational basis, which is denoted by gx; sometimes⊥ is also
written in this form though there is no corresponding x. The algorithm arbitrarily appends a new
element register initialized by|g⟩.
• There are (arbitrary) quantum gates that map qubits to qubi ts, which cannot take element registers as
input.
14

<!-- page 15 -->

• There are two special gates called element gates that can access the element wires as follows:
Group Operation Gate. It takes two element registers X, Y and a single qubit register B and applies
the unitary UG.op that works on the computational basis as follows:
UG.op :
{
|b⟩B|gx, gy⟩X,Y↦→|b⟩B
⏐⏐gx+by, gy⟩
X,Y if gx, gy⁄=⊥,
|b⟩B|gx, gy⟩X,Y↦→|b⟩B|gx, gy⟩X,Y otherwise.
(2)
Inverse-Operation Gate. It takes two element registers X, Y and a single qubit register B and applies
the unitary UG.inv that works on the computational basis as follows:
UG.inv :
{
|b⟩B|gx, gy⟩X,Y↦→|b⟩B
⏐⏐gx−by, gy⟩
X,Y if gx, gy⁄=⊥,
|b⟩B|gx, gy⟩X,Y↦→|b⟩B|gx, gy⟩X,Y otherwise.
Equality Gate. It takes two element registers X, Y and a single qubit register B. It then applies the
unitary operation UG.eq that works on the computational basis as follows:
UG.eq :
{
|b⟩B|gx, gy⟩X,Y↦→|b⊕ δx,y⟩B|gx, gy⟩X,Y if gx, gy⁄=⊥,
|b⟩B|gx, gy⟩X,Y↦→|b⟩B|gx, gy⟩X,Y otherwise,
where δx,y = 1 if x = y and 0 otherwise.
• W e allow the intermediate measurements for registers. Whe n we apply the measurements on all of
B, X, Y right before applying the element gates, we call them classical. An element gate that is not
classical is called quantum. For simplicity , we allow the cl assical labeling gate that does not much
affect the result.
Classical Labeling Gate. It takes⌈log2 N⌉ qubit registers, measures it, and interprets them as an el-
ement in x∈ ZN . It appends a new element register holding |gx⟩. If there is no corresponding
element x∈ ZN to the input wires, it outputs an element wire containing |⊥⟩.
A QGGM algorithm denotes an algorithm A in this model and is occasionally written by A|G⟩. As in the
classical GGM, we assume the element gates have some order to be applied sequentially with the relevant
qubit gates.
The formal complexity measure of the generic algorithms is d escribed in the next subsection. Roughly ,
we count the number of quantum element gates including the equality gates as the cost metric. The main
reason is that while the equality check between two classica l data is essentially free, e.g., using hash tables,
the equality check between two element registers that store superpositions is not freely done. W e also note
that Shor’s algorithm does not use any equality query .
5.1.2 QGGM with Coherent Indices
Now , we consider more general operations that can coherentl y access the indices of registers. Let t, w be
positive integers. W e deﬁne the (t, w)-QGGM similarly to the basic QGGM, but it also has qudit registers of
dimension t and w, and the element gates are deﬁned as follows.
• There are two special gates called element gates that can access the element wires as follows. The
unspeciﬁed registers are unchanged by the operations.
Group Operation Gate. It takes three registers B, T, W and t+w element registers X1, ..., Xt, Y1, ..., Yw
and applies the unitary U (t,w)
G.op that works on the computational basis as follows:
U (t,w)
G.op :|b, i, j⟩BTW|gxi, gyj⟩Xi,Yj↦→|b, i, j⟩BTW
⏐⏐gxi+byj , gyj
⟩
Xi,Yj
for i∈ [t], j∈ [w], gxi , gyj⁄=⊥ and Xi⁄= Yj, otherwise do nothing.
15

<!-- page 16 -->

Inverse-Operation Gate. It takes three registers B, T, W and t+w registers X1, ..., Xt, Y1, ..., Yw and
applies the unitary U (t,w)
G.inv that works on the computational basis as follows:
U (t,w)
G.inv :|b, i, j⟩BTW|gxi, gyj⟩Xi,Yj↦→|b, i, j⟩BTW
⏐⏐gxi−byj , gyj
⟩
Xi,Yj
for i∈ [t], j∈ [w], gxi , gyj⁄=⊥ and Xi⁄= Yj, otherwise do nothing.
Equality Gate. It takes three registers B, T, W and t + w element registers X1, ..., Xt, Y1, ..., Yw and
applies the unitary U (t,w)
G.eq that works on the computational basis as follows:
U (t,w)
G.eq :|b, i, j⟩BTW|gxi, gyj⟩Xi,Yj↦→
⏐⏐b⊕ δxiyj , i, j
⟩
BTW|gxi, gyj⟩Xi,Yj
for i∈ [t], j∈ [w], gxi, gyj⁄=⊥ and Xi⁄= Yj, and do nothing other cases, where δx,y = 1 if x = y
and 0 otherwise.
Note that the (1, 1)-QGGM is identical to the basic QGGM. W e remark that allowing coherent access to
indices is relevant to practice. Coherent access to indices means the corresponding unitary operation should
be large and implemented differently from the above gates. F urthermore, setting t > 1 implies that the
quantum storage should store t group elements, requiring a large quantum memory . Allowing w > 1 was
studied in [ Gid19], and the estimation in [ GE21] mainly used t = 1 and w = 5.
When we say the QGGM, the choice of (t, w) is unimportant in that context.
Remark 4. W e did not explicitly state that the element registers are di fferent. This potentially allows the
group operations between the registers Xi, Xj.
5.1.3 Quantum Generic Group Algorithm with Classical Prepr ocessing
This paper considers the generic algorithms for the discret e logarithm that may perform classical generic
computation before running the quantum parts. Formally , a g eneric (C, Q)-algorithmA in the QGGM
decomposes into two generic algorithmsAc,Aq as follows.
1. Given the problem instance, Ac consists of at most C classical group operation gates and arbitrar-
ily many classical equality gates. It may have arbitrarily m any qubit gates. At the end, it gives all
registers toAq.
2. Given the registers from Ac as input, it applies at most Q quantum element gates along with arbi-
trarily many qubit gates. It measures the output registers a nd returns the measurement result as the
outcome.
The following lemma shows the classical equality gates can b e safely removed. The proof can be found
in Appendix A.2.
Lemma 5.1. LetG be a cyclic group of order N , and p the smallest prime divisor of N . For any (C, 0)-algorithmAc
in the (arbitrary) QGGM forG, there is another (C, 0)-algorithmA′
c without equality gates such that
Pr
x←[N ]m
[Ac|0n, g, gx1, ..., gxm⟩ =A′
c|0n, g, gx1, ..., gxm⟩]≥ 1− (C + m + 1)2
2p .
In particular, for generic (C, Q)-algorithmsA = (Ac,Aq) andA′ = (A′
c,Aq) forA′
c deﬁned above, the outputs of
two algorithms are identical with probability at least 1− (C+m+1)2
2p .
16

<!-- page 17 -->

5.2 Discrete Logarithms in the QGGM
The basic QGGM. W e begin with the DL lower bound in the basic QGGM.
Theorem 5.2. LetG be a cyclic group of order N with a generator g. Suppose that the smallest prime divisor of N is
p. LetADL be a (C, Q)-algorithm in the basic QGGM, then the following holds:
Pr
ADL,x←[N ]
[
A|G⟩
DL (g, gx)→ x
]
≤ (C + 2)2
2p + 22Q
N .
Proof. Let ǫ be the success probability of ADL. Decompose ADL = (Ac,Aq) as described in the previous
section. By Lemma 5.1, it sufﬁces to consider A′
DL = (A′
c,Aq) whereA′
c does not have any equality gates,
whose output is identical to ADL = (Ac,Aq) with probability 1− (C + 2)2/2p. In other words, A′
DL solves
the DL problem with a probability of at least
ǫ′≥ ǫ− (C + 2)2
2p . (3)
Similarly to the classical case, we will construct an interactive compression protocol and apply Corollary 2.3.
In the protocol, Alice holds group registers and applies ele ment gates. Bob only holds the qubit registers
and delegates all group-related operations to Alice.
W e introduce the simple sub-protocols between Alice and Bob , showing that Alice sends one qubit
during one element gate delegation.
Subprotocol Delegate.Gop for group operation gates. The initial states are
∑
b
βb|b⟩B⊗
∑
z,w
αz,w|gz, gw⟩XY (4)
where Alice holds the registers X, Y and Bob holds B.
1. Bob sends his register B to Alice. Alice applies quantum group operation gates on BXY to obtain
∑
b
βb|b⟩B⊗
∑
z,w
αz,w
⏐⏐gz+bw, gw⟩
XY . (5)
2. Alice returns the register B to Bob.
In this protocol, Alice only sent one qubit and the group operation gate is applied as a result (compareEquations (4)
and (5) and Equation (2)).
Subprotocol Delegate.Ginv and Delegate.Geq. These are almost the same as the protocol Delegate.Gop. The
difference is as follows.
1. Alice applies the quantum inversion-operation gate or eq uality gate instead of the group operation
gate.
Now , we return to the proof. W e construct the following inter active protocol between Alice and Bob,
where Alice selects x∈ [N ] and tries to send x using this protocol. Given a (T, Q)-algorithmA′
DL = (A′
c,Aq)
for T = C + 2, we consider the following protocol.
17

<!-- page 18 -->

Main interactive protocol. Suppose that Alice chooses x ∈ [N ]. In the protocol, Alice and Bob try to
execute the algorithmA′
DL together, while Alice holds all element registers and Bob holds all qubit registers.
For qubit gates, Bob applies them locally without interacti ng with Alice.
T o apply element gates, Alice and Bob use the above protocol. For the classical preprocessing, a simpler
protocol sufﬁces. W e give the overall protocol below .
1. Alice prepares two element registers holding |g, gx⟩. If they are stored in the i, j-th element registers
inA′
c’s input, Alice also stores them in the i, j-th element registers.
2. Alice and Bob together execute A′
c, with the following modiﬁcations.
• Every qubit register is stored in Bob’s memory , and every qu bit gate is applied to Bob’s side
accordingly . Every element register is stored in Alice’s me mory . Alice and Bob use the same
name/order of the registers as inA′
c.
• For each classical group operation gate that is applied to t he registers B and X, Y, Bob measures
B in the computational basis and sends the measurement outcom e b to Alice. Alice applies the
group operation on her registers XY controlled on b, and discards b.
• Each classical labeling gate is processed analogously .
W e make some observations on this part. Alice’s state is alwa ys classical during this procedure, so
the measurement of Alice’s registers can be ignored, and dis carding bit b is not problematic. Alice has
not sent any information to Bob until this point. Finally , th e overall states between Alice and Bob are
identical to the state after A′
c(g, gx), except that all qubit registers are stored in Bob’s memory a nd all
element registers are stored in Alice’s memory .
3. Alice and Bob execute Aq together in a similar way:
• Every qubit gate is applied to Bob’s registers accordingly .
• For each group operation gate UG.op that is applied to the qubit register B and element registers
X, Y, Alice and Bob executes Delegate.Gop on BXY.
• Similarly , Delegate.Ginv or Delegate.Geq is executed for each UG.inv or UG.eq, respectively .
4. Finally , Bob outputs the ﬁnal output of Aq.
It is not hard to see that the overall states between Alice and Bob are always identical to the corresponding
intermediate states of A′
DL (ignoring the discarded bits). Therefore, the probability that Bob successfully
recovers x is exactly the same as that A′
DL solves the DL problem on input (g, gx).
W e then count the number of qubits sent from Alice to Bob. Alic e sends a bit only when ADL applies an
element gate. Thus, the total number of qubits is Q. At this point, we can apply Corollary 2.3 to have the
following inequality:
log ǫ′ + log N
2 ≤ Q =⇒ ǫ≤ ǫ′ + (C + 2)2
2p ≤ 22Q
N + (C + 2)2
2p
where we use Equation (3), which completes the proof.
The (t, w)-QGGM. W e then extend the lower bounds in the QGGM for more general se ttings. The proof
ideas are almost the same, except for the sub-protocols; Ali ce needs to send one qudit for appropriate
dimensions. W e present the following generalization to the MDL problem.
Theorem 5.3. LetG be a cyclic group of order N with a generator g. Suppose that the smallest prime divisor of N is
p. Let m be a positive integer. LetAMDL be a (C, Q)-algorithm in the (t, w)-QGGM, then the following holds:
Pr
ADL,x←[N ]m
[
A|G⟩
DL (g, gx)→ x
]
≤ (C + m + 1)2
p + (2tw)2Q
N m .
18

<!-- page 19 -->

Proof. Applying Lemma 5.1, it sufﬁces to consider the generic algorithm A′
MDL with no classical equality
queries, which solves the MDL problem with probability at le ast ǫ′≥ ǫ− (C+m+1)2
2p . Then, we can construct
a protocol between Alice and Bob where Alice aims to send x∈ [N ]m to Bob using this algorithm. W e need
appropriate subroutines for the (t, w)-QGGM. For the group operation gate, it works as follows.
Subprotocol Delegate.Gop for group operation gates. The initial states are
∑
b,i∈[t],j∈[w]
βb,i,j|b, i, j⟩BTW⊗
∑
z,w
αz,w|..., gz, ..., gw, ...⟩...Xi...Yj...
where Alice holds the registers X = ( X1, ..., Xt), Y = ( Y1, ..., Yw) and Bob holds B, T, W. gz and gw are
stored in Xi, Yj, respectively .
1. Bob sends B, T, W to Alice. Alice applies quantum group operation gates on BTWXY.
2. Alice returns the register B, T, W to Bob.
In this protocol, Alice sends a quantum state of dimension 2tw. The other element gates can be delegated
analogously .
Each quantum element gate is operated with a quantum state wi th 2tw dimension, thus Corollary 2.3
implies that
log ǫ′ + m log N
2 ≤ Q log(2tw) =⇒ ǫ≤ (2tw)2Q
N m + (C + m + 1)2
2p ,
which concludes the proof.
5.3 Unknown-order QGGM
W e can prove the following QGGM variant of Theorems 4.1 and 4.2.
Theorem 5.4. LetAord be a (C, Q)-algorithm to solve the order-ﬁnding problem overD(n)
prime in the (t, w)-QGGM. It
holds that
Pr
Aord,N
[
A|GN⟩
ord (g)→ N
]
= O
( C3
2n + n(2tw)2Q
2n
)
.
For the product-order-ﬁnding algorithm overD(n)
prime in the QGGM, it holds that
Pr
Aord,p,q
[
A|Gpq⟩
ord (g)→ pq
]
= O
( T 4
22n + n2(2tw)2Q
22n
)
.
Proof sketch. The proof is almost identical with the known-order QGGM proofs. Instead of applying Lemma 5.1,
whenever the classical preprocessing ﬁnds an informative c ollision, we use it to compress N . Otherwise,
Bob can delegate quantum group operations to Alice to constr uct the interactive protocol encoding N . The
product-order-ﬁnding case is analogous.
6 Lower Bounds in the Quantum Generic Ring Model
6.1 Quantum Generic Ring Model
W e deﬁne the quantum generic group model (QGRM) in this secti on. The QGRM is a natural analog of the
classical generic ring model [ AM09, JS13], similar to the relation between the QGGM and GGM.
LetR be a commutative ring isomorphic to ZN for some integer N to be speciﬁed later. Let t, w be
positive integers. A quantum generic ring algorithm A in the QGRM is deﬁned as follows. Note that the
19

<!-- page 20 -->

deﬁnition of ring multiplication and division is rather com plicated because of their subtlety; for example,
they are not invertible as is, or there is no inverse. Our abst raction closely resembles the actual target
arithmetic gates of circuit optimizations, e.g., [ Bea03, Gid19]. W e also remark that the (t, w)-QGGM can be
deﬁned analogously .
• There are two registers: qubit and element registers holdi ng superpositions of some information.
In contrast, element registers take a set of elements x∈R∪{⊥} as the computational basis. The
algorithm arbitrarily appends a new element register initi alized by|0⟩ or|1⟩.
• There are (arbitrary) quantum gates that map qubits to qubi ts, which cannot take element registers as
input.
• There are special gates called element gates that can access the element wires as follows. The unspeci-
ﬁed registers are unchanged by the operations.
Ring Addition Gate. It takes a qubit register B and two element registers X, Y and applies the uni-
tary that works on the computational basis as follows:
|b⟩B|x, y⟩XY↦→|b⟩B|x + by, y⟩XY
for x, y⁄=⊥, otherwise do nothing.
Ring Subtraction Gate. It is essentially identical to the ring addition gate, excep t for the choice of
unitary:
|b⟩B|x, y⟩XY↦→|b⟩B|x− by, y⟩XY .
Ring Product-Addition Gate. It takes a qubit register B and three element registers X, Y, Z and ap-
plies the unitary that works on the computational basis as fo llows:
|b⟩B|x, y, z⟩XYZ↦→|b⟩B|x + byz, y, z⟩XYZ
for x, y, z⁄=⊥ and registers, otherwise do nothing.
T esting Invertible Gate. It takes an element register X and a qubit register C, and applies the unitary
UTest that works on the computational basis as follows:
UTest :|x, c⟩XC↦→|x, c⊕ Test(x)⟩XC
where Test(x) = 1 if x is invertible, otherwise Test(x) = 0 .
Ring inversion-addition Gate. It takes a qubit register B and three element registers X, Y, Z. It ap-
pends an ancillary qubit register C initialized by|0⟩ and applies the following sequence of uni-
taries that works on the computational basis as follows:
|b⟩B|x, y, z⟩XYZ|0⟩C
↦→|b⟩B|x, y, z⟩Xi,Yj ,Yk|Test(z)⟩C
↦→|b⟩B
⏐⏐x, +bTest(z)y· z−1, y, z
⟩
XYZ|Test(z)⟩C
↦→|b⟩B
⏐⏐x, +bTest(z)y· z−1, y, z
⟩
XYZ|0⟩C
for x, y, z⁄=⊥, and do nothing other cases. Here, the ﬁrst and last unitarie s are UTest on ZC. In
the second unitary , it adds y· z−1 only if Test(yk) = 1 and b = 1. It discards C in the end.
Equality Gate. It takes a qubit register B and two element registers X, Y and applies the unitary that
works on the computational basis as follows:
|b⟩B|x, y⟩XY↦→|b⊕ δx,y⟩B|x, y⟩XY
for x, y⁄=⊥, otherwise do nothing, where δx,y = 1 if x = y and 0 otherwise.
20

<!-- page 21 -->

• W e allow the intermediate measurements for registers and t he labeling gate.
Classical Labeling Gate. It takes⌈log2 N⌉ qubit registers, measures it, and interprets them as an ele-
ment in x∈ ZN≃R . It appends a new element register holding |x⟩. If there is no corresponding
element x∈ ZN to the input wires, it outputs an element wire containing |⊥⟩.
W e count the number of element gates as the cost metric, denot ed by the ring operation complexity .
W e stress that the modulus N is NOT given to the generic algorithms explicitly . Instead, the al gorithm
only accesses the ring (or modular) operations. This still c aptures most quantum parts of the quantum fac-
toring algorithms. For Shor’s algorithm, the quantum part a ims to ﬁnd the order r of the randomly chosen
integer a, which only requires modular arithmetic. W e prove the lower bound for the order ﬁnding in the
QGRM in Theorem 6.1. The knowledge of N beyond our model is used in the classical post-processing
parts for computing (say) gcd(ar/2 + 1, N).
Regev’s algorithm does not compute the order. Instead, it co mputes a short vector z = ( z1, ..., zd) in
a certain lattice, and then compute gcd(bz1
1 ...bzd
d − 1, N). In the QGRM, the algorithm still can compute
bz1
1 ...bzd
d − 1 as an integer, which is relatively small, having a nontrivia l common factor with N . W e prove
that this algorithm needs to make a logarithmic number of rin g operations in Theorem 6.2.
6.1.1 Quantum Generic Ring Algorithm with Classical Prepro cessing
W e consider a slightly more general algorithm that can do cla ssical preprocessing without the testing or
equality gates. The classical ring operations are deﬁned by the ring operations that element gates are mea-
sured before applying ring operations. Recall the ring oper ations are done on Alice’s side in the proofs.
The delegation of classical ring operations can be done with out Alice’s messages, except for the equality
gates, where Bob needs to take the output of gates. Therefore , the number of classical ring operations, such
as precomputing x2k
, is irrelevant to our lower bounds. W e do not explicitly disc uss this setting in the
remainder of this section.
6.2 Lower Bounds in the QGRM
This section is devoted to proving that the order-ﬁnding pro blems with certain distributions and a certain
type of factoring algorithms have logarithmic ring operati on complexity . In a ring R≃ ZN , the order of
x∈R , denoted by ordN (x), is deﬁned by the minimal positive integer e such that xe = 1 mod N . A prime
number p is safe if p−1
2 is also prime. W e consider the following problem.
Problem 5. LetD(n)
safe be a uniform distribution over the set of n-bit safe primes. An order-ﬁnding problem
overD(n)
safe in the QGRM is deﬁned as follows. First, two distinct primes p, q are sampled fromD(n)
safe and let
N = pq. Choose a random x∈ ZN . The adversary is given x stored in the element register in the QGRM
forR≃ ZN and asked to ﬁnd ordN (x).
W e assume that the number of n-bit safe primes is at least C· 2n/n2 for some constant C > 0, which is a
variant of the conjecture that the number of safe primes belo w N is of order Θ(N/ log2 N ) [Sho09, Section
5.5.5].
Theorem 6.1. LetAord be an order-ﬁnding algorithm over D(n)
safe in the (t, w)-QGRM with the ring operation com-
plexity of Q. Assuming that the number of n-bit safe primes is at least C· 2n/n2 for C > 0, it holds that
Pr
Aord,p,q,x
[Aord(x)→ ordpq(x)] = O
( n4(2tw)2Q
22n + 1
2n
)
Proof. Let N = pq. W e ﬁrst observe that the order of x is a divisor of (p−1)(q−1)
2 = 2 · p−1
2 · q−1
2 . With
probability 1− O(1/p) over random x, ordN (x) = (p−1)(q−1)
2 or (p−1)(q−1)
4 . In this case, one can recover (p, q)
for safe primes p, q from ordN (x) using the factorization.
21

<!-- page 22 -->

Based on this observation, we construct a protocol between A lice and Bob where Alice wants to send
(p, q) to Bob. The proof is identical to that of Theorem 5.2, except that we need the delegation sub-protocols
for ring operations. By the assumption, Alice sends one out o f O
(
22n
n4
)
candidates to Bob using Q qubits of
communications.
W e then consider the factoring algorithms, where the generic algorithm’s goal is to ﬁnd an integer with
a nontrivial common divisor with N . W e prove the following theorem.
Theorem 6.2. LetA be an algorithm in the (t, w)-QGRM with the ring operation complexity of Q. For two primes
p, q sampled fromD(n)
prime and N = pq, it holds that
Pr
A,p,q
[1 < gcd(Z, N) < N :A()→ Z] = O
( n log Z(2tw)2Q
2n
)
.
In particular, if log Z = O(2(2−ǫ)n) for any ǫ > 0, this implies that Q = Ω( log N
log(2tw) ) to have the constant success
probability.
Before proceeding with the proof, we give some interpretati ons of this theorem. As we do not give N
to the generic algorithm, it cannot apply the modulus operat ion. Therefore, the known quantum factoring
algorithms must be explained with some modiﬁcations, where the ﬁnal steps usually compute the common
divisor of some integer and N .
Instead of giving N , we ask to ﬁnd an integer that sufﬁces for factoring N . In the QGRM, this integer
must be computed in plain, without modulus computation. For Regev’s algorithm, the ﬁnal integer is of
the form Z =∏
i∈[d] bzi
i for zi = exp(O(√n)) and d≈√n. The last statement holds in this case as well.
The output of Shor’s algorithm corresponds to Z = ar/2− 1 for r = ordN (a). The bit length of Z is about
log Z≤ r
2· log a≤ nN
2 . Therefore, we cannot apply this theorem to Shor’s algorith m in general.
Proof. Let ǫ be the success probability of A. W e construct a protocol that sends (p, q) usingA. Precisely ,
Bob runs A using the delegation of quantum ring operations using Q log(2tw) qubits. After obtaining
the outputs Z fromA, Alice additionally sends an index of the prime factor of Z among its n-bit prime
factors. Since the number of n-bit primes factors of Z is bounded by log Z/n, the index can be described
in log(log Z)− log n classical bits. Finally , Alice sends the other prime factor which can be speciﬁed by
n− log n + O(1) classical bits. Appying Corollary 2.3, we have
2Q log(2tw) + (log log Z− log n) + (n− log n + O(1))≥ 2n− 2 log n + log ǫ + O(1),
which implies
ǫ = O
( n(log Z)(2tw)2Q
2n
)
,
concluding the proof.
7 Lower Bounds for Index Calculus Algorithms
This section introduces a new model called the smooth index calculus model (SGGM) of generic algorithms,
including the (simplest) index calculus methods.
A main feature of index calculus is using the set of B-smooth numbers, denoted by SB, whose prime
factors are all less than or equal to B. These numbers are relatively quickly factorized, and the i ndex
calculus method ﬁnds many nontrivial elements in SB to leverage this fact.
22

<!-- page 23 -->

7.1 Smooth Generic Group Model
The smooth GGM is parameterized by a parameter B, which induces the factor base B and the set S =
{h1, ..., h|S|} of smooth elements. Precisely , the factor base is a set of pri mesB ={p1, ..., pb} and the smooth
element hi∈ S is of the form
hi = pc(i)
1
1 ····· p
c(i)
b
b (6)
for c(i) = (c(i)
1 , ..., c(i)
b ), whose precise conditions will be speciﬁed later.
An SGGM algorithm A overG of order N with the parameter B, denoted by an algorithm in the B-
SGGM, is given by a circuit with the following features:
• There are two types of wires: bit wires and element wires. Bi t wires take a bit in {0, 1}, and element
wires take an element in x∈ ZN∪{⊥} , which is denoted by gx.
• There are bit gates and element gates that are identically d eﬁned as the generic group model.
• There are special element gates deﬁned as follows:
Smooth T est Gate. It takes an element wire containing h. If h∈ S, it outputs 1, otherwise outputs 0.
Smoothing Gate. It takes an element wire containing h. If it is smooth, i.e., h = hi for some i∈ [|S|],
outputs c(i) deﬁned in Equation (6). Otherwise, it outputs⊥.
W e further establish the properties of the factor base and th e smooth elements regarding the parameter
B. Let g be the generator of G, and let u > 0 be such that B = N 1/u. Let cbase, csmooth, dsmooth≥ 1 be the
universal constants that are independent from B. Here, o(1) hides a factor much less than 1.
• The set B is given to the algorithm. The set S is randomly chosen and unknown to the algorithm. For
the factor baseB ={p1, ..., pb}, it holds that pi = gzi for some random zi for each i, which is unknown
to the algorithm.
• The size of the factor base |B| = b is (cbase + o(1))B/ log B.
• The number of smooth elements is
pS :=|S|
N = (csmooth + o(1))·
( dsmooth + o(1)
u log u
)u
. (7)
• For any rank- c afﬁne space V in Zb
N , deﬁne
SV :={h(i)∈ S : c(i)∈ V}.
If c = (cbase + o(1))C/ log C for some C = N 1/v, it holds that
|SV|
N ≤ (csmooth + o(1))·
( dsmooth + o(1)
v log v
)v
. (8)
W e explain the reasoning behind these assumptions. The assu mption on the prior knowledge of the algo-
rithm reﬂects the reality . The randomness ofS and zi prevents the generic algorithm from using the explicit
values related to the smooth elements.
The sizes of B and S stem from the original choices in the index calculus, whose e stimated sizes are
well-studied. W e refer the survey on this topic [ Gra08] to the readers.
The last assumption describes that the vectors c(i) are well-distributed. In particular, it asserts that the
factor base {p≤ C}, which corresponds to the subspace V = Zc
N×{ 0}b−c, maximizes the size of SV ,
according to the estimated size by Equation (7).
23

<!-- page 24 -->

7.1.1 Polynomial Representations
Again, we identify the group elements by the corresponding p olynomials. W e mainly focus on the dis-
crete logarithm problems where the problem instance is give n as (g, gx1, ..., gxm), which corresponds to
1, X1, ..., Xm. Furthermore, because of the factor base, we have more forma l variables Z1, ..., Zb. Therefore,
each element corresponds to the polynomial in
ZN [X1, ..., Xm, Z1, ..., Zb].
W e stress that we occasionally identify the polynomial with its coefﬁcient vector.
W e consider the answer from the smoothing gate to be the colli sion. Precisely , if an element h corre-
sponding to the polynomial P is given to the smoothing gate and the answer is (c1, ..., cb), then it induces
the collision
P = c1Z1 + ... + cbZb.
If it is not included in the span of the previous zero set Z, we include it as an informative collision as well.
7.2 The Discrete Logarithm Problem in the SGGM
In this section, we assume that the variables N = N (λ), B = B(λ), u = u(λ) are parameterized by some
implicit parameter λ so that we can work in the asymptotic regime. Still, we drop th e parameter λ for
simplicity .
Theorem 7.1. LetG be a cyclic group of prime order N . Let B be an integer such that B = N 1/u for some u > 0. Let
ADL be a DL algorithm in the B-SGGM with a constant success probability. Then, the number of group operations T
ofADL must satisfy
T = exp
(
Ω
(√
log N log log N
))
.
Proof. T oward contradiction, we assume that ADL successfully solves the DL problem in the SGGM with
smaller group operations than the statement. W e ﬁrst observ e that each equality query makes an informa-
tive collision with probability 1
N ; thus, with probability 1− T 2
N , there are no informative collisions from the
equality queries. From now on, we ignore the equality gates a nd assume that all informative collisions are
from the smoothing gate.
As before, we assume that ADL makes the equality gate at the end so that the collision is fou nd. W e
begin with the following fact, which is a SGGM variant of Lemma 3.2.
Fact 3. Each group operation introduces a new informative collisio n (through the smoothing gate) with
probability at most pS deﬁned in Equation (7). In particular, the input element to the smoothing gate col-
lides with a random element in S.
Proof of fact. Let h be a new group element corresponding to (c0, a, c1, ..., cb), which is linearly independent
from the vectors inZ. This means that h is uniformly distributed over random X, Z1, ..., Zb conditioned on
the equations inZ hold. That is, h∈ S holds with probability|S|/N = pS.
Case 1. W e ﬁrst consider the case that u is sufﬁciently large so that
u8u2
≥ N =⇒ u log u = Ω
(√
log N log log N
)
.
In this case, by Fact 3,ADL must make
1/pS = Ω(uu) = exp
(
Ω
(√
log N log log N
))
group operations to ﬁnd an informative collision with a cons tant probability .6
6A formal proof requires some probabilistic arguments, whic h we omitted here.
24

<!-- page 25 -->

Case 2. W e consider the other case that u is relatively small so that
u8u2
≤ N.
In this case, we choose v > u such that vv2
= N . Note that
(2u)(2u)2
= (2u)4u2
≤ u8u2
≤ N,
thus v≥ 2u holds. Suppose that the algorithm ﬁnds K informative collisions at total. W e will prove that
K = Ω
{
N 1/2v)
in this case. Since
v2 log v = log N =⇒ v = Θ
(√
log N
log log N
)
,
we have
T≥ K = exp
(
Ω
( log N
v
))
= exp
(
Ω
(√
log N log log N
))
.
Combining the two cases, we prove the theorem.
It remains to prove the lower bound of K in the second case. W e identify the formal variable X to
represent gx. In particular, the span of the ﬁnal zero set Z must include the polynomial X− x, or a vector
(−x, 1, 0, ..., 0). W e deﬁneZ (t) to denote the zero set right after the t-th informative collision. Deﬁne the
following projections ofZ (t):
Z (t)
X=x :={(ax + c0, c1, ..., cb) : c0 + aX + c1Z1 + ... + cbZb∈Z (t)}
Z (t)
B :={(c1, ..., cb) : c0 + aX + c1Z1 + ... + cbZb∈Z (t)}
W e observe the following facts.
Fact 4. The rank ofZ (K)
X=x is less than K. In particular, there must exist a smoothing gate making the t(≤ K)-
th informative collision P such that P (t)
X=x is included in the span of Z (t−1)
X=x . The rank ofZ (t)
X=x is equal to
the rank ofZ (t)
B for each t∈ [K].
Proof of fact. Let (−x, 1, 0, ..., 0) = b and{b, b2, ..., bK} be the basis extension of Z =Z (K) from{b}. The
projection π : ( c0, a, c1, ..., cb)↦→(c0 + ax, c1, ..., cb) mapsZ toZ (K)
B and π(b) = 0 , thus the rank of Z (K)
B
must be K− 1. The ﬁnal statement follows from (1, 0, ..., 0) is not included in the span of Z.
W e call the ﬁrst smoothing gate by critical with input h and output h(i) ∈ S satisfying the condition
described in Fact 4. Let (h1, ..., hb) and c(i) be the corresponding coefﬁcient vectors of h and h(i).
W e give an upper bound for the probability pt that the t-th informative collision is critical. This means
that the rank ofZ (t−1)
B is t− 1, and (h1, ..., hb)− c(i) is included inZ (t−1)
B . In other words,
c(i)∈ (h1, ..., hb) + span
(
Z (t−1)
B
)
=: V.
Since h(i) is a random element in S, Equation (8) implies that the probability pt is bounded by
pt = Pr
[
c(i)∈ V
]
=|SV|
|S| .
Let C = N 1/v and c = cbaseC/ log C. If t≤ c, the logarithm of the above equation becomes for a constant
α≈ log dsmooth
log
(|SV|
|S|
)
≤− v log(v log v) + u log(u log u) + α(v− u) + O(1)
≤− 0.5v log(v log v)− u log(2u log 2u) + u log(u log u) + αv + O(1)
≤− 0.5v log v + O(1).
25

<!-- page 26 -->

where we use the fact that dsmooth is constant and v ≥ 2u, and set α ≈ log dsmooth, which is less than
0.5 + 0.5 log log v in the interested parameter regime. It implies that pt≤ β/v 0.5v for some constant β > 0.
In other words, with constant probability , the critical inf ormative collision will be found after Ω(v0.5v) =
Ω(N 1/2v) informative collisions are found.
References
[AGK20] Benedikt Auerbach, Federico Giacon, and Eike Kiltz . Everybody’s a target: Scalability in public-
key encryption. In Anne Canteaut and Yuval Ishai, editors, Advances in Cryptology - EURO-
CRYPT 2020 - 39th Annual International Conference on the The ory and Applications of Cryptographic
T echniques, Zagreb, Croatia, May 10-14, 2020, Proceedings , Part III , volume 12107 of Lecture Notes
in Computer Science, pages 475–506. Springer, 2020.
[AHP23] Benedikt Auerbach, Charlotte Hoffmann, and Guille rmo Pascual-Perez. Generic-group lower
bounds via reductions between geometric-search problems: With and without preprocessing.
IACR Cryptol. ePrint Arch. , page 808, 2023.
[AM09] Divesh Aggarwal and Ueli Maurer. Breaking rsa generi cally is equivalent to factoring. In Ad-
vances in Cryptology-EUROCRYPT 2009: 28th Annual Internat ional Conference on the Theory and
Applications of Cryptographic T echniques, Cologne, Germany, April 26-30, 2009. Proceedings 28, pages
36–53. Springer, 2009.
[Bea03] Stephane Beauregard. Circuit for shor’s algorithm using 2n+ 3 qubits. Quantum Information &
Computation, 3(2):175–185, 2003.
[BFP21] Balthazar Bauer, Georg Fuchsbauer, and Antoine Plo uviez. The one-more discrete logarithm
assumption in the generic group model. In Mehdi Tibouchi and Huaxiong W ang, editors, Ad-
vances in Cryptology - ASIACRYPT 2021 - 27th International Conference on the Theory and Application
of Cryptology and Information Security, Singapore, December 6-10, 2021, Proceedings, Part IV, volume
13093 of Lecture Notes in Computer Science , pages 587–617. Springer, 2021.
[BL96] Dan Boneh and Richard J Lipton. Algorithms for black- box ﬁelds and their application to cryp-
tography . In Annual International Cryptology Conference , pages 283–297. Springer, 1996.
[BV98] Dan Boneh and Ramarathnam V enkatesan. Breaking rsa m ay be easier than factoring. In Ad-
vances in Cryptology—EUROCRYPT, volume 98, pages 59–71. Citeseer, 1998.
[CDG18] Sandro Coretti, Y evgeniy Dodis, and Siyao Guo. Non- uniform bounds in the random-
permutation, ideal-cipher, and generic-group models. In H ovav Shacham and Alexandra
Boldyreva, editors, Advances in Cryptology - CRYPTO 2018 - 38th Annual Internati onal Cryptol-
ogy Conference, Santa Barbara, CA, USA, August 19-23, 2018, Proceedings, Part I , volume 10991 of
Lecture Notes in Computer Science , pages 693–721. Springer, 2018.
[CK18] Henry Corrigan-Gibbs and Dmitry Kogan. The discrete -logarithm problem with preprocessing.
In Jesper Buus Nielsen and Vincent Rijmen, editors, Advances in Cryptology - EUROCRYPT 2018
- 37th Annual International Conference on the Theory and Applications of Cryptographic T echniques, T el
Aviv, Israel, April 29 - May 3, 2018 Proceedings, Part II , volume 10821 of Lecture Notes in Computer
Science, pages 415–447. Springer, 2018.
[CLQ19] Kai-Min Chung, T ai-Ning Liao, and Luowen Qian. Lowe r bounds for function inversion with
quantum advice. arXiv preprint arXiv:1911.09176 , 2019.
[Den02] Alexander W Dent. Adapting the weaknesses of the ran dom oracle model to the generic group
model. In International Conference on the Theory and Application of C ryptology and Information Se-
curity, pages 100–109. Springer, 2002.
26

<!-- page 27 -->

[DGK17] Y evgeniy Dodis, Siyao Guo, and Jonathan Katz. Fixin g cracks in the concrete: Random oracles
with auxiliary input, revisited. In Annual International Conference on the Theory and Applicat ions
of Cryptographic T echniques, pages 473–495. Springer, 2017.
[DK02] Ivan Damgård and Maciej Koprowski. Generic lower bou nds for root extraction and signature
schemes in general groups. In International Conference on the Theory and Applications of Crypto-
graphic T echniques, pages 256–271. Springer, 2002.
[DTT10] Anindya De, Luca Trevisan, and Madhur Tulsiani. Tim e space tradeoffs for attacks against one-
way functions and prgs. In Annual Cryptology Conference, pages 649–665. Springer, 2010.
[GE21] Craig Gidney and Martin Ekerå. How to factor 2048 bit r sa integers in 8 hours using 20 million
noisy qubits. Quantum, 5:433, 2021.
[Gid19] Craig Gidney . Windowed quantum arithmetic. arXiv preprint arXiv:1905.07682 , 2019.
[Gra08] Andrew Granville. Smooth numbers: computational n umber theory and beyond. Algorithmic
number theory: lattices, number ﬁelds, curves and cryptogr aphy, 44:267–323, 2008.
[GT00] Rosario Gennaro and Luca Trevisan. Lower bounds on th e efﬁciency of generic cryptographic
constructions. In Proceedings 41st Annual Symposium on Foundations of Comput er Science, pages
305–313. IEEE, 2000.
[HNR18] Shima Bab Hadiashar, Ashwin Nayak, and Renato Renne r. Communication complexity of one-
shot remote state preparation. IEEE T ransactions on Information Theory, 64(7):4709–4728, 2018.
[HXY19] Minki Hhan, Keita Xagawa, and T akashi Y amakawa. Qua ntum random oracle model with aux-
iliary input. In International Conference on the Theory and Application of C ryptology and Information
Security, pages 584–614. Springer, 2019.
[HYY23] Minki Hhan, T akashi Y amakawa, and Aaram Yun. Quantu m complexity for discrete logarithms
and related problems. arXiv preprint arXiv:2307.03065 , 2023.
[JS13] Tibor Jager and Jörg Schwenk. On the analysis of crypt ographic assumptions in the generic ring
model. Journal of cryptology , 26:225–245, 2013.
[KM06] Neal Koblitz and Alfred Menezes. Another look at gene ric groups. Cryptology ePrint Archive ,
2006.
[Mau05] Ueli M. Maurer. Abstract models of computation in cr yptography . In Nigel P . Smart, editor,
Cryptography and Coding, 10th IMA International Conferenc e, Cirencester, UK, December 19-21, 2005,
Proceedings, volume 3796 of Lecture Notes in Computer Science , pages 1–12. Springer, 2005.
[NABT15] Aran Nayebi, Scott Aaronson, Aleksandrs Belovs, a nd Luca Trevisan. Quantum lower bound
for inverting a permutation with advice. Quantum Information & Computation, 15(11-12):901–913,
2015.
[Nec94] V assiliy Ilyich Nechaev . Complexity of a determina te algorithm for the discrete logarithm. Math-
ematical Notes, 55(2):165–172, 1994.
[NS06] Ashwin Nayak and Julia Salzman. Limits on the ability of quantum states to convey classical
messages. Journal of the ACM (JACM) , 53(1):184–206, 2006.
[PH78] S Pohlig and M Hellman. An improved algorithm for comp uting logarithms over gf (p) and
its cryptographic signiﬁcance (corresp.). IEEE T ransactions on Information Theory, 24(1):106–110,
1978.
27

<!-- page 28 -->

[Pol78] John M Pollard. Monte carlo methods for index comput ation (mod p)). Mathematics of computa-
tion, 32(143):918–924, 1978.
[Reg23] Oded Regev . An efﬁcient quantum factoring algorith m. arXiv preprint arXiv:2308.06572 , 2023.
[Sho97] Victor Shoup. Lower bounds for discrete logarithms and related problems. In W alter Fumy ,
editor, Advances in Cryptology - EUROCRYPT ’97, International Conf erence on the Theory and Appli-
cation of Cryptographic T echniques, Konstanz, Germany, Ma y 11-15, 1997, Proceeding , volume 1233
of Lecture Notes in Computer Science , pages 256–266. Springer, 1997.
[Sho99] Peter W Shor. Polynomial-time algorithms for prime factorization and discrete logarithms on a
quantum computer. SIAM review, 41(2):303–332, 1999.
[Sho09] Victor Shoup. A computational introduction to number theory and algebra . Cambridge university
press, 2009.
[Sut07] Andrew V Sutherland. Order computations in generic groups . PhD thesis, Massachusetts Institute
of T echnology , 2007.
[Yun15] Aaram Yun. Generic hardness of the multiple discret e logarithm problem. In Elisabeth Oswald
and Marc Fischlin, editors, Advances in Cryptology - EUROCRYPT 2015 - 34th Annual Intern a-
tional Conference on the Theory and Applications of Cryptog raphic T echniques, Soﬁa, Bulgaria, April
26-30, 2015, Proceedings, Part II , volume 9057 of Lecture Notes in Computer Science , pages 817–836.
Springer, 2015.
[YYHK20] T akashi Y amakawa, Shota Y amada, Goichiro Hanaoka, and Noboru Kunihiro. Generic hardness
of inversion on ring and its relation to self-bilinear map. Theoretical Computer Science, 820:60–84,
2020.
[Zha22] Mark Zhandry . T o label, or not to label (in generic gr oups). In Y evgeniy Dodis and Thomas
Shrimpton, editors, Advances in Cryptology - CRYPTO 2022 - 42nd Annual Internati onal Cryptol-
ogy Conference, CRYPTO 2022, Santa Barbara, CA, USA, August 15-18, 2022, Proceedings, Part III ,
volume 13509 of Lecture Notes in Computer Science , pages 66–96. Springer, 2022.
A Missing Proofs
A.1 Missing proofs in the GGM
Proof of Lemma 3.1. Suppose thatA is deterministic; ifA is randomized, we include the random seed as its
description. W e construct an algorithmA′ that has the same circuits asA, but the element wires are replaced
by the polynomial wires. The initialization P ={(w1, P1), ..., (wm, Pm)} for input can be done without any
query , and each input element wirewi is replaced by Pi inA′. The labeling gates and group operation gates
are processed as in the polynomial list. For the equality gat es with element wires wi, wj , the output can be
computed by checking if Pi− Pj is included in the span of Z; if included the output of the equality gate is
1, otherwise 0.
Proof of Fact 1. Let Pi := ai,1X1 + ... + ai,mXm + bi. A collision (i, j) induces a linear equation over Zp as
0 = Pi− Pj = (ai,1− aj,1)X1 + ... + (ai,m− aj,m)Xm + (bi− bj).
Since collisions are informative, they are nontrivial and l inearly independent due to Equation (1). Thus
m informative collisions give a system of m linear equations over Zp with m variables that are linearly
independent, which can be easily solvable.
28

<!-- page 29 -->

Proof of Theorem 3.6, sketch. Observe that without ﬁnding an informative collision, the o utput should corre-
spond to aX + bY + c for some a, b, c, where X, Y are the variables corresponding to gx, gy. The probability
that aX + bY + c = XY is at most 1/|G| over the random choice of X, Y . Therefore, the algorithm must ﬁnd
an informative collision.
Given an informative collision exists, the ﬁrst part of the encoding is the ﬁrst informative collision. If this
collision has a nonzero coefﬁcient for the monomial contain ing X, then the second part of the encoding is
x. Otherwise, it is y. Given the encoding, the decoding procedure is 1) parses the ﬁrst informative collision
and one of x or y, and 2) plugs it in the ﬁrst collision. The collision collaps es to a one-variable polynomial
of degree less than 1, and the correct solution can be guessed with probability at least 1/2.
A.2 A QGGM lemma
Proof of Lemma 5.1. Except for the equality gates, we deﬁne the algorithm A′
c as identical toAc. It removes
all equality gates, except the trivial equality gate (as in t he classical GGM) that are replaced by bit ﬂipping.
Given the ﬁrst assertion, the “In particular” part is obviou s because the trace distance between the inter-
mediate outputs of two (C, Q)-algorithms are identical with probability 1− (C+m+1)2
2p , and the remaining
parts are the same.
The proof proceeds as follows. As the algorithmAc is only given classical group elements and can apply
classical group gates, it only maintains at most C +m+1 classical group elements, which are represented by
polynomials P1, ..., PC+m+1 as done in the classical generic group models. Each equality query corresponds
to the difference between polynomials Pi− Pj. If Pi− Pj is identically zero or never be zero, then there is
no difference betweenAc andA′
c from these equality gates.
Consider an equality gate corresponding to Pi− Pj that is not identically zero. There exists some prime
power qt that exactly divides N such that Pi− Pj is nonzero modulo qt. Since Pi− Pj is linear, the portion
of inputs where the equality gate corresponding to Pi− Pj behaves differently from the identity gate is at
most 1/q≤ 1/p. Since there are at most
{C+m+1
2
)
≤ (C+m+1)2
2 different pairs of group elements, at most
(C+m+1)2
2p -fraction of inputs make difference on the behaviors of Ac andA′
c. In other words, the output
states of the two algorithms are identical with probability at least 1− (C+m+1)2
2p for random inputs.
B An Alternative Proof for the MDL Lower Bound
W e give a simple proof for the MDL lower bound Theorem 3.4. W e begin with the proof of Lemma 3.2.
Proof of Lemma 3.2. LetZ ={Q1, ..., Qs} be the current zero set. Assume that s < t ; otherwise, there is no
more informative collision. Let P be the linear polynomial corresponding to the new collision . Assume that
P /∈ span(Z). This implies that P is nonzero in the quotient ring ZN [X1, ..., Xt]/span(Z)≃ ZN [L1, ..., Lt−s]
for some linear polynomials L1, ..., Lt−s, and each variable Li is uniform random over random choice of
x1, ..., xt conditioned on Q1, ..., Qs = 0, making P uniform over ZN . That is, P = 0 holds and is informative
with probability 1/N.
For the readability , we restate the lower bound.
Theorem B.1. LetG be a cyclic group of prime order. Let Am-MDL be an m-MDL algorithm in the GGM having at
most T group operation gates. It holds that:
Pr
Am-MDL,x
[
AG
m-MDL(g, gx)→ x
]
= O
(( e(T + 2m)2
2m|G|
)m)
.
Proof. As seen in the original proof of Theorem 3.4, we can assume that the algorithm ﬁnds m informative
collisions to solve the m-MDL problem. Let T be the number of group operations.
29

<!-- page 30 -->

By Lemma 3.2, each equality gate induces an informative collision with p robability at most 1/N. W e
further assume that the algorithm never applies the equalit y gates to the predictable inputs. This makes
the probability that each equality gate is informative equa l to 1/N independent from the previous equality
gates.
Let E be the number of equality gates, which is at most
{T +2m
2
)
≤ (T +2m)2
2 . Assume that
{T +2m
2
)
≤ mN,
otherwise the upper bound becomes larger than 1. Let C be the number of informative collisions during
the algorithm and µ = E[C] = E
N . Let δ = mN
E − 1. Note that δµ≤ (1 + δ)µ = m. By the multiplicative
Chernoff bound, we have
Pr[C≥ m]≤
( eδ
(1 + δ)1+δ
)µ
= eµδ
(mN/E)m
≤ em
(mN/E)m =
( eE
mN
)m
≤
( eE
mN
)m
≤
( e(m + 2T )2
2mN
)m
.
Since this is an upper bound of the success probability of the m-MDL algorithm, it concludes the proof.
C Equivalence between GGMs
This section proves that any single-stage problems secure i n the Maurer-style (or type-safe) generic group
model are also secure in the Shoup-style (or random represen tation) generic group model. The proof is
essentially the same as [ Zha22, Theorem 3.5] with some additional ﬁner analysis. 7
W e call the generic algorithms described in Section 3 by type-safe (TS). W e consider another style of
generic algorithm that is called random representation (RR ) introduced in [ Sho97]. In this model, a set S∈
{0, 1}∗ (with the known maximal length of elements) is given public, and a random injection L : ZN→ S
is chosen, which is called by the labeling function . L(x) is understood as a group element gx. A generic
algorithm in the random representation model is able to make the following queries:
Labeling Query . It takes x∈ ZN as input and outputs L(x).
Group Operation Query . It takes ℓ1, ℓ2∈ S and a single bit b as input. If there exist x1, x2∈ ZN such that
L(x1) = ℓ1 and L(x2) = ℓ2, it outputs L(x1 + bx2). Otherwise, it outputs⊥.
W e count the number of queries as a unit cost. A generic algori thm in this model is denoted byAGRR . Note
that there is no equality query in this model, which can be don e by comparing the labels without accessing
the oracle. If an algorithm only makes queries with the input s that it received before by some queries or
input, then we call it faithful.
The following lemma shows that, when considering a single-s tage game as in this paper, a faithful
generic algorithm in the RR model is essentially the same as o ne in the TS model, but there is a subtle
difference otherwise. W e write L(x) = ( L(x1), ..., L(xm)) for x = (x1, ..., xm)∈ Zm
N .
Theorem C.1. Let f be a function that takes an element in Zm
N as input, p > 0, and D a distribution over Zm
N .
Suppose for any generic algorithmB in the TS model with T + Λ group operation complexity, it holds that
Pr
B,x←D
[BG(gx, aux) = f (x)]≤ p
where aux is a bit string, Λ is to be speciﬁed and suppose that f includes k group element wires.
7In the original paper, the author only considers the polynom ially-bounded algorithms and negligible advantage. W e nee d to
consider more ﬁne-grained equivalence for the exact advant age and any number of group operations.
30

<!-- page 31 -->

Then, in the RR model, the following inequality holds
Pr
A,L,x←D
[AGRR (L(x), aux) = f (x)]≤ p− ∆
where
• for a faithful generic algorithmA with T queries and Λ = ∆ = 0 , and
• in general, for a generic algorithm A with T queries such that at most t labels that are not given to A before,
where Λ = tr and ∆ = r·
{T
N
)r
for any positive integer r.
In particular, when T = N 1−1/c for some constant c > 0 and p≥ 1/N, we can choose r = 2c, which asserts that the
asymptotic results equally hold.
Proof. T oward contradiction, we assume that there exists a generic algorithmA in the RR model with the
winning probability larger than p−∆. W e ﬁrst consider the case thatA is faithful. In this case, the algorithm
B proceeds as follows.B initializes an empty table T , which will contain pairs (h, ℓ) for h in an element wire
and ℓ∈ S. This will be interpreted as L(x) = ℓ. W e deﬁne the following subroutines ofB:
FindLabel(h): It takes an element wire containing h as input. It searches for a pair (h′, ℓ)∈ T with h = h′
using the equality gates. If such a pair exists, it returns ℓ. Otherwise, it samples a random ℓ∈ S
conditioned on ℓ not being in the table T . It adds (h, ℓ) to T and returns ℓ.
FindElement(ℓ): It searches for a pair (h, ℓ′)∈ T with ℓ = ℓ′. If such a pair exists, it returns h on an element
wire. Otherwise, it generates an element wire containing ⊥ and adds (⊥, ℓ) to ℓ. It returns ⊥. (This
case does not occur for the faithful algorithms.)
B executesA and processes the queries fromA and the inputs/outputs as follows.
• Given the problem instance, B parses it into a list L of element wires. For each element wire h∈ L,B
runs ℓ← FindLabel(h) and sends ℓ toA as a part of input corresponding to h.
• For a labeling query x fromA,B constructs an element wire containing gx using a labeling gate. Then
it runs ℓ← FindLabel(gx) and returns ℓ toA.
• For a group operation query (ℓ1, ℓ2, b),B runs h1← FindElement(ℓ1), h2← FindElement(ℓ2), and com-
putes h = h1· hb
2 using a group operation gate. Then it runs ℓ← FindLabel(h) and returns ℓ toA.
• The ﬁnal output of B is identical to that of A. Precisely , ifA outputs (ℓ1, ..., ℓk, τ) for labels ℓ1, ..., ℓk
and a string τ ,B runs hi← FindElement(ℓi) for i∈ [k] and outputs (h1, ..., hk, τ).
Note that each labeling query and group operation query incu rs a single element gate, thus the group
operation complexity of B is the same as one of A. T o prove that B wins with probability at least p, we
consider the following sequence of hybrid experiments.
H0. In this hybrid,A interacts with the group oracleGRR.A wins with probability at least p by the assump-
tion.
H1. This hybrid is the same as H0 except that the random injection L is lazily sampled. This is possible
becauseA is faithful. In the perspective of A, this is identical to H0, thus the winning probability is
the same as H0.
H2. Here,A is a subroutine ofB. The view of A is identical to that of H1, and the translation between two
models is done inside ofB. The winning probability ofB is equal to that ofA, which is the same as in
H1.
31

<!-- page 32 -->

This completes the proof for the faithful A.
W e then consider the general case. In this case, A may ask queries with the labels it never received. T o
remedy this, we need to modify the subroutine FindElement, taking the probability that such a label is valid
(i.e., an image of L) into account. The modiﬁed subroutine is as follows.
FindElement′(ℓ): It searches for a pair (h, ℓ′)∈ T with ℓ = ℓ′. If such a pair exists, it returns h on an element
wire. Otherwise, let m :=|{(h, ℓ)∈ T : h⁄=⊥}|, and it does the following:
• With probability 1− (N− m)/(|S|−| T|), it generates an element wire containing ⊥ and adds
(⊥, ℓ) to ℓ. It returns⊥.
• With probability (N− m)/(|S|−| T|), it does the following procedures t times: It randomly
samples x∈ ZN and construct the corresponding element wire containing gx, and searches for
(h, ℓ′)∈ T with h = gx using the equality gates. If such a pair does not exist, it add s (gx, ℓ) to T ,
returns gx on an element wire and halts. Otherwise, it discards gx, and samples a fresh x∈ ZN
and repeats.
A single iteration of the second case of FindElement′ terminates with probability at least 1− m/N≥ 1− T /N,
and takes one labeling gate.
In this case, the algorithm B in the TS model is deﬁned with FindElement′ instead of FindElement. This
change makes B ﬁnd the corresponding element to the label that is not previo usly given. The success
probability computation is almost identical, but incurs (2T + k)·
{T
N
)r
errors in the success probability
regarding the failure of FindElement′.8 If we carefully count the number t of the labels that are not given
before, the number of gates becomes q + tr and ∆ = r·
{T
N
)r
.
C.1 Lower bounds in the Random Representation GGM
Let L : ZN → S be the labeling function, which will be lazily sampled. W e pr ove the RR GGM variant
of Theorem 4.1 in this section.
Note that the proof of Theorem C.1 for the faithful case works well for the unknown-order group case.
In other words, it sufﬁces to focus on the algorithm’s behavi or to look for a new label that was not given to
the algorithm before.
Theorem C.2. LetAord be an order-ﬁnding algorithm overD(n)
prime in the random-representation GGM with the group
operation complexity T . It holds that
Pr
Aord,N,L
[
AGN
ord ()→ N
]
= O
( T 3
2n
)
.
Proof sketch. Suppose that t labels to queries that are not given to A before and also not corresponding to
⊥. W e let them ℓ1 = L(x1), ..., ℓt = L(xt) and x = ( x1, ..., xt). W e must maintain the representations of the
elements ofAord as a polynomial in Z[X1, ..., Xt] where Xi corresponds to xi. The deﬁnition of informative
collisions is a pair of elements that have the same labels butas the polynomials different, and their difference
is not included in the span of the previous informative colli sions. Note that the algorithm must ﬁnd at least
one informative collision. Let us assume that it is represen ted by
P (x1, ..., Xt) = a1X1 + ... + atXt + c = 0,
where we can assume that|ai|,|c|≤ 2T N by the same reason to the original proof.
W e make the encoding scheme for (N, x).
8If we assume that T ≤ N 1−1/c for some constant c > 0, then repeating r = 2 c times ensures that the probability of failure is
1/N2 for each FindElement′.
32

<!-- page 33 -->

Encode(N, x): It runsAGN
ord () and computes the ﬁrst informative collision c. It additionally includes x as a
part of the encoding. Note that the probability that M = P (x1, ..., xt) = 0 mod p for another n-bit
prime p is 1/p, and|P (x1, ..., xt)|≤ (t + 1)2T N 2. Let ℓ be the index of N among the divisor of M .
Decode(c, ℓ, x): If c =⊥, it outputs a random sample fromD(n)
prime. Otherwise, it recovers the ﬁrst informative
collision and plugs x to X1, ..., Xt to compute M = P (x1, ..., xt), and outputs the ℓ-th prime factor N′.
The encoding size is 3 log T− log log N + log
{|G|
t
)
+ O(1), which should be larger than log 2n
n + log
{|G|
t
)
+ logǫ.
Rearranging this concludes the proof.
33
