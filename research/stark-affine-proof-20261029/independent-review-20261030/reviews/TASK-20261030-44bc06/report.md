# Independent adversarial mathematical review — TASK-20261030-44bc06 / J1

Verdict: **holds, with the qualifications below**. This is an independent manual derivation from the two blinded mathematical inputs. It establishes the algebraic and functional statements; it does not verify any Lean theorem, Rust implementation, native receipt, serialization, security property, execution claim, or cost claim.

The mathematical inputs contain five numbered questions and a four-point refinement. I enumerate seven conclusions by treating the refinement's exact conjunction and its relationship to the global assertion separately. Throughout, a commutative ring has a multiplicative identity, may have zero divisors, and may be the zero ring. This convention is needed to interpret the designated coordinate `1`; a ring convention without an identity does not by itself define these probes. “Nontrivial” means `0 != 1`, equivalently that the ring has more than one element.

For fixed coefficients, write `A(x,y) = E(a,b,c,x,y) = ax + by + c`. Direct substitution gives

```text
A(0,0) = c
A(1,0) = a + c
A(0,1) = b + c
A(1,1) = a + b + c.
```

These four identities supply all the derivations below. They require neither division nor cancellation of a possibly nonzero zero divisor.

1. **Coefficient extraction holds in every such ring, including the zero ring.**

   By the additive group laws,
   `A(1,0)-A(0,0) = (a+c)-c = a`,
   `A(0,1)-A(0,0) = (b+c)-c = b`, and
   `A(0,0)=c`.
   Thus the requested ordered tuple is exactly `(a,b,c)`. Additive cancellation is valid in a ring with zero divisors.

2. **The three designated probes determine the coefficient triple and therefore the entire affine function.**

   Suppose `A=E(a,b,c,-,-)` and `A'=E(a',b',c',-,-)` agree at `(0,0),(1,0),(0,1)`. Equality at the origin gives `c=c'`. Equality at `(1,0)` then gives `a+c=a'+c`, hence `a=a'`; the remaining probe gives `b=b'`. Substitution into the defining expression yields `A(x,y)=A'(x,y)` for every `x,y`. Conversely, equality everywhere implies equality at these probes and hence equality of triples. There is no nontriviality assumption here: uniqueness is also true when there is only one possible triple.

3. **Multiplication cannot be represented by an affine triple on a nontrivial ring.**

   Suppose `ax+by+c=xy` for every `x,y`. At `(0,0)` this forces `c=0`; at `(1,0)` it then forces `a=0`; at `(0,1)` it forces `b=0`. Evaluation at `(1,1)` now asserts `0=1`. This contradicts nontriviality. The failure is therefore already witnessed among these four points, regardless of any other values of the function.

4. **Deleting the third designated probe can admit distinct affine functions.**

   In the ordered list `(0,0),(1,0),(0,1)`, the third probe is `(0,1)`. On any nontrivial ring, take `F(x,y)=0` and `G(x,y)=y`, with triples `(0,0,0)` and `(0,1,0)`. They agree at the two retained probes but differ at `(0,1)`, where their values are `0` and `1`. For example this works over both `F_2` and `Z/4Z`.

   There is no dependence on this ordering convention: deleting `(1,0)` admits `0` and `x`; deleting `(0,0)` admits `0` and `x+y-1`, which agree at `(1,0),(0,1)` and differ at the origin. Thus if “third” meant the third coordinate of the extraction tuple, namely the origin value, the deletion conclusion still holds. In the zero ring there cannot be distinct affine functions or distinct triples.

5. **Nontriviality is necessary for the nonrepresentation assertion.**

   In the zero ring, `0=1` and every element is zero: for any `r`, `r=r*1=r*0=0`. Consequently the sole coefficient triple `(0,0,0)` represents multiplication everywhere, since both sides are zero at the sole input pair. Combining this example with conclusion 3 gives the exact classification:

   ```text
   an affine representation of multiplication exists  iff  0 = 1;
   no affine representation exists                    iff  0 != 1.
   ```

   Thus removal of nontriviality produces a concrete counterexample, rather than a remaining unproved case.

