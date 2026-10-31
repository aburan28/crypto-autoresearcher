#!/usr/bin/env python3
"""Synthetic adapter unit tests only; no C++ module or scientific trial runs."""
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('pilot_driver', Path(__file__).with_name('driver.py'))
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


class DriverTests(unittest.TestCase):
    def row(self, track, fixture='fixture-test', **extra):
        return {'track': track, 'fixture': fixture, 'scope': 'exploratory_toy_diagnostic', **extra}

    def put(self, root, name, rows):
        data = b''.join(json.dumps(row, allow_nan=False).encode()+b'\n' for row in rows)
        path = root/('.'+name+'.full.jsonl')
        path.write_bytes(data)
        return path, data

    def test_partition_preserves_verbatim_rows_and_multichunk_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [self.row('L9', padding='x'*1000) for _ in range(150)]
            path, data = self.put(root, 'lossy', rows)
            result, slot = driver.partition(root, {'name':'lossy','tracks':['L9']}, 0, {'fixture-test'})
            self.assertEqual(result['row_count'],150)
            self.assertEqual(result['original_sha256'],hashlib.sha256(data).hexdigest())
            self.assertGreater(slot,1)
            self.assertFalse(path.exists())
            rebuilt = b''.join((root/x['path']).read_bytes() for x in result['parts'])
            self.assertEqual(rebuilt,data)
            self.assertTrue(all(x['bytes']<=driver.CHUNK_LIMIT for x in result['parts']))

    def test_oversized_row_is_retained_and_rescuable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path,data=self.put(root,'lossy',[self.row('L9',padding='x'*driver.CHUNK_LIMIT)])
            with self.assertRaisesRegex(ValueError,'individual JSONL row'):
                driver.partition(root,{'name':'lossy','tracks':['L9']},0,{'fixture-test'})
            self.assertEqual(path.read_bytes(),data)
            target=root/'lossy-rescue.jsonl.gz'
            driver.rescue(path,target)
            self.assertEqual(gzip.decompress(target.read_bytes()),data)
            self.assertFalse(path.exists())

    def test_missing_track_rejects_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path,data=self.put(root,'algebraic',[self.row('L5')])
            with self.assertRaisesRegex(ValueError,'missing track'):
                driver.partition(root,{'name':'algebraic','tracks':['L5','L7','L8']},0,{'fixture-test'})
            self.assertEqual(path.read_bytes(),data)

    def test_global_alias_is_exact_and_only_l4(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            module={'name':'circuit','tracks':['D','L4'],'global_fixture_aliases':['shared_boolean_gate_grammar']}
            self.put(root,'circuit',[self.row('D'),self.row('L4','shared_boolean_gate_grammar')])
            result,_=driver.partition(root,module,0,{'fixture-test'})
            self.assertEqual(set(result['tracks']),{'D','L4'})
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.put(root,'circuit',[self.row('D','shared_boolean_gate_grammar'),self.row('L4','shared_boolean_gate_grammar')])
            with self.assertRaisesRegex(ValueError,'unknown fixture'):
                driver.partition(root,module,0,{'fixture-test'})

    def test_partial_output_is_never_overwritten_after_capacity_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            old=root/'rows-part-000.jsonl';old.write_bytes(b'archived-first-attempt\n')
            path,data=self.put(root,'lossy',[self.row('L9')])
            with self.assertRaises(FileExistsError):
                driver.partition(root,{'name':'lossy','tracks':['L9']},0,{'fixture-test'})
            self.assertEqual(old.read_bytes(),b'archived-first-attempt\n')
            self.assertEqual(path.read_bytes(),data)

    def make_batch(self,root):
        table={'circuit':['D','L4'],'padic_endo':['L1','L3'],'sequences':['L2','L6'],'algebraic':['L5','L7','L8'],'lossy':['L9']}
        modules=[];parts=[];slot=0
        for name,tracks in table.items():
            config={'name':name,'tracks':tracks}
            self.put(root,name,[self.row(t) for t in tracks])
            result,slot=driver.partition(root,config,slot,{'fixture-test'})
            modules.append(config);parts.append(result)
        slots=[]
        for i in range(driver.PART_COUNT):
            p=root/f'rows-part-{i:03}.jsonl'
            if not p.exists():p.touch()
            slots.append({'path':p.name,'sha256':driver.sha(p),'bytes':p.stat().st_size})
        driver.write_once(root/'parts-manifest.json',{'slots':slots,'modules':parts,'errors':[]})
        config={'modules':modules,'fixture_ids':['fixture-test'],'experiment_id':'synthetic-unit','run_id':'synthetic-unit'}
        driver.write_once(root/'raw-result.json',{'schema':'classical.ecdlp.batch-result.v1','attack_claimed':False,'experiment_id':'synthetic-unit','run_id':'synthetic-unit',
            'errors':[],'parts_manifest_sha256':driver.sha(root/'parts-manifest.json'),'metrics':{'rows':10},
            'module_execution':[{'name':x['name'],'build':{'returncode':0},'self_test':{'returncode':0},'measurement':{'returncode':0}} for x in modules]})
        return config

    def test_checker_accepts_complete_synthetic_batch_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config=self.make_batch(root)
            with contextlib.redirect_stdout(io.StringIO()):
                driver.check(config,root)
            (root/'rows-part-000.jsonl').write_bytes(b'changed\n')
            with self.assertRaisesRegex(ValueError,'part size/hash'):
                driver.check(config,root)

    def test_nonfinite_values_rejected_recursively(self):
        for value in ({'a':[float('nan')]},{'a':float('inf')}):
            with self.assertRaisesRegex(ValueError,'nonfinite'):
                driver.finite(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)
