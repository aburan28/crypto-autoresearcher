#!/usr/bin/env python3
"""Keep one OpenCode/Cairn MCP node alive for the campaign autopilot.

OpenCode owns the MCP child, including Cairn's exclusive log lock. Attaching
each bounded campaign action to this server preserves one node across actions
and leaves the campaign's own evidence and retry rules in autopilot.py.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from orchestration.campaign.autopilot import supervise  # noqa: E402


def mcp_connected(url: str) -> bool:
    """A healthy HTTP server alone says nothing about its Cairn child."""
    with urllib.request.urlopen(url + "/global/health", timeout=3) as response:
        if not json.load(response).get("healthy"):
            return False
    with urllib.request.urlopen(url + "/mcp", timeout=3) as response:
        status = json.load(response).get("cairn", {})
    return status.get("status") == "connected"


def wait_for_mcp(process: subprocess.Popen, url: str, seconds: int = 300) -> None:
    deadline = time.monotonic() + seconds
    last = "not ready"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"OpenCode server exited {process.returncode}: {last}")
        try:
            if mcp_connected(url):
                return
            last = "Cairn MCP is not connected"
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last = str(exc)
        time.sleep(1)
    raise RuntimeError(f"OpenCode/Cairn MCP did not become ready: {last}")


@contextmanager
def stop_on_sigterm():
    """Allow the child cleanup blocks to run when launchd stops the service."""
    previous = signal.getsignal(signal.SIGTERM)

    def stop(signum, _frame):
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, stop)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--cairn-bin", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--cairn-data", type=Path, required=True)
    parser.add_argument("--opencode-port", type=int, default=4096)
    parser.add_argument("--cairn-listen", default="127.0.0.1:9000")
    parser.add_argument("--cairn-serve", default="127.0.0.1:8080")
    parser.add_argument("--bootstrap", type=Path, action="append", default=[],
                        help="trusted Cairn peer bootstrap file; repeat for more peers")
    parser.add_argument("--attest-identity", type=Path,
                        help="separate funded validator identity for this node")
    parser.add_argument("--local-model-url",
                        help="override opencode.json's local vLLM base URL")
    parser.add_argument("--backend", action="append", default=None)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--check", action="store_true",
                        help="verify the OpenCode/Cairn server, then stop without an action")
    parser.add_argument("--idle-seconds", type=int, default=60)
    parser.add_argument("--timeout", type=int, default=7200)
    args = parser.parse_args(argv)

    repo, state_dir = args.repo.resolve(), args.state_dir.resolve()
    if not (repo / "opencode.json").is_file():
        parser.error(f"no opencode.json in {repo}")
    try:
        local_model_url = (args.local_model_url or json.loads(
            (repo / "opencode.json").read_text(encoding="utf-8"))
            ["provider"]["vllm"]["options"]["baseURL"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(f"cannot resolve the local model URL: {exc}")
    if not args.cairn_bin.is_file() or not os.access(args.cairn_bin, os.X_OK):
        parser.error(f"Cairn binary is not executable: {args.cairn_bin}")
    if not args.identity.is_file():
        parser.error(f"Cairn identity is missing: {args.identity}")
    for peer in args.bootstrap:
        if not peer.is_file():
            parser.error(f"Cairn bootstrap file is missing: {peer}")
    if args.attest_identity and not args.attest_identity.is_file():
        parser.error(f"Cairn validator identity is missing: {args.attest_identity}")
    if not 1 <= args.opencode_port <= 65535:
        parser.error("--opencode-port must be between 1 and 65535")

    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state_dir, 0o700)
    cairn_data = args.cairn_data.resolve()
    cairn_data.mkdir(parents=True, exist_ok=True, mode=0o700)
    xdg = state_dir / "xdg"
    for name in ("data", "state", "cache", "config"):
        (xdg / name).mkdir(parents=True, exist_ok=True, mode=0o700)
    env = os.environ.copy()
    # A demo epoch, another node's log, or a legacy MCP binary inherited from
    # an operator shell would change this service's identity and log semantics.
    for name in ("CAIRN_EPOCH_SECONDS", "CAIRN_LOG", "CAIRN_MCP_BIN",
                 "CAIRN_BOOTSTRAP", "CAIRN_ATTEST_IDENTITY"):
        env.pop(name, None)
        os.environ.pop(name, None)
    env.update({
        # OpenCode indexes this large checkout. The machine's system volume
        # can be full while the research SSD still has working space.
        "XDG_DATA_HOME": str(xdg / "data"),
        "XDG_STATE_HOME": str(xdg / "state"),
        "XDG_CACHE_HOME": str(xdg / "cache"),
        "XDG_CONFIG_HOME": str(xdg / "config"),
        "CAIRN_BIN": str(args.cairn_bin.resolve()),
        "CAIRN_IDENTITY": str(args.identity.resolve()),
        "CAIRN_DATA": str(cairn_data),
        "CAIRN_MODE": "node",
        "CAIRN_SEEDS": "off",
        "CAIRN_LISTEN": args.cairn_listen,
        "CAIRN_SERVE": args.cairn_serve,
        "CAIRN_MCP_MAX_SPEND": "0",
        "CAIRN_KEY": str(state_dir / "cairn.key"),
        "CAIRN_BRIDGE_LOG": str(state_dir / "stage0.jsonl"),
        "LOCAL_LLM_BASE_URL": local_model_url,
    })
    if args.bootstrap:
        env["CAIRN_BOOTSTRAP"] = ":".join(str(peer.resolve()) for peer in args.bootstrap)
    if args.attest_identity:
        env["CAIRN_ATTEST_IDENTITY"] = str(args.attest_identity.resolve())
    # Keep the adapter and its child process on the same backend endpoint.
    os.environ.update(env)
    url = f"http://127.0.0.1:{args.opencode_port}"
    with stop_on_sigterm(), (state_dir / "opencode.log").open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            ["opencode", "serve", "--hostname", "127.0.0.1", "--port",
             str(args.opencode_port)], cwd=repo, env=env,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            wait_for_mcp(process, url)
            print(f"Cairn MCP connected through {url}; campaign state: {state_dir}",
                  flush=True)
            if args.check:
                return 0

            def sleep_or_fail(seconds: float) -> None:
                if process.poll() is not None:
                    raise RuntimeError("OpenCode/Cairn server stopped during campaign")
                time.sleep(seconds)

            supervise(repo, state_dir, backends=args.backend or ["local"],
                      max_actions=1 if args.once else None,
                      idle_seconds=args.idle_seconds, timeout=args.timeout,
                      attach=url, sleeper=sleep_or_fail)
            return 0
        finally:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as exc:
        print(f"cairn_autopilot_service: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
