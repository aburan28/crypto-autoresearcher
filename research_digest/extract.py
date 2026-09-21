"""Extract first-page text from PDFs in /Volumes/Volume/research into JSONL manifest.

Resumable: skips files already present in the output JSONL.
Usage: python extract.py [start] [count]
"""
import os, sys, json, re
from concurrent.futures import ProcessPoolExecutor

SRC = "/Volumes/Volume/research"
OUT = "/Volumes/Volume/crypto-autoresearcher/research_digest/manifest.jsonl"
EXCLUDE = re.compile(r"VISASTMT|MCSTMT|STMSS|Bank statement", re.I)


def probe(fn):
    p = os.path.join(SRC, fn)
    rec = {"file": fn, "pages": None, "text": "", "error": None}
    try:
        from pypdf import PdfReader
        r = PdfReader(p)
        rec["pages"] = len(r.pages)
        parts = []
        for pg in r.pages[:2]:
            parts.append(pg.extract_text() or "")
            if sum(len(x) for x in parts) > 2500:
                break
        rec["text"] = re.sub(r"\s+", " ", " ".join(parts)).strip()[:2500]
        if len(rec["text"]) < 40:
            rec["error"] = "no_text_layer"
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    return rec


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
    files = sorted(
        f for f in os.listdir(SRC)
        if f.lower().endswith(".pdf") and not EXCLUDE.search(f)
    )
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)["file"])
                except Exception:
                    pass
    todo = [f for f in files if f not in done][start:start + count]
    print(f"total={len(files)} done={len(done)} processing={len(todo)}")
    with open(OUT, "a") as out:
        with ProcessPoolExecutor(max_workers=8) as ex:
            for i, rec in enumerate(ex.map(probe, todo, chunksize=8)):
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if (i + 1) % 200 == 0:
                    out.flush()
                    print(f"  {i + 1}/{len(todo)}", flush=True)
    print("chunk complete")


if __name__ == "__main__":
    main()