6. **The exact four-point conjunction is equivalent to the zero-ring condition.**

   For a fixed triple define the requested conjunction `C(a,b,c)`. Substitution, independently of any implementation, gives exactly

   ```text
   C(a,b,c) iff
     c = 0 and a+c = 0 and b+c = 0 and a+b+c = 1.
   ```

   The first three equations force `c=a=b=0`, so this is equivalent to

   ```text
   c = 0 and a = 0 and b = 0 and 0 = 1.
   ```

   Conversely those four conditions imply each of the original four equations. In a unital ring `0=1` already forces every coefficient to be zero, so, for every fixed triple,

   ```text
   C(a,b,c) iff 0 = 1.
   ```

   Therefore the assertion `for every a,b,c, not C(a,b,c)` holds precisely for nontrivial rings. In the zero ring the conjunction is true for its sole triple, and its asserted negation is false.

   A second compact certificate is the mixed corner difference
   `A(1,1)-A(1,0)-A(0,1)+A(0,0)=0`.
   The same difference for `xy` is `1-0-0+0=1`. Agreement at all four corners would force `0=1`.

7. **The finite result strengthens the witness, but is not a strictly stronger classification within this ring family.**

   The finite assertion implies global nonrepresentation immediately: a function equal to multiplication everywhere must agree at the four designated points. It also gives a single fixed set of four inputs containing a disagreement for every affine candidate. Global nonrepresentation, viewed merely as a statement about arbitrary functions, does not by itself specify such a fixed witness set.

   Within the present family of commutative unital rings and affine expressions, however, both universal assertions are equivalent to `0 != 1`, by conclusions 5 and 6. Thus they are logically equivalent as properties of these rings. “Strengthens” is justified as an explicit finite localization of the obstruction; it must not be read as a strict implication between different classes of rings.

   All four corners are necessary for this particular uniform corner obstruction. Every subset of at most three of them can be matched by an affine expression. It suffices to give the four triples obtained by omitting one corner:

   | Omitted corner | Affine expression agreeing with multiplication on the other three |
   | --- | --- |
   | `(0,0)` | `x+y-1` |
   | `(1,0)` | `x` |
   | `(0,1)` | `y` |
   | `(1,1)` | `0` |

   Direct substitution gives the required values. In a nontrivial ring each displayed expression fails at the omitted corner: the discrepancy there is respectively `-1,1,1,-1`. This statement does not assert a minimum over every possible input selection.

**Exceptional rings and the difference between expressions, polynomials, and functions.** In characteristic two, including `F_2`, the implication `0=1` is still a contradiction in a nontrivial ring. The identity `-1=1` and the equation `1+1=0` do not turn either into zero. Both the direct four-equation derivation and the mixed difference therefore remain valid.

For a concrete zero-divisor ring, in `Z/4Z` the nonzero element `2` satisfies `2*2=0`. Nevertheless `A(0,0)=c` and the other corner identities are unchanged. The first three target values force the actual residue classes `a=b=c=0`; the last target value is the nonzero class `1`. At no point is cancellation by `2`, a field axiom, or an integral-domain hypothesis used.

The defining expression determines the formal polynomial `aX+bY+c` and its associated evaluation function. If the ring is nontrivial, that polynomial differs from `XY` by the nonzero coefficient of the monomial `XY`. Formal polynomial nonidentity alone would not prove inequality of the associated functions on a finite ring. For example, `X^2-X` is a nonzero formal polynomial over `F_2` but evaluates to zero at both elements. Also `2X(X-1)` is a nonzero polynomial over `Z/4Z` (its coefficients of `X^2` and `X` are both `2`) and evaluates to zero on the ring: every integer representative `t` has `t(t-1)` even. The four-point argument separately proves the required functional nonidentity. Conclusion 2 proves that, despite these general polynomial-function collisions, no two distinct affine triples induce the same function.

**Concrete known-false controls.** Each rejected assertion below has a fully specified witness; these are manual evaluations, not executed scientific trials.

