"""Deterministic software conformance tests; no confirmation cohort is drawn."""
from __future__ import annotations
from argparse import Namespace
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import prepare as g
import public_inputs as p


FIXED = [
    {"fixture_id":"fixed17","stratum":"ordinary","p":17,"a":2,"b":2,"gx":5,"gy":1,"r":19,"N":19,"seed":1},
    {"fixture_id":"fixed37","stratum":"ordinary","p":37,"a":29,"b":3,"gx":30,"gy":30,"r":17,"N":34,"seed":2},
    {"fixture_id":"fixed61","stratum":"ordinary","p":61,"a":1,"b":4,"gx":41,"gy":55,"r":19,"N":57,"seed":3},
    {"fixture_id":"fixed127","stratum":"ordinary","p":127,"a":13,"b":45,"gx":26,"gy":68,"r":41,"N":123,"seed":4},
]


class ArithmeticTests(unittest.TestCase):
    def test_fixed_affine_projective_vectors(self):
        for row in FIXED:
            pp,aa,rr = row["p"],row["a"],row["r"]
            base = (row["gx"],row["gy"])
            for scalar in (0,1,2,rr-1,rr,rr+1):
                with self.subTest(fixture=row["fixture_id"],scalar=scalar):
                    self.assertEqual(g.mul_jacobian(pp,aa,base,scalar),
                                     g.mul_affine(pp,aa,base,scalar))
            self.assertIsNone(g.mul_affine(pp,aa,base,rr))

    def test_fixed_certificates_and_invalid_witness(self):
        for row in FIXED:
            cert = g.certify_fixture(row)
            self.assertEqual(cert["python_euler_count"],row["N"])
            self.assertTrue(cert["identity"]["curve_uid"].startswith("urn:ec-record:1:sha256:"))
        bad = dict(FIXED[0],gy=2)
        with self.assertRaises(g.Refused):
            g.certify_fixture(bad)
        bad = dict(FIXED[0],N=38)
        with self.assertRaises(g.Refused):
            g.certify_fixture(bad)

    def test_private_stream_determinism_and_domain_separation(self):
        # All material is fixed and public in this software test.
        a = g.TargetStream(bytes(range(32)),"0"*64,"1"*64,"fixed17",0)
        b = g.TargetStream(bytes(range(32)),"0"*64,"1"*64,"fixed17",0)
        c = g.TargetStream(bytes(range(32)),"0"*64,"1"*64,"fixed17",1)
        aa = [a.bounded(19) for _ in range(4)]
        self.assertEqual(aa,[b.bounded(19) for _ in range(4)])
        self.assertNotEqual(aa,[c.bounded(19) for _ in range(4)])
        self.assertTrue(all(0<=x<19 for x in aa))

    def test_exact_rejection_branch(self):
        class Block:
            def __init__(self,value):
                self.value=value
            def digest(self):
                return self.value.to_bytes(32,"big")
        stream = g.TargetStream(bytes(32),"0"*64,"1"*64,"fixed17",0)
        with patch.object(g.hmac,"new",side_effect=[Block((1<<256)-1),Block(3)]):
            self.assertEqual(stream.bounded(3),0)
        self.assertEqual(stream.counter,2)

    def test_public_seed_and_settings_law(self):
        seed = g.public_seed("0"*64,"1"*64,"fixed17",0,"solver_cell")
        self.assertEqual(seed,p._seed("0"*64,"1"*64,"fixed17",0,"solver_cell"))
        self.assertNotEqual(seed,g.public_seed("0"*64,"1"*64,"fixed17",0,"arm_order"))
        rows = g.settings_for([FIXED[0]],"0"*64,"1"*64)
        self.assertEqual(len(rows),2)
        self.assertEqual((rows[0]["dp_bits"],rows[0]["initial_chains"],rows[0]["endpoint_cap"]),(1,5,20))
        self.assertEqual(rows[0]["max_precomp_ops"],18432)
        self.assertEqual(rows[0]["max_online_ops"],9472)

    def test_exclusion_union_is_exact_and_overlap_aware(self):
        union,manifest = g.exclusion_union()
        self.assertEqual(len(union),114)
        self.assertEqual([s["rows"] for s in manifest["sources"]],[48,32,34,24,4])
        self.assertGreater(sum(s["rows"] for s in manifest["sources"]),len(union))
        self.assertIn((61,1,4),union)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.prefix = self.repo/"harness"/"cohort"
        self.prefix.mkdir(parents=True)
        for name in ("prepare.py","public_inputs.py","curve_identity.py","src","exclusions"):
            source = g.HERE/name
            if source.is_dir():
                shutil.copytree(source,self.prefix/name)
            else:
                shutil.copyfile(source,self.prefix/name)
        subprocess.run(["git","init","-q"],cwd=self.repo,check=True)
        subprocess.run(["git","config","user.name","fixed-conformance"],cwd=self.repo,check=True)
        subprocess.run(["git","config","user.email","fixed-conformance@example.invalid"],cwd=self.repo,check=True)
        self.original_here = g.HERE
        g.HERE = self.prefix
        self.addCleanup(setattr,g,"HERE",self.original_here)
        self.source_commit = self.commit("source","2019-12-31T00:00:00+00:00")
        body = {"schema":"experiment.protocol/v1","test_scope":"binding-only fixture, not a scientific protocol"}
        self.protocol_hash = g.digest(g.canonical(body))
        self.protocol = {**body,"freeze":{"status":"frozen","protocol_sha256":self.protocol_hash,
                                       "commit":self.source_commit,"frozen_at":"2020-01-01T00:00:01Z",
                                       "filed_before_affected_data":True}}
        (self.repo/"protocol.json").write_text(json.dumps(self.protocol))
        protocol_commit = self.commit("protocol","2020-01-01T00:00:02+00:00")
        files = {name:g.sha(self.repo/name) for name in g.required_source_paths("harness/cohort")}
        self.lock = {"schema":"classical.ecdlp.endpoint-cohort-lock/v1",
                     "source_commit":self.source_commit,"source_prefix":"harness/cohort",
                     "protocol_commit":protocol_commit,"protocol_path":"protocol.json",
                     "protocol_sha256":self.protocol_hash,
                     "protocol_file_sha256":g.sha(self.repo/"protocol.json"),
                     "design":{"subgroup_bits":[12,14,16,18],"curves_per_size":16,"replicates":2,
                               "targets_per_cell":64,"endpoint_cap_multiplier":4},
                     "files":files}
        self.lock_path = self.repo/"source-lock.json"
        self.lock_path.write_text(json.dumps(self.lock))
        self.lock_commit = self.commit("lock","2020-01-01T00:00:03+00:00")
        self.nonce_path = self.repo/"external-nonce.json"
        self.nonce = {"schema":"classical.ecdlp.endpoint-cohort-nonce/v1",
                      "protocol_sha256":self.protocol_hash,
                      "source_lock_sha256":g.sha(self.lock_path),
                      "drawn_at":"2020-01-01T00:00:04Z","nonce_hex":"1"*64}
        self.nonce_path.write_text(json.dumps(self.nonce))

    def tearDown(self):
        self.temporary.cleanup()

    def commit(self,message,date):
        subprocess.run(["git","add","."],cwd=self.repo,check=True)
        env = {**os.environ,"GIT_AUTHOR_DATE":date,"GIT_COMMITTER_DATE":date}
        subprocess.run(["git","commit","-q","-m",message],cwd=self.repo,env=env,check=True)
        return subprocess.check_output(["git","rev-parse","HEAD"],cwd=self.repo,text=True).strip()

    def verify(self):
        return g.verify_bindings(self.repo,self.lock_path,self.lock_commit,
                                 self.protocol_hash,self.nonce_path)

    def test_committed_bindings_without_claiming_protocol_schema(self):
        record = self.verify()
        self.assertEqual(record["lock_commit"],self.lock_commit)
        self.assertEqual(record["protocol_sha256"],self.protocol_hash)
        # This tests immutable bindings only; official validate is a separate gate.

    def test_runtime_source_tamper_refused(self):
        with (self.prefix/"src/common.hpp").open("a") as stream:
            stream.write("\n// changed\n")
        with self.assertRaisesRegex(g.Refused,"source differs"):
            self.verify()

    def test_nonce_before_commit_refused(self):
        self.nonce["drawn_at"]="2020-01-01T00:00:02Z"
        self.nonce_path.write_text(json.dumps(self.nonce))
        with self.assertRaisesRegex(g.Refused,"nonce predates"):
            self.verify()

    def test_protocol_tamper_and_lock_tamper_refused(self):
        with (self.repo/"protocol.json").open("a") as stream:
            stream.write("\n")
        with self.assertRaises(g.Refused):
            self.verify()
        self.lock_path.write_text(self.lock_path.read_text()+"\n")
        with self.assertRaises(g.Refused):
            self.verify()

    def test_entropy_and_output_not_touched_before_official_validation(self):
        args = Namespace(repo_root=self.repo,source_lock=self.lock_path,
                         lock_commit=self.lock_commit,protocol_sha256=self.protocol_hash,
                         nonce=self.nonce_path,out=self.repo/"no-output")
        with patch.object(g.secrets,"token_bytes",side_effect=AssertionError("entropy was touched")):
            with self.assertRaisesRegex(g.Refused,"official protocol validator"):
                g.generate(args)
        self.assertFalse(args.out.exists())


