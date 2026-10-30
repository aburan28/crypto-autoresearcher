#!/usr/bin/env python3
"""Synthetic integrity/arithmetic regressions; no follow-up measurements."""
import contextlib
import copy
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('followup_driver',HERE/'driver.py')
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)

@contextlib.contextmanager
def scratch():
    with tempfile.TemporaryDirectory(prefix='integrity-',dir=HERE) as tmp:
        yield Path(tmp)

@contextlib.contextmanager
def cwd(path):
    before=Path.cwd();os.chdir(path)
    try:yield
    finally:os.chdir(before)

def config():
    return {'fixture_ids':['f17'],'fixture_meta':[{'id':'f17','p':17,'r':19,'N':19}],
            'target_meta':[{'fixture_id':'f17','target_id':'q3'}]}

def row(track,**extra):
    return {'track':track,'fixture':'f17','scope':driver.SCOPE,'outcome':'complete_valid',**extra}

def decoder_rows():
    values=[row('L9-decoder',row_kind='kernel',feature='constant',training_samples=2048,heldout_samples=512,calibration_used_for_tuning=False),
            row('L9-decoder',row_kind='not_applicable',feature='power_residue_5',outcome='not_applicable')]
    for mode in ('model','exact'):
        for width in (1,8):
            candidates=[3] if width==1 else [1,2,3,4,5,6,7,8]
            values.append(row('L9-decoder',row_kind='target',feature='constant',target_id='q3',prefix_mode=mode,beam_width=width,candidates=candidates,candidate_count=len(candidates),candidate_verification_hits=1,verified_scalar=3))
    return values

