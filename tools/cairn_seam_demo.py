#!/usr/bin/env python3
"""One committed experiment through the cairn seam, end to end, on a node of
its own: the executable form of docs/cairn-runbook.md.

    python3 tools/cairn_seam_demo.py                      # EXP-DTREE-001 / RUN-DTREE-010
    python3 tools/cairn_seam_demo.py --exp EXP-X --run RUN-Y --index 3 --keep

What it does, in the order an operator would:

  1. mints three identities -- a treasury that funds the objective, an
     executor that submits, a validator that attests under bond -- and
     declares a supply, so a bond costs something;
  2. renders the experiment as a certificate objective with
     tools/exp_to_objective.py, holds it to cairn's shape rules, and posts
     it signed by the treasury;
  3. starts `cairn run` the way a Claude Code session does through
     .mcp.json: MCP on stdin, the HTTP API on --serve, the validator loop
     under --attest-identity, one exclusive log;
  4. drives the MCP tools an Executor has (list_objectives, score_candidate,
     submit_claim twice: commit, then reveal after the epoch turns);
  5. waits for the validator loop to re-run the pinned checker on the claim
     and stand behind its verdict, and reads that back from
     GET /knowledge/{claim} the way a Validator session would;
  6. prints the `external_verification:` block the Coordinator carries into
     the evidence record, holds it to tools/validate_ledger.py's invariant
     (b), and audits the finished log.

Nothing here touches the ledger or the committed experiment: the objective,
the log and the node's data live in a temporary directory (or --work), and
the printed block is for the Coordinator to carry, not for this script to
write. Epochs are shortened with CAIRN_EPOCH_SECONDS, which is for a log
used for nothing else -- never set it on a node that talks to peers.

Exit status: 0 when the claim was accepted, attested, and the block is
clean; 2 with one line on stderr when a step refused; 3 when cairn cannot
be used here (no binary, or one built without the reader `cairn run` needs).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import exp_to_objective as e2o  # noqa: E402

DEFAULT_EXP = "EXP-DTREE-001"
DEFAULT_RUN = "RUN-DTREE-010"
CLAIM_ID = re.compile(r"claim (sha256:[0-9a-f]{64})")
OBJECTIVE_ID = re.compile(r"objective (sha256:[0-9a-f]{64})")
VERDICT = re.compile(r"^verdict: (accept|reject|unavailable|invalid_spec)", re.M)
SCORE = re.compile(r"^(accept|reject|unavailable|invalid_spec)\b", re.M)
SUPPLY = 1_000_000


class Refused(Exception):
    """A step said no, with a reason. Exit 2."""


class Unusable(Exception):
    """cairn cannot be used on this machine. Exit 3."""


def say(line: str = "") -> None:
    print(line, flush=True)


def rule(title: str) -> None:
    say(f"\n== {title}")


# -- cairn, the binary -------------------------------------------------------------


def find_cairn(explicit: str | None) -> str:
    path = explicit or os.environ.get("CAIRN_BIN") or shutil.which("cairn")
    if not path or not os.access(path, os.X_OK):
        raise Unusable("no cairn binary: pass --cairn, set CAIRN_BIN, or put `cairn` on PATH")
    version = subprocess.run([path, "--version"], capture_output=True, text=True, check=False)
    banner = (version.stdout + version.stderr).strip()
    if "embedded" not in banner:
        raise Unusable(
            f"{path} was built without the reader, and `cairn run` needs it "
            f"(--version says: {banner.splitlines()[0] if banner else 'nothing'}); use a release "
            f"binary or `make ui-build` in the cairn checkout"
        )
    return path


class Cli:
    def __init__(self, cairn: str, log: Path, root: Path, env: dict[str, str]) -> None:
        self.cairn, self.log, self.root, self.env = cairn, log, root, env

    def run(self, *args: str, check: bool = True) -> str:
        proc = subprocess.run(
            [self.cairn, "--log", str(self.log), "--root", str(self.root), *args],
            capture_output=True, text=True, env=self.env, check=False,
        )
        if check and proc.returncode != 0:
            raise Refused(f"cairn {' '.join(args[:2])}: {(proc.stderr or proc.stdout).strip()}")
        return proc.stdout + proc.stderr


def public_key(identity: Path) -> str:
    return json.loads(identity.read_text(encoding="utf-8"))["public"]


# -- MCP over stdio, the way a client drives it ------------------------------------


class Mcp:
    """Newline-delimited JSON-RPC on the node's stdin/stdout. Closing stdin
    stops the node, which is the arrangement `cairn run` documents: the MCP
    client is the process supervisor."""

    def __init__(self, proc: subprocess.Popen[str]) -> None:
        self.proc = proc
        self.next_id = 1
        self.lines: list[str] = []
        self.lock = threading.Condition()
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self) -> None:
        assert self.proc.stdout is not None
        for line in self.proc.stdout:
            with self.lock:
                self.lines.append(line)
                self.lock.notify_all()

    def send(self, method: str, params: dict[str, Any] | None = None) -> int:
        """Write one request; returns its id for `receive`."""
        assert self.proc.stdin is not None
        request_id = self.next_id
        self.next_id += 1
        message = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()
        return request_id

    def call(self, method: str, params: dict[str, Any] | None = None, timeout: float = 120.0) -> dict[str, Any]:
        return self.receive(self.send(method, params), method, timeout)

    def receive(self, request_id: int, method: str = "?", timeout: float = 120.0) -> dict[str, Any]:
        """The answer carrying `request_id`, whenever it arrives: answers are
        matched by id, never by order."""
        deadline = time.monotonic() + timeout
        while True:
            with self.lock:
                for index, line in enumerate(self.lines):
                    try:
                        doc = json.loads(line)
                    except ValueError:
                        continue
                    if doc.get("id") == request_id:
                        del self.lines[index]
                        return doc
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise Refused(f"MCP {method}: no answer within {timeout:.0f}s")
                if self.proc.poll() is not None:
                    raise Refused(f"MCP {method}: the node exited with {self.proc.returncode}")
                self.lock.wait(min(remaining, 0.5))

    def tool(self, name: str, arguments: dict[str, Any]) -> str:
        doc = self.call("tools/call", {"name": name, "arguments": arguments})
        if "error" in doc:
            raise Refused(f"{name}: {doc['error'].get('message', doc['error'])}")
        result = doc.get("result") or {}
        text = "\n".join(
            part.get("text", "") for part in result.get("content", []) if isinstance(part, dict)
        )
        if result.get("isError"):
            raise Refused(f"{name}: {text.strip()}")
        return text


# -- HTTP, the way a reader asks -------------------------------------------------------


def http_json(url: str, timeout: float = 5.0) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310 (loopback)
        return json.loads(response.read().decode("utf-8"))


def wait_for(url: str, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    last = ""
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2.0) as response:  # noqa: S310 (loopback)
                if 200 <= response.status < 300:
                    return
                last = f"HTTP {response.status}"
        except (urllib.error.URLError, OSError, ValueError) as error:
            last = str(error)
            time.sleep(0.25)
    raise Refused(f"{url} did not answer within {seconds:.0f}s ({last})")


# -- the walk ----------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--exp", default=DEFAULT_EXP)
    parser.add_argument("--run", default=DEFAULT_RUN)
    parser.add_argument("--index", type=int, default=0, help="which of the run's kept witnesses to claim")
    parser.add_argument("--cairn", help="the cairn binary (default: $CAIRN_BIN, then PATH)")
    parser.add_argument("--work", help="working directory (default: a temporary one, removed unless --keep)")
    parser.add_argument("--keep", action="store_true", help="keep the working directory")
    parser.add_argument("--reward", type=int, default=100_000)
    parser.add_argument("--epoch-seconds", type=int, default=2)
    parser.add_argument("--serve", default="127.0.0.1:8787", help="the node's HTTP address")
    parser.add_argument("--listen", default="127.0.0.1:9107", help="the node's P2P address")
    parser.add_argument("--attest-wait", type=float, default=60.0, help="seconds to wait for the validator")
    args = parser.parse_args(argv)

    try:
        cairn = find_cairn(args.cairn)
    except Unusable as error:
        print(f"cairn_seam_demo: {error}", file=sys.stderr)
        return 3

    work = Path(args.work).resolve() if args.work else Path(tempfile.mkdtemp(prefix="cairn-seam-"))
    work.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "CAIRN_EPOCH_SECONDS": str(args.epoch_seconds), "CAIRN_SEEDS": "off"}
    log = work / "cairn.jsonl"
    node = NodeHandle()
    try:
        return walk(args, cairn, work, env, log, node)
    except Refused as error:
        print(f"cairn_seam_demo: {error}", file=sys.stderr)
        return 2
    except e2o.BridgeError as error:
        print(f"cairn_seam_demo: exp_to_objective: {error}", file=sys.stderr)
        return 2
    finally:
        node.stop()
        if args.keep or args.work:
            say(f"\nkept {work}")
        else:
            shutil.rmtree(work, ignore_errors=True)


class NodeHandle:
    """The one node this script starts, so the finally block can stop it
    however the walk ended: closing MCP stdin is the documented stop."""

    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None

    def stop(self) -> None:
        process, self.process = self.process, None
        if process is None or process.poll() is not None:
            return
        try:
            if process.stdin is not None:
                process.stdin.close()
            process.wait(timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            process.kill()


def walk(args: argparse.Namespace, cairn: str, work: Path, env: dict[str, str], log: Path,
         node: NodeHandle) -> int:
    cli = Cli(cairn, log, REPO, env)
    say(f"cairn    {cairn}")
    say(f"repo     {REPO}")
    say(f"log      {log}")
    say(f"epochs   {args.epoch_seconds}s (CAIRN_EPOCH_SECONDS; a local log, nothing else)")

    rule("identities and a declared supply")
    identities = {name: work / f"{name}.json" for name in ("treasury", "executor", "validator")}
    for name, path in identities.items():
        cli.run("identity", "--out", str(path))
    keys = {name: public_key(path) for name, path in identities.items()}
    for name in ("treasury", "validator"):
        cli.run("issue", "--holder", keys[name], "--units", str(SUPPLY))
    for name, key in keys.items():
        say(f"  {name:9} {key[:16]}…{' (funded)' if name != 'executor' else ''}")

    rule(f"render {args.exp} / {args.run} as a certificate objective")
    objective, provenance = e2o.render(REPO, args.exp, args.run, "certificate", args.reward, None, None)
    problems = e2o.check(objective, REPO)
    if problems:
        raise Refused("rendered objective fails its own check: " + "; ".join(problems))
    objective_path = work / "objective.json"
    objective_path.write_text(json.dumps(objective, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (work / "objective.provenance.yaml").write_text(yaml.safe_dump(provenance, sort_keys=True), encoding="utf-8")
    checker_sha256 = objective["verifier"]["checker_sha256"]
    say(f"  verifier {objective['verifier']['checker']} sha256 {checker_sha256[:16]}…")
    say(f"  specification sha256 {provenance['specification']['sha256'][:16]}…  run commit "
        f"{(provenance.get('run') or {}).get('commit') or '?'}")

    rule("post it, signed by the treasury (the Coordinator's funding decision, here a demo's)")
    posted = cli.run("post", str(objective_path), "--identity", str(identities["treasury"]))
    match = OBJECTIVE_ID.search(posted)
    if not match:
        raise Refused(f"post did not return an objective id: {posted.strip()}")
    objective_id = match.group(1)
    say(f"  {objective_id}")
    for line in posted.splitlines()[2:4]:
        say(f"  {line.strip()}")

    rule("the claim: one witness the run kept on disk")
    kept = e2o.witnesses(REPO, args.exp, args.run)
    if not kept:
        raise Refused(f"{args.run} kept no witness statement on disk; nothing to claim")
    if not 0 <= args.index < len(kept):
        raise Refused(f"{args.run} keeps {len(kept)} witness(es); --index {args.index} is out of range")
    chosen = kept[args.index]
    artifact = chosen["statement"]
    witness_name = f"{args.run} {chosen['source']}"
    say(f"  {len(kept)} witness(es) on disk; claiming #{args.index} from {chosen['source']}")
    say(f"  {json.dumps(artifact, sort_keys=True)}")

    rule("start the node: MCP on stdin, HTTP on --serve, the validator loop under bond")
    data = work / "node"
    data.mkdir(exist_ok=True)
    command = [
        cairn, "--log", str(log), "--root", str(REPO), "--data-dir", str(data),
        "run", "--listen", args.listen, "--serve", args.serve,
        "--mcp-identity", str(identities["executor"]),
        "--attest-identity", str(identities["validator"]),
        "--queue", str(data / "queue"),
    ]
    stderr_path = work / "node.stderr"
    process = subprocess.Popen(  # noqa: S603
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=stderr_path.open("w", encoding="utf-8"), text=True, env=env, bufsize=1,
    )
    node.process = process
    base = f"http://{args.serve}"
    wait_for(f"{base}/health", 30.0)
    say(f"  up: {base}  (stderr in {stderr_path.name})")
    mcp = Mcp(process)
    tools = mcp.call("tools/list")
    names = sorted(tool["name"] for tool in (tools.get("result") or {}).get("tools", []))
    say(f"  MCP tools: {', '.join(names)}")

    rule("the Executor's loop: list, score, commit, reveal")
    listing = mcp.tool("list_objectives", {})
    if objective_id not in listing:
        raise Refused("the posted objective is not in the node's listing")
    say(f"  list_objectives: the objective is open, reward {objective['reward']}")
    scored = mcp.tool("score_candidate", {"objective_id": objective_id, "artifact": artifact})
    verdict = SCORE.search(scored)
    say(f"  score_candidate: {scored.splitlines()[0]}")
    if not verdict or verdict.group(1) != "accept":
        raise Refused(f"the pinned checker did not accept the harness's witness: {scored.strip()}")
    submit = {"objective_id": objective_id, "submitter": keys["executor"], "artifact": artifact}
    committed = mcp.tool("submit_claim", submit)
    say(f"  submit_claim #1: {committed.splitlines()[0]}")
    time.sleep(args.epoch_seconds + 0.5)
    revealed = mcp.tool("submit_claim", submit)
    claim_match = CLAIM_ID.search(revealed)
    verdict_match = VERDICT.search(revealed)
    if not claim_match or not verdict_match:
        raise Refused(f"the reveal did not return a claim and a verdict: {revealed.strip()}")
    claim_id, claim_verdict = claim_match.group(1), verdict_match.group(1)
    say(f"  submit_claim #2: claim {claim_id[:24]}…  verdict {claim_verdict}")
    if claim_verdict != "accept":
        raise Refused(f"the node's verdict on the revealed claim is {claim_verdict}: {revealed.strip()}")

    rule("the validator loop re-runs the pinned checker and stands behind its verdict")
    deadline = time.monotonic() + args.attest_wait
    knowledge: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            knowledge = http_json(f"{base}/knowledge/{claim_id}")
        except (urllib.error.URLError, OSError, ValueError):
            knowledge = {}
        attestations = knowledge.get("attestations") or {}
        if attestations.get("accept", 0) >= 1:
            break
        time.sleep(1.0)
    attestations = knowledge.get("attestations") or {}
    if attestations.get("accept", 0) < 1:
        tail = stderr_path.read_text(encoding="utf-8", errors="replace").splitlines()[-5:]
        raise Refused(
            f"no attestation on the claim within {args.attest_wait:.0f}s; GET /knowledge says "
            f"{json.dumps(attestations)}; node stderr ends: {' | '.join(tail)}"
        )
    state = knowledge.get("state") or {}
    say(f"  GET /knowledge/{claim_id[:24]}…")
    say(f"    state: {json.dumps({k: v for k, v in state.items() if k != 'assertions'}, sort_keys=True)}")
    say(f"    attestations: accept {attestations.get('accept')}  reject {attestations.get('reject')}  "
        f"slashed {attestations.get('slashed')}  bond each {attestations.get('bond_each')}")
    for row in (attestations.get("attestations") or [])[:3]:
        say(f"      {row.get('status')} by {str(row.get('attestor'))[:16]}… at {row.get('created_at')}"
            f"  slashed {row.get('slashed')}")
    if not any(str(row.get("attestor")) == keys["validator"] for row in attestations.get("attestations") or []):
        raise Refused("an attestation landed, but not from this node's validator identity")

    rule("settlement: batched when the reveal epoch closes and clears the finality delay")
    settled = False
    deadline = time.monotonic() + max(30.0, 8 * args.epoch_seconds)
    while time.monotonic() < deadline:
        shown = mcp.tool("get_claim", {"claim_id": claim_id})
        if "settled: yes" in shown:
            settled = True
            say("  " + next(line for line in shown.splitlines() if line.startswith("settled:")))
            break
        time.sleep(1.0)
    if not settled:
        say("  not settled within the wait; the receipt says so (settled: false means not yet, never rejected)")
    chain = http_json(f"{base}/chain")
    log_head = chain.get("head")
    say(f"  GET /chain: head {str(log_head)[:24]}…  height {chain.get('height')}")

    rule("the receipt the Coordinator carries into the evidence record")
    block = e2o.record_block(
        args.exp, args.run, objective_id, claim_id, claim_verdict, base, log_head,
        settled, checker_sha256, e2o.NETWORK, None, witness=witness_name,
    )
    text = yaml.safe_dump({"external_verification": [block]}, sort_keys=False)
    (work / "external_verification.yaml").write_text(text, encoding="utf-8")
    say("  " + text.replace("\n", "\n  ").rstrip())

    rule("held to the ledger rule (tools/validate_ledger.py invariant (b))")
    import validate_ledger  # noqa: WPS433

    class Ctx:
        def __init__(self) -> None:
            self.errors: list[str] = []
            self.legacy_paths: set[str] = set()
            self.legacy_warnings: list[str] = []

        def err(self, path: str, msg: str, *, force: bool = False) -> None:
            self.errors.append(msg)

    ctx = Ctx()
    validate_ledger.check_external_verification(
        "ledger/evidence/EV-DEMO.yaml",
        {"proof_status": "certificate", "proof_refs": [claim_id], "external_verification": [block]},
        ctx,
    )
    if ctx.errors:
        raise Refused("the block fails the ledger rule: " + "; ".join(ctx.errors))
    say("  clean: an accepted, settling verdict may back a certificate proof_ref")

    rule("stop the node (closing MCP stdin) and audit the log it leaves")
    node.stop()
    audit = cli.run("audit")
    say("  " + audit.strip().splitlines()[-1])
    if "verified" not in audit:
        raise Refused(f"audit did not verify the log: {audit.strip()}")

    say("\nseam closed: objective rendered from the experiment, witness accepted by the pinned checker, "
        "attested under bond by an independent validator, receipt clean for the ledger")
    say(f"  objective {objective_id}")
    say(f"  claim     {claim_id}")
    say(f"  witness   {witness_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
