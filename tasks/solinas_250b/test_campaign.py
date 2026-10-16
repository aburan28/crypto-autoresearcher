"""Engineering seeds and small fixtures; never use the scientific stream."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from analyze import analyze
from campaign import run_campaign,read_record
from common import HERE,jobs_for,model_for,sha
from counts import summarize,discordance
from native import Engine,build,seed_for
from stores import make_archive,persist_archive
from verify_chunk import verify_job
from verify_chunk import frames
from oracle import affine_draw


class FakeS3:
    def __init__(self,bad=False):self.bad=bad;self.items={}
    def put_object(self,**params):
        body=params['Body'].read();digest=base64.b64encode(hashlib.sha256(body).digest()).decode()
        if digest!=params['ChecksumSHA256']:raise ValueError('Bad upload checksum')
        self.items[params['Key']]={'ContentLength':len(body),'ChecksumSHA256':'incorrect' if self.bad else digest,'Metadata':params['Metadata']}
    def head_object(self,**params):return self.items[params['Key']]


class CampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=json.loads((HERE/'inputs.json').read_text());cls.config=json.loads((HERE/'config.json').read_text())

    def test_exact_count_and_planted_joint_counts(self):
        jobs=jobs_for(self.inputs,self.config)
        self.assertEqual(sum(j['count']*(3 if j['named'] else 1)*256 for j in jobs),250000000000)
        self.assertEqual(len({m['p'] for m in self.inputs['ordinary_controls']}),125)
        scores=np.zeros((4,3,3),dtype=np.uint32);scores[:,:,0]=[[0,1,0],[1,1,0],[1,0,1],[0,0,1]]
        cfg=dict(self.config,longrun_spectrum=[1]);model={'metric_index':0};row=summarize(scores,model,cfg,True)['events']['run1']
        self.assertEqual(row['hits'],[2,2,2]);self.assertEqual(row['joint_counts'],[0,0,1,1,1,1,0,0]);self.assertEqual(discordance(row['joint_counts'],0,2),(1,1))

    def test_native_retention_cap_and_resource_failure(self):
        model=copy.deepcopy(self.inputs['candidates'][0]);model.update(metric_index=0,threshold_integer=1)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);directory=root/'attempts'/'sample';directory.mkdir(parents=True);(root/'artifacts').mkdir()
            engine=Engine(build(root/'engine.so'));job={'id':'fixture','model':model['id'],'named':True,'offset':0,'count':16}
            starts=seed_for('engineering-250b-v1','starts');gens=seed_for('engineering-250b-v1','generators')
            result=engine.sample(model['curve'],model['G'],1,16,0,1,starts,gens,directory,True,max_event_frames=2)
            result['bits'].tofile(directory/'bits.bin');result['scores'].astype('<u4').tofile(directory/'scores.bin');result['public_scalars'].tofile(directory/'public-scalars.bin')
            (directory/'invocation.json').write_text(json.dumps({'start_seed':starts.hex(),'generator_seed':gens.hex()}))
            (root/'artifacts'/'fixture').symlink_to(directory)
            record={'id':'fixture','files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in directory.iterdir()},'event_frame_cap':2,
                    'online_oncurve_checks':16*3*256,'selected_metric_event_counts':[16,16,16]}
            verified=verify_job(root,job,model,record)
            self.assertEqual(verified['rare_event_window_count'],16);self.assertEqual(verified['rare_frame_count'],2)
            raw=(directory/'coordinates.raw').read_bytes();stride=256*2*24
            expected=[hashlib.sha256(b''.join(raw[(w*3+c)*stride:(w*3+c+1)*stride] for w in range(16))).hexdigest() for c in range(3)]
            self.assertEqual(result['coordinate_sha256'],expected)
            with self.assertRaises(ArithmeticError) as failed:engine.sample(model['curve'],model['G'],1,2,0,1,starts,gens,root/'fail',event_limit_bytes=1)
            self.assertEqual(failed.exception.native_code,-6);self.assertEqual(failed.exception.oncurve_checks,768)

    def test_s3_checksum_and_preserved_source_on_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'raw').write_bytes(b'engineering public data')
            manifest={'raw':{'bytes':(root/'raw').stat().st_size,'sha256':sha(root/'raw')}}
            archive=root/'shard.zip';make_archive(root,archive,manifest)
            settings={'kind':'s3','bucket':'engineering-fixture','prefix':'fixture'}
            receipt=persist_archive(archive,settings,'design','job',FakeS3());self.assertTrue(receipt['verified'])
            with self.assertRaises(ValueError):persist_archive(archive,settings,'design','job',FakeS3(bad=True))
            self.assertTrue(archive.exists());self.assertEqual((root/'raw').read_bytes(),b'engineering public data')

    def test_extreme_frame_positive_control(self):
        curve={'p':101,'A':100,'B':0}
        curve['N']=1+sum(1+(0 if (x*x*x-x)%101==0 else (1 if pow((x*x*x-x)%101,50,101)==1 else -1)) for x in range(101))
        # Engineering-only seed selection avoids the order-two subgroup's infinity.
        for index in range(100):
            seed=seed_for('engineering-tiny-positive',index);counter=0;starts=[]
            for _ in range(16):point,counter=affine_draw(curve,seed,counter);starts.append(point)
            if all(point!=(0,0) for point in starts):break
        else:self.fail('No suitable engineering fixture seed')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);engine=Engine(build(root/'engine.so'))
            result=engine.sample(curve,[0,0],0,16,2,1000000,seed,seed_for('engineering-tiny-generators'),root/'sample',max_event_frames=2)
            self.assertTrue(np.all(result['scores'][:,:,0]==256))
            self.assertEqual((root/'sample/events.frames').stat().st_size,0)
            records=list(frames(root/'sample/events.frames.extreme',1,1))
            self.assertEqual(len(records),8);self.assertEqual([r[0] for r in records],list(range(8)))
            self.assertTrue(all(r[3]==1 for r in records))

    def test_resume_pipeline_and_record_corruption(self):
        inputs=copy.deepcopy(self.inputs);inputs['ordinary_controls']=[m for arm in ('R','C') for m in [x for x in inputs['ordinary_controls'] if x['arm']==arm][:2]]
        for model in inputs['candidates']+inputs['ordinary_controls']:model['windows']=4
        config=dict(self.config,seed='engineering-250b-pipeline-v1',chunk_windows=2,requested_point_observations=13312)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'run';first=run_campaign(root,inputs,config,{'kind':'aggregate'},1);second=run_campaign(root,inputs,config,{'kind':'aggregate'},1)
            self.assertTrue(first['fixed_sample_complete']);self.assertEqual(first['point_observations'],second['point_observations'])
            result=analyze(root);self.assertEqual(len(result['primary_tests']),20);self.assertEqual(len(result['rates']),30)
            path=next((root/'records').glob('*/record.json.gz'));blob=bytearray(path.read_bytes());blob[-5]^=1;path.write_bytes(blob)
            with self.assertRaises(ValueError):read_record(path)
            with self.assertRaises(ValueError):run_campaign(root,inputs,dict(config,seed='changed'),{'kind':'aggregate'},1)


if __name__=='__main__':unittest.main()
