# Digit-control calibration: two admission issues

Preparation TASK-20260905-e4fc90. Unreviewed analytical supplement, not an
experiment, accepted finding, independent review, or admission decision.
Prospective snapshot assignment: TASK-20260905-5e710a, not executed.

## Scope and provenance

The source proposal IDEA-20260901-b4e6eb was read in full. The hypothesis
H-ECDLP-07c7c6 and experiment EXP-ECDLP-a98ea9 were inspected at their
control, metric, approval and provenance sections, not treated as accepted
records. They are absent from this worktree but exist in reachable commit
09e153a7468c115bde656ce3eadf355c3e80b18a and as byte-identical untracked
copies in the main shared checkout. Sources and hashes are in sources.json.
The 2026-09-05 refresh also found the same four draft-input byte strings on
origin/main at de0d003cc9c1fde42da05b34b3bef4d7407bf372. Upstream publication
does not change the experiment's draft/unapproved flags or cure either
hypothesis's duplicate `status` key. This worktree has not merged that refresh;
five correction files and their registry have overlapping changes. Neither
version was replaced, and no archive or review is authorized by this packet.

The original TASK-20260904-2f7237 requires an independent session and four
separate deconfliction answers. This root supplement does not execute that
task, complete any of its deliverables, answer the full Q1-Q4 comparison,
take its claim, or change its queue. No hypothesis, source or run is edited.

## 1. The anomalous non-generator control has no nontrivial instance

The proposal's nearby-object control and Stage 5 ask for a prime-to-p
non-generator on an anomalous curve with #E(F_p)=p. Let S be such a point.
Its order n divides p by Lagrange's theorem. Since p is prime, n is 1 or p.
The requirement gcd(n,p)=1 leaves only n=1, hence S=O.

Thus the proposed replacement does not supply a nontrivial prime-to-p
positive control. The identity has no finite affine x-coordinate, so an
affine-digit or x-difference statistic on it also needs an explicit domain
extension. Even if such an extension is defined, a singleton input cannot
demonstrate discrimination among nontrivial points. This observation does
not invalidate ordinary prime-to-p lifting, say anything about a successful
anomalous-curve method, or close the digit-statistic research direction.

The suggestion was inherited from validation-report.yaml F-4's forward
guidance and erratum section D.6. Those passages call it a design question,
not a demonstrated working calibration. The later proposal and hypothesis
adopt it as a control; its nontrivial domain must be repaired before use.

External provenance: retrieved. Michel Goemans, MIT 18.310 notes,
*Modular Arithmetic and Elementary Algebra*, Theorem 1 and the element-order
corollary, page Algebra-6 (PDF page 6), read 2026-09-05:
https://ocw.mit.edu/courses/18-310-principles-of-discrete-applied-mathematics-fall-2013/f348af83c95da4719f344b34ac310523_MIT18_310F13_Ch14.pdf
The specialization above is this preparer's inference, not a claim that the
notes discuss this experiment.

## 2. Mixture weight is not automatically majority advantage

EXP-ECDLP-a98ea9's dynamic_range_demonstration specifies weights
w in {1, 0.2, 0.06, 0.02} and calls their advantages approximately
{0.5, 0.1, 0.03, 0.01}. It does not specify a mixing kernel sufficient to
derive those ground truths. A gate that increases its threshold when a
mislabelled planted rung is not recovered can confuse incorrect calibration
with poor estimator resolution.

Here is an explicit natural mixing model showing why the distinction
matters. This is a mathematical diagnostic model, NOT an assertion about an
unimplemented mixing rule, not a measurement of the source's s-label ladder,
and not permission to change that ladder.

Let G be a finite abelian group of odd order n. Fix g:G->{-1,+1}.
Independently for each x choose B_x~Bernoulli(w) and an unbiased sign R_x.
Freeze all draws once and define the fixed statistic

    f(x) = B_x g(x) + (1-B_x) R_x.

In particular E f(x)=w g(x); different point labels are independent.
Draw X,Y independently and uniformly from G, including zero. Write

    mu_f = E_X f(X),
    tau_f = E_{X,Y} f(X) f(Y) f(X+Y),
    q(f) = max_F Pr[f(X+Y)=F(f(X),f(Y))],
    p_max(f) = (1+|mu_f|)/2,
    Delta(f) = q(f)-p_max(f).

