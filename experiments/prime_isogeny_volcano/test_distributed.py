import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess

MODULE = Path(__file__).with_name("distributed.py")
spec = importlib.util.spec_from_file_location("isogeny_distributed", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class DistributedTests(unittest.TestCase):
    def test_key_stable(self):
        a = {"p":101,"a":1,"b":0,"primes":[2,3]}
        self.assertEqual(mod.job_key(a), mod.job_key(dict(reversed(list(a.items())))))

    def test_success_and_resume(self):
        job = {"p":101,"a":1,"b":0,"primes":[2,3]}
        with tempfile.TemporaryDirectory() as d:
            def fake_run(cmd, **kwargs):
                Path(cmd[cmd.index("--out")+1]).write_text("{}\n{}\n")
                return subprocess.CompletedProcess(cmd, 0, "", "")
            with patch.object(mod.subprocess, "run", side_effect=fake_run) as run:
                self.assertEqual(mod.run_job(job,d,"sage",10)["status"],"ok")
                self.assertEqual(mod.run_job(job,d,"sage",10)["status"],"cached")
                self.assertEqual(run.call_count,1)

    def test_failure_receipt(self):
        job = {"p":101,"a":1,"b":0,"primes":[2]}
        with tempfile.TemporaryDirectory() as d:
            with patch.object(mod.subprocess,"run",return_value=subprocess.CompletedProcess([],1,"","bad")):
                self.assertEqual(mod.run_job(job,d,"sage",10)["status"],"failed")
                self.assertFalse((Path(d)/(mod.job_key(job)+".jsonl")).exists())

if __name__ == "__main__":
    unittest.main()