class PublicFormatTests(unittest.TestCase):
    def test_lossless_target_assembly_and_tamper_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parts=[]
            logical=bytearray(g.tsv_bytes(g.TARGET_COLUMNS,[]))
            for index in (0,1):
                row={"fixture_id":f"fixed{index}","replicate":0,"target_id":f"fixed{index}-t0",
                     "target_ordinal":0,"qx":5,"qy":1,"infinity":0}
                data=g.tsv_bytes(g.TARGET_COLUMNS,[row])
                name=f"part{index}.tsv"
                (root/name).write_bytes(data)
                parts.append({"path":name,"fixture_id":f"fixed{index}","rows":1,
                              "bytes":len(data),"sha256":g.digest(data)})
                logical.extend(data.split(b"\n",1)[1])
            manifest={"schema":"classical.ecdlp.endpoint-target-parts/v1",
                      "columns":list(g.TARGET_COLUMNS),"rows":2,"parts":parts,
                      "logical_bytes":len(logical),"logical_sha256":g.digest(logical)}
            path=root/"manifest.json"
            path.write_text(json.dumps(manifest))
            result=g.assemble(path,root/"assembled.tsv")
            self.assertEqual((root/"assembled.tsv").read_bytes(),logical)
            self.assertEqual(result["rows"],2)
            (root/"part1.tsv").write_bytes(b"tampered")
            with self.assertRaises(g.Refused):
                g.assemble(path,root/"never.tsv")
            self.assertFalse((root/"never.tsv").exists())

    def test_cell_writer_uses_public_rows_only_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            fixture={k:str(v) for k,v in FIXED[0].items()}
            settings=g.settings_for([fixture],"0"*64,"1"*64)[0]
            rows=[{"fixture_id":"fixed17","replicate":"0","target_id":f"fixed17-rep0-t{i:02d}",
                   "target_ordinal":str(i),"qx":"5","qy":"1","infinity":"0"} for i in range(64)]
            cohort=p.PublicInputs(root,"0"*64,"0"*64,"1"*64,{"fixed17":fixture},
                                  {"fixed17-rep0":settings},{"fixed17-rep0":rows})
            written=p.write_cell(cohort,"fixed17-rep0",root/"slice")
            self.assertEqual(written["targets.tsv"]["rows"],64)
            self.assertEqual(p.read_table(root/"slice/targets.tsv",p.TARGET_COLUMNS),rows)
            with self.assertRaises(p.Refused):
                p.write_cell(cohort,"fixed17-rep0",root/"slice")

    def test_path_escape_and_undeclared_tree_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ("../private/target-root.json","/tmp/private","a/../../private"):
                with self.assertRaises(p.Refused):
                    p.public_path(root,name)
            with self.assertRaises(p.Refused):
                p.load_inputs(root,"not-a-hash")


if __name__ == "__main__":
    unittest.main(verbosity=2)
