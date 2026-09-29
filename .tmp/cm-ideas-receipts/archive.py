import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

root = Path.cwd().resolve()
queue_path = Path(sys.argv[2] if len(sys.argv) > 2 else 'coordination/intake/cm-factor-base-20260905/dispatch_queue.json')
task_id = sys.argv[1]
queue = json.loads(queue_path.read_text())
tasks = {task['id']: task for task in queue['tasks']}
task = tasks[task_id]
assert task['role'] == 'coordinator' and task['archive']['kind'] == 'snapshot'
assert task['state'] == 'queued'
source_ids = task['archive']['source_task_ids']
assert all(tasks[source]['state'] == 'completed' for source in source_ids)
paths = sorted({*task['artifact_paths'], *(path for source in source_ids for path in tasks[source]['artifact_paths'])})
assert str(queue_path) not in paths
for path in paths:
    local = root / path
    assert not Path(path).is_absolute() and '..' not in Path(path).parts
    assert local.is_file() and not local.is_symlink()
    assert local.resolve().is_relative_to(root)

def git(*args):
    return subprocess.run(['git', *args], check=True, text=True, capture_output=True).stdout.strip()

assert not git('diff', '--cached', '--name-only'), 'Unexpected pre-existing staged work'
parent = git('rev-parse', 'HEAD')
hashes = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths}
git('add', '--', *paths)
assert git('diff', '--cached', '--name-only').splitlines() == paths
whitespace = subprocess.run(['git', 'diff', '--cached', '--check'], text=True, capture_output=True)
whitespace_notes = whitespace.stdout.splitlines()
if whitespace.returncode:
    allowed_eof_paths = {
        'coordination/intake/cm-factor-base-continuation-20260905/TASK-20260905-9a5084/' + name
        for name in ('ideas.json', 'generator-report.md', 'sources.json')
    }
    assert '--preserve-producer-eof' in sys.argv[3:], whitespace.stdout + whitespace.stderr
    assert whitespace_notes and not whitespace.stderr, whitespace.stdout + whitespace.stderr
    assert all(any(re.fullmatch(re.escape(path) + r':\d+: new blank line at EOF\.', line)
                   for path in allowed_eof_paths) for line in whitespace_notes), whitespace.stdout
    print('Preserving exact producer bytes; accepted only these EOF blank-line warnings:')
    print(whitespace.stdout)
message = task_id + ': snapshot ' + ' '.join(task['archive']['record_ids'])
print(git('commit', '-m', message))
commit = git('rev-parse', 'HEAD')
assert git('rev-parse', commit + '^') == parent
assert git('diff-tree', '--no-commit-id', '--name-only', '-r', commit).splitlines() == paths
for path, digest in hashes.items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
receipt = {'task_id': task_id, 'kind': 'snapshot', 'source_task_ids': source_ids,
           'commit_sha': commit, 'parent_sha': parent, 'path_sha256': hashes,
           'record_ids': task['archive']['record_ids'], 'commit_message': message,
           'verification': 'Exact staged/committed path sets, parent and live hashes checked after commit',
           'preserved_producer_eof_warnings': whitespace_notes}
output = Path('/Volumes/SSD990/crypto-autoresearcher/.tmp/cm-ideas-receipts') / (task_id + '-commit.json')
output.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'commit_sha': commit, 'parent_sha': parent, 'files': len(paths), 'receipt': str(output)}, indent=2))
