#!/usr/bin/env python3
"""Tests for the inter-session message bus.

The tests that matter are the ones pinning properties the bus would be
worthless without, each of which is a defect this repository has already paid
for once in another component:

  - `test_message_bytes_are_unchanged_by_reading_it` -- read state is DERIVED.
    The moment acking edits the message, two readers of a broadcast race on the
    same bytes and the bus acquires the conflict shape that took
    `knowledge/INDEX.md` out of git.
  - `test_two_sends_never_draw_the_same_name` -- ids are drawn, never counted.
    Sequential allocation is why `EXP-RT1476-001` and `DEC-20260727-003` exist
    as cautionary records; a bus with N concurrent writers cannot repeat it.
  - `test_broadcast_ack_is_per_reader` -- one reader acking a broadcast must
    not mark it handled for everyone else, which would silently drop mail.
  - `test_git_success_is_the_exit_code_not_the_output` -- `fetch` and `push`
    report on stderr and leave stdout empty, so a stdout-truthiness test calls
    a good push a failure and retries it four times.
  - `test_address_cannot_escape_the_bus_directory` -- an address becomes part
    of a filename.
"""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent_bus as ab


def run(root, *argv) -> int:
    return ab.main([argv[0], "--root", str(root), *argv[1:]])


class BusTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "bus"
        self.addCleanup(self._tmp.cleanup)
        # These are CLI entry points and they print. Every assertion below is
        # against parsed store state rather than stdout, so capturing it costs
        # no coverage and keeps a 21-test run readable.
        self._out = io.StringIO()
        ctx = contextlib.redirect_stdout(self._out)
        ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def send(self, sender="coordinator", to="executor", subject="s",
             body="b", **kw) -> str:
        before = set(os.listdir(ab._dir(str(self.root), "messages")))
        argv = ["send", "--from", sender, "--to", to, "--subject", subject,
                "--body", body, "--no-sync-hint"]
        for key, value in kw.items():
            argv += [f"--{key.replace('_', '-')}", str(value)]
        self.assertEqual(0, run(self.root, *argv))
        after = set(os.listdir(ab._dir(str(self.root), "messages")))
        return sorted(after - before)[0][:-len(".yaml")]

    def inbox(self, addr, **kw) -> list[str]:
        return [m["id"] for m in ab.inbox_for(str(self.root), addr, **kw)]


class Immutability(BusTestCase):
    def test_message_bytes_are_unchanged_by_reading_it(self) -> None:
        mid = self.send()
        path = self.root / "messages" / f"{mid}.yaml"
        before = path.read_bytes()
        run(self.root, "ack", mid, "--as", "executor")
        self.assertEqual(before, path.read_bytes(),
                         "acking edited the message; read state must be derived "
                         "from receipts, never written into the message")
        self.assertTrue((self.root / "receipts" / f"{mid}--executor.yaml").exists())

    def test_a_message_path_cannot_be_written_twice(self) -> None:
        mid = self.send()
        path = self.root / "messages" / f"{mid}.yaml"
        with self.assertRaises(SystemExit):
            ab._write_once(str(path), {"message": {"id": mid}}, header="#")

    def test_acking_twice_is_idempotent_not_an_error(self) -> None:
        mid = self.send()
        self.assertEqual(0, run(self.root, "ack", mid, "--as", "executor"))
        self.assertEqual(0, run(self.root, "ack", mid, "--as", "executor"))


class Identifiers(BusTestCase):
    def test_two_sends_never_draw_the_same_name(self) -> None:
        ids = {self.send(subject=f"m{i}") for i in range(50)}
        self.assertEqual(50, len(ids))

    def test_mint_does_not_scan_state_to_choose(self) -> None:
        # Same seed, empty store: the draw is a function of the RNG alone. If
        # minting ever consults "what is the highest so far", this diverges.
        a = ab.mint_id(str(self.root), seed=7, today="20260809")
        b = ab.mint_id(str(self.root), seed=7, today="20260809")
        self.assertEqual(a, b)
        self.assertRegex(a, ab.MSG_ID)

    def test_malformed_message_id_is_refused(self) -> None:
        for bad in ("MSG-2026-08-09-abc", "MSG-20260809-ZZZZZZ", "../../etc/passwd",
                    "MSG-20260809-abc"):
            with self.assertRaises(SystemExit, msg=bad):
                ab._check_msg_id(bad)


class Addressing(BusTestCase):
    def test_address_cannot_escape_the_bus_directory(self) -> None:
        # An address becomes part of a receipt filename, so a separator or a
        # bare `..` here would write outside the store.
        for bad in ("../etc", "a/b", "..", "/abs", "Upper", "", "x" * 65):
            with self.assertRaises(SystemExit, msg=bad):
                ab._check_addr(bad)

    def test_sender_does_not_receive_own_message(self) -> None:
        self.send(sender="coordinator", to="coordinator,executor")
        self.assertEqual([], self.inbox("coordinator"))
        self.assertEqual(1, len(self.inbox("executor")))

    def test_broadcast_reaches_an_address_that_was_never_named(self) -> None:
        mid = self.send(to="all")
        self.assertIn(mid, self.inbox("red-team"))
        self.assertIn(mid, self.inbox("validator"))

    def test_broadcast_ack_is_per_reader(self) -> None:
        mid = self.send(to="all")
        run(self.root, "ack", mid, "--as", "validator")
        self.assertEqual([], self.inbox("validator"))
        self.assertIn(mid, self.inbox("red-team"),
                      "one reader's ack hid a broadcast from another reader")

    def test_empty_body_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            run(self.root, "send", "--from", "a", "--to", "b",
                "--subject", "s", "--body", "   ")


