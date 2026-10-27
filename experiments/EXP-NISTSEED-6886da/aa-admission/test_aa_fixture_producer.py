"""Mock-only complete producer tests; VM, subprocess, legacy, and storage tripwired."""
from __future__ import annotations
import copy, hashlib, importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location("aa_tested",HERE/"aa_fixture_producer.py");aa=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(aa)
def put(p,b):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def dump(p,x):put(p,(json.dumps(x,sort_keys=True)+"\n").encode())
def digest(b):return hashlib.sha256(b).hexdigest()
CERT=b"101\n-1\n1\n5\n2\n0\n2\n2\n0\n\n5\n-1\n0\n5\n2\n1\n2\n1\n0\n0\n"
class Boundary:
 def __init__(self,mutate=None):self.calls=0;self.mutate=mutate
 def __call__(self,out,cache,payload,config):
  self.calls+=1;assert not cache.exists() and payload==aa.INPUT;cache.mkdir();(cache/"images").mkdir();put(cache/"vmlinuz-lts",aa.read(aa.RUNTIME/"vmlinuz-lts"));raw=out/"raw"
  pbody=b"% N_0=101\nThis number is prime\n";cbody=b"0: -1 1\n1: -1 1\n";pfull=pbody+b"__ECPP_CERTIFICATE_BEGIN__\n"+CERT+b"\n__ECPP_CERTIFICATE_END__";ps=b"__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n"+pfull+b"\n__ECPP_CHILD_EXIT__ 0 timeout=0\n__ECPP_GUEST_COMPLETE__\n";cs=b"__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n"+cbody+b"\n__ECPP_CHILD_EXIT__ 0 timeout=0\n__ECPP_GUEST_COMPLETE__\n"
  for n,v in (("input.txt",payload),("prover/serial.raw",ps),("prover/program.stdout",pfull),("prover/qemu.stderr",b""),("prover/certificate.cformat",CERT),("checker/serial.raw",cs),("checker/program.stdout",cbody),("checker/qemu.stderr",b"")):put(raw/n,v)
  pe=aa.stage_expectation(out,cache,config["runtime"],"prover",payload);ce=aa.stage_expectation(out,cache,config["runtime"],"checker",CERT)
  for e in (pe,ce):put(e["image_path"],e["image"])
  def start(e):return {"utc":"2026-10-26T00:00:00+00:00","command":e["command"],"program_sha256":digest(e["artifacts"][e["program"]]),"init_sha256":digest(e["artifacts"]["qemu-init"]),"initramfs_sha256":digest(e["image"]),"input_sha256":digest(payload if e is pe else CERT),"stdin_sha256":digest(b""),"data_mode":e["data_mode"],"guest_limit_seconds":e["guest"],"host_limit_seconds":e["host"]}
  dump(raw/"prover/started.json",start(pe));dump(raw/"checker/started.json",start(ce));dump(raw/"prover/result.json",{"vm_valid":True,"qemu_exit":33,"child_exit":0,"reason":None,"serial_sha256":digest(ps),"certificate_count":1,"elapsed_host_seconds":1});dump(raw/"checker/result.json",{"vm_valid":True,"qemu_exit":33,"child_exit":0,"reason":None,"serial_sha256":digest(cs),"certificate_count":0,"elapsed_host_seconds":1})
  if self.mutate:self.mutate(raw,out,cache)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);runtime=json.loads((aa.COMPAT/"runtime-bindings.json").read_text());self.manifest=self.root/"binding.json";dump(self.manifest,{"fixture":aa.FIXTURE,"limits":aa.LIMITS,"primary_configuration":aa.PRIMARY,"input_bindings":aa.SOURCE_HASHES,"runtime":runtime});self.old=subprocess.run;subprocess.run=lambda *a,**k:(_ for _ in ()).throw(AssertionError("subprocess tripwire"));self.saved={n:sys.modules.get(n) for n in ("qemu_controls","cohort_case","cohort_runner","artifact_store")};[sys.modules.__setitem__(n,self) for n in self.saved]
 def tearDown(self):
  subprocess.run=self.old
  for n,v in self.saved.items():sys.modules.pop(n,None) if v is None else sys.modules.__setitem__(n,v)
  self.tmp.cleanup()
 def vm(self,*a,**k):raise AssertionError("VM tripwire")
 def execute_case(self,*a,**k):raise AssertionError("cohort tripwire")
 def run_trial(self,*a,**k):raise AssertionError("runner tripwire")
 def upload(self,*a,**k):raise AssertionError("storage tripwire")
 def call(self,tag,mutation=None):
  b=Boundary(mutation);result=aa.build_pair(self.root/(tag+"-left"),self.root/(tag+"-right"),self.manifest,b);self.assertEqual(b.calls,2);return result
 def test_complete_actual_binding_and_incidental_elapsed_path_values_accept(self):
  def mutate(raw,out,cache):
   if out.name.endswith("right"):
    x=json.loads((raw/"prover/result.json").read_text());x["elapsed_host_seconds"]=2;dump(raw/"prover/result.json",x)
    x=json.loads((raw/"checker/result.json").read_text());x["elapsed_host_seconds"]=3;dump(raw/"checker/result.json",x)
    x=json.loads((raw/"prover/started.json").read_text());x["utc"]="2026-10-27T00:00:00+00:00";dump(raw/"prover/started.json",x)
  r=self.call("baseline",mutate);self.assertTrue(r["aa"]["equal"]);self.assertNotEqual(r["raw_custody"]["left"],r["raw_custody"]["right"])
 def test_real_output_timing_normalizes_and_checker_semantics_remain_visible(self):
  for stage in ("prover","checker"):
   left=(HERE/"fixtures"/f"real-101-left-{stage}.stdout").read_bytes();right=(HERE/"fixtures"/f"real-101-right-{stage}.stdout").read_bytes()
   self.assertNotEqual(left,right)
   self.assertEqual(aa.semantic_events(left),aa.semantic_events(right))
   self.assertNotEqual(aa.semantic_events(left+b"\n% UNEXPECTED SEMANTIC EVENT\n"),aa.semantic_events(right))
  checker=(HERE/"fixtures/real-101-left-checker.stdout").read_bytes()
  self.assertEqual(len(aa.semantic_events(checker)),2)
  self.assertNotEqual(aa.semantic_events(checker),aa.semantic_events(checker.replace(b"-1 1",b"-1 0",1)))
  self.assertNotEqual(aa.semantic_events(b"% Time for unknown setting is 1s"),aa.semantic_events(b"% Time for unknown setting is 2s"))
 def test_schema_accepts_actual_result_and_refuses_nested_semantic_mutations(self):
  try:
   import jsonschema
  except ImportError:
   self.skipTest("optional jsonschema dependency is unavailable")
  schema=json.loads((HERE/"aa_fixture_schema.json").read_text());validator=jsonschema.Draft202012Validator(schema);result=self.call("schema")
  self.assertEqual(list(validator.iter_errors(result)),[])
  def changed(path,value):
   item=copy.deepcopy(result);target=item
   for key in path[:-1]:target=target[key]
   target[path[-1]]=value;return item
  bad=[changed(("left","fixture","public_input"),"102\n"),changed(("left","fixture","id"),"other"),changed(("left","labels"),["composite"]),changed(("left","certificate","root"),103),changed(("left","prover","qemu_exit"),0)]
  missing=copy.deepcopy(result);del missing["left"]["trace"]["prover_events"];bad.append(missing)
  missing=copy.deepcopy(result);del missing["left"]["runtime"]["limits"];bad.append(missing)
  unknown=copy.deepcopy(result);unknown["left"]["trace"]["unknown"]=True;bad.append(unknown)
  for item in bad:self.assertTrue(list(validator.iter_errors(item)))
 def test_raw_identity_and_semantic_mutations_refuse_after_two_boundaries(self):
  def setfield(path,key,value):
   x=json.loads(path.read_text());x[key]=value;dump(path,x)
  def rejected(raw,out,cache):
   s=(raw/"checker/serial.raw").read_bytes().replace(b"1: -1 1",b"1: -1 0");put(raw/"checker/serial.raw",s);put(raw/"checker/program.stdout",b"0: -1 1\n1: -1 0\n");setfield(raw/"checker/result.json","serial_sha256",digest(s))
  def duplicate(raw,out,cache):
   s=(raw/"prover/serial.raw").read_bytes()+b"__ECPP_CHILD_EXIT__ 1 timeout=0\n";put(raw/"prover/serial.raw",s);setfield(raw/"prover/result.json","serial_sha256",digest(s))
  cases={"command":lambda r,o,c:setfield(r/"prover/started.json","command",["/unexpected-program","-m","999"]),"mode":lambda r,o,c:setfield(r/"prover/started.json","data_mode","empty"),"stdin":lambda r,o,c:setfield(r/"prover/started.json","stdin_sha256","0"*64),"initramfs":lambda r,o,c:setfield(r/"prover/started.json","initramfs_sha256","0"*64),"payload":lambda r,o,c:setfield(r/"prover/started.json","input_sha256","0"*64),"init":lambda r,o,c:setfield(r/"prover/started.json","init_sha256","0"*64),"limits":lambda r,o,c:setfield(r/"prover/started.json","guest_limit_seconds",999),"status":lambda r,o,c:setfield(r/"prover/result.json","vm_valid",False),"labels":lambda r,o,c:put(r/"prover/program.stdout",b"This number is composite\n"),"rejected":rejected,"exit":duplicate,"certificate":lambda r,o,c:put(r/"prover/certificate.cformat",b""),"extra":lambda r,o,c:put(r/"extra",b"x"),"missing":lambda r,o,c:(r/"checker/qemu.stderr").unlink(),"cache":lambda r,o,c:put(c/"vmlinuz-lts",b"wrong")}
  for tag,mutation in cases.items():
   with self.subTest(tag=tag):
    b=Boundary(mutation)
    with self.assertRaises(aa.Refusal):aa.build_pair(self.root/(tag+"-left"),self.root/(tag+"-right"),self.manifest,b)
    self.assertEqual(b.calls,2)
 def test_binding_payload_kernel_data_tampering_refuses_before_boundary(self):
  original=aa.read
  for tag,suffix in (("payload","runtime-payloads/runecpp"),("kernel",".work/qemu-runtime/vmlinuz-lts"),("data",".work/build-v4/ECPP/Ecpp/Data/ecpp.DfD")):
   with self.subTest(tag=tag):
    aa.read=lambda p,old=original,suffix=suffix: b"tampered" if str(p).endswith(suffix) else old(p);b=Boundary()
    with self.assertRaises(aa.Refusal):aa.build_pair(self.root/(tag+"-left"),self.root/(tag+"-right"),self.manifest,b)
    self.assertEqual(b.calls,0);aa.read=original
 def test_fresh_nested_and_ancestor_symlink_refuse_without_default_boundary(self):
  b=Boundary();(self.root/"exists").mkdir();
  with self.assertRaises(aa.Refusal):aa.build_pair(self.root/"exists",self.root/"new",self.manifest,b)
  with self.assertRaises(aa.Refusal):aa.build_pair(self.root/"a",self.root/"a"/"nested",self.manifest,b)
  link=self.root/"link";link.symlink_to(self.root/"real",target_is_directory=True)
  with self.assertRaises(aa.Refusal):aa.build_pair(link/"left",self.root/"right",self.manifest,b)
  self.assertEqual(b.calls,0);self.assertIsNotNone(aa.default_legacy_boundary)
if __name__=="__main__":unittest.main(verbosity=2)
