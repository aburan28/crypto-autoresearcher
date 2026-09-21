import sys,json,pathlib,importlib.util,hashlib
root=pathlib.Path('/Volumes/SSD990/crypto-autoresearcher/.worktrees/coordinator-a-recovery/coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch/fixtures/mirror-hardlink-native-receipt/repo')
target=pathlib.Path('/Volumes/SSD990/crypto-autoresearcher/.worktrees/coordinator-a-recovery/coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch/fixtures/mirror-hardlink-native-receipt/repo/experiments/EXP-ECDLP-abf981/source-v4/locked_entry.py')
raw_source=target.read_text()
source=raw_source.rsplit('\nif __name__ == "__main__":',1)[0]
__file__=str(target)
exec(compile(source,str(target),'exec'),globals())
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--launch-context-fd',type=int,required=True)
parser.parse_args(['--launch-context-fd','3'])
path=root/'harness/finite_yaml_locked_v3.py'
spec=importlib.util.spec_from_file_location('_finite_yaml_locked_v3',path)
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
import fcntl
origins={name:str(pathlib.Path(m.__file__).resolve()) for name,m in sys.modules.copy().items() if getattr(m,'__file__',None) and not str(m.__file__).startswith('<')}
images=module.loaded_images()
print(json.dumps({'module_origins':origins,'loaded_images':images,'source_file':str(target),'source_sha256':hashlib.sha256(raw_source.encode()).hexdigest(),'probe_scope':'Actual top-level source import and runtime dependency metadata only. Main, descriptor admission, worker and scientific functions were not executed. Expected identities remain subject to exact comparison during independent normal admission.'},sort_keys=True))
