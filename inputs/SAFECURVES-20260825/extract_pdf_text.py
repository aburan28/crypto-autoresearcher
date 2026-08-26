import re, sys, zlib
def extract(path):
    raw = open(path,'rb').read()
    out = []
    for m in re.finditer(rb'stream\r?\n', raw):
        start = m.end()
        end = raw.find(b'endstream', start)
        if end < 0: continue
        chunk = raw[start:end]
        try: data = zlib.decompress(chunk)
        except Exception:
            try: data = zlib.decompressobj().decompress(chunk)
            except Exception: continue
        if b'Tj' not in data and b'TJ' not in data: continue
        txt = []
        for tm in re.finditer(rb'\((?:\\.|[^\\()])*\)|<([0-9A-Fa-f\s]+)>|(TJ|Tj|Td|TD|T\*|ET)', data):
            g = tm.group(0)
            if g in (b'Td', b'TD', b'T*', b'ET'):
                txt.append('\n'); continue
            if g in (b'TJ', b'Tj'): continue
            if g.startswith(b'<'):
                hexs = re.sub(rb'\s', b'', tm.group(1))
                try: b = bytes.fromhex(hexs.decode())
                except Exception: continue
                try: txt.append(b.decode('utf-16-be' if len(b)%2==0 else 'latin-1', 'replace'))
                except Exception: pass
                continue
            s = g[1:-1]
            s = re.sub(rb'\\([nrtbf()\\])', lambda mm: {b'n':b'\n',b'r':b'\r',b't':b'\t',b'b':b'',b'f':b''}.get(mm.group(1), mm.group(1)), s)
            s = re.sub(rb'\\([0-7]{1,3})', lambda mm: bytes([int(mm.group(1),8)&0xFF]), s)
            txt.append(s.decode('latin-1','replace'))
        out.append(''.join(txt))
    return '\n'.join(out)
if __name__ == '__main__':
    t = extract(sys.argv[1])
    t = re.sub(r'[ \t]+\n','\n',t); t = re.sub(r'\n{3,}','\n\n',t)
    sys.stdout.write(t)
