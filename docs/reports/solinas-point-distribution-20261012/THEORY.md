# What uniform random curve models already tell us

Derived algebra for p > 3. These formulas apply to uniformly drawn coefficients
A,B conditioned on a nonsingular short-Weierstrass model, which is this task's
curve population. They do not describe a fixed curve or an arbitrary special
curve family. Finite exhaustive software checks are recorded separately in
`theory-check.json`; the argument below gives the general derivation.

For one coordinate x, x³+Ax+B is uniform in F_p when A,B are uniform, before
excluding singular models. Consequently, its quadratic character chi has
mean zero and second moment (p-1)/p. For two distinct coordinates x,z, the
map (A,B) -> (x³+Ax+B, z³+Az+B) is invertible: its determinant x-z is nonzero.
Those two values, and their characters, are independent. This is an exact
two-coordinate fact, not independence of every coordinate jointly.

Write t = -sum_x chi(x³+Ax+B). Before singular-model exclusion, E[t]=0 and
E[t²]=p-1. This uses the independent pairs and the p character variances.

There are exactly p singular coefficient pairs: A=-3r², B=2r³ for r in F_p.
Their cubic is (x-r)²(x+2r). At r=0 its trace is zero; at nonzero r its trace
is chi(3r), whose square is one. Thus excluding the singular pairs subtracts
p-1 from the total trace-square sum p²(p-1), and leaves p²-p models. Hence

E[t] = 0,

E[t²] = (p²-1)/p,

E[t²/(4p)] = (1-1/p²)/4.

For cubic roots, the average number Z over all coefficient pairs is one:
each x fixes B=-x³-Ax for p choices of A. Singular models have one distinct
root at r=0 and two at other r, totalling 2p-1 roots. Nonsingular-model root
sum is therefore p²-(2p-1)=(p-1)², giving E[Z]=(p-1)/p.
Since liftable x count is (p-t+Z)/2,

E[x coverage] = 1/2 + (p-1)/(2p²).

The implications are useful for interpretation. In a uniform random model
population, the average coverage and trace-square metric already have nearly
fixed expectations for every prime of a given size. Seeing similar averages
in sparse and random primes is therefore expected. An interesting prime-family
effect would have to concern other distribution features, higher moments,
conditional curve classes, or reproducible local patterns. The current
prespecified window and bin metrics provide direct measurements of some such
features; their means do not exhaust every possible distribution difference.

The coordinate map x'=u²x, y'=u³y preserves N and the group up to isomorphism,
while changing numerical x positions. Distinguish invariant point-count
features from coordinate-dependent bins, gaps and correlations. No statement
here concerns scalar recovery or ECDLP resistance.

Sources: internal derived algebra in this session; independent scalar
enumeration in `theory-check.py`, with exact retained outcomes. No unverified
literature citation is used as support.
