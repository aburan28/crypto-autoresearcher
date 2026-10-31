# Blind finite-profile review: TASK-20261031-9a6bc2

## Derivation

For either supplied system, write (F_m=\{x^m,x^m+x\}), with (m=D) for (G_D) and (m=D+1) for (H_D). Both generators have degree (m) because (m\ge2). Their difference is (x), so ((F_m)=(x)).

For (i<m), no generator is admitted. The zero space is closed under the stated degree-bounded multiplication rule, hence minimality gives (V_{F_m,i}=0). For (i\ge m), subtracting the two admitted generators gives (x\in V_{F_m,i}). Multiplying (x) by any polynomial (q\in k[x]) with \(\deg(xq)\le i\) gives every multiple of (x) of degree at most (i). Conversely, every admitted generator and every subsequent linear combination or polynomial multiple belongs to ((x)), and the degree cap remains (i). Thus

\[
V_{F_m,i}=\begin{cases}
0,&i<m,\\
(x)\cap k[x]_{\le i},&i\ge m.
\end{cases}
\]

In particular (d_x=m). For every nonzero (f\in(F_m)=(x)), (f\in V_{F_m,\max(m,\deg f)}). The witness (x), whose degree is (1<m), rules out every (d<m) in the definition of (d_F). Therefore (d_{F_m}=m): specifically, (d_{G_D}=D) and (d_{H_D}=D+1).

## Finite-profile boundary and false controls

The profiles (\{V_{F,i}:0\le i\le D-1\}) are identical for (G_D) and (H_D): every space is zero. Both ideals are ((x)). Knowing this common ideal and the absence of (x) through (D-1) proves the lower bound (d_F\ge D). The profile alone does not supply that ideal-membership witness, so this lower-bound inference explicitly uses the supplied systems.

The proposed implication “no fall through (D-1) means no later fall” is false: (G_D) yields (x) at degree (D), while (H_D) yields it at degree (D+1). The proposed cutoff (d_F=D) for every system with this profile is also false, with (H_D) as the control. Indeed (F_m) for any (m\ge D) has this same profile and ideal but (d_{F_m}=m), so the finite profile gives no finite upper bound on (d_F). This is a logical extension of the same symbolic derivation, not an experimental observation.

The generator degrees in a full system description distinguish (G_D) from (H_D). The indistinguishability claim applies to the truncated (V)-profile and common ideal, not to their full input lists.

## Evidence and limits

The raw algebraic checks are in [raw/derivation.md](raw/derivation.md). They are symbolic consequences of the two permitted inputs; no scientific trials, code inspection, Lean proof, or Cargo build was performed. The derivation relies on the supplied definition of (V_{F,i}), including its degree cap. It makes no claim about finite-profile behavior without a known ideal witness.

Input SHA-256: `e4c3a431ef3850a5868de9cd052328a57cb2d60b5690f1ca9029116234de114e` for `blind-input.yaml` at `adb26ef1295b2d97d6b8328875670c866e602377`.
