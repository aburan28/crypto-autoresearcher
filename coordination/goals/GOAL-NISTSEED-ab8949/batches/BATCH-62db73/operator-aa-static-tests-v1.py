#!/usr/bin/env python3
"""Immutable operator capture: static/mocked A/A tests, no original calls."""
import contextlib, datetime, hashlib, io, json, platform, subprocess, sys, traceback, unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[5]
BATCH=Path(__file__).resolve().parent
IMPL=ROOT/'experiments/EXP-NISTSEED-6886da/aa-admission'
COMPAT=ROOT/'research/nist_seed_ecpp_compat_20261024'
PREFIX='executor-aa-implementation-v1'
for suffix in ('.test-receipt.json','.tests.log','.compile.stdout','.compile.stderr'):
 if (BATCH/(PREFIX+suffix)).exists():raise SystemExit('Refuse overwrite: '+suffix)
names=['aa_fixture_producer.py','test_aa_fixture_producer.py','aa_fixture_schema.json']
source_hashes={n:hashlib.sha256((IMPL/n).read_bytes()).hexdigest() for n in names}
json.loads((IMPL/'aa_fixture_schema.json').read_text())
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
environment={'python':sys.version,'platform':platform.platform()}
argv=[sys.executable,'-m','py_compile',*(str(IMPL/n) for n in names[:2])]
compiled=subprocess.run(argv,capture_output=True,cwd=ROOT)
(BATCH/(PREFIX+'.compile.stdout')).write_bytes(compiled.stdout)
(BATCH/(PREFIX+'.compile.stderr')).write_bytes(compiled.stderr)
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(COMPAT))
import qemu_controls,cohort_case
blocked=[]
def forbidden(*args,**kwargs):
 blocked.append('original VM/legacy/subprocess boundary attempted')
 raise AssertionError('ZERO-RUN operator guard: original execution forbidden')
qemu_controls.vm=forbidden;cohort_case.execute_case=forbidden
original_files={str((COMPAT/'qemu_controls.py').resolve()):'vm',str((COMPAT/'cohort_case.py').resolve()):'execute_case'}
def profile_guard(frame,event,arg):
 if event=='call' and frame.f_code.co_name in ('vm','execute_case'):
  name=str(Path(frame.f_code.co_filename).resolve())
  if original_files.get(name)==frame.f_code.co_name:forbidden()
previous_profile=sys.getprofile();capture=io.StringIO();result=None;operator_error=None
try:
 with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(capture),mock.patch('subprocess.Popen',side_effect=forbidden),mock.patch('os.system',side_effect=forbidden):
  sys.setprofile(profile_guard)
  suite=unittest.defaultTestLoader.discover(str(IMPL),pattern='test_aa_fixture_producer.py')
  result=unittest.TextTestRunner(stream=capture,verbosity=2).run(suite)
except BaseException as exc:
 operator_error=type(exc).__name__+': '+str(exc);traceback.print_exc(file=capture)
finally:sys.setprofile(previous_profile)
log=capture.getvalue();(BATCH/(PREFIX+'.tests.log')).write_text(log)
receipt={'operator_guard_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'task_id':'TASK-20261025-ad9d68','handoff_sha256':hashlib.sha256((BATCH/'handoffs/TASK-20261025-ad9d68.yaml').read_bytes()).hexdigest(),'scope':'static and fully mocked A/A implementation tests only','started_at':started,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),**environment,'source_sha256':source_hashes,'compile_argv':argv,'compile_returncode':compiled.returncode,'unittest_driver':'unittest discovery in operator-aa-static-tests-v1.py; VM symbols and subprocess APIs blocked; profile guard intercepts original-function aliases before body execution','tests_run':result.testsRun if result else 0,'failures':len(result.failures) if result else 0,'errors':len(result.errors) if result else 0,'operator_error':operator_error,'successful':compiled.returncode==0 and result is not None and result.testsRun>0 and result.wasSuccessful() and not blocked and operator_error is None,'blocked_original_call_attempts':blocked,'named_orders_executed':0,'legacy_program_executed':False}
(BATCH/(PREFIX+'.test-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2));print(log[-22000:]);raise SystemExit(0 if receipt['successful'] else 1)
