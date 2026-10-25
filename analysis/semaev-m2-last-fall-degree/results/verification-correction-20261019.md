# Correction: dimensions certified by the closure checker

Recorded 2026-10-19. This corrects the interpretation of the closure-certificate
table in [`verification.md`](verification.md), at commit
`e64f8b401b6f0d5729d68f726f6ef5687ec3ccbc`. The original file has SHA-256
`c2d5c6ae3bd5d5ce797daf3432b0bd82e460c60378ec3fca206b0c8b8902ded0` and remains
unchanged. This correction records no new scientific run or result.

The sentence saying that `nq` is the codimension of $W_4$ which the certificate
proves, and the two dimension-column labels, overstate the independent check.
By Proposition 1.5 of the [theorem dossier](../theorem-dossier.md), an accepted
map $\pi$ establishes $W_4(F)\subseteq U$, where $U=\ker\pi$. Surjectivity gives
$\operatorname{codim}U=\mathrm{nq}$. Therefore the independently certified
relations are

\[
\operatorname{codim}W_4(F)\ge\mathrm{nq},\qquad
\dim(W_4(F)\cap B_{\le3})\le\dim(U\cap B_{\le3}).
\]

The table should be read as follows. All numeric values are copied from the
original record; their interpretation is corrected here.

| instance | certified lower bound on $\operatorname{codim}W_4$ | certified upper bound on $\dim(W_4\cap B_{\le3})$ |
|---|---|---|
| T33a, T33b | 4888 | 2968 |
| R35a, R35b, U35a, U35b | 5287 | 3885 |
| Q35a, Q35b | 5287 | 3885 |
| P45a | 12742 | 8950 |
| C19a | 9253 | 7000 |
| C19b | 6817 | 7420 |
| R37a, R37b | 10066 | 4329 |

The producer reports that $U=W_4$ and supplies the corresponding exact
dimensions. Acceptance by `cert_check.py` does not independently establish
that equality: the checker verifies containment in a closed subspace and
does not verify derivations proving every vector of $U$ belongs to $W_4$.
Exact-dimension claims based on implementation A retain that provenance.

For example, in the Boolean ring on $x,y$, take $D=2$ and $F=\{xy+1\}$.
Then $W_2(F)=\operatorname{span}\{xy+1\}$ has dimension 1. Evaluation at
$(1,1)$ maps every basis monomial $1,x,y,xy$ to 1. Its kernel $U$ has
dimension 3, contains $F$, and is closed under the multiplications checked
by Proposition 1.5; the map is onto and sends 1 to a nonzero value.
This valid certificate has $\operatorname{codim}U=1$ while
$\operatorname{codim}W_2=3$. Also $\dim(U\cap B_{\le1})=2$, while
$\dim(W_2\cap B_{\le1})=0$. Thus acceptance alone cannot prove either
dimension equality.

The nonmembership conclusion $1\notin W_4$ still follows from an accepted
certificate with $\pi(1)\ne0$. The Q35a/Q35b inference using the lower bound
$\operatorname{codim}W_4\ge5287$ and the separately reported solution counts
also uses precisely the inequality that the checker establishes. This
correction neither reruns those counts nor independently replays the
original certificates; their recorded provenance remains unchanged.
