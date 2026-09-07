#!/usr/bin/env python3
"""Two-sample comparison of the SEALED J2 values against the executors' per-seed values (read after the seal)."""
import json, math, sys
import numpy as np
S=json.load(open(sys.argv[1]))
def welch(a,b):
    a=np.array(a,float); b=np.array(b,float)
    va=a.var(ddof=1)/a.size; vb=b.var(ddof=1)/b.size
    t=(a.mean()-b.mean())/math.sqrt(va+vb); df=(va+vb)**2/(va**2/(a.size-1)+vb**2/(b.size-1))
    return {'mean_a':float(a.mean()),'sd_a':float(a.std(ddof=1)),'n_a':int(a.size),'mean_b':float(b.mean()),'sd_b':float(b.std(ddof=1)),'n_b':int(b.size),'diff':float(a.mean()-b.mean()),'welch_t':float(t),'welch_df':float(df),'agree_within_2sigma':bool(abs(t)<2)}
cells={c['log2N']:c for c in S['cells']}
mine20=cells[20]['per_mixer']['murmur3_fmix64']; mine20s=cells[20]['per_mixer']['splitmix64']; mine24=cells[24]['per_mixer']['murmur3_fmix64']; mine24s=cells[24]['per_mixer']['splitmix64']
# executor values (from execution reports / summaries, read post-seal)
ex612_top20=[0.3905,0.3610,0.3879,0.3859,0.3672]          # RUN-001..005 summary basins.top_T_share (a=1/4)
ex869_top20=[0.4393,0.3686,0.3697,0.3991,0.3600]          # RUN-001..005-N20 a=0.25 global_oracle.top_T_share_8W
ex612_top24=[0.3998,0.3765,0.3889,0.4021,0.3820]          # RUN-013..017
ex869_top24=[0.3920,0.3795,0.4080,0.3772,0.3915]          # RUN-011..015-N24 a=0.25
ex612_cost24=[1.728,1.821,1.613,1.695,1.687]; ex869_cost24=[1.707,1.637,1.660,1.866,1.694]
ex612_cost20=[1.779,2.292,1.587,1.747,1.915]; ex869_cost20=[1.845,2.144,2.065,1.864,2.085]
ex612_P24=[1.229,1.138,1.375,1.315,1.158]; ex869_P24=[1.335,1.136,1.364,1.189,1.348]
ex612_P20=[1.269,1.245,1.296,1.253,1.628]; ex869_P20=[1.570,1.180,1.319,1.116,1.335]
out={}
out['topT_2^20_vs_612fb1']=welch(mine20['a_topT_share_over_N_cap8W']['values'],ex612_top20)
out['topT_2^20_vs_869870']=welch(mine20['a_topT_share_over_N_cap8W']['values'],ex869_top20)
out['topT_2^20_splitmix_vs_612fb1']=welch(mine20s['a_topT_share_over_N_cap8W']['values'],ex612_top20)
out['topT_2^24_vs_612fb1']=welch(mine24['a_topT_share_over_N_cap8W']['values'],ex612_top24)
out['topT_2^24_vs_869870']=welch(mine24['a_topT_share_over_N_cap8W']['values'],ex869_top24)
out['cost_2^24_vs_612fb1']=welch(mine24['b_scaled_cost_per_key']['values'],ex612_cost24)
out['cost_2^24_vs_869870']=welch(mine24['b_scaled_cost_per_key']['values'],ex869_cost24)
out['cost_2^24_splitmix_vs_612fb1']=welch(mine24s['b_scaled_cost_per_key']['values'],ex612_cost24)
out['cost_2^20_vs_612fb1']=welch(mine20['b_scaled_cost_per_key']['values'],ex612_cost20)
out['cost_2^20_vs_869870']=welch(mine20['b_scaled_cost_per_key']['values'],ex869_cost20)
out['cost_2^20_splitmix_vs_869870']=welch(mine20s['b_scaled_cost_per_key']['values'],ex869_cost20)
out['P_2^24_vs_612fb1']=welch(mine24['b_scaled_P_per_key']['values'],ex612_P24)
out['P_2^24_vs_869870']=welch(mine24['b_scaled_P_per_key']['values'],ex869_P24)
out['P_2^20_vs_612fb1']=welch(mine20['b_scaled_P_per_key']['values'],ex612_P20)
out['P_2^20_vs_869870']=welch(mine20['b_scaled_P_per_key']['values'],ex869_P20)
out['executors_cost_2^20_612fb1_vs_869870']=welch(ex612_cost20,ex869_cost20)
out['model_and_published']={'topT_2^20_murmur_over_0.39':mine20['a_topT_share_over_N_cap8W']['mean']/0.39,'topT_2^24_murmur_over_0.39':mine24['a_topT_share_over_N_cap8W']['mean']/0.39,
  'cost_2^24_murmur_pooled_minus_1.79':mine24['b_scaled_cost_pooled_over_keys']-1.79,'cost_2^24_splitmix_pooled_minus_1.79':mine24s['b_scaled_cost_pooled_over_keys']-1.79,'cost_2^24_all13_pooled_minus_1.79':cells[24]['b_scaled_cost_pooled_all_keys']-1.79,
  'cost_2^20_murmur_pooled_minus_1.79':mine20['b_scaled_cost_pooled_over_keys']-1.79,'P_2^24_murmur_mean_over_1.24':mine24['b_scaled_P_per_key']['mean']/1.24,'P_2^20_murmur_mean_over_1.24':mine20['b_scaled_P_per_key']['mean']/1.24,
  'inside_612fb1_G2_cost_band_0.18':abs(cells[24]['b_scaled_cost_pooled_all_keys']-1.79)<=0.18,'inside_869870_fixture_band_0.10_all13':abs(cells[24]['b_scaled_cost_pooled_all_keys']-1.79)<=0.10,'inside_869870_fixture_band_0.10_murmur_only':abs(mine24['b_scaled_cost_pooled_over_keys']-1.79)<=0.10,'inside_869870_fixture_band_0.10_splitmix_only':abs(mine24s['b_scaled_cost_pooled_over_keys']-1.79)<=0.10}
json.dump(out,open(sys.argv[2],'w'),indent=1)
for k,v in out.items():
    if 'welch_t' in v: print(f"{k}: mine {v['mean_a']:.4f}±{v['sd_a']:.4f} (n={v['n_a']}) vs {v['mean_b']:.4f}±{v['sd_b']:.4f} (n={v['n_b']}) diff {v['diff']:+.4f} t={v['welch_t']:+.2f} df={v['welch_df']:.1f} agree={v['agree_within_2sigma']}")
    else: print(k, {kk:(round(vv,4) if isinstance(vv,float) else vv) for kk,vv in v.items()})