| Known-false assertion | Counterexample and decisive evaluations |
| --- | --- |
| Two retained probes `(0,0),(1,0)` always determine an affine function. | Over `F_2`, `0` and `y` both give zero at the retained probes and give `0,1` at `(0,1)`. |
| Multiplication admits an affine representation on `Z/4Z`. | Any proposed representation must have `a=b=c=0` from the first three corners, then gives `0` at `(1,1)`, whose product is `1`. |
| No affine representation of multiplication exists even when the zero ring is allowed. | In the one-element zero ring, `a=b=c=x=y=0` always gives `E=xy=0`. |
| Three of the four product corners always suffice to refute every affine candidate. | Over `F_2`, omit `(1,1)` and take `E=0`; it matches all three remaining product values. The table in conclusion 7 handles every other omission. |
| Every affine candidate fails to match multiplication specifically at `(1,1)`. | Over `F_2`, the constant candidate `E=1` matches that product value; it instead fails at `(0,0)`. |
| Equality as functions over a finite ring implies equality as formal polynomials. | Over `F_2`, the nonzero polynomial `X^2-X` and the zero polynomial induce the same function. The affine subclass has the separate injectivity proof in conclusion 2. |

**Source bindings and review boundary.** All four files below were read only from `/workspace/pr-integration/review-2681-inputs/J1`. The two mathematical file hashes match the declarations in `ADMISSION.json`.

| Source | SHA256 of exact file bytes | Role |
| --- | --- | --- |
| `ADMISSION.json` | `623e08dd67cf9bbf3afccfe7b6e23f3cef81e5fe632c47b1fcfeb25abd71721c` | Administrative admission |
| `HANDOFF.json` | `5a0aeb0e111714567a71c420f169078daa97949563b8c36f2c421dc4a85bd781` | Administrative handoff |
| `blind-math.md` | `854236e982008c70057d981a072ed8683756734db3d1e5d1e2e325b9b6ed20b4` | Mathematical input |
| `blind-four-probes.md` | `5de718cd2f7c8e9d8b9b335fbf038ba07a65b538e1bd0aab2825ade42f01dfa6` | Mathematical input |

The declared published input commit is `77b2f0052d648f3753f788aa73e21fddc8d0f70b` and the declared claim commit is `fab6ed6e5b58ac68a60f7b3f756494714a4add5e`. These identifiers are administrative declarations; I did not inspect Git or independently authenticate commit contents.

Required generic runtime material was kept separate from mathematical input: the cloud-environment runtime skill (read twice; UTF-8 contents SHA256 `c23513e361a6f9dbe1c28e5c41de635f355469b4ec1740ae1cd2de1d38a91bd3`), the environment-status tool metadata (SHA256 `8ad5686ded504e59cf12398ba9be4543ed743966f1e768485c9ead43e9f93283`), and one environment-status response (SHA256 `e43ecb5aa299743029a10cc3b74fb14f3e93b5d2ef9542d64e5372a735b1854d`). For tool metadata and response these hashes bind their returned objects serialized by JavaScript `JSON.stringify`, UTF-8, without an added newline. None supplied mathematics. Session instructions and the task assignment are governing instruction channels, not external mathematical documents.

I read no producer repository, plan, prior, implementation, native receipt, source report, sibling report, history, or memory, and followed no links out of the blind view. No other reviewer or agent was consulted. No network mathematical material, solver, benchmark, scientific trial, or Lean/Rust build was used. Shell execution was confined to permitted file I/O, SHA256 binding, and output preparation/validation. There is no official scientific state change and no Git add, commit, or push.

The task requests `review-adversarial` with `xhigh` effort. This review uses the prospectively approved native/default-runtime fallback described in the administrative handoff and assignment. Serving model identity, inference provider, capacity, and effective reasoning effort are not authenticated. Accordingly `model_verified=false`, `fallback_used=true`, and the degraded provenance requirements are recorded in the attestation. I did not read the amendment file outside the view and make no claim of verified model identity, Opus execution, an inference CLI probe, or native Lean verification.

Outputs are restricted to this task's `report.md` and `attestation.json`. The assigned archival task is `TASK-20261030-92733b`; publishing and composition are outside this review.