F ranges over binary combining rules; this is the population majority
statistic. It is not a predictor supplied with an unknown scalar.

### 2.1 Majority depends on a triple moment

Pairwise independence of X,Y,X+Y and indicator expansion give

    Pr[f(X)=a,f(Y)=b,f(X+Y)=c]
      = [1+mu_f(a+b+c)+mu_f^2(ab+ac+bc)+abc tau_f]/8.

Maximizing over c for each a,b yields

    q(f) = 1/2 + (1/8) sum_{a,b=+-1}
                  |mu_f + mu_f^2(a+b) + ab tau_f|.                (1)

There is also an exact separation of imbalance from the triple moment.
For u_+=max(u,0), the two identities
|A+B|+|A-B|=2 max(|A|,|B|) give

    q(f) = 1/2 + [max(|mu_f+tau_f|,2 mu_f^2)
                         + |mu_f-tau_f|]/4,

    Delta(f) = (|tau_f|-|mu_f|)_+/2
                 + (2 mu_f^2-|mu_f+tau_f|)_+/4.                (1a)

For the first equality combine the a=b terms of (1) using
A=mu_f+tau_f and B=2 mu_f^2, then add the two a=-b terms.
For the second, write max(A,B)=A+(B-A)_+ with A=|mu_f+tau_f|,
and use |mu_f+tau_f|+|mu_f-tau_f|=2 max(|mu_f|,|tau_f|).

The second term in (1a) lies between zero and mu_f^2/2. A nonzero
triple moment therefore need not yield positive excess over the marginal
baseline: Delta is exactly zero whenever |tau_f|<=|mu_f| and
|mu_f+tau_f|>=2 mu_f^2. These are sufficient conditions for a fixed
statistic, not a probability assertion about the random mixture. This makes
clear why tracking only E tau_f is not a finite-size calibration certificate.
For the constant statistic mu_f=tau_f=1, both terms vanish as required;
formally at mu_f=0 the identity reduces to Delta=|tau_f|/2. An odd-order
binary table cannot have mu_f=0 exactly, so the latter is an algebraic
boundary check, not an available balanced fixture in this domain.

In particular the triangle inequality implies

    |Delta(f) - |tau_f|/2| <= |mu_f| + mu_f^2/2.                 (2)

These definitions and the indicator identity extend the root's earlier
unreviewed binary-majority manuscript, cited internally in sources.json.
They have not received an independent rederivation.

### 2.2 Exact mixture law, including coincident points

If x,y,x+y are distinct, the expected triple product is
w^3 g(x)g(y)g(x+y), not w times that product. Coincident triples must not
be discarded. They occupy x=0, y=0 or x=y, with the common origin counted
only once. For odd-order G, x->2x is a bijection. Their correction gives

    E_f tau_f
      = w^3 tau_g
        + (w-w^3)[n mu_g + (2n-2)g(0)]/n^2.                    (3)

Derivation of the bracket: nonzero x=y contributes
sum_{x!=0} g(2x) = n mu_g-g(0). The two nonzero axes contribute
2(n-1)g(0). The origin contributes g(0). Their sum is
n mu_g+(2n-2)g(0). This also checks w=0 and w=1 exactly.

Equation (3) is an expectation over the frozen random statistic. One must
NOT insert expected moments into (1) and call the result E q: the maximum
and absolute values are nonlinear.

### 2.3 A finite-size error bound for a genuinely nearly balanced plant

We can control that last distinction without treating n^2 ordered pairs as
independent samples. Var(mu_f)<=1/n. For tau_f, disjoint sets of point
labels give zero covariance. Each triple uses at most three labels; at most
9n other ordered-pair triples share one of them. Every covariance has
absolute value at most 1. Consequently Var(tau_f)<=9/n.

Cauchy-Schwarz and (2) therefore give the conservative bound

    |E Delta(f) - |E tau_f|/2|
      <= w|mu_g| + w^2 mu_g^2/2 + 5/(2 sqrt(n)) + 1/(2n).       (4)

