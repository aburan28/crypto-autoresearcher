import sys,json,pathlib,importlib.util,hashlib
root=pathlib.Path('/Volumes/SSD990/crypto-autoresearcher/.worktrees/coordinator-a-recovery/coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch/fixtures/mirror-symlink-native-receipt/repo')
target=pathlib.Path('/Volumes/SSD990/crypto-autoresearcher/.worktrees/coordinator-a-recovery/coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch/fixtures/mirror-symlink-native-receipt/repo/tests/test_finite_yaml_locked_v3.py')
raw_source=target.read_text()
source=raw_source.rsplit('\nif __name__ == "__main__":',1)[0]
__file__=str(target)
exec(compile(source,str(target),'exec'),globals())
module=load(root)
closure=json.loads(pathlib.Path('/Volumes/SSD990/crypto-autoresearcher/.worktrees/coordinator-a-recovery/coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa-admission/linux-runtime-safe-custody.json').read_text())
closure={k:closure[k] for k in ('python','stdlib','distributions')}
closure.update(loaded_images={},module_origins={})
module._bind_dependency_files(closure,{})
module._p.git(root,{'path':'/usr/bin/git','sha256':hashlib.sha256(pathlib.Path('/usr/bin/git').read_bytes()).hexdigest()},['rev-parse','HEAD'],module.tool_environment())
import yaml,jsonschema
jsonschema.Draft202012Validator.check_schema(json.loads((root/'schemas/finite-yaml-execution-plan-v1.schema.json').read_text()))
module._p.load_core(root)
origins={name:str(pathlib.Path(m.__file__).resolve()) for name,m in sys.modules.copy().items() if getattr(m,'__file__',None) and not str(m.__file__).startswith('<')}
images=module.loaded_images()
print(json.dumps({'module_origins':origins,'loaded_images':images,'source_file':str(target),'source_sha256':hashlib.sha256(raw_source.encode()).hexdigest(),'probe_scope':'Actual top-level source import and runtime dependency metadata only. Main, descriptor admission, worker and scientific functions were not executed. Expected identities remain subject to exact comparison during independent normal admission.'},sort_keys=True))
