import hashlib, subprocess
RECEIPT_A = "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/archives/TASK-20260907-c3f20c/snapshot_commit_receipt.json"
r = subprocess.run(["git", "show", "58ea24c71338f7fa53588729f0dfbf0acff17002:" + RECEIPT_A], capture_output=True)
print("receipt bytes at 58ea24c713 sha256:", hashlib.sha256(r.stdout).hexdigest())
live = hashlib.sha256(open(RECEIPT_A, "rb").read()).hexdigest()
print("live receipt sha256:", live)
print("same content:", hashlib.sha256(r.stdout).hexdigest() == live)
# check reachability from current HEAD
for ref in ["HEAD"]:
    p = subprocess.run(["git", "merge-base", "--is-ancestor", "58ea24c71338f7fa53588729f0dfbf0acff17002", ref])
    print(f"58ea24c713 ancestor of {ref}:", p.returncode == 0)
    p2 = subprocess.run(["git", "merge-base", "--is-ancestor", "ab711b0662d620930a3c0a1550916575a48910ce", ref])
    print(f"ab711b0662 ancestor of {ref}:", p2.returncode == 0)
    p3 = subprocess.run(["git", "merge-base", "--is-ancestor", "718af27faed4fbdb12f954663f70ade4b9884acd", ref])
    print(f"718af27fae ancestor of {ref}:", p3.returncode == 0)
    p4 = subprocess.run(["git", "merge-base", "--is-ancestor", "9e6396c35e82e5ef0cec3d95728f5b0c2b447f9e", ref])
    print(f"9e6396c35e ancestor of {ref}:", p4.returncode == 0)
