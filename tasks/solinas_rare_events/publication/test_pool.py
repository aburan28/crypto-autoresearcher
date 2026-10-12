"""Pure engineering fixtures for fixed-seed pooling; no scientific sampling."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from pool import pool


class PoolTests(unittest.TestCase):
    def test_pools_counts_and_refuses_duplicate_or_changed_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);runs=[]
            for index in range(2):
                run=root/str(index);run.mkdir();runs.append(run)
                design={'config':{'seed':f'engineering-pool-{index}','familywise_alpha':.001},'inputs':{'models':'engineering fixture'},'source_sha256':{'engine':'fixture'}}
                rows=[{'id':f'c{i}','rates':[{'cohort':a,'hits':index+1 if a=='selected' else 0,'windows':10} for a in ('selected','published','random')]} for i in range(3)]
                tests=[{'id':f't{i}','a_only':index+1,'b_only':0} for i in range(9)]
                tails=[{'cohort':a,'threshold':threshold,'hits':0,'windows':10} for a in ('selected','published','random') for threshold in (18,20,22,24,26,28,30,32)]
                values={'design.json':design,'completion.json':{'fixed_sample_complete':True},'verification.json':{'validity':'passed stated checks'},
                    'analysis.json':{'point_observations':2560,'candidates':rows,'primary_tests':tests,'tail_spectrum':tails,'ordinary_fields':[{'id':'f1','arm':'R','hits':index,'windows':10}]}}
                for name,value in values.items():(run/name).write_text(json.dumps(value))
            result=pool(runs,root/'pooled.json')
            self.assertEqual(result['rates'][0]['hits'],3);self.assertEqual(result['rates'][0]['windows'],20)
            self.assertAlmostEqual(result['paired_tests'][0]['p_two_sided_exact'],.25)
            self.assertEqual(result['ordinary_field_counts'][0]['hits'],1)
            self.assertEqual(result['point_observations'],5120)
            with self.assertRaises(ValueError):pool([runs[0],runs[0]],root/'duplicate.json')
            design=json.loads((runs[1]/'design.json').read_text());design['source_sha256']['engine']='changed'
            (runs[1]/'design.json').write_text(json.dumps(design))
            with self.assertRaises(ValueError):pool(runs,root/'changed.json')


if __name__=='__main__':unittest.main()
