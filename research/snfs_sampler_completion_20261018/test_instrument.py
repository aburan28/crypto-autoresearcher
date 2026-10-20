"""Small engineering fixtures only; no campaign point searches."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest import mock

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("sampler_checker",HERE/"check_trial.py")
CHECK=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(CHECK)
PRODUCER_SPEC=importlib.util.spec_from_file_location("sampler_producer",HERE/"execute_trial.py")
PRODUCER=importlib.util.module_from_spec(PRODUCER_SPEC);PRODUCER_SPEC.loader.exec_module(PRODUCER)


class TraceChecks(unittest.TestCase):
    def setUp(self):
        self.inp=dict(g=[0,1],p="101",root="0",A="2",B="3")
        row=dict(work=2,shells_completed=0,boundary="before_candidate",points_found_cumulative=1,distinct_residues=1,rational_points_seen=1,points_without_residue=0)
        final=dict(row,boundary="after_search_end")
        self.events=[dict(event="point",work=1,shells_completed=0,x=["3"],y=["6"],rational=True,residue=["3","6"]),
                     dict(event="checkpoint",snapshot=row),dict(event="finished",snapshot=final)]
        self.result=dict(rungs=[row],final=final)

    def test_valid_trace(self):self.assertEqual(CHECK.check_stream(self.events,self.inp,self.result),1)

    def test_tampered_point(self):
        self.events[0]["y"]=["7"]
        with self.assertRaises(AssertionError):CHECK.check_stream(self.events,self.inp,self.result)

    def test_tampered_residue(self):
        self.events[0]["residue"]=["3","7"]
        with self.assertRaises(AssertionError):CHECK.check_stream(self.events,self.inp,self.result)

    def test_missing_point_cannot_be_hidden_in_counts(self):
        with self.assertRaises(AssertionError):CHECK.check_stream(self.events[1:],self.inp,self.result)

    def test_truncated_trace(self):
        with self.assertRaises(AssertionError):CHECK.check_stream(self.events[:-1],self.inp,self.result)

    def test_duplicate_point(self):
        self.events.insert(1,copy.deepcopy(self.events[0]))
        with self.assertRaises(AssertionError):CHECK.check_stream(self.events,self.inp,self.result)

    def test_child_failure_preserves_partial_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture=Path(tmp)
            binary=fixture/"runtime-fixture"
            binary.write_bytes(b"isolated unit-test runtime; never executed\n")
            (fixture/"runtime-bindings.json").write_text(json.dumps({
                "fixture": {"path":str(binary),"sha256":hashlib.sha256(binary.read_bytes()).hexdigest()}
            }))
            run=Path(tmp)/"EXP-FIXTURE-000001/runs/RUN-FIXTURE-000001"
            run.mkdir(parents=True)
            (run/"launch.json").write_text(json.dumps({"argv":["engineering-fixture"]}))
            (run/"environment.json").write_text(json.dumps({"commit":"fixture","source_sha256":{}}))
            def failed_child(argv,**kwargs):
                out=Path(argv[-1]);out.mkdir();(out/"partial.jsonl").write_bytes(b'{"event":"fixture"}\n')
                raise subprocess.CalledProcessError(7,argv)
            # Exercise real binding validation against isolated fixture bytes;
            # historical host-specific bindings and production source stay intact.
            with mock.patch.object(PRODUCER,"HERE",fixture),mock.patch.object(PRODUCER.subprocess,"check_output",return_value=""),mock.patch.object(PRODUCER.subprocess,"run",side_effect=failed_child) as child:
                with self.assertRaises(subprocess.CalledProcessError):PRODUCER.main("panel",run)
            child.assert_called_once()
            with tarfile.open(run/"instrument.tar.gz") as archive:
                self.assertEqual(archive.extractfile("partial.jsonl").read(),b'{"event":"fixture"}\n')
            self.assertEqual(json.loads((run/"instrument-index.json").read_text())[0]["name"],"partial.jsonl")
            self.assertFalse((run/"raw-result.json").exists())


if __name__=="__main__":unittest.main()
