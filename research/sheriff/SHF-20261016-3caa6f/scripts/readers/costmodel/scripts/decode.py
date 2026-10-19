import json, base64, sys
def load(path):
    s = open(path).read()
    for l in s.splitlines():
        if l.startswith('raw_b64='):
            return json.loads(base64.b64decode(l[len('raw_b64='):]))
    return None
def walk(o, p='', depth=0, maxlist=3):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + '.' + k, depth + 1, maxlist)
    elif isinstance(o, list):
        print(p, 'list len', len(o), str(o[:maxlist])[:200])
    else:
        print(p, '=', str(o)[:200])
if __name__ == '__main__':
    o = load(sys.argv[1])
    walk(o)
