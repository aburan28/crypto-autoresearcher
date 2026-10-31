"""Restore the caller environment from a private pipe, then exec admitted V.

Invocation belongs inside a systemd scope with a 2 GiB memory.max and no swap.
The environment is never written to disk or printed. The remaining stdin is
left untouched for Codex's private prompt.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import struct
import sys


def read_exact(size):
    chunks = []
    while size:
        part = os.read(0, size)
        if not part:
            raise RuntimeError('truncated private launch envelope')
        chunks.append(part)
        size -= len(part)
    return b''.join(chunks)


length = struct.unpack('!I', read_exact(4))[0]
assert 0 < length < 1024 * 1024
payload = json.loads(read_exact(length))
env = payload['environment']
assert isinstance(env, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in env.items())
os.environ.clear()
os.environ.update(env)
assert os.getuid() == 1000 and os.getgid() == 1000
assert Path.cwd().resolve() == Path('/var/tmp/sembin-custody-review-20261030').resolve()
assert resource.getrlimit(resource.RLIMIT_AS) == (-1, -1)
cgroup = Path('/sys/fs/cgroup') / Path(Path('/proc/self/cgroup').read_text().strip().split('::', 1)[1]).relative_to('/')
assert (cgroup / 'memory.max').read_text().strip() == '2147483648'
assert (cgroup / 'memory.swap.max').read_text().strip() == '0'
status = {'uid': os.getuid(), 'gid': os.getgid(), 'cgroup': str(cgroup),
          'memory_max_bytes': 2147483648, 'memory_swap_max_bytes': 0,
          'rlimit_as': list(resource.getrlimit(resource.RLIMIT_AS)),
          'caller_environment_restored': True}
if payload.get('check_only') is True:
    print(json.dumps(status), flush=True)
    sys.exit(0)
argv = payload['argv']
assert isinstance(argv, list) and all(isinstance(a, str) for a in argv)
binary = Path(argv[0]).resolve()
assert hashlib.sha256(binary.read_bytes()).hexdigest() == '399ff69c431c066e40de318fba45c2b07f45a76b19939d247ee4828fc70c4215'
assert 'resume' in argv and '01a18ea8-059d-7e33-b337-1bb419b2161d' in argv
assert argv[-1] == '-', 'private prompt must remain on stdin'
print('V_CGROUP_LIMIT ' + json.dumps(status), file=sys.stderr, flush=True)
os.execvpe(str(binary), [str(binary), *argv[1:]], env)
