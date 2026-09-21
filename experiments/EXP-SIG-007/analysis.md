
## COMPLETION SECTION (2026-07-26)

### Measurement complete
state.json: next_col=778,394=ncols, rank_acc=**265,950**, done=true, 76 carries, secs_total=10,806.2.
sum(npiv over 76 carries)=265,950==rank_acc (asserted at every rebuild; carry_075 npiv=947, sha256-verified, mirrored as git blob 9a4e0452…).

### FINAL numbers (verified 2026-07-26, sage re-derivation from s1_vectors.pkl)
- rank(K5)=**10,373** (|K5|=10,374=nrows−sr_pred; exactly one dependent K5 column)
- rank(K5∪F3)=**11,173** → A3_5=**800** ✓ matches EV records
- rank(K5∪F3∪F4)=**11,780** → union-minus-kernel =**1,407** ✓ matches recorded A4_5 (union convention; finer split: A3_5 800 + F4-only 607)
- **deficit_5 = 268,674 − 265,950 = 2,724**
- **extra_5 = (279,048 − 265,950) − 10,373 = 2,725**  (= deficit_5+1, the +1 being the single dependent K5 column)
- **residual_5 = 2,725 − 1,407 = 1,318**  equivalently (nrows − rank) − rank(K5∪F3∪F4) = 13,098 − 11,780

### Saturation-onset telemetry (from state.json units, driver-written)
Rank froze at 265,950 from **col 454,000** onward (unit 92, j1=454,000; NOT ~519,000 as earlier estimated). Tail: cols [454,000, 778,394) = 324,394 columns, 65 consecutive k=0 units, each with real reduce work (~101–111 s recorded per unit). Unit 92 = the final pivot burst: cols [449,000, 454,000), k=947.

### Unexpected observation (rule 8, for idea-generator)
Pre-saturation plateau: cols [364,000, 449,000) — 85,000 consecutive fully dependent columns (17 k=0 units) immediately BEFORE the 947-pivot burst at [449,000, 454,000). A dense dead zone followed by a sharp final burst. Recorded, not explained.

### Two-partition control — IN PROGRESS (unmodified pinned instrument, blob 34ce16d5)
Split at 389,197. Both directions run as checkpointed staircase runs against crafted workdirs:
- **C-forward** (B=[389,197,778,394) against E_A=carries 0..74): 649,197/778,394 (83%). Reproduced the 947-pivot burst exactly, at [449,197, 454,197). Expect completion rank_acc=265,950. ~1 fire remaining.
- **C-reverse** (all cols against E_B=carry_075): 80,000/778,394 (10%), rank re-derived 80,732 so far. Expect 265,950. ~2–3 fires.
Pass criterion (both): final rank_acc == 265,950 ⇒ rank(A)+rank(B|A)=rank(B)+rank(A|B)=265,950 ⇒ intersection 0 ⇒ no cross-partition double-counting ⇒ rank claim FINAL. Any other result invalidates the cell at the recorded failing unit.
Resume: trigger next fire on automation_693aa041 (C-forward, work=control_fwd, fires_dir=fires) / automation_707000ac (C-reverse, work=control_rev, fires_dir=fires_rev), runInput per AUTOMATION.md; fire_budget 2700 fits the 3600 s timeout cleanly.

### Engine-level control (historical, receipted)
C9b staircase engine validation at n=12 seed 2 (two chunk sizes + resume identity) passed in earlier anchor runs (CLOSURE_ANCHORS receipts).
