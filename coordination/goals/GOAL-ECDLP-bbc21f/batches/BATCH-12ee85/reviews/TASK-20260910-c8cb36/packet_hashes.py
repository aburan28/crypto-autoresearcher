import hashlib, json
att = json.load(open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/TASK-20260907-7afa98/reading_attestation.json"))
PK = "experiments/EXP-ECDLP-6ac801/derivation-packet/PA-ECDLP-6ac801-v2-to-v3"
out = {}
for e in att["files_read_before_seal"]:
    p = e["path"]
    live = hashlib.sha256(open(p, "rb").read()).hexdigest()
    out[p.split("/")[-1]] = {
        "attested_sha": e["sha256_as_read"],
        "committed_live_sha": live,
        "match": live == e["sha256_as_read"],
        "matches_manifest_declared": e.get("matches_manifest_declared_hash"),
    }
man = open(f"{PK}/MANIFEST.yaml").read()
print(json.dumps(out, indent=1))
print("manifest declares quantity.md hash:",
      any("7040669a86549365d338fb2062a76b7e5e8a7664c8f555835e38e1ed352ffb68" in man for _ in [0]))
