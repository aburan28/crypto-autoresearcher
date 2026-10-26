"""Pure byte-custody/source-grammar fixtures. No legacy call, QEMU or cohort run."""
import json
import tempfile
import unittest
from pathlib import Path

import capsule
import capsule_check
import printed_trace


class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def case(self, name):
        p = self.root / name
        p.mkdir()
        (p/'legacy-child'/'prover').mkdir(parents=True)
        (p/'legacy-child'/'prover'/'serial.raw').write_bytes(b'partial\x00\xff\r\n')
        (p/'driver.stdout.log').write_bytes(b'driver output\n')
        (p/'driver.stderr.log').write_bytes(b'')
        return p

    def test_exact_bytes_and_determinism(self):
        a,b = self.case('a'),self.case('b')
        first,second = capsule.create(a),capsule.create(b)
        self.assertEqual(first,second)
        self.assertEqual(capsule_check.check(a)['members'],3)
        self.assertEqual((a/capsule.CAPSULE).read_bytes(),(b/capsule.CAPSULE).read_bytes())

    def test_changed_raw_bytes_refused(self):
        p=self.case('a');capsule.create(p)
        (p/'legacy-child'/'prover'/'serial.raw').write_bytes(b'changed')
        with self.assertRaises(ValueError):capsule_check.check(p)

    def test_missing_extra_and_manifest_tampering_refused(self):
        for mutation in ('missing','extra','manifest'):
            with self.subTest(mutation=mutation):
                p=self.case(mutation);capsule.create(p)
                if mutation=='missing':(p/'driver.stdout.log').unlink()
                elif mutation=='extra':(p/'legacy-child'/'extra.raw').write_bytes(b'extra')
                else:
                    f=p/capsule.INVENTORY;x=json.loads(f.read_text());x['members'][0]['sha256']='0'*64
                    f.write_text(json.dumps(x))
                with self.assertRaises(ValueError):capsule_check.check(p)

    def test_symlink_refused_and_empty_child_preserved(self):
        p=self.case('linked')
        (p/'legacy-child'/'link').symlink_to(p/'driver.stdout.log')
        with self.assertRaises(ValueError):capsule.create(p)
        q=self.root/'empty';q.mkdir()
        for name in capsule.DRIVER_LOGS:(q/name).write_bytes(b'')
        capsule.create(q)
        self.assertEqual(capsule_check.check(q)['members'],2)

    def test_v9_inventory_join(self):
        p=self.case('a');capsule.create(p)
        f=p/'legacy-child'/'prover'/'serial.raw'
        (p/'raw-result.json').write_text(json.dumps({'driver_artifacts':{'prover/serial.raw':capsule.digest(f.read_bytes())}}))
        capsule_check.check(p)
        (p/'raw-result.json').write_text(json.dumps({'driver_artifacts':{}}))
        with self.assertRaises(ValueError):capsule_check.check(p)


class PrintedSourceTests(unittest.TestCase):
    def test_offsets_decimal_and_repeated_factors(self):
        raw=b'% D[[2]]=19\r\n% A[[2]]=-7\r\n% B[[2]]=3\r\n% m[[2]]=31\r\n% Factor= 2^1\r\n% Factor= 2^1\n'
        out=printed_trace.extract(raw)['events']
        self.assertEqual(len(out),2)
        self.assertEqual([x['raw_offset'] for x in out],[raw.index(b'% Factor='),raw.rindex(b'% Factor=')])
        self.assertEqual([x['factor'] for x in out],['2','2'])
        self.assertTrue(all(x['preceding_printed_discriminant']['depth']=='2' for x in out))

    def test_ambiguity_and_incomplete_anomalies_retained(self):
        raw=b'% D[[1]]=7\nunknown phase\n% Factor= 1^-1\n% Factor= 123^2'
        out=printed_trace.extract(raw)['events']
        self.assertIsNone(out[0]['preceding_printed_discriminant'])
        self.assertFalse(out[0]['arithmetic_shape_valid'])
        self.assertEqual(out[1]['kind'],'incomplete_or_unrecognized_factor_line')
        self.assertFalse(out[1]['complete_line'])
        other=printed_trace.extract(b'% D[[1]]=7\n% A[[2]]=3\n% Factor= 2^1\n')['events']
        self.assertIsNone(other[0]['preceding_printed_discriminant'])


if __name__=='__main__':
    unittest.main()
