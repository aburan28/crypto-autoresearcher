"""Strict legacy-format binding; this is not a mathematical certificate prover."""
import re


def parse(payload, expected_root):
    text = payload.decode('ascii').replace('\\\n', '')
    words = text.split()
    if not words or any(re.fullmatch(r'-?\d+', w) is None for w in words):
        raise ValueError('noninteger or empty certificate')
    tokens = list(map(int, words))
    pos = 0

    def take():
        nonlocal pos
        if pos == len(tokens): raise ValueError('incomplete certificate')
        n = tokens[pos]; pos += 1
        return n

    def read_list():
        result = []
        while True:
            n = take()
            if n == 0: return result
            if n < 0: raise ValueError('negative list element')
            result.append(n)

    steps = []
    old_order = None
    while True:
        n = take()
        if n == 0:
            if not steps or pos != len(tokens): raise ValueError('trailing or empty certificate')
            break
        if n < 2 or (steps and n >= steps[-1]['n']): raise ValueError('root or chain order')
        if old_order is not None and old_order % n: raise ValueError('broken chain divisor')
        D, h = take(), take()
        step = {'n': n, 'D': D, 'h': h}
        if D == -1:
            if h == 0:
                step['pratt'] = read_list()
                if not step['pratt'] or step['pratt'][0] != n:
                    raise ValueError('Pratt root does not match record')
                if pos >= len(tokens) or tokens[pos] != 0:
                    raise ValueError('Pratt base must terminate chain')
            elif h in (1, 3):
                step['factors'], step['witnesses'] = read_list(), read_list()
                old_order = n - 1
            else: raise ValueError('unknown N-1 theorem')
        elif D == 1:
            if h != 1: raise ValueError('unknown N+1 theorem')
            step['factors'] = read_list()
            step['parameter'], step['witnesses'] = take(), read_list()
            old_order = n + 1
        elif D > 1:
            if h != -1: raise ValueError('unknown elliptic certificate format')
            step['m'], step['m_factors'] = take(), read_list()
            step['a'], step['b'], step['x'], step['y'] = take(), take(), take(), take()
            step['factors'] = read_list()
            old_order = step['m']
        else: raise ValueError('unknown discriminant route')
        steps.append(step)
    if steps[0]['n'] != expected_root: raise ValueError('wrong requested root')
    return steps


def admit(result, stdout, payload, expected_root):
    try:
        steps = parse(payload, expected_root)
    except (ValueError, UnicodeError):
        return False
    if not result.get('vm_valid') or result.get('child_exit') != 0:
        return False
    text = stdout.decode(errors='replace')
    rows = re.findall(r'^\s*(\d+):\s*(-?\d+)\s+([01])\s+', text, re.M)
    return (len(rows) == len(steps) and '%!%' not in text
            and all(int(i) == k and int(D) == step['D'] and ok == '1'
                    for k, ((i, D, ok), step) in enumerate(zip(rows, steps))))
