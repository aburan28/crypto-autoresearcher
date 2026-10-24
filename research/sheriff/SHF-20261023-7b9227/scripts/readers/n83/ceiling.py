"""Method-ceiling model (reader's model, not a measured bound), from the gated probe law: every relation and the
target cost r/(166E) probes on a root index of E entries, independent of the number K' of unknown log columns.
Cold(K', E) = c_b*E + (K'+1)*phi*r/(166E)*c_p + F.  min over E: 2*sqrt((K'+1)*phi*(r/166)*c_b*c_p) + F.
Per-op costs from run 39527997793 (current row, AMD EPYC 9V45): c_b = index_build_ms / root entries,
c_p = rank_stage_ms / rank probes, F = cold path minus index build minus online (self-test, base load, LA, misc).
Validation: predict #985's three arms (K'=600, 60, 16) with that run's own c_p, compare to measured rank stage."""
import json, math
r = 8569786107849059; L = r / 166
# current row (run 39527997793), from rederive_1013.out / band_1013.out / row wall_ms
rank_ms, rank_probes = 2806.5, 29627704          # mean kM38RF rank stage, mean rank probes per process
E = 30366551; index_ms = 3246.3; cold_wo_rank = 4467.0; online_ms = 158.6; rho_cold = 1853.5
c_p = rank_ms / rank_probes * 1e-3                 # s per probe
c_b = index_ms / E * 1e-3                          # s per root entry
F = (cold_wo_rank - index_ms - online_ms) * 1e-3   # s
phi = rank_probes / 16 / (L / E)                   # measured probes per relation over law
out = dict(c_p_ns=round(c_p * 1e9, 1), c_b_ns=round(c_b * 1e9, 1), F_s=round(F, 3), phi=round(phi, 4), rho_cold_s=rho_cold / 1e3)
def cold(K, E_, ph=phi): return c_b * E_ + (K + 1) * ph * L / E_ * c_p + F
out['model_current_K16_E_current_s'] = round(cold(16, E), 3)
out['measured_current_s'] = 7.2735
rows = {}
for K in (0, 1, 4, 16, 60, 600):
    Eopt = math.sqrt((K + 1) * phi * L * c_p / c_b)
    m = 2 * math.sqrt((K + 1) * phi * L * c_b * c_p)
    rows[K] = dict(E_opt=round(Eopt), cold_opt_no_F_s=round(m, 3), gap_no_F=round(m / (rho_cold / 1e3), 3),
                   cold_opt_with_F_s=round(m + F, 3), gap_with_F=round((m + F) / (rho_cold / 1e3), 3))
out['ceiling_by_K'] = rows
# validation against #985 (run 39305259093): per probe 104.63 ns (kP), 105.03 (kM38), 104.37 (kM10); law per relation
v = {}
for name, K, ns, law, meas in (('kP', 600, 104.63, 1727857, 108021.2), ('kM10', 60, 104.37, 1731124, 11460.5), ('kM38', 16, 105.03, 1700069, 2749.8)):
    v[name] = dict(predicted_rank_ms_at_law=round(K * law * ns * 1e-6, 1), measured_rank_ms=meas)
out['validation_985_rank_stage'] = v
json.dump(out, open(__file__.replace('.py', '.out'), 'w'), indent=1); print(json.dumps(out, indent=1))
