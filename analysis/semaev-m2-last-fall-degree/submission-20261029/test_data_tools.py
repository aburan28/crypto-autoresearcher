"""Small exhaustive software fixtures; not a research sweep or timing evidence."""
import importlib.util
import itertools
import os
from pathlib import Path
import random
import subprocess
import shutil
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'code'))
from gf2n import Field, find_modulus
from s3sys import Subspace, random_basis
spec=importlib.util.spec_from_file_location('campaign',HERE/'certificate_campaign.py')
campaign=importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


class DataTools(unittest.TestCase):
    def test_count_against_all_pairs(self):
        found=shutil.which(os.environ.get('SEMAEV_COUNT_BIN','count_by_sum'))
        if not found:self.skipTest('compile count_by_sum.c and set SEMAEV_COUNT_BIN')
        binary=Path(found)
        rng=random.Random(270629)
        cases=0
        for n in range(3,13):
            field=Field(n,find_modulus(n))
            for k in range(1,min(n,5)+1):
                for _ in range(4):
                    basis=random_basis(field,k,rng)
                    a6=rng.randrange(1,1<<n); z=rng.randrange(1,1<<n)
                    values=list(Subspace(field,basis).elements())
                    expected=sum(field.sq(field.mul(a,b)^field.mul(z,a^b)) ^ field.mul(z,field.mul(a,b)) ^ a6 == 0
                                 for a,b in itertools.product(values,repeat=2))
                    got=int(subprocess.check_output([str(binary),str(n),format(field.f,'x'),format(z,'x'),format(a6,'x'),str(k),*[format(x,'x') for x in basis]],text=True))
                    self.assertEqual(got,expected,(n,k,z,a6,basis));cases+=1
        self.assertEqual(cases,188)

    def test_batch_boundary_against_other_algorithm(self):
        a=shutil.which(os.environ.get('SEMAEV_COUNT_BIN','count_by_sum'))
        b=shutil.which(os.environ.get('SEMAEV_REFERENCE_COUNT_BIN','s3count2'))
        if not a or not b:self.skipTest('compile both independent counters')
        for n,k in [(13,12),(13,13),(14,13),(15,14)]:
            field=Field(n,find_modulus(n))
            argv=[str(n),format(field.f,'x'),'3','2',str(k),*[format(1<<j,'x') for j in range(k)]]
            self.assertEqual(subprocess.check_output([a,*argv]),subprocess.check_output([b,*argv]))

    def test_retention_and_memory(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td); f=d/'sys'; f.write_text('4 1\n2 0 3\n')
            result=campaign.memory_admission(f,2,16,2**32)
            self.assertEqual((result['columns'],result['initial_rows']),(11,1))
            self.assertTrue(result['admitted'])
            self.assertFalse(campaign.memory_admission(f,2,16,1)['admitted'])
            campaign.save(d/'record',{'a':1})
            with self.assertRaises(FileExistsError):campaign.save(d/'record',{'a':2})

    def test_timeout(self):
        with tempfile.TemporaryDirectory() as td:
            result=campaign.command([sys.executable,'-c','import time;time.sleep(30)'],Path(td),'timeout',0.05,2**30)
            self.assertEqual(result['status'],'timeout')
            self.assertNotEqual(result['returncode'],0)


if __name__=='__main__':unittest.main()
