# One M2 transport step, three formulations

TASK-20261005-32debd; archive owner TASK-20261005-ed2c6a. This is a
zero-run bounded definition search. Three formulations of the same source-to-target
operator transport were inspected; none is a finalist. No implementation,
experiment, independent review, security result or universal obstruction is claimed.

The supplied maps have type E -> E. Their matrices on E[N] can select an
integral alpha with alpha(P)=Q. That selection is not an operation on C.
The desired response is W=gamma(X) in C[N], where
gamma=phi_s alpha dual(phi_s). If W is actually evaluated, the public
scalar inverse gives Y=[D^(-1) mod N]W. The factor D must not be omitted:
gamma(X)=[D]phi_s(Q), rather than phi_s(Q).

| Formulation | Constructed prefix | Exact absent or expensive arrow | Actual output |
| --- | --- | --- | --- |
| F1 finite target frame | Source matrices and a public complementary point T on C[N] | Determine the calibrated u for which phi_s(Q)=T+uX | Tagged bottom, not Y |
| F2 quaternion word / evaluation DAG | Integral coordinates of alpha and a formal sandwich word | Turn a formal operator into a domain-labelled evaluator C -> C without phi_s or a correspondence | Tagged bottom, not a map |
| F3 unique public map lookup | Uniform finite replay of all D slope quotients | D public constructions, plus normalization; this recovers a connecting map at exponential cost | An evaluated matching map and its Y, conditionally on admitted honest inputs |

F1 makes the missing coordinate visible. Choose T with
e_N(X,T)=e_N(P,Q)^D. Every T+uX has the same pairing and gives a basis
(X,T+uX). In coordinates (X,T), the hypothetical transport matrix is
B_u=[[1,u],[0,1]]. The source matrix A gives the hypothetical target
matrix D B_u A B_u^(-1). Its action on X has coordinates D(u,1).
This is a family of algebraically consistent frames, not a family of honest
degree-D maps. The strict fiber lemma selects at most one honest frame but
does not compute its u. The source algebra acts on a module only after its
identification with the target module is supplied. Adding that identification
is precisely the missing target datum. Randomly guessing u has no uniform
all-input success guarantee beyond 1/N, conditional on a sampled complete frame.

F2 tries to keep the sandwich compressed. A word with two unevaluated map
symbols is a formal expression, not a circuit on C. Quaternion multiplication
produces source-algebra coordinates; it supplies neither an embedding in
End^0(C) nor evaluation at X. An abstract isomorphism of quaternion algebras
does not calibrate phi_s alpha dual(phi_s). Even an uncalibrated evaluated
End(C) basis would require the missing correspondence. Supplying a path,
ideal realization, orientation, Hom anchor, retained tau or sender map changes
the interface. No such object is imported here. A prospective restriction to
short, bounded-evaluation source circuits changes the acceptance law and still
does not supply the target evaluator.

F3 tests whether uniqueness itself can realize the word. A fixed program can
construct every public quotient, compare the normalized first image, recover
the unique matching map, then evaluate its dual, alpha and forward map.
This is a finite public connecting-map recovery, not a polynomial End(E)-only
transport. D=2^lambda iterations remain exponential even with one streamed
chain. Exact global model normalization adds its own unresolved cost; brute
finite-field normalization is a finite expensive fallback. The recovered chain
also permits a direct all-message slope decoder, with no secret ring use.
The actual partial prefixes of F1/F2 and full finite program of F3 are specified
and charged in transport-algorithm.yaml and correctness-and-cost.yaml.

The conditional singleton lemma remains intact: for compatible separable
degree-D f,g into the same normalized C agreeing on order-N P, a nonzero
f-g has degree at least N and at most 4D. N>4D gives f=g. Thus the complete
honest P1 fiber is {s} and its low-k residue count is 1. This establishes
uniqueness, including the target automorphism ambiguity, but not construction,
admission, uniform evaluation, actual-message polynomial decoding or secrecy.

The accepted law and all unresolved admission properties are frozen separately.
In particular the present convention is exactly L=lambda^2 total edges, with
one first edge and L-1 continuations. An earlier bare statement says both
"first" and "continue L steps"; that wording admits an L+1 reading. This packet
selects the total-L convention matching the prior word count and tau degree;
it does not claim the earlier inconsistency was already settled. An L+1 variant
would have different weights, tau degree and acceptance probability.

The single continuation remains OBL-CSTAR-TRANSPORT-1: construct a typed,
uniform target-response evaluator from exactly the declared source order and
one-column input, with admission, evaluation and actual-message costs. The
scope and clearing condition are in attack-gates.yaml. No second route is
launched. Primary texts were not newly retrieved; named scheme comparisons
are internal-source reports, and all three IDEA inputs remain proposed.
