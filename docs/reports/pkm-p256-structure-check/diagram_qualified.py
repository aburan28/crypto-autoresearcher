# Draws diagram_qualified.svg/png for QUALIFICATION-20261019: the corrected scope of the coset lemma. Run from this directory.
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig, ax = plt.subplots(figsize=(9, 4.0)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4.6)
def box(x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", fc=fc, ec="#333", lw=1))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8)
box(0.2, 0.4, 4.6, 3.1, "n ∤ |K|   (gcd(|K|, n) = 1)\n\nK ∩ E(F_p) = {O}\nso every coset R + K contains\nat most ONE F_p-rational point.\n\nCovers: the proposed 2-power chain\n(|K| = 2^L, n odd), every ℓ-power\nkernel with ℓ ≠ n, any such K.\nLemma as stated in the report.", "#e8f5e9")
box(5.2, 0.4, 4.6, 3.1, "n | |K| with E(F_p) ⊆ K\n\nK ∩ E(F_p) = E(F_p)  (all n points)\nso for R ∈ E(F_p) the coset R + K\ncontains ALL n rational points.\n\nExample: K = E(F_p), the F_p-stable\nsubgroup of order n; the separable\nquotient E → E/K maps every rational\npoint to O. Not excluded by the lemma;\nit gives no useful decomposition.", "#fff3e0")
ax.text(5.0, 4.05, "Corrected scope: K ∩ E(F_p) is {O} or E(F_p), because E(F_p) has prime order n", ha="center", fontsize=9)
fig.suptitle("Coset lemma for E(F_p) of prime order n — what it does and does not cover", fontsize=9)
fig.tight_layout()
for e in ("svg", "png"): fig.savefig(f"diagram_qualified.{e}", dpi=150)
