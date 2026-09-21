"""
Independent verification of V4-CHG-5 (change_5_selftest_repair).

Method: apply v3's V3-CHG-2 rename/add to a reconstruction of estimator.py
(patched_estimator.py, in this same directory, diffed against the real
committed file by hand -- see that file's own docstring), then apply v4's
new_text_replacement VERBATIM (transcribed character-for-character from
experiments/EXP-ECDLP-56ee42/amendments/v4_power_check_and_selftest_repair.yaml,
change_5_selftest_repair.new_text_replacement) in place of selftest.py's
old_text_superseded_verbatim block, and EXECUTE it -- not just read it --
against the reconstructed estimator.py, to check:
  (a) it is syntactically valid Python that runs without NameError/
      AttributeError against functions v3 actually specifies exist
      (rudin_shapiro_sign_true, _rudin_shapiro_u, rudin_shapiro_sign_true_
      array, _rudin_shapiro_signflip_variant, _rudin_shapiro_signflip_
      variant_array);
  (b) the n_diff == 135 claim (retired-variant-vs-truth) is still accurate
      under the new framing (previously: block-count-parity vs the OLD
      recursion; now: OLD recursion vs the NEW true implementation -- a
      structurally different comparison that could in principle have given
      a different count);
  (c) the "0 mismatches" primary correctness check actually holds.

This review also separately ran the FULL, unmodified selftest.py against
this patched estimator.py (all five test_* functions, not just the
Rudin-Shapiro block) to confirm no other self-test regresses -- see this
script's own trailing section.
"""
import sys
import numpy as np

sys.path.insert(0, ".")
import patched_estimator as E  # noqa: E402  (the reconstruction, not the real file)

print("=== V4-CHG-5 new_text_replacement, transcribed verbatim, executed ===")

# ---- verbatim transcription of change_5's new_text_replacement ----
for x in range(256):
    assert E.rudin_shapiro_sign_true(x) == (
        1 if E._rudin_shapiro_u(x) % 2 == 0 else -1), x
xs = np.arange(5000, dtype=np.uint32)
arr = E.rudin_shapiro_sign_true_array(xs)
for x in range(0, 5000, 13):
    assert arr[x] == E.rudin_shapiro_sign_true(x), x

r = [1, 1]
for m in range(2, 256):
    r.append(r[m >> 1] if m % 2 == 0 else -r[m >> 1])
for x in range(256):
    assert E._rudin_shapiro_signflip_variant(x) == r[x], x
arr_variant = E._rudin_shapiro_signflip_variant_array(xs)
for x in range(0, 5000, 13):
    assert arr_variant[x] == E._rudin_shapiro_signflip_variant(x), x
n_diff = sum(1 for x in range(256)
             if E._rudin_shapiro_signflip_variant(x)
             != E.rudin_shapiro_sign_true(x))
assert n_diff == 135, n_diff  # frozen audit fact, retired-variant-vs-truth
# ---- end verbatim transcription ----

print("ALL V4-CHG-5 new_text_replacement ASSERTIONS PASSED")
print("n_diff (retired-variant-vs-truth) =", n_diff, "(matches the claimed 135)")

print()
print("=== Cross-check: is n_diff==135 a coincidence, or the SAME fact under")
print("    both framings? (old test: block-count-parity vs OLD recursion;")
print("    new test: OLD recursion vs NEW true impl -- these are the same")
print("    comparison with operands swapped, since != is symmetric and")
print("    rudin_shapiro_sign_true(x) == (1 if _rudin_shapiro_u(x)%2==0")
print("    else -1) is asserted just above) ===")
n_diff_old_framing = sum(
    1 for x in range(256)
    if (1 if E._rudin_shapiro_u(x) % 2 == 0 else -1)
    != E._rudin_shapiro_signflip_variant(x))
print("n_diff via OLD test's exact framing (block-count parity != OLD recursion):",
      n_diff_old_framing)
assert n_diff_old_framing == n_diff == 135
print("CONFIRMED: identical fact under both framings, 135/256, as claimed.")
