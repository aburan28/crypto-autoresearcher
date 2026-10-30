import datetime
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

session = Path(__file__).resolve().parent
name = sys.argv[1]
plan = json.loads((session / 'commands.json').read_text())[name]
out = session / 'logs'
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
clock = time.monotonic()
before = resource.getrusage(resource.RUSAGE_CHILDREN)
with (out / (name + '.stdout.txt')).open('wb') as stdout, (out / (name + '.stderr.txt')).open('wb') as stderr:
    result = subprocess.run(['timeout', '--signal=TERM', '--kill-after=5s', '120s', *plan['argv']], cwd=plan['cwd'], stdout=stdout, stderr=stderr)
after = resource.getrusage(resource.RUSAGE_CHILDREN)
receipt = {'name': name, 'argv': plan['argv'], 'cwd': plan['cwd'], 'started_utc': started,
    'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'wall_seconds': time.monotonic()-clock, 'cpu_user_seconds': after.ru_utime-before.ru_utime,
    'cpu_system_seconds': after.ru_stime-before.ru_stime, 'peak_child_rss_kib': after.ru_maxrss,
    'exit_code': result.returncode, 'classification': 'complete_valid' if result.returncode == 0 else ('timeout' if result.returncode == 124 else 'process_failed'),
    'scope': 'development_command_only', 'scientific_trial': False}
(out / (name + '.receipt.json')).write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
sys.exit(result.returncode)
