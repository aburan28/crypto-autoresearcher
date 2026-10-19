import json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user/bc80ee7c-3e63-5cdc-8921-64b426219182/scratchpad/readers/costmodel/scripts')
from decode import load, walk
o = load(sys.argv[1])
for i, r in enumerate(o['records']):
    print('--- record', i)
    walk(r, maxlist=4)
