"""Engineering checks use a distinct seed; no fresh scientific seed is drawn."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from runner import HERE, jobs, one_job, analyze, paired, cp, build


class FollowupTests(unittest.TestCase):
    def test_every_candidate_raw_partition_oracle_and_analysis(self):
        config=copy.deepcopy(json.loads((HERE/'config.json').read_text()))
        config.update(seed='engineering-rare-followup-only',pairs_per_candidate=4,chunk_pairs=2,points_per_window=64)
        with tempfile.TemporaryDirectory() as scratch:
            output=Path(scratch);library=build(output/'sampler.so')
            for job in jobs(config):
                one_job(job,config,str(output),str(library),'engineering')
                check=one_job(job,config,str(output),str(library),'engineering',True)
                self.assertEqual(check['points'],256)
                self.assertEqual(check['generator_scalars'],1)
            analyze(output,config)
            result=json.loads((output/'analysis.json').read_text())
            self.assertEqual(len(result['comparisons']),6)
            self.assertEqual(len(result['rare_event_rates']),3)
            self.assertTrue(all(r['pairs']==4 for r in result['comparisons']))

    def test_mean_and_exact_zero_hit_bounds(self):
        self.assertEqual(paired([1,1,1],.0001)['interval'],[1,1])
        interval=cp(0,4096,.0001/6)
        self.assertEqual(interval[0],0)
        self.assertGreater(interval[1],.002)


if __name__=='__main__':unittest.main()
