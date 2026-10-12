# Notation lock — EXP-BINSTD-38e4ad (HOLD-S)

| Symbol | Meaning                         | Forbidden overload                          |
|--------|----------------------------------|---------------------------------------------|
| **n**  | Field extension degree (=\|⟨τ⟩\| on Koblitz) | Never use n for Semaev arity                |
| **m**  | Semaev / decomposition arity     | Never use m for \|⟨τ⟩\| or field degree     |
| **l**  | Factor-base / window dimension  | —                                           |
| **V**  | Window subspace of F_{2^n}      | —                                           |
| **τ**  | Absolute Frobenius (x ↦ x²)      | —                                           |

Frozen Stage 1 cell: **n=17**, **m=2**, **l=8**.

Source IDEA-20260922-2a3771 mixed n/m in places; this experiment and all
artifacts under `experiments/EXP-BINSTD-38e4ad/` obey the lock above.