This is deliberately a loose finite bound, not a confidence interval for
the draft's bootstrap. The randomness unit is the point-labelled table, not
an independent draw for every pair in its full population enumeration.

For a checkable diagnostic plant take G=Z/(4m+1)Z and g positive exactly
on {-m,...,m}. With n=4m+1, mu_g=1/n, g(0)=1, and

    tau_g = (n^2+1)/(2n^2).

For completeness, writing s=2m+1, the number of ordered x,y in the positive
interval with x+y also in it is M=3m^2+3m+1. Expanding
(2*1_S(x)-1)(2*1_S(y)-1)(2*1_S(x+y)-1) gives
tau_g=(8M-12s^2)/n^2+6s/n-1, which simplifies to the displayed expression.

Equations (3)-(4) show, for fixed w along this family,

    E Delta(f) = w^3/4 + O(n^{-1/2}),                           (5)

not w/4. The following are formula specializations of this diagnostic model,
not measured rungs and NOT replacements for the draft's target values:

| w | Asymptotic E Delta under pointwise mixing | Fraction of full-signal limit |
|---:|---:|---:|
| 1 | 0.25 | 1 |
| 0.2 | 0.002 | 0.008 |
| 0.06 | 0.000054 | 0.000216 |
| 0.02 | 0.000002 | 0.000008 |

The finite-size qualification is consequential. For any diagnostic instance
with n <= 2^30, the term 5/(2 sqrt(n)) in (4) alone is at least
approximately 0.0000763, larger than the 0.000002 limiting excess in the last
row. Thus this conservative bound does NOT certify that row's finite-size
effect at those sizes. This is a limitation of the present bound, not a lower
bound on estimator error and not evidence that a smaller effect is
undetectable. A sharper bound or separately approved calibration would be
needed before treating that asymptotic row as a known finite-size rung.

For the draft's uncentered binary interval, the previous manuscript already
warns that the full-signal control need not have positive majority excess.
The centered interval here is intentionally a different, explicit diagnostic
plant with a nonzero limiting excess. No value in this table is attributed
to the original draft or to a run.

### 2.4 A different mixing kernel has a different meaning

Choosing the WHOLE statistic as g with probability w, otherwise a random
function, gives a linear mixture of expected advantages. But each realized
statistic belongs to one of two arms; it does not automatically give a fixed
intermediate rung. Resampling labels on every query is yet another object:
it is no longer the same fixed point statistic.

Thus the needed amendment is not to mechanically replace w by w^3. Freeze
the kernel, alphabet, base plant, marginal baseline, randomness unit and
target population first; then derive or independently certify each rung's
actual effect. Changing the calibration threshold cannot cure a missing
ground-truth derivation.

## 3. Scope checks before any successor is admitted

- Baseline: (3) returns zero at w=0 and tau_g at w=1.
- Collision audit: x=0, y=0 and x=y are counted explicitly; odd order is used
  only for bijectivity of doubling in the closed-form correction.
- Quantifiers: g is fixed, labels are sampled independently per point and
  then frozen, pairs are uniform, and expectation in (3)-(5) is over label
  tables. This is not an identity for each realized table.
- Nearby objects: constant g requires the marginal term in (2); whole-table
  mixing is a separate control against falsely claiming every mixing model
  has a cubic law.
- Ceiling: these are generic finite-group calibration statements. They
  construct no inexpensive elliptic statistic, supply no scalar-recovery
  procedure, move no complexity exponent and establish no breakthrough.
- Novelty is unverified. No new experiment, simulation, numerical sweep,
  formal proof certificate, independent review or scientific transition
  occurred. Formula specializations are not experimental observations.

Before spending on the draft's digit ladder, require a nontrivial,
assumption-compatible positive control and a precisely calibrated planted
ladder. The binary-majority calibration issue, the geometric degree gap, and
the historical certificate-coverage issue remain separate. The four
certificate errors remain in this local tree; upstream has since registered
summary-completion manifests explicitly without arithmetic re-verification.
Those metadata changes do not supply the returned tail scalars missing from
the earlier artifact inventory. This packet does not validate or reject the
upstream corrections, and it does not report an upstream full-ledger check.
The full deconfliction/admission decision is still outstanding.
