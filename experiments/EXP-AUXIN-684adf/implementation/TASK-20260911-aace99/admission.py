"""Canonical-supervisor admission bridge. No caller boolean is accepted."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
class AdmissionRefused(RuntimeError): pass
def _read(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def _digest(path):
    with open(path,"rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def canonical_admission(repo:Path, plan:Path, trial_id:str, run_dir:Path, *, authority_adapter=None):
    launch=run_dir/"launch.json"
    if not launch.is_file(): raise AdmissionRefused("missing canonical supervisor launch")
    record=_read(launch)
    if record.get("trial_id")!=trial_id:raise AdmissionRefused("trial identity mismatch")
    if record.get("plan_sha256")!=_digest(plan):raise AdmissionRefused("plan digest mismatch")
    # The adapter is injectable only by unit_checks; CLI callers have no bypass flag.
    if authority_adapter is None:
        sys.path.insert(0,str(repo)); from tools import experiment_execution as supervisor
        try: authority_adapter=supervisor.authorize
        except AttributeError as exc: raise AdmissionRefused("canonical supervisor authorize unavailable") from exc
    owner,epoch=record.get("owner"),record.get("epoch")
    if not isinstance(owner,str) or not isinstance(epoch,int) or epoch<=0:raise AdmissionRefused("missing supervisor owner/epoch")
    try: authority_adapter(repo,plan,record,owner,epoch)
    except Exception as exc: raise AdmissionRefused("canonical authorization refused") from exc
    return {"lock_enforcement":"canonical_supervisor_owned","lock_independently_verified_by_payload":False,"launch":record}
