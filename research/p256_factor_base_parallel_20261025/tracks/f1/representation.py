"""Exact symbolic shape and operation accounting; no runtime benchmark."""
import itertools,json,math
from pathlib import Path
from forward import forward
from f1 import write
ROOT=Path(__file__).resolve().parent

def main():
    rec={'status':'PASS','scope':'symbolic representation/branch accounting; no measured speed comparison',
      'quadratic_stage_arithmetic_model':{'squarings':3,'general_multiplications':1,
           'small_constant_scalings':8,'additions_or_subtractions':11,
           'model':'share u^2,v^2,w^2,u*w; count each written small-scalar product separately'},
      'unexpanded_circuit':{'initial_unknowns':3,'auxiliary_unknowns_per_stage':3,
                           'quadratic_equations_per_stage':3,'terminal_equations':3,
                           'additional_s4_equations':1,'s4_total_degree':4},
      'expanded':[],'inverse_complete_state_formula':'binomial(N+2,3), N=number of distinct rational domain roots',
      'generic_membership_scheme_length_formula':'S^3, S=2^k',
      'generic_distinct_state_formula':'binomial(S+2,3)',
      'scaling_warning':'scheme length and inverse enumeration counts do not lower-bound all implicit solvers'}
    for k in range(1,6):
        equations,levels=forward(k,7)
        counts=[v['terms'] for v in levels[-1]['polynomials']]
        rec['expanded'].append({'k':k,'degree':1<<k,'terms_by_output':counts,
          'coefficient_slots':sum(counts),'three_variable_dense_degree_cap_slots':3*math.comb((1<<k)+3,3)})
        print(json.dumps(rec['expanded'][-1]),flush=True)
    rec['generic_diagonal_local_multiplicities']=[
       {'S':S,'all_equal_states':S,'two_equal_states':S*(S-1),'all_distinct_states':math.comb(S,3),
        'multiplicities':[1,3,6],'length':S**3,'distinct':math.comb(S+2,3)} for S in [2,4,8,16,256,2**96]]
    for row in rec['generic_diagonal_local_multiplicities']:
        assert row['all_equal_states']+3*row['two_equal_states']+6*row['all_distinct_states']==row['length']
    write(ROOT/'representation-01.json',rec)

if __name__=='__main__':main()
