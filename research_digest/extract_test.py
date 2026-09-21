import os, sys, time, json
from concurrent.futures import ProcessPoolExecutor
from pypdf import PdfReader

SRC = "/Volumes/Volume/research"
files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".pdf"))[:100]

def probe(fn):
    p = os.path.join(SRC, fn)
    try:
        r = PdfReader(p)
        t = (r.pages[0].extract_text() or "")[:300]
        return (fn, len(r.pages), len(t))
    except Exception as e:
        return (fn, -1, str(e)[:80])

t0 = time.time()
with ProcessPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(probe, files))
dt = time.time() - t0
ok = sum(1 for r in res if r[1] > 0 and isinstance(r[2], int) and r[2] > 50)
print(f"100 files in {dt:.1f}s -> est {dt/100*6439/60:.1f} min for all; text-ok={ok}/100")
for r in res[:5]: print(r)
