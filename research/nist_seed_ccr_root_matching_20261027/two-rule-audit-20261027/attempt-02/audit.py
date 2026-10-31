"""Cross-check every feature, alias, exact fit and non-fit collision witness."""
import hashlib,json,pathlib
D=pathlib.Path(__file__).resolve().parent

def main():
 a=json.loads((D/'bitset-result.json').read_text());b=json.loads((D/'rowwise-result.json').read_text())
 for key in a:
  if key not in ('method','elapsed_seconds_diagnostic'):assert a[key]==b[key],key
 for suffix in ['columns.json','atoms.json','signatures.json','witnesses.u16le']:
  assert (D/('bitset-'+suffix)).read_bytes()==(D/('rowwise-'+suffix)).read_bytes(),suffix
 out={'status':'PASS','complete':True,'feature_columns_equal':True,'all_pairs_and_truth_tables_equal':True,'all_collision_witnesses_equal':True,'counts':{k:a[k] for k in ['cohort','published','omitted','streams','atoms','signatures','pairs','truth_functions_examined','robust_pairs','possible_pairs','robust_functions','possible_functions']},'limitations':['Finite two-atom library only; not all mathematically possible pairs of rules.','All labels and imported observations were already visible; no p-value, out-of-sample or historical attribution claim.','Possible fits allow unknown inputs to vary rowwise and need not have a jointly realizable mathematical completion.','Shared source imports are re-used observations, not independently repeated historical executions.'],'historical_criterion_identified':False}
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