class Threading(BusTestCase):
    def test_reply_goes_to_the_sender_and_keeps_the_thread(self) -> None:
        parent = self.send(sender="coordinator", to="executor")
        self.assertEqual(0, run(self.root, "reply", parent, "--from", "executor",
                                "--body", "ok", "--no-sync-hint"))
        got = ab.inbox_for(str(self.root), "coordinator")
        self.assertEqual(1, len(got))
        self.assertEqual(parent, got[0]["thread"])
        self.assertEqual(parent, got[0]["in_reply_to"])
        self.assertTrue(got[0]["subject"].startswith("Re: "))

    def test_replying_acks_the_parent(self) -> None:
        parent = self.send(sender="coordinator", to="executor")
        run(self.root, "reply", parent, "--from", "executor", "--body", "ok",
            "--no-sync-hint")
        self.assertEqual([], self.inbox("executor"))

    def test_reply_to_a_broadcast_does_not_rebroadcast(self) -> None:
        # Otherwise every reply fans back out to everyone, and each of those
        # replies fans out again. The bus becomes a loop generator.
        parent = self.send(sender="coordinator", to="all")
        run(self.root, "reply", parent, "--from", "validator", "--body", "ok",
            "--no-sync-hint")
        reply = ab.inbox_for(str(self.root), "coordinator")[0]
        self.assertEqual(["coordinator"], reply["to"])

    def test_thread_of_a_reply_gathers_the_whole_exchange(self) -> None:
        parent = self.send(sender="coordinator", to="executor")
        run(self.root, "reply", parent, "--from", "executor", "--body", "ok",
            "--no-sync-hint")
        reply = ab.inbox_for(str(self.root), "coordinator")[0]["id"]
        self.assertEqual(0, run(self.root, "thread", reply))


class Ordering(BusTestCase):
    def test_same_second_messages_get_a_stable_order(self) -> None:
        # Two readers must agree on order even when wall-clock cannot separate
        # the sends, so the id is the tiebreak.
        sent = {self.send(subject=f"m{i}") for i in range(8)}
        order = [m["id"] for m in ab.load_messages(str(self.root))]
        self.assertEqual(sent, set(order))
        self.assertEqual(order, [m["id"] for m in ab.load_messages(str(self.root))])
        # Sends inside one second share a timestamp, so the id alone decides.
        self.assertEqual(sorted(order), order)

    def test_unparseable_message_is_skipped_not_fatal(self) -> None:
        good = self.send()
        (self.root / "messages" / "MSG-20260809-bad999.yaml").write_text(
            "message: [unclosed\n")
        self.assertIn(good, self.inbox("executor"))


class GitTransport(BusTestCase):
    def test_git_success_is_the_exit_code_not_the_output(self) -> None:
        repo = Path(self._tmp.name) / "repo"
        repo.mkdir()
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        subprocess.run(["git", "init", "-q"], cwd=repo, env=env, check=True)
        # `git gc --quiet` succeeds with empty stdout. Under the old
        # stdout-truthiness test this read as failure, which is exactly how a
        # good `push` got retried four times and then reported as an error.
        ok, out = ab._git_run(["gc", "--quiet"], cwd=str(repo))
        self.assertTrue(ok)
        self.assertEqual("", out)
        self.assertFalse(ab._git_run(["rev-parse", "no-such-ref"], cwd=str(repo))[0])

    def test_sync_outside_a_repo_is_not_an_error(self) -> None:
        import argparse
        args = argparse.Namespace(root=str(self.root), remote="origin",
                                  branch=None, push=False, message=None)
        self.assertEqual(0, ab.cmd_sync(args))


class Registration(BusTestCase):
    def test_register_preserves_first_seen_and_refreshes_last_seen(self) -> None:
        run(self.root, "register", "--as", "executor", "--role", "executor")
        path = self.root / "sessions" / "executor.yaml"
        first = ab._load(str(path))["session"]["first_registered_at"]
        run(self.root, "register", "--as", "executor")
        again = ab._load(str(path))["session"]
        self.assertEqual(first, again["first_registered_at"])
        self.assertEqual("executor", again["role"],
                         "re-registering without --role dropped the role")

    def test_peers_and_inbox_work_on_an_empty_store(self) -> None:
        self.assertEqual(0, run(self.root, "peers"))
        self.assertEqual(0, run(self.root, "inbox", "--as", "coordinator"))


if __name__ == "__main__":
    unittest.main()
