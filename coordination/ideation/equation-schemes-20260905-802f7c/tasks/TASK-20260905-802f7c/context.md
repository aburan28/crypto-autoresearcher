# Seed context for TASK-20260905-802f7c (user-supplied; a pointer, not a citation, not evidence)

Recorded 2026-09-05 by session `coordinator-eqschemes-1` (worktree
`elliptic-curve-equations-5210ae`). Provenance: user-supplied, unverified,
comparison target only. The user's message consisted of one instruction line
followed by a pasted text rendering of the SafeCurves *Equations* page
(version 2013.10.14). The live page was fetched in the same session and stored
with its hash at `research/equation-schemes-20260905/retrieved-pages/safecurves-equation.html`
(sha256 `035dddc23bedb7754f8b54f1d2601b3a941509ce1d68d2b9537bb9dcb2602c58`);
the twenty "Result" values of the paste were compared with that page and with
a stdlib recomputation and agree (check E1 of
`research/equation_schemes_safecurves_20260905.md`).

## Instruction, verbatim

> Investigate novel equation schemes

## Pasted page, verbatim content (navigation links elided; tables kept exactly)

SafeCurves: choosing safe curves for elliptic-curve cryptography — Equations

There are several different ways to express elliptic curves over F_p:

- The short Weierstrass equation y^2 = x^3 + ax + b, where 4a^3+27b^2 is nonzero in F_p, is an elliptic curve over F_p. Every elliptic curve over F_p can be converted to a short Weierstrass equation if p is larger than 3.
- The Montgomery equation By^2 = x^3 + Ax^2 + x, where B(A^2-4) is nonzero in F_p, is an elliptic curve over F_p. Substituting x = Bu-A/3 and y = Bv produces the short Weierstrass equation v^2 = u^3 + au + b where a = (3-A^2)/(3B^2) and b = (2A^3-9A)/(27B^3). Montgomery curves were introduced by 1987 Montgomery.
- The Edwards equation x^2 + y^2 = 1 + dx^2y^2, where d(1-d) is nonzero in F_p, is an elliptic curve over F_p. Substituting x = u/v and y = (u-1)/(u+1) produces the Montgomery equation Bv^2 = u^3 + Au^2 + u where A = 2(1+d)/(1-d) and B = 4/(1-d). Edwards curves were introduced by 2007 Edwards in the case that d is a 4th power. SafeCurves requires Edwards curves to be complete, i.e., for d to not be a square; complete Edwards curves were introduced by 2007 Bernstein–Lange.

The rational points of a short Weierstrass curve are the pairs (x,y) of elements of F_p satisfying the equation, together with one extra "point at infinity". The rational points of a Montgomery curve are defined the same way. The rational points of a complete Edwards curve are the pairs (x,y) of elements of F_p satisfying the equation; there is no extra "point at infinity".

The following table shows the equations for various curves:

| Curve | Shape | Equation |
|---|---|---|
| Anomalous | short Weierstrass | y^2 = x^3+15347898055371580590890576721314318823207531963035637503096292x+7444386449934505970367865204569124728350661870959593404279615 |
| M-221 | Montgomery | y^2 = x^3+117050x^2+x |
| E-222 | Edwards | x^2+y^2 = 1+160102x^2y^2 |
| NIST P-224 | short Weierstrass | y^2 = x^3-3x+18958286285566608000408668544493926415504680968679321075787234672564 |
| Curve1174 | Edwards | x^2+y^2 = 1-1174x^2y^2 |
| Curve25519 | Montgomery | y^2 = x^3+486662x^2+x |
| BN(2,254) | short Weierstrass | y^2 = x^3+0x+2 |
| brainpoolP256t1 | short Weierstrass | y^2 = x^3-3x+46214326585032579593829631435610129746736367449296220983687490401182983727876 |
| ANSSI FRP256v1 | short Weierstrass | y^2 = x^3-3x+107744541122042688792155207242782455150382764043089114141096634497567301547839 |
| NIST P-256 | short Weierstrass | y^2 = x^3-3x+41058363725152142129326129780047268409114441015993725554835256314039467401291 |
| secp256k1 | short Weierstrass | y^2 = x^3+0x+7 |
| E-382 | Edwards | x^2+y^2 = 1-67254x^2y^2 |
| M-383 | Montgomery | y^2 = x^3+2065150x^2+x |
| Curve383187 | Montgomery | y^2 = x^3+229969x^2+x |
| brainpoolP384t1 | short Weierstrass | y^2 = x^3-3x+19596161053329239268181228455226581162286252326261019516900162717091837027531392576647644262320816848087868142547438 |
| NIST P-384 | short Weierstrass | y^2 = x^3-3x+27580193559959705877849011840389048093056905856361568521428707301988689241309860865136260764883745107765439761230575 |
| Curve41417 | Edwards | x^2+y^2 = 1+3617x^2y^2 |
| Ed448-Goldilocks | Edwards | x^2+y^2 = 1-39081x^2y^2 |
| M-511 | Montgomery | y^2 = x^3+530438x^2+x |
| E-521 | Edwards | x^2+y^2 = 1-376014x^2y^2 |

The following table shows the quantities in F_p that are required to be nonzero for these curves to be elliptic, i.e., 4a^3+27b^2 or B(A^2-4) or d(1-d):

| Curve | Elliptic? | Result |
|---|---|---|
| Anomalous | True | 11727648024975671349546803128441217519000050500482270354686052 |
| M-221 | True | 13700702496 |
| E-222 | True | 6739986666787659948666753771754907668409286105635143120250270071885 |
| NIST P-224 | True | 11286604486433664602000942456042078497941322427273965674759527357535 |
| Curve1174 | True | 3618502788666131106986593281521497120414687020801267626233049500247283921789 |
| Curve25519 | True | 236839902240 |
| BN(2,254) | True | 108 |
| brainpoolP256t1 | True | 57658212939451454047362440458822499786448049740370722175159801125840878929880 |
| ANSSI FRP256v1 | True | 79787647489891169820553912837105662027419783964415804103003411012672767526332 |
| NIST P-256 | True | 76665531554481589733451106912866963084117386858640348521070896428385330110353 |
| secp256k1 | True | 1323 |
| E-382 | True | 9850501549098619803069760025035903451269934817616361666987073351061430442874302652853566563721228910201652474408829 |
| M-383 | True | 4264844522496 |
| Curve383187 | True | 52885740957 |
| brainpoolP384t1 | True | 5181212714295366734216266753166056344803944016281454944474282600874932100420353077879019424596754753434846239416135 |
| NIST P-384 | True | 34547176980116681824645216591738245691976440597762634059085075689656433507713054265850219419421678489421763812122908 |
| Curve41417 | True | 42307582002575910332922579714097346549017899709713998034217522897561970639123926132812109468141778230245837569601494918393295 |
| Ed448-Goldilocks | True | 726838724295606890549323807888004534353641360687318060281490199180612328166730772686396383698676545930088884461843637361053496491001797 |
| M-511 | True | 281364471840 |
| E-521 | True | 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028149728152941 |

Are short Weierstrass equations required to have a=-3?

IEEE P1363 claims that y^2=x^3-3x+b provides "the fastest arithmetic on elliptic curves". Similarly, the NIST curves use y^2=x^3-3x+b "for reasons of efficiency". Similarly, Brainpool uses y^2=x^3-3x+b for its "arithmetical advantages". All of these are efficiency claims, not security claims, so they are outside the scope of SafeCurves.

Version: This is version 2013.10.14 of the equation.html web page.
