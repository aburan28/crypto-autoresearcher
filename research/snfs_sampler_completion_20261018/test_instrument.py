"""Small engineering fixtures only; no campaign point searches."""
import copy
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("sampler_checker",HERE/"check_trial.py")
CHECK=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(CHECK)


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


if __name__=="__main__":unittest.main()
