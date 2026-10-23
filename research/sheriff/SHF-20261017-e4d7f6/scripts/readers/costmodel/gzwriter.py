#!/usr/bin/env python3
"""Does fbarchive.py's gz writer (gzip.compress(level 9, mtime 0)) reproduce the three newly indexed .gz archives?
Usage: python3 -I -B gzwriter.py <fb-archive-dir>"""
import gzip, hashlib, sys, os, platform
d = sys.argv[1]
print("python", platform.python_version(), "OS byte of gzip.compress here:", gzip.compress(b"x", compresslevel=9, mtime=0)[9])
for p in ["bases/EC1N23Ckb1h32a1300cea95/geomtraceu-l12-s1-52255f249712.json.gz",
          "bases/EC1N23Ckb1h32a1300cea95/geomtraceu-l13-s1-3765b6511827.json.gz",
          "bases/EC1N41Ckb1h9d49bc0affd2/geomtraceu-l15-s1-9207924c70d0.json.gz"]:
    blob = open(os.path.join(d, p), "rb").read()
    again = gzip.compress(gzip.decompress(blob), compresslevel=9, mtime=0)
    print(p.split("/")[-1], "file_sha256", hashlib.sha256(blob).hexdigest()[:16], "re-compressed identical:", again == blob, len(blob), len(again))
print("-- byte positions that differ between file and re-compression:")
for p in ["bases/EC1N23Ckb1h32a1300cea95/geomtraceu-l12-s1-52255f249712.json.gz",
          "bases/EC1N23Ckb1h32a1300cea95/geomtraceu-l13-s1-3765b6511827.json.gz",
          "bases/EC1N41Ckb1h9d49bc0affd2/geomtraceu-l15-s1-9207924c70d0.json.gz"]:
    blob = open(os.path.join(d, p), "rb").read()
    again = gzip.compress(gzip.decompress(blob), compresslevel=9, mtime=0)
    print(p.split("/")[-1], [i for i in range(len(blob)) if blob[i] != again[i]][:10])
