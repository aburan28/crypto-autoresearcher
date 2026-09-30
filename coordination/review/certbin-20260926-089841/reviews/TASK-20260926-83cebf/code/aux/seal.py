import hashlib, datetime, os, sys
d = sys.argv[1]
files = ["rederivation.json", "stream-replay.jsonl.gz", "wcerts.jsonl.gz"]
extra = ["logs/driver-pass1.log"]
def h(p):
    x = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            x.update(c)
    return x.hexdigest()
out = os.path.join(d, "seal.txt")
assert not os.path.exists(out), "seal.txt exists"
lines = ["# TASK-20260926-83cebf seal (BR-7). Written after the three sealed files and before report.yaml / attestation.yaml.",
         "sealed_utc: " + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")]
for f in files:
    lines.append("sha256 %s  %s  (%d bytes)" % (h(os.path.join(d, f)), f, os.path.getsize(os.path.join(d, f))))
for f in extra:
    lines.append("sha256 %s  %s  (%d bytes; run log of the same pass, sealed alongside)" % (h(os.path.join(d, f)), f, os.path.getsize(os.path.join(d, f))))
with open(out, "w") as fo:
    fo.write("\n".join(lines) + "\n")
print(open(out).read())
