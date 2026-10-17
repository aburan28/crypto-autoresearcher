"""tools/sheriff.py: the sweep must see each defect it claims to see, must not
see the look-alikes, and the case check must refuse a verdict the evidence
does not carry.

A detector that has never been shown to fail on a planted defect is not a
detector, so the canary is tested twice: once passing, and once against a
deliberately broken scanner, where it has to fail.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import sheriff as sh  # noqa: E402


def test_canary_passes():
    result = sh.canary()
    assert result["passed"], result
    assert len(result["caught"]) == len(sh.CANARY_EXPECT)


def test_canary_fails_when_a_rule_is_removed(monkeypatch):
    monkeypatch.setattr(sh, "LEAN_RULES", tuple(r for r in sh.LEAN_RULES if r[0] != "lean.sorry"))
    result = sh.canary()
    assert not result["passed"]
    assert any(m[0] == "lean.sorry" for m in result["missed"])


def test_canary_fails_when_comments_are_not_stripped(monkeypatch):
    monkeypatch.setattr(sh, "strip_lean", lambda src: src)
    result = sh.canary()
    assert not result["passed"]
    assert any(f[0] == "lean.sorry" for f in result["false_positives"])


def test_canary_fails_when_tracing_counts_uncited_files(monkeypatch):
    monkeypatch.setattr(sh, "cited_paths", lambda text, home, repos, base="", absent=None: {(home, ".")})
    result = sh.canary()
    assert not result["passed"]


def test_strip_lean_keeps_offsets_and_hides_only_non_code():
    src = ("/- a /- nested sorry -/ b -/ theorem x : 1 = 1 := rfl -- sorry\n"
           'def s := "sorry \\" still string" def c : Char := \'"\' def n := ``Lean.ofReduceBool\n'
           "def f' := sorry\n")
    out = sh.strip_lean(src)
    assert len(out) == len(src)
    assert [i for i, ch in enumerate(src) if ch == "\n"] == [i for i, ch in enumerate(out) if ch == "\n"]
    assert "theorem x : 1 = 1 := rfl" in out
    assert out.count("sorry") == 1 and "def f' := sorry" in out
    assert "ofReduceBool" not in out and "def c : Char :=" in out


def test_axiom_rule_matches_declarations_not_mentions():
    rx = dict((r[0], r[1]) for r in sh.LEAN_RULES)["lean.axiom"]
    assert rx.search("axiom cheat : False")
    assert rx.search("@[simp] private axiom cheat : False")
    assert not rx.search("theorem t : collectAxioms_ok := rfl")
    assert not rx.search("#print axioms foo")


def test_rust_verifier_body_skips_declarations_and_handles_arrays(tmp_path):
    repo = tmp_path / "r"
    (repo / "src/zk").mkdir(parents=True)
    (repo / "src/zk/v.rs").write_text(
        "trait V { fn verify(&self) -> bool; }\n"
        "fn other() { let _ = unrelated; }\n"
        "fn verify_arr(x: [u8; 32]) -> [u8; 4] {\n    let _ = y;\n    [0; 4]\n}\n")
    rows = sh.scan_zk("r", repo, ["src/zk/v.rs"])
    discards = [(r["line"], r["excerpt"]) for r in rows if r["rule"] == "zk.discarded_value"]
    assert discards == [(4, "let _ = y;")]


def test_tex_numbers_skip_years_comments_and_dimensions():
    src = ("In 2024 we saw 3.217 and 12{,}345 and 1\\,234\\,567; % 9.876\n"
           "\\includegraphics[width=0.75\\textwidth]{f.pdf} \\cite{ref1234} 0.5 12.5pt 0.0058\n")
    values = [v for v, _ in sh.tex_numbers(src)]
    assert values == ["3.217", "12345", "1234567", "0.0058"]


def test_tex_numbers_split_lists_and_stop_at_the_bibliography():
    src = ("primes $\\{19,37,79,109\\}$, 621 primes, 1{,}234 and 5,678 rows\n"
           "\\begin{thebibliography}{9}\n\\bibitem{a} vol. 4321\n")
    values = [v for v, _ in sh.tex_numbers(src)]
    assert values == ["109", "621", "1234", "5678"]


def test_cited_paths_resolve_relative_to_the_paper(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/x.json").write_text("{}")
    (tmp_path / "papers/p").mkdir(parents=True)
    got = sh.cited_paths("see ../../data/x.json and data/x.json and research/", "r", {"r": tmp_path},
                         base="papers/p")
    assert got == {("r", "data/x.json")}


def test_tracing_accepts_rounding_and_truncation_only():
    exact = {"0.005762506", "120871"}
    rounded = sh.rounding_index(exact, [0.005762506, 120871.0], {4, 5})
    assert sh.is_traced("0.0058", exact, rounded)     # rounded
    assert sh.is_traced("0.00576", exact, rounded)    # truncated
    assert sh.is_traced("120871", exact, rounded)
    assert not sh.is_traced("0.0059", exact, rounded)
    assert not sh.is_traced("12087", exact, rounded)


def _case(tmp_path: Path, claims: list[dict], findings: list[dict] | None = None,
          canary_passed: bool = True) -> Path:
    case = tmp_path / "SHF-20261016-abcdef"
    case.mkdir()
    (case / "sweep.json").write_text(json.dumps({"canary": {"passed": canary_passed}}))
    (case / "findings.yaml").write_text(yaml.safe_dump({"sheriff_case": {
        "schema": sh.CASE_SCHEMA, "id": case.name,
        "readers": [{"role": "validator", "model": "m", "joint": "B3"}],
        "claims": claims, "findings": findings or []}}))
    return case


GOOD = {"id": "C1", "text": "t", "location": "tools/sheriff.py:1", "verdict": "upheld",
        "beats": {"B3": "pass", "B8": "n/a"}, "evidence": ["tools/sheriff.py"]}
BLOCKER = {"id": "F1", "beat": "B3", "severity": "blocker", "what": "w", "fix": "f"}


def errors(tmp_path, claims, findings=None, canary_passed=True):
    return sh.check_case(_case(tmp_path, claims, findings, canary_passed), {sh.HOME: REPO})


def test_check_case_accepts_a_supported_verdict(tmp_path):
    assert errors(tmp_path, [GOOD]) == []


@pytest.mark.parametrize("change, needle", [
    ({"beats": {"B3": "not_covered"}}, "never a pass"),
    ({"beats": {"B3": "fail"}}, "failed beat"),
    ({"evidence": ["does/not/exist.json"]}, "evidence"),
    ({"verdict": "upheld_scoped"}, "scoped_to"),
    ({"verdict": "overclaimed", "scoped_to": "x"}, "linked finding"),
    ({"verdict": "plausible"}, "not in"),
])
def test_check_case_refuses_unearned_verdicts(tmp_path, change, needle):
    errs = errors(tmp_path, [{**GOOD, **change}])
    assert any(needle in e for e in errs), errs


def test_check_case_refuses_upheld_with_a_linked_blocker(tmp_path):
    errs = errors(tmp_path, [{**GOOD, "findings": ["F1"]}], [BLOCKER])
    assert any("blocker" in e for e in errs)


def test_check_case_refuses_upheld_when_the_canary_failed(tmp_path):
    errs = errors(tmp_path, [GOOD], canary_passed=False)
    assert any("canary" in e for e in errs)


def _canary_repo(tmp_path: Path) -> Path:
    root = tmp_path / "canary"
    for rel, text in sh.CANARY_FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def test_sweep_writes_a_new_case_once(tmp_path):
    root = _canary_repo(tmp_path)
    out = tmp_path / "SHF-20261016-000000"
    args = argparse.Namespace(target="canary:.", deep=False, repo=[f"canary={root}"], no_siblings=True,
                              no_checkers=True, out=str(out))
    assert sh.sweep(args) == 0
    record = json.loads((out / "sweep.json").read_text())
    assert record["schema"] == sh.SCHEMA and record["canary"]["passed"]
    rules = {(f["repo"], f["rule"]) for f in record["findings"]}
    assert ("canary", "lean.sorry") in rules and ("canary", "zk.discarded_value") in rules
    assert (out / "sweep.md").read_text().startswith("# Sheriff sweep")
    assert (out / "sweep.svg").read_text().startswith("<svg")
    with pytest.raises(SystemExit):
        sh.sweep(args)


def test_unrun_checkers_are_recorded_not_covered(tmp_path):
    spec = {"id": "x", "repo": "crypto", "beat": "B5", "tier": "deep", "argv": ["true"]}
    row = sh.run_checker(spec, tmp_path, deep=False, scratch=tmp_path)
    assert row["status"] == "not_covered" and "deep" in row["reason"]
    row = sh.run_checker({**spec, "tier": "quick", "needs": ["target/release/ecbench"]}, tmp_path,
                         deep=False, scratch=tmp_path)
    assert row["status"] == "not_covered" and "ecbench" in row["reason"]
    row = sh.run_checker(spec, None, deep=True, scratch=tmp_path)
    assert row["status"] == "not_covered"


# ---------------------------------------------------------------------------
# Instrument defects of SHF-20261017-e4d7f6 I1: tree identity, session
# enumeration from HEAD, sparse checkouts marked partial, ~/.elan/bin.
# ---------------------------------------------------------------------------

GIT_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


def _git(root: Path, *args: str) -> None:
    import os
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                   env={**os.environ, **GIT_ENV})


def _repo(tmp_path: Path, name: str, files: dict[str, str]) -> Path:
    root = tmp_path / name
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "init")
    sh._outside.cache_clear()
    return root


def _sparse(root: Path, *patterns: str) -> None:
    _git(root, "sparse-checkout", "set", "--no-cone", *patterns)
    sh._outside.cache_clear()


def test_snapshot_identifies_the_tree_not_just_its_cleanliness(tmp_path):
    a = _repo(tmp_path, "a", {"x.txt": "one\n"})
    b = _repo(tmp_path, "b", {"x.txt": "two\n"})
    sa, sb = sh.snapshot("a", a), sh.snapshot("b", b)
    assert "tree_digest" not in sa and sa["dirty_paths"] == sb["dirty_paths"] == 0
    assert sa["head_tree"] and sa["head_tree"] != sb["head_tree"]
    assert sa["worktree_digest"] != sb["worktree_digest"]
    (a / "x.txt").write_text("changed\n")
    dirty = sh.snapshot("a", a)
    assert dirty["head_tree"] == sa["head_tree"] and dirty["worktree_digest"] != sa["worktree_digest"]
    assert sh.tree_identity(dirty) != sh.tree_identity(sa)
    legacy = {"head": "h", "tree_digest": "d"}
    assert sh.tree_identity(legacy) == ("h", None, "d")


FAKE_ECBENCH = "#!/bin/sh\n[ -f \"$3/BAD\" ] && exit 1\nexit 0\n"
SESSION = '{"schema": "ecbench.session/v1"}'


def _ecbench_repo(tmp_path: Path, bad: bool = False) -> Path:
    files = {"research/a/sessions/s1/session.json": SESSION,
             "research/a/sessions/s1/records.jsonl": "{}\n",
             "research/deep/x/y/sessions/s2/session.json": SESSION,
             "research/b/sessions/s3/session.json": SESSION,
             "research/b/sessions/s3/records.jsonl": "{}\n",
             "research/other/session.json": '{"schema": "something.else/v1"}',
             "README.md": "x\n"}
    if bad:
        files["research/a/sessions/s1/BAD"] = ""
    root = _repo(tmp_path, "crypto", files)
    exe = root / sh.ECBENCH
    exe.parent.mkdir(parents=True)
    exe.write_text(FAKE_ECBENCH)
    exe.chmod(0o755)
    return root


def _ecbench_spec() -> dict:
    return next(c for c in sh.CHECKERS if c["id"] == "ecbench-sessions-integrity")


def test_ecbench_sessions_are_enumerated_by_schema_from_head(tmp_path):
    root = _ecbench_repo(tmp_path)
    sessions, _ = sh.committed_ecbench_sessions(root)
    assert sessions == ["research/a/sessions/s1", "research/b/sessions/s3", "research/deep/x/y/sessions/s2"]
    row = sh.run_checker(_ecbench_spec(), root, deep=True, scratch=tmp_path)
    assert row["status"] == "pass", row
    assert row["sessions"] == {"total": 3, "materialised": 3, "passed": 3, "failed": 0, "timed_out": 0,
                               "not_materialised": 0}


def test_ecbench_sessions_on_a_sparse_checkout_are_partial_never_pass(tmp_path):
    root = _ecbench_repo(tmp_path)
    _sparse(root, "/*", "!/research/b/")
    assert not (root / "research/b/sessions/s3/session.json").exists()
    row = sh.run_checker(_ecbench_spec(), root, deep=True, scratch=tmp_path)
    assert row["status"] == "partial", row
    assert row["sessions"]["total"] == 3 and row["sessions"]["passed"] == 2
    assert row["sessions"]["not_materialised"] == 1
    assert row["not_materialised_sessions"] == ["research/b/sessions/s3"]
    assert row["coverage"] == "partial" and row["outside_sparse"]["files"] == 2


def test_ecbench_sessions_fail_is_reported(tmp_path):
    root = _ecbench_repo(tmp_path, bad=True)
    row = sh.run_checker(_ecbench_spec(), root, deep=True, scratch=tmp_path)
    assert row["status"] == "fail" and row["failed_sessions"] == ["research/a/sessions/s1"]


def test_checker_passing_on_a_sparse_checkout_is_partial(tmp_path):
    root = _repo(tmp_path, "r", {"a/x.txt": "1\n", "b/y.txt": "2\n"})
    spec = {"id": "x", "repo": "r", "beat": "B7", "tier": "quick", "argv": ["true"]}
    assert sh.run_checker(spec, root, deep=False, scratch=tmp_path)["status"] == "pass"
    _sparse(root, "/*", "!/b/")
    row = sh.run_checker(spec, root, deep=False, scratch=tmp_path)
    assert row["status"] == "partial" and row["coverage"] == "partial"
    assert row["outside_sparse"] == {"files": 1, "roots": {"b": 1}}


def test_sparse_sweep_reports_unscanned_paths_and_cited_artifacts_as_not_covered(tmp_path):
    root = _repo(tmp_path, "s", {
        "kept/Ok.lean": "theorem t : 1 = 1 := rfl\n",
        "gone/deep/Hole.lean": "def h : Nat := sorry\n",
        "papers/p/main.tex": "A ratio of 3.217, from \\texttt{data/out/r.json}.\n",
        "data/out/r.json": '{"ratio": 3.217}\n'})
    _sparse(root, "/*", "!/gone/", "!/data/")
    out = tmp_path / "SHF-20261017-111111"
    args = argparse.Namespace(target="s:.", deep=False, repo=[f"s={root}"], no_siblings=True,
                              no_checkers=True, out=str(out))
    assert sh.sweep(args) == 0
    rec = json.loads((out / "sweep.json").read_text())
    assert rec["repos"]["s"]["sparse"]["sparse"] and rec["repos"]["s"]["sparse"]["outside_files"] == 2
    rows = {(f["rule"], f["path"]): f for f in rec["findings"]}
    gap = rows[("sheriff.outside_sparse", "gone/deep")]
    assert gap["kind"] == "not_covered" and ".lean 1" in gap["message"]
    assert rows[("sheriff.outside_sparse", "data/out")]["kind"] == "not_covered"
    partial = rows[("paper.trace_partial", "papers/p")]
    assert partial["kind"] == "not_covered" and "data/out/r.json" in partial["message"]
    assert not any(f["rule"] in ("paper.untraced_number", "paper.no_cited_artifacts") for f in rec["findings"])
    assert rec["summary"]["s"]["papers"][0]["cited_outside_sparse"] == ["s:data/out/r.json"]


def test_toolchain_is_found_under_elan_when_not_on_path(tmp_path, monkeypatch):
    home = tmp_path / "home"
    lake = home / ".elan" / "bin" / "lake"
    lake.parent.mkdir(parents=True)
    lake.write_text("#!/bin/sh\necho lake-ok\n")
    lake.chmod(0o755)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("ELAN_HOME", raising=False)
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    assert sh.find_bin("lake") == str(lake)
    spec = {"id": "f", "repo": "r", "beat": "B3", "tier": "quick", "needs_bin": ["lake"],
            "argv": ["bash", "-c", "lake"]}
    work = tmp_path / "w"
    work.mkdir()
    row = sh.run_checker(spec, work, deep=False, scratch=tmp_path)
    assert row["status"] == "pass" and "lake-ok" in row["tail"], row
    assert row["toolchain"] == {"lake": str(lake)}
    lake.unlink()
    row = sh.run_checker(spec, work, deep=False, scratch=tmp_path)
    assert row["status"] == "not_covered" and ".elan" in row["reason"]