class IntegrityTests(unittest.TestCase):
    def test_shard_job_names_and_path_guard(self):
        self.assertTrue(all(driver.module_name_valid(x) for x in driver.MODULES))
        for name in ('../escape', '/absolute', 'scale/shard', 'scale;rm', '0prefix', ''):
            self.assertFalse(driver.module_name_valid(name))

    def test_projection_exact_coverage_and_na(self):
        module={'name':'projection_scale_0','kind':'projection_scale','tracks':['L9-scale'],'fixture_ids':['f17'],'features':['constant','power_residue_5']}
        values=[row('L9-scale',projection='constant'),row('L9-scale',projection='power_residue_5',outcome='not_applicable')]
        driver.validate_rows(module,values,config())
        with self.assertRaisesRegex(ValueError,'coverage'):driver.validate_rows(module,values[:1],config())
        with self.assertRaisesRegex(ValueError,'applicability'):driver.validate_rows(module,[values[0],row('L9-scale',projection='power_residue_5')],config())

    def test_decoder_requires_both_prefix_modes_and_beams(self):
        module={'name':'decoder','tracks':['L9-decoder'],'features':['constant','power_residue_5']}
        values=decoder_rows();driver.validate_rows(module,values,config())
        with self.assertRaisesRegex(ValueError,'coverage'):driver.validate_rows(module,values[:-1],config())
        with self.assertRaisesRegex(ValueError,'duplicate'):driver.validate_rows(module,values+[values[-1]],config())
        wrong=copy.deepcopy(values);wrong[0]['heldout_samples']=511
        with self.assertRaisesRegex(ValueError,'sample contract'):driver.validate_rows(module,wrong,config())

    def test_decoder_candidate_range_and_consistency(self):
        module={'name':'decoder','tracks':['L9-decoder'],'features':['constant','power_residue_5']}
        values=decoder_rows();values[-1]['verified_scalar']=18
        with self.assertRaisesRegex(ValueError,'consistency'):driver.validate_rows(module,values,config())
        values=decoder_rows();values[-1]['candidates'][-1]=19
        with self.assertRaisesRegex(ValueError,'range'):driver.validate_rows(module,values,config())

    def test_incomplete_basis_bundle_is_rejected(self):
        module={'name':'basis_audit','tracks':['L4-audit'],'global_fixture_aliases':['shared_basis_audit']}
        values=[row('L4-audit',fixture='shared_basis_audit',row_kind='summary')]
        with self.assertRaisesRegex(ValueError,'coverage'):driver.validate_rows(module,values,config())

    def test_partitions_preserve_verbatim_rows(self):
        module={'name':'projection_scale_0','kind':'projection_scale','tracks':['L9-scale'],'fixture_ids':['f17'],'features':['constant','power_residue_5']}
        values=[row('L9-scale',projection='constant',padding='x'*40000),row('L9-scale',projection='power_residue_5',outcome='not_applicable',padding='x'*40000)]
        with scratch() as directory:
            data=b''.join(json.dumps(x).encode()+b'\n' for x in values)
            source=directory/'.projection_scale_0.full.jsonl';source.write_bytes(data)
            result,slot=driver.partition(directory,module,0,config())
            self.assertEqual(slot,2);self.assertFalse(source.exists())
            self.assertEqual(b''.join((directory/x['path']).read_bytes() for x in result['parts']),data)
            self.assertEqual(result['original_sha256'],hashlib.sha256(data).hexdigest())

    def test_oversized_or_incomplete_stream_retained(self):
        module={'name':'projection_scale_0','kind':'projection_scale','tracks':['L9-scale'],'fixture_ids':['f17'],'features':['constant','power_residue_5']}
        with scratch() as directory:
            source=directory/'.projection_scale_0.full.jsonl';data=(json.dumps(row('L9-scale',projection='constant',padding='x'*driver.CHUNK_LIMIT))+'\n').encode();source.write_bytes(data)
            with self.assertRaisesRegex(ValueError,'individual JSONL'):driver.partition(directory,module,0,config())
            self.assertEqual(source.read_bytes(),data)
            target=directory/'rescue.gz';driver.rescue(source,target);self.assertEqual(gzip.decompress(target.read_bytes()),data)
        with scratch() as directory:
            source=directory/'.projection_scale_0.full.jsonl';source.write_text(json.dumps(row('L9-scale',projection='constant'))+'\n')
            with self.assertRaisesRegex(ValueError,'coverage'):driver.partition(directory,module,0,config())
            self.assertTrue(source.exists())

    def test_nonfinite_and_existing_outputs_rejected(self):
        for value in ({'x':[float('nan')]},{'x':float('inf')}):
            with self.assertRaisesRegex(ValueError,'nonfinite'):driver.finite(value)
        with scratch() as directory:
            p=directory/'once.json';driver.write_once(p,{'first':1})
            with self.assertRaises(FileExistsError):driver.write_once(p,{'second':2})
            self.assertEqual(json.loads(p.read_text()),{'first':1})

    def test_independent_jacobian_positive_witness_and_replay(self):
        with scratch() as directory,cwd(directory):
            (directory/'fixtures.tsv').write_text('id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed\nf17 main 17 2 2 5 1 19 19 1\n')
            (directory/'targets.tsv').write_text('fixture_id\ttarget_id\tQx\tQy\tQinf\nf17 q3 10 6 0\n')
            shutil.copyfile(HERE/'verify_candidates.cpp',directory/'verifier.cpp')
            values=decoder_rows();part=directory/'rows-part-000.jsonl';part.write_text(''.join(json.dumps(x)+'\n' for x in values))
            parts={'modules':[{'name':'decoder','parts':[{'path':part.name}]}]}
            cfg={**config(),'fixtures':'fixtures.tsv','public_targets':'targets.tsv','verifier_source':'verifier.cpp','compiler_flags':['-std=c++20','-O2','-Wall','-Wextra','-Werror'],'watchdog_seconds':120}
            result=driver.verify_public_candidates(cfg,directory,parts)
            self.assertEqual(result['candidate_cases'],4);self.assertEqual(result['recovered_cases'],4);self.assertEqual(result['unique_recovered_targets'],1)
            replay=driver.verify_public_candidates(cfg,directory,parts,replay=True)
            self.assertEqual(replay['candidate_cases'],4)
            self.assertFalse((directory/'.verification-input.tsv').exists())
            self.assertEqual(len(list(directory.glob('verification-part-*.jsonl'))),driver.VERIFICATION_PART_COUNT)

    def test_independent_arithmetic_rejects_false_producer_hit(self):
        with scratch() as directory,cwd(directory):
            (directory/'fixtures.tsv').write_text('id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed\nf17 main 17 2 2 5 1 19 19 1\n')
            (directory/'targets.tsv').write_text('fixture_id\ttarget_id\tQx\tQy\tQinf\nf17 q3 10 6 0\n')
            shutil.copyfile(HERE/'verify_candidates.cpp',directory/'verifier.cpp')
            values=decoder_rows();values[2]['candidates']=[4];values[2]['verified_scalar']=4
            part=directory/'rows-part-000.jsonl';part.write_text(''.join(json.dumps(x)+'\n' for x in values))
            cfg={**config(),'fixtures':'fixtures.tsv','public_targets':'targets.tsv','verifier_source':'verifier.cpp','compiler_flags':['-std=c++20','-O2'],'watchdog_seconds':120}
            with self.assertRaisesRegex(ValueError,'contradicts decoder'):
                driver.verify_public_candidates(cfg,directory,{'modules':[{'name':'decoder','parts':[{'path':part.name}]}]})
            self.assertTrue((directory/'verification-input-rescue.tsv.gz').exists())


if __name__=='__main__':unittest.main(verbosity=2)
