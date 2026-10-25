# Draws diagram.svg/png: the two curves and what the lemma forbids. Run from this directory.
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig, ax = plt.subplots(figsize=(9, 4.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 5)
def box(x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", fc=fc, ec="#333", lw=1))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8)
box(0.2, 2.9, 3.9, 1.7, "E0: y² = x³ + x  (auxiliary curve)\nsupersingular, #E0(F_p) = p + 1\n2-adic valuation of p+1 = 96\ncyclic 2⁹⁶-part: the chain's kernel K and the\ncoset R + ⟨K⟩ live here, so V = x(R + ⟨K⟩) ⊂ F_p", "#fbe9e7")
box(5.9, 2.9, 3.9, 1.7, "E_P: P-256, y² = x³ − 3x + b  (target)\nordinary (trace t: 127 bits, odd)\n#E_P(F_p) = n, an odd prime\n2-division polynomial irreducible:\nno F_p-rational 2-isogeny, no 2-torsion point", "#e3f2fd")
ax.annotate("", xy=(5.8, 3.75), xytext=(4.2, 3.75), arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=2))
ax.text(5.0, 4.15, "no isogeny\nover any extension", ha="center", fontsize=8, color="#c0392b")
ax.text(5.0, 3.3, "(supersingular ≠ ordinary)", ha="center", fontsize=7, color="#c0392b")
box(0.2, 0.3, 9.6, 1.9, "What survives is only the coordinate trick: V ⊂ F_p is a set of x-values chosen through E0 and plugged into E_P's\nsummation polynomial S_{m+1}; from E_P's side V is an arbitrary subset that happens to have a short description.\n\nLemma (coset). If #E(F_p) = n is prime and K ⊂ E(F̄_p) has order coprime to n, then K ∩ E(F_p) = {O},\nso every coset R + K contains at most ONE F_p-rational point: kernel-coset factor bases cannot sit inside E_P(F_p).", "#f3f3f3")
fig.suptitle("PKM-style factor base vs P-256: where the group structure is, and where it is not", fontsize=9)
fig.tight_layout()
for e in ("svg", "png"): fig.savefig(f"diagram.{e}", dpi=150)
