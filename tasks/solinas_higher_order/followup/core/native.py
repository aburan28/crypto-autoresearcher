"""Small wrapper around the auditable OpenSSL sampler; public seeds only."""
import ctypes
import hashlib
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build(target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['cc', '-O3', '-shared', '-fPIC', str(HERE / 'native.c'),
                    '-o', str(target), '-lcrypto', '-Wall', '-Wextra'], check=True)
    return target


class Sampler:
    def __init__(self, library):
        self.lib = ctypes.CDLL(str(library))
        self.lib.sample.argtypes = [ctypes.c_char_p] * 6 + [ctypes.c_char_p, ctypes.c_int,
                                                          ctypes.c_uint64, ctypes.c_void_p,
                                                          ctypes.POINTER(ctypes.c_uint64)]
        self.lib.sample.restype = ctypes.c_int

    def sample(self, curve, generator, seed, mode, count):
        width = (curve['p'].bit_length() + 7) // 8
        output = ctypes.create_string_buffer(count * 2 * width)
        used = ctypes.c_uint64()
        parameters = [curve[k] for k in ('p', 'A', 'B', 'N')] + list(generator)
        if not self.lib.sample(*[str(v).encode() for v in parameters], seed,
                               mode, count, output, ctypes.byref(used)):
            raise ArithmeticError('Native point sampler refused an input or failed')
        return output.raw, used.value


def seed_for(*parts):
    return hashlib.sha256('|'.join(map(str, parts)).encode()).digest()
