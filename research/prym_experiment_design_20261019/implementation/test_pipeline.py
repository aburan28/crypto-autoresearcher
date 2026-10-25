"""Planted software controls only: no W/S/E scientific panel or timing claim."""
import importlib.util
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from blind_recovery import require_gates,candidate,baseline
from census import Census
from relations import Context
from selector_pipeline import require_w_gate,phase,split_bucket
from test_relations import planted_fixture

HERE=Path(__file__).resolve().parent


class PipelineTests(unittest.TestCase):
    def test_independent_census_agrees_on_fixed_planted_branches(self):
        fixture=planted_fixture();ctx=Context(fixture);census=Census(fixture)
        # Exhaust the declared 64 sign/deck branches on a known toy identity.
        # This is a fixed software regression, never an unknown-log benchmark.
        for options in product(range(4),repeat=3):
            descriptor,reason=ctx.descriptor(1,(0,1,2),options)
            row=None if descriptor is None else ctx.construct(descriptor)[0]
            independently=census.accepted(1,(0,1,2),options)
            self.assertEqual(row is not None,independently is not None)
            if row is not None:self.assertEqual(row,independently)

    def test_gates_refuse_missing_and_rank_deficient_evidence(self):
        with self.assertRaisesRegex(RuntimeError,'closed'):require_gates({})
        result={'complete':True,'cells':[{'curve_uid':'software','seed':0,'qualifying_unknown_rank':False}]}
        with self.assertRaisesRegex(RuntimeError,'rank'):require_w_gate(result,{'status':'passed'})

    def test_planted_recovery_and_same_base_ic_interface(self):
        from independent import multiply,verify_row
        fixture=planted_fixture();fixture['base_rule']='deliberately planted public software fixture'
        target=multiply(19,0,0,5,tuple(fixture['P']))
        public={'fixture':fixture,'Q':target,'seed':0,'arm':'candidate',
                'algorithm':{'domain':'software-only-recovery','public_source_max':12,
                             'branches_per_source':64,'baseline_max_attempts':1000}}
        answer=candidate(public)
        self.assertEqual(answer['status'],'recovered');self.assertEqual(answer['k'],5)
        self.assertTrue(verify_row(fixture,answer['descent_witness'],target=target))
        ic=baseline(public)
        self.assertEqual(ic['status'],'recovered');self.assertEqual(ic['k'],5)
        self.assertEqual(ic['ic']['factor_base']['size'],len(fixture['factor_base']))

    def test_finite_support_is_explicit_not_resampled(self):
        config={'domain':'software-support-only','public_source_max':1,'candidates_per_split':10000}
        answer=phase({'fixture':planted_fixture(),'config':config,'mode':'train','seed':0},lambda v:None)
        self.assertEqual(answer['status'],'finite_support_exhausted')
        self.assertNotIn('models',answer)
        self.assertLess(answer['candidates'],10000)

    def test_null_feature_preserves_geometric_alias(self):
        import copy
        context=Context(planted_fixture());descriptor,_=context.descriptor(1,(0,1,2),(2,0,0))
        deck=copy.deepcopy(descriptor);deck['points']=[(-x%19,y) for x,y in descriptor['points']]
        self.assertEqual(split_bucket(context,descriptor),split_bucket(context,deck))

    def test_selector_aa_and_coordinate_transport_on_planted_input(self):
        config={'domain':'software-selector-only','public_source_max':1,'candidates_per_split':4}
        public={'fixture':planted_fixture(),'config':config,'seed':0}
        training=phase({**public,'mode':'train'},lambda v:None)
        self.assertEqual(training['status'],'complete')
        arms={arm:phase({**public,'mode':'arm','arm':arm,'models':training['models']},lambda v:None)
              for arm in ['identity','identity_aa','real','coordinate']}
        for key in ['rank','candidates','operation_vector','rows']:
            self.assertEqual(arms['identity'][key],arms['identity_aa'][key])
        for key in ['rank','candidates','rows']:
            self.assertEqual(arms['real'][key],arms['coordinate'][key])

    def test_blind_checker_rejects_changed_seal_and_commitment(self):
        from copy import deepcopy
        from hashlib import sha256
        from independent import multiply
        root=HERE.parents[2];path=root/'experiments/EXP-ECDLP-e193fa/independent_check.py'
        spec=importlib.util.spec_from_file_location('blind_final_checker',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        fixture=planted_fixture();fixture['base_rule']='planted software fixture'
        Q=multiply(19,0,0,5,tuple(fixture['P']))
        output=candidate({'fixture':fixture,'Q':Q,'seed':0,'arm':'candidate','algorithm':{
             'domain':'software-only-recovery','public_source_max':12,'branches_per_source':64}})
        text=json.dumps(output,sort_keys=True)+'\n';salt='00'*32;identifier='public-software-fixture'
        record={'challenge_id':identifier,'Q':Q,'reveal_after_outputs':{'k':5,'salt':salt},
          'commitment_before_attack':sha256(f'prym-E/v1|{identifier}|{salt}|5'.encode()).hexdigest(),
          'sealed_outputs':[{'arm':'candidate','seed':0,'output':output,'sealed_output_utf8':text,
                             'sealed_output_sha256':sha256(text.encode()).hexdigest(),'verified':True}]}
        self.assertTrue(module.check_challenge(fixture,record,require_isolation=False)[0]['verified'])
        for key in ['commitment_before_attack','seal']:
            invalid=deepcopy(record)
            if key=='seal':invalid['sealed_outputs'][0]['sealed_output_utf8']+=' '
            else:invalid[key]='00'*32
            with self.assertRaises(ValueError):module.check_challenge(fixture,invalid,require_isolation=False)

    def test_isolation_denies_access_or_refuses_unsupported_runtime(self):
        # This process holds the named private fixture. The child sees only
        # its path for the deliberate denial probe; science IPC omits it.
        with tempfile.TemporaryDirectory(prefix='prym-denial-control-') as tmp:
            path=Path(tmp)/'private.txt';path.write_text('public planted software sentinel')
            program='''
import json,socket,sys
from isolation import isolate
try:record=isolate()
except (OSError,RuntimeError) as exc:
 print(json.dumps({'status':'refused','reason':str(exc),'fallback_used':False}))
 raise SystemExit(0)
record['status']='isolated'
try:open(sys.argv[1]).read()
except PermissionError:record['private_file_denied']=True
else:record['private_file_denied']=False
try:socket.socket()
except PermissionError:record['network_denied']=True
else:record['network_denied']=False
print(json.dumps(record))
'''
            result=subprocess.run([sys.executable,'-c',program,str(path)],cwd=HERE,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            record=json.loads(result.stdout)
            self.assertFalse(record['fallback_used'])
            if record['status']=='refused':
                self.assertIn('Landlock',record['reason'])
                self.assertNotIn('private_file_denied',record)
            else:
                self.assertTrue(record['private_file_denied']);self.assertTrue(record['network_denied'])

    def test_actual_v2_manifest_success_and_failure_schema(self):
        root=HERE.parents[2]
        helper=root/'experiments/EXP-ECDLP-ad0ffe/review-corrections/pr2415-manifest-schema/test_runtime_draft.py'
        spec=importlib.util.spec_from_file_location('manifest_fixture_helper',helper)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for error in (None,'planted software failure'):
            result=module.result_literal(HERE/'native_runtime_v2.py',error)
            self.assertEqual(module.validate_synthetic(result,error),[])


if __name__=='__main__':unittest.main()
