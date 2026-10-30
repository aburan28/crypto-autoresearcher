"""Software equivalence controls for the separate batched exporter."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

from quotient_lift import write_certificate
from test_quotient_lift import oracle, independent_conditions


class BatchedExport(unittest.TestCase):
    def test_exact_bytes_and_partial_block(self):
        reference = os.environ['SEMAEV_REFERENCE_BINARY']
        candidate = os.environ['SEMAEV_BATCHED_BINARY']
        rows = []
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for index, (n,d,polys) in enumerate([
                (7,3,[{3,12,16}]), (10,4,[{3,12,16},{5,32}]),
                (16,4,[{1,2}])
            ]):
                seed,sq,_ = oracle(n,d,polys)
                source=root/f'seed-{index}.bin'
                write_certificate(source,n,d,seed,sq)
                outputs=[]
                for name,binary in [('reference',reference),('batched',candidate)]:
                    output=root/f'{name}-{index}.bin'
                    run=subprocess.run([binary,str(source),str(output),'4096',str(2**30)],text=True,capture_output=True,timeout=120,check=True)
                    observation=json.loads(run.stdout)
                    self.assertEqual(observation['status'],'candidate_certificate')
                    outputs.append(output.read_bytes())
                self.assertEqual(outputs[0],outputs[1])
                nn,dd,cols,q=struct.unpack_from('<4q',outputs[1])
                masks=struct.unpack_from('<'+str(cols)+'Q',outputs[1],32)
                width=8*max(1,(q+63)//64);offset=32+8*cols
                images={m:int.from_bytes(outputs[1][offset+j*width:offset+(j+1)*width],'little') for j,m in enumerate(masks)}
                independent_conditions(n,d+1,images,q,polys)
                if index==2:
                    self.assertGreater(cols,4096)
                    self.assertNotEqual(cols%4096,0)
                    self.assertNotEqual(q%64,0)
                rows.append(dict(variables=n,seed_degree=d,output_degree=dd,columns=cols,codimension=q,
                    certificate_sha256=hashlib.sha256(outputs[1]).hexdigest(),byte_identical=True,independent_conditions=True))
        if os.environ.get('SEMAEV_BATCHED_RECEIPT'):
            out=Path(os.environ['SEMAEV_BATCHED_RECEIPT'])
            with out.open('x') as f:
                json.dump(dict(scope='Software controls only; no timing or frontier inference',cases=rows,
                    binaries={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in [reference,candidate]}),f,indent=2)
                f.write('\n')


if __name__=='__main__':
    unittest.main()
