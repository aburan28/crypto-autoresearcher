"""Deterministic preparation utilities; public synthetic mathematical inputs only."""
import hashlib
import hmac
import json
import os
import resource
import subprocess
import time
from pathlib import Path

from finite_math import Curve

GP = Path('/workspace/solinas-runtime/pari/usr/bin/gp')
PARI_LIB = str(GP.parent.parent / 'lib/x86_64-linux-gnu')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


class Stream:
    """HMAC-SHA256 stream; rejection gives exact uniform bounded integers."""
    def __init__(self, domain):
        self.key = hashlib.sha256(str(domain).encode()).digest()
        self.counter = 0
        self.buffer = b''

    def bytes(self, n):
        while len(self.buffer) < n:
            self.buffer += hmac.new(self.key, self.counter.to_bytes(8, 'big'), hashlib.sha256).digest()
            self.counter += 1
        out, self.buffer = self.buffer[:n], self.buffer[n:]
        return out

    def below(self, n):
        bits = n.bit_length()
        while True:
            x = int.from_bytes(self.bytes((bits + 7) // 8), 'big') & ((1 << bits) - 1)
            if x < n:
                return x


def gp_environment():
    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = PARI_LIB + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
    return env


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (4 << 30, 4 << 30))


def gp_file(source, output, timeout=600):
    started = time.monotonic()
    result = subprocess.run([str(GP), '-q', '-f', '-s', '128M', str(source)],
                            capture_output=True, text=True, env=gp_environment(),
                            timeout=timeout, preexec_fn=limits)
    Path(str(output) + '.stdout').write_text(result.stdout)
    Path(str(output) + '.stderr').write_text(result.stderr)
    if result.returncode or '***' in result.stderr:
        raise RuntimeError(f'GP failed: {source}: {result.stderr[:500]}')
    return result.stdout, {'elapsed_seconds': time.monotonic() - started,
                           'exit_code': result.returncode, 'command': [str(GP), '-q', '-f', '-s', '128M', str(source)]}


def sqrt_mod(x, p):
    if x == 0:
        return 0
    if pow(x, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(x, (p + 1) // 4, p)
    s, d = 0, p - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    c, r, t, m = pow(z, d, p), pow(x, (d + 1) // 2, p), pow(x, d, p), s
    while t != 1:
        i, v = 0, t
        while v != 1:
            v = v * v % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        r, t, c, m = r * b % p, t * b * b % p, b * b % p, i
    return r


def generator(row, ell=None, domain='generator'):
    p, A, B, N = row['p'], row['A'], row['B'], row['N']
    ell = ell or row['ell']
    curve = Curve(p, A, B)
    stream = Stream(f'{domain}/{row["modulus_id"]}/{row["index"]}/{ell}')
    for draw in range(20000):
        x = stream.below(p)
        y = sqrt_mod((x * x * x + A * x + B) % p, p)
        if y is None:
            continue
        if stream.below(2):
            y = -y % p
        point = curve.mul((x, y), N // ell)
        if point is not None:
            assert curve.on_curve(point) and curve.mul(point, ell) is None
            return list(point), draw + 1
    raise RuntimeError('Fixed generator candidate limit reached')
