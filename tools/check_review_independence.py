#!/usr/bin/env python3
"""Check that a review round rests on the independence it claims.

WHY THIS EXISTS. Independence is a property of how a review was SET UP, and it
is invisible in the output: three concurring reports look identical whether the
reviewers worked blind on separate joints or all read each other and converged
on the most legible step. The difference is decisive -- the first is coverage,
the second is correlated taste wearing the shape of corroboration -- and no
amount of reading the reports recovers which one happened.

So the setup is declared in advance (`review_plan` on the handoff opening the
round) and each reviewer declares what it actually read (`review_attestation`
in its report). This tool checks the two against each other. It cannot verify
that an attestation is truthful; it verifies that the round is internally
consistent and that no declared rule was declared and then broken -- which is
the part that goes wrong silently.

A PLAN IS THE PLAN PLUS ITS ADDENDA, and this tool composes them before
checking. A round's setup is declared before it runs, and the plan file is
immutable once committed -- so the only honest way to add a joint or move one
between reviewers is a companion file that `extends` the plan (an addendum), and
the base plan can never name the addenda that will later extend it. A checker
that reads only `--plan` therefore holds every reviewer to a pre-addendum
assignment. That is not a cosmetic gap: on 2026-09-15 it reported that
`TASK-20260913-6c5729` failed to claim a joint an addendum had reassigned away
from it, and the only way to turn the check green was for the reviewer to claim
an ownership it did not have and invent a verdict on a joint it could not
evaluate -- precisely the fabrication this tool exists to catch. So addenda are
discovered beside the plan, ordered by `written_at`, and applied; what was
applied is printed, because a composed check that looks identical to a bare one
is its own trap. `--no-addenda` restores the old behaviour for auditing a round
against its original plan.

WHAT IT CHECKS.
  * every joint in the plan has exactly one owner, and that owner attested;
  * no reviewer read a sibling report unless a legacy deliberate lift or an
    exact per-task prior-blind-artifact scoped lift authorizes that read;
  * a claim-changing round declares a proves-too-much control with objects;
  * a blind re-deriver's declared `sources_read` does not intersect the plan's
    `blind_from` -- the one independence property here that is fully mechanical;
  * reviewers report verdicts on the joints they own;
  * the reachable COMMIT-MESSAGE history of the tree a blind agent was given
    states none of the batch's protected literals (--blind-history).

Phased addenda bind a separate blind task to its unchanged full-joint owner.
The checker enforces those declarations and exact source scopes. It cannot
authenticate the actual Reviewer identity, immutable blind snapshot, four-run
archive gate, or deliberate-unblind timing; those remain external handoff and
archive obligations. A preparatory blind report alone cannot satisfy the full
round's unchanged joints or substitute for their missing attestations.
An explicit lost-session ``blind_phase_replacement`` retains the old joint,
attestation, phase and scoped grant as history. Only the new seven own files
become the full owner's active grant; every retained blind owner is still
checked against protected sources. This authenticates neither session identity,
archive contents/timing nor scientific verdicts: all are external obligations.

WHY THE HISTORY CHECK EXISTS, AND WHAT IT COSTS. `blind_from` is a list of
FILES, and the checks above can only see declared FILE reads. On 2026-09-05 a
blind re-transcription was nearly contaminated by something that is not a file:
a commit message. Reverting the commit restored the files and could not retract
the message, so `git log --oneline` -- a routine orientation command, in nobody's
blind list -- displayed the protected verdict twice on the branch the blind agent
was to run in (CORR-20260905-547849). Nothing downstream could have detected it
either: a re-derivation that agrees because it was told the answer is
indistinguishable from one that agrees because the answer is right.

This check closes that hole and only that hole.

THE DECLARATION IS BY HASH, AND IT HAS TO BE. A batch running a blind phase
declares that no control-plane file restates the protected values -- so the list
of protected values cannot itself be a plaintext list in the batch file the blind
agent must read to learn its assignment. `blind_phase_hygiene.protected_sha256`
therefore holds sha256 of each protected literal; this tool tokenizes each commit
message and hashes each token, so it can recognise a value it was never told.
Stated plainly: that is obfuscation against a reader, NOT secrecy against a
determined search -- the space of plausible figures is small and brute-forceable.
It keeps the value out of the blind agent's eyes, which is all it claims.

A batch that declares nothing is reported UNCHECKABLE, never passed: silence here
would read as a guarantee. The check cannot see paraphrase, a value written to
different precision, or a verdict described in words it was not given. It
strengthens a declaration; it does not replace giving a blind agent a clean tree.

    python3 tools/check_review_independence.py --plan <handoff.yaml> \
        --reports <dir-or-file> [<dir-or-file> ...]
    python3 tools/check_review_independence.py --batch <batch-dir>
    python3 tools/check_review_independence.py --blind-history origin/main \
        --protected-from <batch.yaml> [--max-commits 500]
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import os
import re
import subprocess
import sys
from functools import lru_cache

import yaml

try:
    from review_phase_seals import InvalidPhase, check_sealed_phases, load_phase_yaml
except ImportError:
    from tools.review_phase_seals import InvalidPhase, check_sealed_phases, load_phase_yaml

try:  # libyaml, with the pure loader's errors (orchestration/fast_yaml.py)
    import fast_yaml
except ImportError:  # imported as tools.<name>, the repository root importable
    from orchestration import fast_yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VERDICTS = {"holds", "breaks", "inconclusive"}
_TASK_ID = re.compile(r"TASK-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\Z")
_NATIVE_TASK_ID = re.compile(r"TASK-\d{8}-(?:[0-9a-f]{6}|\d{3})\Z")
_OWN_SEVEN = {"independent_enumerator.py", "predicted-counts.json", "report.md",
              "diagram.svg", "report.pdf", "visual-inspection.json", "read-attestation.yaml"}


def _replacement_locations(value, prefix=(), ancestors=frozenset()):
    """Find explicit replacement directives, including otherwise ignored nesting."""
    found = []
    if id(value) in ancestors:
        return found
    ancestors = ancestors | {id(value)}
    if isinstance(value, dict):
        for key, child in value.items():
            location = prefix+(key,)
            if key == "blind_phase_replacement":
                found.append(location)
            found.extend(_replacement_locations(child, location, ancestors))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_replacement_locations(child, prefix+(index,), ancestors))
    return found


def _replacement_allowlist(raw, task):
    paths = _allowlist_paths(raw, task)
    if (len(paths) != 7 or {path.rsplit("/", 1)[-1] for path in paths} != _OWN_SEVEN
            or len({path.rsplit("/", 1)[0] for path in paths}) != 1
            or any(path.split("/")[-2] != task for path in paths)):
        raise ValueError("blind-phase replacement requires exactly the seven own-artifact files in its new TASK directory")
    return paths


def _valid_task(value, *, native=False):
    """Legacy task labels remain readable; new phase directives use real IDs."""
    pattern = _NATIVE_TASK_ID if native else _TASK_ID
    return isinstance(value, str) and bool(pattern.fullmatch(value))


class InvalidGitSource(ValueError):
    """A Git source must not silently become an unrelated filesystem path."""


@lru_cache(maxsize=128)
def _git_source_commit(repo, abbreviation):
    """Resolve only hexadecimal object identities, never branch/tag names."""
    def git(*args):
        try:
            result = subprocess.run(
                ["git", "-C", repo, *args], capture_output=True, text=True,
                timeout=10, env={**os.environ, "GIT_NO_REPLACE_OBJECTS": "1"})
        except (OSError, subprocess.TimeoutExpired) as error:
            raise InvalidGitSource(f"cannot resolve Git commit {abbreviation!r}: {error}") from error
        if result.returncode:
            raise InvalidGitSource(f"cannot resolve Git commit {abbreviation!r}")
        return result.stdout.strip()

    objects = git("rev-parse", "--disambiguate="+abbreviation).splitlines()
    if (len(objects) != 1 or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", objects[0])
            or not objects[0].startswith(abbreviation)):
        raise InvalidGitSource(f"unknown or ambiguous Git commit {abbreviation!r}")
    if git("cat-file", "-t", objects[0]) != "commit":
        raise InvalidGitSource(f"Git identity {abbreviation!r} is not a commit")
    return objects[0]


def _read_path(value):
    """Compare path scopes across Git revisions; do not authenticate blob bytes.

    A Git citation is an existing commit (or unambiguous hexadecimal prefix)
    plus an exact repository-relative path. Version custody is checked by the
    archive verifier, separately. All revisions obey the same read restrictions.
    """
    raw = str(value)
    source = raw.strip()
    if source.lower().startswith("git:"):
        match = re.fullmatch(r"git:([0-9a-f]{7,40}|[0-9a-f]{64}):(.+)", source)
        if not match or source != raw:
            raise InvalidGitSource(f"malformed Git citation {raw!r}")
        revision, path = match.groups()
        if (os.path.isabs(path) or any(c in path for c in "\\*?[]:")
                or any(ord(c) < 32 or ord(c) == 127 for c in path)
                or any(part in ("", ".", "..") for part in path.split("/"))):
            raise InvalidGitSource(f"invalid Git source path {path!r}")
        _git_source_commit(REPO, revision)
        canonical = os.path.realpath(os.path.join(REPO, path))
        if not _within(canonical, os.path.realpath(REPO)):
            raise InvalidGitSource(f"Git source path escapes repository: {path!r}")
        return canonical
    return os.path.realpath(os.path.join(REPO, source.replace("\\", "/")))


def _within(path, directory):
    return path == directory or path.startswith(directory.rstrip(os.sep)+os.sep)


def _path_task_parts(canonical):
    root = os.path.realpath(REPO)
    local = os.path.relpath(canonical, root) if _within(canonical, root) else canonical
    return [part for part in local.split(os.sep) if _valid_task(part)]


def _allowlist_paths(raw, blind_task):
    """Exact repo-relative files in this Reviewer's declared prior blind task."""
    if not isinstance(raw, list) or not raw:
        raise ValueError("lift_read_allowlist must be a nonempty list of exact prior blind-artifact paths")
    result = []
    for path in raw:
        if (not isinstance(path, str) or not path or path != path.strip()
                or os.path.isabs(path) or any(c in path for c in "\\*?[]:")
                or any(part in ("", ".", "..") for part in path.split("/"))
                or path.split("/")[-1] == blind_task):
            raise ValueError(f"invalid exact blind-artifact allowlist path: {path!r}")
        task_parts = [part for part in path.split("/") if _valid_task(part)]
        if task_parts != [blind_task]:
            raise ValueError(f"allowlist path {path!r} must belong only to prior blind task {blind_task}")
        canonical = _read_path(path)
        if not _within(canonical, os.path.realpath(REPO)):
            raise ValueError(f"allowlist path escapes repository: {path!r}")
        resolved_tasks = _path_task_parts(canonical)
        if resolved_tasks != [blind_task] or os.path.isdir(canonical):
            raise ValueError(f"allowlist path is a directory or resolves outside prior blind task {blind_task}: {path!r}")
        if canonical in {_read_path(previous) for previous in result}:
            raise ValueError(f"duplicate blind-artifact allowlist path: {path!r}")
        result.append(path)
    return result


def _named_joints(plan, owner):
    return [_joint_name(entry) for entry in plan.get("joints", [])
            if isinstance(entry, dict) and _joint_owner(entry) == owner]


def _phase_problems(plan):
    """Validate composed phase bindings even after a later owner reassignment."""
    problems = []
    phases = plan.get("_blind_phase_assignments", {})
    if not isinstance(phases, dict):
        return ["malformed blind-phase assignment audit"]
    blind = plan.get("blind_rederivation")
    blind = blind if isinstance(blind, dict) else {}
    blindness = plan.get("blindness")
    blindness = blindness if isinstance(blindness, dict) else {}
    for full_owner, phase in phases.items():
        if (not _valid_task(full_owner, native=True) or not isinstance(phase, dict)
                or not _valid_task(phase.get("blind_task"), native=True)
                or not isinstance(phase.get("full_joints"), list) or not phase["full_joints"]):
            problems.append("invalid blind-phase owner/full-joint audit")
            continue
        if blind.get("required") is not True or blind.get("assigned_to") != phase["blind_task"]:
            problems.append(f"blind-phase owner for {full_owner} no longer matches required blind_rederivation")
        if not _named_joints(plan, phase["blind_task"]):
            problems.append(f"blind-phase owner {phase['blind_task']} owns no explicitly declared joint")
        for name in phase["full_joints"]:
            entries = [entry for entry in plan.get("joints", []) if isinstance(entry, dict)
                       and _joint_label(_joint_name(entry)).casefold() == _joint_label(name).casefold()]
            if len(entries) != 1 or _joint_owner(entries[0]) != full_owner:
                problems.append(f"full joint '{_joint_label(name)}' must remain assigned to {full_owner} after blind-phase split")
    history = plan.get("_blind_phase_history", [])
    if not isinstance(history, list):
        return problems+["malformed blind-phase replacement history"]
    seen = set()
    for record in history:
        if (not isinstance(record, dict) or not _valid_task(record.get("full_task"), native=True)
                or not isinstance(record.get("phase_assignment"), dict)
                or not isinstance(record.get("scoped_lift"), dict)
                or not isinstance(record.get("blind_rederivation"), dict)
                or not isinstance(record.get("retained_joints"), list)):
            problems.append("malformed retained blind-phase history")
            continue
        full = record["full_task"]
        old = record["phase_assignment"].get("blind_task")
        if not _valid_task(old, native=True) or old in seen:
            problems.append("invalid or duplicate retained blind-phase owner")
            continue
        seen.add(old)
        current_phase = phases.get(full)
        if not isinstance(current_phase, dict) or not _named_joints(plan, old):
            problems.append(f"retained blind owner {old} and unchanged full owner {full} must remain declared")
        for joint in record["retained_joints"]:
            if joint not in plan.get("joints", []):
                problems.append(f"retained joint must remain unchanged after blind-phase replacement for {old}")
        prior = record["blind_rederivation"]
        prior_sources = prior.get("blind_from")
        if (not isinstance(prior_sources, list) or not prior_sources
                or any(not isinstance(source, str) or not source.strip() for source in prior_sources)):
            problems.append("malformed retained blind_from protections")
            continue
        for field in ("required", "quantity", "parameters"):
            if blind.get(field) != prior.get(field):
                problems.append(f"replacement must preserve blind_rederivation.{field}")
        if any(source not in (blind.get("blind_from") or []) for source in prior_sources):
            problems.append("replacement must preserve every retained blind_from source")
        if blindness.get("mutual") is not True:
            problems.append("blind-phase replacement must preserve mutual=true")
        # A later legacy lift must not broaden the replacement's exact grant.
        lifted = blindness.get("lifted_for") or []
        if any(task in lifted for task in (full, old, current_phase.get("blind_task") if isinstance(current_phase, dict) else None)):
            problems.append("blind-phase replacement cannot use a broad blindness lift")
    return problems


def _scoped_lift(task, scope, plan):
    """Validate one explicit lift; return its exact canonical allowed files."""
    if (not _valid_task(task, native=True) or not isinstance(scope, dict)
            or not isinstance(scope.get("rationale"), str) or not scope["rationale"].strip()):
        raise ValueError("scoped blindness lift requires a valid named TASK owner and nonempty rationale")
    if not _named_joints(plan, task):
        raise ValueError(f"scoped lift owner {task} owns no declared full joint")
    blind_owner = scope.get("blind_task")
    phases = plan.get("_blind_phase_assignments") or {}
    phase = phases.get(task) if isinstance(phases, dict) else None
    if not isinstance(phase, dict) or phase.get("blind_task") != blind_owner:
        raise ValueError(f"scoped lift for {task} has no declared same-Reviewer blind-phase assignment")
    if blind_owner == task or not _valid_task(blind_owner, native=True):
        raise ValueError("scoped lift must name the separate declared prior blind task")
    blindness = plan.get("blindness")
    if not isinstance(blindness, dict) or blindness.get("mutual") is not True:
        raise ValueError("scoped blindness lift must preserve mutual=true")
    validator = _replacement_allowlist if phase.get("replacement") is True else _allowlist_paths
    return {_read_path(path) for path in validator(scope.get("read_allowlist"), blind_owner)}


def _joint_label(name: str) -> str:
    """The short label a reviewer will actually write, e.g. 'J1'.

    Plan joints are named with a label and a full statement of the joint
    ('J1 -- SEMAEV'S MEMORY MODEL. That the peak memory ...'), because the
    statement is what makes the assignment reviewable. A reviewer then refers
    to it as `J1`, or paraphrases the statement. Requiring the exact string
    back made this tool unrunnable on every round it was written for.
    """
    head = re.split(r"\s+--\s+|\s+—\s+|:\s+|\.\s+", str(name).strip(), 1)[0]
    return head.strip().rstrip(".").strip()


def _joint_name(entry: dict) -> str:
    """Use an explicit joint ID for matching, retaining legacy joint-only plans.

    A plan may carry both an ID such as P3 and a full-sentence ``joint``
    statement. The ID is the reviewer's attested label; the statement remains
    in the plan for the attack and breaking-artifact obligations. An explicit
    malformed ID must not silently fall back to the statement: ``check``
    reports it as a plan defect.
    """
    if "id" in entry:
        identifier = entry["id"]
        return identifier.strip() if isinstance(identifier, str) else ""
    return str(entry.get("joint") or "")


def _owner_key(entry: dict) -> str:
    return "owner" if "owner" in entry and "assigned_to" not in entry else "assigned_to"


def _joint_owner(entry: dict) -> str:
    return str(entry.get(_owner_key(entry)) or "").strip()


def _claims_joint(owned: list, name: str) -> bool:
    """Does this attestation's `joints_owned` name the plan's joint?"""
    label = _joint_label(name).casefold()
    full = str(name).strip().casefold()
    for entry in owned:
        entry = str(entry).strip().casefold()
        if entry == full or _joint_label(entry).casefold() == label:
            return True
    return False


def _verdict_for(attestation: dict, name: str,
                 declared_joint_count: int = 1) -> tuple[str | None, str | None]:
    """This reviewer's verdict on one joint, and why it could not be read.

    A reviewer that owns several joints reports one verdict PER JOINT -- the
    contract is explicit that a whole-claim verdict from a blinded reviewer is
    an opinion formed from a fraction of the evidence. So the compliant shape
    is a mapping keyed by joint label, and `verdict: holds` is only meaningful
    for a single-joint reviewer. This accepts both, under either `verdict` or
    `verdicts`, and returns a readable problem for anything else rather than
    raising on it.
    """
    raw = attestation.get("verdict")
    if raw is None:
        raw = attestation.get("verdicts")
    if isinstance(raw, str):
        owned = attestation.get("joints_owned")
        owned_count = (len({_joint_label(str(item)).casefold() for item in owned})
                       if isinstance(owned, list) else 0)
        if max(declared_joint_count, owned_count) != 1:
            return None, ("a reviewer with multiple joints needs a per-joint "
                          "verdict mapping; one scalar verdict cannot cover them")
        value = raw.strip()
        if value in VERDICTS:
            return value, None
        return None, (f"verdict '{value}' must be "
                      f"{'|'.join(sorted(VERDICTS))}")
    if isinstance(raw, dict):
        label = _joint_label(name).casefold()
        for key, value in raw.items():
            key = str(key).strip().casefold()
            if key == label or key == str(name).strip().casefold():
                value = str(value).strip()
                if value in VERDICTS:
                    return value, None
                return None, (f"verdict on '{_joint_label(name)}' is "
                              f"'{value}', which must be "
                              f"{'|'.join(sorted(VERDICTS))}")
        return None, (f"per-joint verdict mapping carries no entry for "
                      f"'{_joint_label(name)}' (has "
                      f"{', '.join(sorted(str(k) for k in raw))})")
    if raw is None:
        return None, ("neither verdict nor verdicts is set; every owned joint "
                      "carries an explicit verdict")
    return None, (f"verdict must be a {'|'.join(sorted(VERDICTS))} string or a "
                  f"mapping from joint label to one, not "
                  f"{type(raw).__name__}")


def _load(path: str, *, content: str | None = None):
    try:
        if content is None:
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
        # The normal legacy loader keeps the last duplicate YAML key.
        # Explicit phase/replacement authority must never silently shadow one,
        # including a duplicate wrapper containing either directive.
        def inspect(node, replacement=False, ancestors=frozenset()):
            if id(node) in ancestors:
                return set()
            ancestors = ancestors | {id(node)}
            contains = set()
            if isinstance(node, yaml.MappingNode):
                seen = {}
                for key, value in node.value:
                    name = key.value if isinstance(key, yaml.ScalarNode) else None
                    directive = name in {"blind_phase_replacement", "phased_release"}
                    child_contains = inspect(value, replacement or directive, ancestors)
                    special = directive or bool(child_contains)
                    if name in seen and (replacement or special or seen[name]):
                        raise ValueError(f"{path}: duplicate blind-phase directive/field {name}")
                    seen[name] = special
                    contains.update(child_contains)
                    if directive:
                        contains.add(name)
            elif isinstance(node, yaml.SequenceNode):
                for value in node.value:
                    contains.update(inspect(value, replacement, ancestors))
            return contains
        directives = inspect(yaml.compose(content, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader)))
        if "phased_release" in directives:
            return load_phase_yaml(content)
        return fast_yaml.safe_load(content)
    except InvalidPhase as exc:
        # A malformed phased report must not disappear from directory scans.
        raise ValueError(f"{path}: {exc}") from exc
    except (OSError, yaml.YAMLError) as exc:
        return {"__error__": str(exc).splitlines()[0]}


#: A round's plan is spelled `review_plan` by the template and `read_plan` by
#: zero-compute rounds whose joints are readings of external sources. The two are
#: the same object and this tool checks the same things of both; the alias exists
#: because a committed plan is immutable, so a round that chose the other spelling
#: cannot be brought into line by editing it. Refusing it reported a naming
#: difference as "no review_plan block", which is the least informative failure
#: available and which no reader of that message would diagnose.
PLAN_KEYS = ("review_plan", "read_plan")
ADDENDUM_KEYS = ("review_plan_addendum", "read_plan_addendum")


def _plan_of(doc) -> dict | None:
    """A plan may be given as a handoff record or as a bare plan."""
    if not isinstance(doc, dict):
        return None
    for key in PLAN_KEYS:
        if isinstance(doc.get(key), dict):
            return doc[key]
    handoff = doc.get("handoff")
    if isinstance(handoff, dict):
        for key in PLAN_KEYS:
            if isinstance(handoff.get(key), dict):
                return handoff[key]
    return None


def _addendum_of(doc) -> dict | None:
    if not isinstance(doc, dict):
        return None
    locations = _replacement_locations(doc)
    if locations and locations != [("review_plan_addendum", "blind_phase_replacement")]:
        raise ValueError("blind_phase_replacement belongs only at review_plan_addendum top level")
    for key in ADDENDUM_KEYS:
        if isinstance(doc.get(key), dict):
            return doc[key]
    return None


def _same_file(declared: str, plan_path: str) -> bool:
    """Does an addendum's `extends` value point at this plan?

    Compared by resolved path, so a repo-relative declaration and a path given
    on the command line agree. Falls back to basename: an addendum sitting in
    the round's own directory that names the plan by file name is unambiguous
    there, and refusing it would push a Coordinator toward editing the plan.
    """
    declared = str(declared or "").strip()
    if not declared:
        return False
    plan_abs = os.path.abspath(plan_path)
    for candidate in (declared, os.path.join(REPO, declared),
                      os.path.join(os.path.dirname(plan_abs), declared)):
        if os.path.abspath(candidate) == plan_abs:
            return True
    return os.path.basename(declared) == os.path.basename(plan_abs)


def find_addenda(plan_path: str) -> list[tuple[str, dict]]:
    """Addenda beside the plan that extend it, oldest declaration first.

    Ordered by `written_at` so a later addendum's reassignment wins over an
    earlier one's, with the file name as a stable tiebreak. An addendum that
    declares no `written_at` sorts first: it cannot claim to supersede anything.
    """
    directory = os.path.dirname(os.path.abspath(plan_path)) or "."
    found = []
    for path in sorted(glob.glob(os.path.join(directory, "*.yaml"))
                       + glob.glob(os.path.join(directory, "*.yml"))):
        if os.path.abspath(path) == os.path.abspath(plan_path):
            continue
        addendum = _addendum_of(_load(path))
        if addendum is None:
            continue
        targets = [addendum.get("extends")] + list(
            addendum.get("also_extends") or []
            if isinstance(addendum.get("also_extends"), list)
            else [addendum.get("also_extends")])
        if any(_same_file(target, plan_path) for target in targets):
            found.append((path, addendum))
    found.sort(key=lambda item: (str(item[1].get("written_at") or ""), item[0]))
    return found


def compose_plan(plan: dict, addenda: list[tuple[str, dict]]) -> tuple[dict, list[str]]:
    """The plan as the round actually stands, plus a line per change applied.

    An addendum may add joints, reassign the
    owner of a joint, declare further proves-too-much objects, and WIDEN
    `blind_rederivation.blind_from`. It may not remove a joint or weaken a
    control -- an addendum that tried would be a silent narrowing of a declared
    review, so unknown keys are simply not acted on and the plan they extend
    keeps its own values. Explicit attempts to drop protections leave those
    originals in force and add an enforced composition-audit failure.

    A phase split may separately reassign required blind rederivation to a
    valid TASK owning a declared joint, while preserving the former owner's
    full joints and all original blind requirements. Explicit scoped lifts
    authorize only exact files of that same Reviewer's prior blind task;
    they never become new blanket ``blindness.lifted_for`` entries. These are
    declared phase/source bindings, not proof of archive or unblind timing.

    `blind_from_additions` was the fourth for a while only on paper. Two addenda
    on BATCH-cbb416 declared it -- ADD2 over the collision audit's disclosed
    fall-degree integers, ADD3 over a Coordinator prior stating the very value
    being re-derived -- and neither reached the leak check below, because an
    unknown key is left alone and `blind_from` was therefore always the parent
    plan's. That is the worst failure mode available to this file: a protection
    that reads as in force, is cited in a receipt as in force, and is enforced
    nowhere. Honouring it cannot let an addendum weaken anything, because the
    only permitted direction is wider -- a longer `blind_from` can add leak
    findings and can never remove one.

    Accepted at two spellings, `what_changes.blind_from_additions` and a
    top-level `blind_from_additions`, because both are already committed in the
    corpus and neither is more canonical than the other.
    """
    import copy

    if _replacement_locations(plan):
        raise ValueError("blind_phase_replacement belongs only at review_plan_addendum top level")
    composed = copy.deepcopy(plan)
    notes: list[str] = []
    joints = composed.get("joints")
    composed["joints"] = list(joints) if isinstance(joints, list) else []

    for path, addendum in addenda:
        label = _rel(path)
        if not isinstance(addendum, dict):
            raise ValueError(f"{label}: addendum must be a mapping")
        locations = _replacement_locations(addendum)
        if locations and locations != [("blind_phase_replacement",)]:
            raise ValueError(f"{label}: blind_phase_replacement belongs only at addendum top level")
        if any(str(key).startswith("blind_phase_replac") and key != "blind_phase_replacement" for key in addendum):
            raise ValueError(f"{label}: unknown blind-phase replacement directive")
        changes = addendum.get("what_changes")
        if changes is not None and not isinstance(changes, dict):
            raise ValueError(f"{label}: what_changes must be a mapping")
        changes = changes or {}
        phase_replacement = addendum.get("blind_phase_replacement")
        previous_phase = previous_scope = None
        retained_joints = copy.deepcopy(composed["joints"])
        if "blind_phase_replacement" in addendum:
            required = {"full_task", "replaces_blind_task", "replacement_blind_task", "reason",
                        "retained_blind_archive", "prior_artifacts_remain_required"}
            if not isinstance(phase_replacement, dict) or set(phase_replacement) != required:
                raise ValueError(f"{label}: malformed or unknown blind_phase_replacement fields")
            full, old, new = (phase_replacement[key] for key in
                              ("full_task", "replaces_blind_task", "replacement_blind_task"))
            if (any(not _valid_task(task, native=True) for task in (full, old, new))
                    or len({full, old, new}) != 3
                    or not isinstance(phase_replacement["reason"], str) or not phase_replacement["reason"].strip()
                    or phase_replacement["prior_artifacts_remain_required"] is not True):
                raise ValueError(f"{label}: replacement requires distinct native TASK IDs, a reason and retained prior artifacts")
            archive = phase_replacement["retained_blind_archive"]
            if (not isinstance(archive, dict) or set(archive) != {"task", "commit_sha", "verification"}
                    or archive.get("task") != old or not isinstance(archive.get("commit_sha"), str)
                    or not re.fullmatch(r"[0-9a-f]{40}", archive["commit_sha"])):
                raise ValueError(f"{label}: replacement requires an exact retained old blind archive binding")
            verification = archive.get("verification")
            if (not isinstance(verification, str) or not verification or verification != verification.strip()
                    or os.path.isabs(verification) or any(c in verification for c in "\\*?[]:")
                    or any(part in ("", ".", "..") for part in verification.split("/"))
                    or not _within(_read_path(verification), os.path.realpath(REPO))
                    or os.path.isdir(_read_path(verification))):
                raise ValueError(f"{label}: retained archive verification must be an exact repository file path")
            errors = _phase_problems(composed)
            if errors:
                raise ValueError(f"{label}: invalid prior blind-phase binding: "+"; ".join(errors))
            phases = composed.get("_blind_phase_assignments") or {}
            previous_phase = phases.get(full)
            current_blind = composed.get("blind_rederivation")
            if (not isinstance(previous_phase, dict) or previous_phase.get("blind_task") != old
                    or not _named_joints(composed, full)
                    or not isinstance(current_blind, dict) or current_blind.get("assigned_to") != old):
                raise ValueError(f"{label}: stale or unknown replacement must name an existing unchanged full/blind-phase binding")
            sources = current_blind.get("blind_from")
            if (not isinstance(current_blind.get("quantity"), str) or not current_blind["quantity"].strip()
                    or not isinstance(sources, list) or not sources
                    or any(not isinstance(source, str) or not source.strip() for source in sources)):
                raise ValueError(f"{label}: replacement requires intact quantity and blind_from declarations")
            if _named_joints(composed, new) or any(new == record["phase_assignment"]["blind_task"]
                                                for record in composed.get("_blind_phase_history", [])):
                raise ValueError(f"{label}: duplicate/replayed replacement task already owns or owned a blind joint")
            current_blindness = composed.get("blindness")
            prior_scopes = current_blindness.get("scoped_lifts") if isinstance(current_blindness, dict) else None
            previous_scope = prior_scopes.get(full) if isinstance(prior_scopes, dict) else None
            _scoped_lift(full, previous_scope, composed)
            if ("blind_rederivation_assigned_to" in changes or changes.get("owners")
                    or addendum.get("blindness_lifted_for_additions") != [full]):
                raise ValueError(f"{label}: replacement conflicts with split/owner changes or requires its exact named full-owner lift")
            _replacement_allowlist(addendum.get("lift_read_allowlist"), new)
        if "blind_rederivation_assigned_to" in addendum:
            raise ValueError(f"{label}: blind_rederivation_assigned_to belongs under what_changes")
        lift_keys = {"blindness_lifted_for_additions", "blindness_lift_rationale", "lift_read_allowlist"}
        if lift_keys.intersection(changes):
            raise ValueError(f"{label}: scoped lift directives must be at addendum top level")
        if lift_keys.intersection(addendum) and "blindness_lifted_for_additions" not in addendum:
            raise ValueError(f"{label}: scoped lift rationale/allowlist requires blindness_lifted_for_additions")
        # Retain immutable protections, and make any attempted removal visible
        # to check(), including legacy compose callers that inspect the result.
        refused = []
        if addendum.get("joints_removed") or changes.get("joints_dropped"):
            refused.append("attempted to remove required joints")
        blind_before = composed.get("blind_rederivation")
        blind_before = blind_before if isinstance(blind_before, dict) else {}
        replacement = addendum.get("blind_rederivation")
        if isinstance(replacement, dict):
            for key in ("required", "quantity", "parameters", "assigned_to", "phased_release"):
                if key in replacement and replacement[key] != blind_before.get(key):
                    refused.append(f"attempted to replace protected blind_rederivation.{key}")
            if "blind_from" in replacement and replacement["blind_from"] != (blind_before.get("blind_from") or []):
                refused.append("attempted blind_from narrowing/replacement; use blind_from_additions only")
        if "blind_from" in changes:
            refused.append("attempted blind_from narrowing/replacement; use blind_from_additions only")
        replacement = addendum.get("blindness")
        if isinstance(replacement, dict):
            if replacement.get("mutual") is False and (composed.get("blindness") or {}).get("mutual") is not False:
                refused.append("attempted to disable mutual blindness")
            if "lifted_for" in replacement and replacement["lifted_for"] != (composed.get("blindness") or {}).get("lifted_for", []):
                refused.append("attempted to replace original blindness lift entries")
        replacement = addendum.get("proves_too_much")
        if isinstance(replacement, dict) and "objects" in replacement:
            original = (composed.get("proves_too_much") or {}).get("objects") or []
            if not isinstance(replacement["objects"], list) or any(item not in replacement["objects"] for item in original):
                refused.append("attempted to remove proves-too-much objects")
        if refused:
            for problem in refused:
                audit = f"{label}: REFUSED {problem}; original declarations remain enforced"
                composed.setdefault("_composition_errors", []).append(audit)
                notes.append(audit)
            continue
        split = "blind_rederivation_assigned_to" in changes
        previous_blind_owner = blind_before.get("assigned_to")
        previous_full_joints = _named_joints(composed, previous_blind_owner)
        added = addendum.get("joints_added")
        if "joints_added" in addendum and not isinstance(added, list):
            raise ValueError(f"{label}: joints_added must be a list of explicit joint mappings")
        if isinstance(added, list):
            for entry in added:
                if (not isinstance(entry, dict) or not _joint_name(entry).strip()
                        or not _valid_task(entry.get(_owner_key(entry)))
                        or not isinstance(entry.get("attack_plan"), str) or not entry["attack_plan"].strip()):
                    raise ValueError(f"{label}: added joint requires a name, valid TASK owner and attack_plan")
                composed["joints"].append(copy.deepcopy(entry))
                notes.append(f"{label}: added joint '{_joint_label(_joint_name(entry))}'")
        owners = changes.get("owners")
        if "owners" in changes and not isinstance(owners, dict):
            raise ValueError(f"{label}: what_changes.owners must be a mapping")
        if isinstance(owners, dict):
            for joint_label, owner in owners.items():
                if not isinstance(joint_label, str) or not joint_label.strip() or not _valid_task(owner):
                    raise ValueError(f"{label}: invalid joint label or TASK owner in reassignment")
                wanted = _joint_label(str(joint_label)).casefold()
                matches = [entry for entry in composed["joints"] if isinstance(entry, dict)
                           and _joint_label(_joint_name(entry)).casefold() == wanted]
                if len(matches) != 1:
                    raise ValueError(f"{label}: reassignment names unknown or ambiguous joint '{joint_label}'")
                for entry in matches:
                    name = _joint_name(entry)
                    if _joint_owner(entry) != owner:
                        notes.append(
                            f"{label}: joint '{_joint_label(name)}' reassigned "
                            f"{_joint_owner(entry)} -> {owner}")
                    entry[_owner_key(entry)] = owner
        extra = addendum.get("proves_too_much_objects_added")
        if isinstance(extra, list) and extra:
            control = composed.get("proves_too_much")
            control = dict(control) if isinstance(control, dict) else {}
            control["objects"] = list(control.get("objects") or []) + list(extra)
            composed["proves_too_much"] = control
            notes.append(f"{label}: added {len(extra)} proves-too-much object(s)")

        widened = []
        for source in (changes, addendum):
            if "blind_from_additions" not in source:
                continue
            values = source["blind_from_additions"]
            if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{label}: blind_from_additions must be a list of nonempty source paths")
            widened.extend(value for value in values if value not in widened)
        if widened:
            rederivation = composed.get("blind_rederivation")
            rederivation = dict(rederivation) if isinstance(rederivation, dict) else {}
            existing = [str(p).strip() for p in (rederivation.get("blind_from") or [])]
            added = [str(p).strip() for p in widened
                     if str(p).strip() and str(p).strip() not in existing]
            if added:
                rederivation["blind_from"] = existing + added
                composed["blind_rederivation"] = rederivation
                notes.append(f"{label}: widened blind_from by {len(added)} path(s) "
                             f"-- {', '.join(added)}")
        if split:
            owner = changes["blind_rederivation_assigned_to"]
            if not _valid_task(owner, native=True):
                raise ValueError(f"{label}: blind_rederivation_assigned_to must be a valid TASK ID")
            if (blind_before.get("required") is not True or not _valid_task(previous_blind_owner, native=True)
                    or not str(blind_before.get("quantity") or "").strip()
                    or not isinstance(blind_before.get("blind_from"), list) or not blind_before["blind_from"]):
                raise ValueError(f"{label}: phase split requires the original required/owned/quantity/blind_from declarations")
            if owner == previous_blind_owner or not _named_joints(composed, owner):
                raise ValueError(f"{label}: separate blind owner {owner} must own an explicitly declared joint")
            if not previous_full_joints:
                raise ValueError(f"{label}: original blind owner has no declared full joint to preserve")
            phases = composed.setdefault("_blind_phase_assignments", {})
            if previous_blind_owner in phases:
                raise ValueError(f"{label}: repeated blind-phase split needs a separately declared phase contract")
            phases[previous_blind_owner] = {"blind_task": owner, "full_joints": previous_full_joints}
            composed["blind_rederivation"]["assigned_to"] = owner
            errors = _phase_problems(composed)
            if errors:
                raise ValueError(f"{label}: "+"; ".join(errors))
            notes.append(f"{label}: blind_rederivation.assigned_to reassigned {previous_blind_owner} -> {owner}; full-joint owner unchanged")
        if phase_replacement is not None:
            full, old, new = (phase_replacement[key] for key in
                              ("full_task", "replaces_blind_task", "replacement_blind_task"))
            if not _named_joints(composed, new):
                raise ValueError(f"{label}: replacement blind task must own a newly explicit joint")
            composed.setdefault("_blind_phase_history", []).append({
                "full_task": full, "phase_assignment": copy.deepcopy(previous_phase),
                "scoped_lift": copy.deepcopy(previous_scope),
                "retained_blind_archive": copy.deepcopy(phase_replacement["retained_blind_archive"]),
                "reason": phase_replacement["reason"], "prior_artifacts_remain_required": True,
                "retained_joints": retained_joints,
                "blind_rederivation": copy.deepcopy(blind_before)})
            composed["_blind_phase_assignments"][full] = dict(copy.deepcopy(previous_phase), blind_task=new, replacement=True)
            composed["blind_rederivation"]["assigned_to"] = new
            # Every old exact artifact is now forbidden to the fresh Reviewer,
            # even where a report path contains no recognizable TASK directory.
            protected = composed["blind_rederivation"]["blind_from"]
            for source in previous_scope["read_allowlist"]:
                if source not in protected:
                    protected.append(source)
            notes.append(f"{label}: explicit blind-phase replacement {old} -> {new} for unchanged full owner {full}; old phase and grant retained as history")
        if "blindness_lifted_for_additions" in addendum:
            tasks = addendum["blindness_lifted_for_additions"]
            rationale = addendum.get("blindness_lift_rationale")
            if (not isinstance(tasks, list) or not tasks or any(not _valid_task(task, native=True) for task in tasks)
                    or len(set(tasks)) != len(tasks) or not isinstance(rationale, str) or not rationale.strip()):
                raise ValueError(f"{label}: scoped lifts require valid unique full-joint TASK owners and nonempty blindness_lift_rationale")
            blindness = composed.get("blindness")
            if not isinstance(blindness, dict) or blindness.get("mutual") is not True:
                raise ValueError(f"{label}: scoped lift must preserve mutual=true")
            scopes = blindness.setdefault("scoped_lifts", {})
            if not isinstance(scopes, dict):
                raise ValueError(f"{label}: malformed scoped_lifts mapping")
            for task in tasks:
                phase = (composed.get("_blind_phase_assignments") or {}).get(task)
                if not isinstance(phase, dict):
                    raise ValueError(f"{label}: scoped lift owner {task} has no declared full-joint/blind-phase binding")
                allowlist = _allowlist_paths(addendum.get("lift_read_allowlist"), phase["blind_task"])
                scope = {"blind_task": phase["blind_task"], "rationale": rationale.strip(), "read_allowlist": allowlist}
                _scoped_lift(task, scope, composed)
                if task in scopes and phase_replacement is None:
                    prior = scopes[task]
                    if not isinstance(prior, dict) or prior.get("blind_task") != phase["blind_task"]:
                        raise ValueError(f"{label}: scoped lift cannot replace an unrelated prior blind-task binding")
                    scope["read_allowlist"] = list(prior["read_allowlist"])+[item for item in allowlist if item not in prior["read_allowlist"]]
                    _scoped_lift(task, scope, composed)
                scopes[task] = scope
                notes.append(f"{label}: scoped blindness lift for {task}: {len(scope['read_allowlist'])} exact prior blind-artifact path(s) from {phase['blind_task']}; legacy lift entries preserved")
    errors = _phase_problems(composed)
    if errors:
        raise ValueError("invalid composed blind-phase assignment: "+"; ".join(errors))
    return composed, notes


def _attestation_of(doc) -> dict | None:
    if not isinstance(doc, dict):
        return None
    if isinstance(doc.get("review_attestation"), dict):
        return doc["review_attestation"]
    for value in doc.values():          # nested under validation_report etc.
        if isinstance(value, dict) and isinstance(
                value.get("review_attestation"), dict):
            return value["review_attestation"]
    return None


def _collect_reports(targets: list[str]) -> list[tuple[str, dict]]:
    reports = []
    for target in targets:
        paths = []
        if os.path.isdir(target):
            for pattern in ("**/*.yaml", "**/*.yml"):
                paths.extend(glob.glob(os.path.join(target, pattern),
                                       recursive=True))
        else:
            paths = [target]
        for path in sorted(set(paths)):
            attestation = _attestation_of(_load(path))
            if attestation is not None:
                reports.append((path, attestation))
    return reports


def _rel(path: str) -> str:
    """Repo-relative where that is shorter, absolute otherwise.

    Reports normally live under `coordination/`, but a caller may point this
    at a path outside the repo; `../../../..` chains help nobody read a
    failure.
    """
    relative = os.path.relpath(path, REPO)
    return path if relative.startswith("..") else relative


def check(plan: dict, reports: list[tuple[str, dict]]) -> list[str]:
    # Recheck abbreviations on every invocation: Git may have gained objects
    # since an earlier check in this process, changing their uniqueness.
    _git_source_commit.cache_clear()
    try:
        return _check(plan, reports)
    except InvalidGitSource as error:
        return [f"invalid Git source identity: {error}"]


def _check(plan: dict, reports: list[tuple[str, dict]]) -> list[str]:
    problems: list[str] = list(plan.get("_composition_errors") or [])
    if _replacement_locations(plan):
        problems.append("blind_phase_replacement belongs only at review_plan_addendum top level")
    problems.extend(_phase_problems(plan))
    rel = _rel

    if not str(plan.get("coordinator_prior") or "").strip():
        problems.append(
            "review_plan.coordinator_prior is empty; the prior is recorded "
            "before the round so that concurrence can be told apart from "
            "agreement with the Coordinator")

    by_task = {}
    for path, attestation in reports:
        task_id = str(attestation.get("task_id") or "").strip()
        if not task_id:
            problems.append(f"{rel(path)}: review_attestation.task_id is empty")
            continue
        if not _valid_task(task_id):
            problems.append(f"{rel(path)}: invalid review_attestation.task_id {task_id!r}")
        if task_id in by_task:
            problems.append(f"{rel(path)}: duplicate attestation for {task_id}")
        by_task[task_id] = (path, attestation)

    # --- joints: enumerated, owned, attested, and reported on ----------------
    joints = plan.get("joints")
    if not isinstance(joints, list) or not joints:
        problems.append("review_plan.joints is empty; a review with no named "
                        "load-bearing step cannot show coverage")
        joints = []
    declared_joint_counts: dict[str, int] = {}
    for entry in joints:
        if isinstance(entry, dict):
            owner = _joint_owner(entry)
            if owner:
                declared_joint_counts[owner] = declared_joint_counts.get(owner, 0) + 1
    owners: dict[str, list[str]] = {}
    task_joints: dict[str, list[str]] = {}
    for index, entry in enumerate(joints):
        if not isinstance(entry, dict):
            problems.append(f"review_plan.joints[{index}] must be a mapping")
            continue
        if "id" in entry and (not isinstance(entry["id"], str) or not entry["id"].strip()):
            problems.append(f"review_plan.joints[{index}].id must be a nonempty string")
        if "id" in entry and "joint" in entry and (
            not isinstance(entry.get("joint"), str)
            or not entry["joint"].strip()
            or entry["joint"].strip() == str(entry["id"]).strip()
        ):
            problems.append(
                f"review_plan.joints[{index}].joint needs a nonempty "
                "full statement for its explicit id")
        name = _joint_name(entry).strip() or f"joints[{index}]"
        owner = _joint_owner(entry)
        if not owner:
            problems.append(f"joint '{name}' has no assigned_to; an unowned "
                            f"joint is the coverage gap this plan exists to "
                            f"make visible")
            continue
        if not _valid_task(entry.get(_owner_key(entry))):
            problems.append(f"joint '{name}' has invalid TASK owner {owner!r}")
        if ("owner" in entry and "assigned_to" in entry and entry["owner"] != entry["assigned_to"]):
            problems.append(f"joint '{name}' has conflicting owner and assigned_to")
        owners.setdefault(_joint_label(name).casefold(), []).append(owner)
        task_joints.setdefault(owner, []).append(name)
        if not str(entry.get("attack_plan") or "").strip():
            problems.append(f"joint '{name}' has no attack_plan; 'review this' "
                            f"returns an opinion, a worked attack returns a "
                            f"result either way")
        if owner not in by_task:
            problems.append(f"joint '{name}' is assigned to {owner}, which "
                            f"filed no review_attestation")
            continue
        _, attestation = by_task[owner]
        owned = attestation.get("joints_owned") or []
        if not isinstance(owned, list):
            problems.append(f"{owner}: joints_owned must be a list")
            owned = []
        if not _claims_joint(owned, name):
            problems.append(f"{owner} does not claim joint "
                            f"'{_joint_label(name)}' in joints_owned")
        _, problem = _verdict_for(attestation, name, declared_joint_counts.get(owner, 1))
        if problem:
            problems.append(f"{owner}: {problem}")
    for name, assigned in owners.items():
        if len(assigned) > 1:
            problems.append(f"joint '{name}' has {len(assigned)} owners "
                            f"({', '.join(assigned)}); two reviewers on one "
                            f"joint means another joint has none")
    rederivation = plan.get("blind_rederivation")
    rederivation = rederivation if isinstance(rederivation, dict) else {}
    if "phased_release" in rederivation and rederivation.get("required") is not True:
        problems.append("phased_release requires blind_rederivation.required=true")
    for _, attestation in reports:
        if "phased_release" in attestation and (
                "phased_release" not in rederivation
                or attestation.get("task_id") != rederivation.get("assigned_to")):
            problems.append("attested phased_release has no matching prospective blind task contract")
    declared_tasks = set(task_joints)
    if rederivation.get("required"):
        declared_tasks.add(str(rederivation.get("assigned_to") or "").strip())
    for task_id, (path, attestation) in by_task.items():
        if task_id not in declared_tasks:
            problems.append(f"{rel(path)}: {task_id} owns no declared joint or required blind task; unowned attestation")
        owned = attestation.get("joints_owned") or []
        if isinstance(owned, list):
            for claim in owned:
                if not any(_claims_joint([claim], name) for name in task_joints.get(task_id, [])):
                    problems.append(f"{task_id} claims unassigned joint '{_joint_label(claim)}'")
        read = attestation.get("sources_read", [])
        if not isinstance(read, list) or any(not isinstance(value, str) or not value.strip() for value in read):
            problems.append(f"{task_id}: sources_read must be a list of nonempty paths/source strings")
        elif read:
            # Validate even a broadly lifted/non-blind reviewer's Git reads.
            # Malformed citations cannot bypass the later scope comparisons.
            for value in read:
                _read_path(value)

    # --- blindness ----------------------------------------------------------
    blindness = plan.get("blindness")
    blindness = blindness if isinstance(blindness, dict) else {}
    raw_lifts = blindness.get("lifted_for") or []
    if not isinstance(raw_lifts, list) or any(not _valid_task(task) for task in raw_lifts):
        problems.append("blindness.lifted_for must be a list of valid TASK owners")
        raw_lifts = []
    lifted = set(raw_lifts)
    if "mutual" in blindness and type(blindness["mutual"]) is not bool:
        problems.append("blindness.mutual must be an explicit boolean")
    if lifted and not str(blindness.get("rationale") or "").strip():
        problems.append("blindness.lifted_for is nonempty but rationale is "
                        "empty; blindness is lifted on purpose, never drifted "
                        "out of")
    scopes = blindness.get("scoped_lifts", {})
    if not isinstance(scopes, dict):
        problems.append("blindness.scoped_lifts must be a per-task mapping")
        scopes = {}
    allowed_scopes = {}
    for task_id, scope in scopes.items():
        try:
            allowed_scopes[task_id] = _scoped_lift(task_id, scope, plan)
        except ValueError as error:
            problems.append(f"invalid scoped lift for {task_id}: {error}")
    if blindness.get("mutual") is not False:
        for task_id, (path, attestation) in sorted(by_task.items()):
            # An explicit scoped addition overrides a legacy broad lift for this
            # task only; all other legacy lift semantics remain unchanged.
            if task_id in allowed_scopes:
                allowed = allowed_scopes[task_id]
                read = attestation.get("sources_read")
                if not isinstance(read, list) or any(not isinstance(value, str) for value in read):
                    continue  # already refused above; do not coerce bogus reads
                if type(attestation.get("read_sibling_reports")) is not bool:
                    problems.append(f"{task_id}: a scoped lift requires explicit read_sibling_reports true/false")
                authorized = set()
                for source in read:
                    canonical = _read_path(source)
                    task_parts = set(_path_task_parts(canonical))
                    sibling = bool(task_parts-{task_id}) or any(
                        other != task_id and (_within(canonical, _read_path(report_path))
                            or (source.rstrip().endswith(("/", "\\")) and _within(_read_path(report_path), canonical)))
                        for other, (report_path, _) in by_task.items())
                    if canonical in allowed:
                        authorized.add(canonical)
                    elif sibling:
                        problems.append(f"{rel(path)}: {task_id} read sibling artifact outside scoped lift_read_allowlist -- {source}")
                if attestation.get("read_sibling_reports") and not authorized:
                    problems.append(f"{task_id}: declared sibling reads have no exact source in scoped lift_read_allowlist")
            elif attestation.get("read_sibling_reports") and (task_id not in lifted or task_id in scopes):
                problems.append(
                    f"{rel(path)}: {task_id} read sibling reports but is not "
                    f"named in blindness.lifted_for; this round's concurrence "
                    f"is not independent")
            if task_id not in lifted and task_id not in allowed_scopes:
                read = attestation.get("sources_read")
                if isinstance(read, list):
                    for source in read:
                        if not isinstance(source, str):
                            continue
                        canonical = _read_path(source)
                        tasks = set(_path_task_parts(canonical)) & set(task_joints)
                        sibling = bool(tasks-{task_id}) or any(
                            other != task_id and (_within(canonical, _read_path(report_path))
                                or (source.rstrip().endswith(("/", "\\")) and _within(_read_path(report_path), canonical)))
                            for other, (report_path, _) in by_task.items())
                        if sibling:
                            problems.append(f"{rel(path)}: {task_id} sources_read includes sibling artifact without an authorized blindness lift -- {source}")

    # --- proves-too-much ----------------------------------------------------
    control = plan.get("proves_too_much")
    control = control if isinstance(control, dict) else {}
    if not (control.get("objects") or []):
        problems.append("proves_too_much.objects is empty; a claim-changing "
                        "review runs the argument against objects where its "
                        "conclusion is known false")
    elif not str(control.get("failure_signature") or "").strip():
        problems.append("proves_too_much.failure_signature is empty; state "
                        "what the argument must DO on a known-false object, "
                        "or the control cannot fail")

    # --- blind re-derivation ------------------------------------------------
    rederivation = plan.get("blind_rederivation")
    rederivation = rederivation if isinstance(rederivation, dict) else {}
    if "required" in rederivation and type(rederivation["required"]) is not bool:
        problems.append("blind_rederivation.required must be an explicit boolean")
    if rederivation.get("required"):
        owner = str(rederivation.get("assigned_to") or "").strip()
        raw_blind = rederivation.get("blind_from") or []
        if not isinstance(raw_blind, list) or any(not isinstance(value, str) or not value.strip() for value in raw_blind):
            problems.append("blind_rederivation.blind_from must be a list of nonempty source paths")
            raw_blind = []
        blind_from = [value.strip() for value in raw_blind]
        if not str(rederivation.get("quantity") or "").strip():
            problems.append("blind_rederivation.quantity is empty; the "
                            "re-deriver starts from the statement alone")
        if not blind_from:
            problems.append("blind_rederivation.blind_from is empty; name the "
                            "producer's implementation, notes and report, or "
                            "the independence is not checkable")
        if not owner:
            problems.append("blind_rederivation.required is true with no "
                            "assigned_to")
        elif not _valid_task(rederivation.get("assigned_to")):
            problems.append("blind_rederivation has an invalid TASK assigned_to")
        owner_protections = {owner: blind_from}
        history = plan.get("_blind_phase_history")
        if isinstance(history, list):
            for record in history:
                if (isinstance(record, dict) and isinstance(record.get("phase_assignment"), dict)
                        and _valid_task(record["phase_assignment"].get("blind_task"), native=True)
                        and isinstance(record.get("blind_rederivation"), dict)):
                    owner_protections[record["phase_assignment"]["blind_task"]] = record["blind_rederivation"].get("blind_from", [])
        for owner, protected_sources in owner_protections.items():
            if owner not in by_task:
                problems.append(f"blind_rederivation is assigned to retained/current owner {owner}, which "
                                f"filed no review_attestation")
                continue
            path, attestation = by_task[owner]
            raw_read = attestation.get("sources_read") or []
            read = [value.strip() for value in raw_read if isinstance(value, str)] if isinstance(raw_read, list) else []
            if owner == rederivation.get("assigned_to") and "phased_release" in rederivation:
                phase_errors = check_sealed_phases(plan, attestation, REPO)
                problems.extend(phase_errors)
                if not phase_errors:
                    # Only a complete prospective content/timeline check may
                    # replace the legacy union-of-all-reads restriction.
                    continue
            leaked = sorted({b for b in protected_sources
                             for r in read if _within(_read_path(r), _read_path(b))
                             or (r.endswith(("/", "\\")) and _within(_read_path(b), _read_path(r)))})
            if leaked:
                problems.append(
                    f"{rel(path)}: re-deriver {owner} read {len(leaked)} "
                    f"blind_from path(s) -- {', '.join(leaked)}; the "
                    f"re-derivation is not independent of the implementation "
                    f"it was meant to check")
            if attestation.get("blind_from_respected") is not True and not leaked:
                problems.append(f"{owner}: blind_from_respected must be "
                                f"explicitly true for a re-derivation task")
    return problems


# ---------------------------------------------------------------------------
# blind-history check: the tree a blind agent is GIVEN, not the files it reads
# ---------------------------------------------------------------------------

# A token a commit message could carry a protected value as: a number (with
# optional sign, decimal part and exponent) or a bare word. Hashed one by one,
# so a value can be recognised without this tool ever being told it.
_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def protected_hashes(batch_doc) -> dict[str, str]:
    """{sha256: label} a batch declares protected for its blind phase.

    Read from `blind_phase_hygiene.protected_sha256`, either as a list of
    hex digests or as a {digest: label} mapping. Absent means the batch declared
    nothing, which this tool reports as UNCHECKABLE -- never as a pass. A rule
    stated only in prose cannot be enforced mechanically, and reporting it as
    checked is the false assurance that let CORR-20260905-547849 through.
    """
    batch = (batch_doc or {}).get("batch") or batch_doc or {}
    hygiene = batch.get("blind_phase_hygiene") or {}
    if not isinstance(hygiene, dict):
        return {}
    declared = hygiene.get("protected_sha256")
    if isinstance(declared, dict):
        return {str(k).strip().lower(): str(v) for k, v in declared.items()
                if str(k).strip()}
    if isinstance(declared, list):
        return {str(x).strip().lower(): "protected value" for x in declared
                if str(x).strip()}
    return {}


def _token_hashes(text: str) -> dict[str, str]:
    """{sha256: token} over every token in `text`."""
    import hashlib
    return {hashlib.sha256(t.encode()).hexdigest(): t
            for t in _TOKEN_RE.findall(text)}


def commit_messages(ref: str, max_commits: int = 500,
                    repo: str = REPO) -> list[tuple[str, str]]:
    """(sha, full message) for commits reachable from `ref`, newest first."""
    import subprocess
    # ASCII record/unit separators: neither appears in a commit message, and
    # unlike NUL both survive text-mode subprocess arguments.
    out = subprocess.run(
        ["git", "-C", repo, "log", f"-{int(max_commits)}",
         "--format=%H%x1f%B%x1e", ref],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git log {ref} failed: {out.stderr.strip()[:200]}")
    commits = []
    for chunk in out.stdout.split("\x1e"):
        if "\x1f" not in chunk:
            continue
        sha, _, body = chunk.partition("\x1f")
        commits.append((sha.strip(), body))
    return commits


def check_blind_history(ref: str, hashes: dict[str, str], max_commits: int = 500,
                        repo: str = REPO) -> list[str]:
    """Problems if any protected value appears in `ref`'s reachable messages.

    Reports the OFFENDING COMMIT and the batch's own label for the value, never
    the value itself -- this tool's output is read by the same people the blind
    phase protects.
    """
    if not hashes:
        return ["no protected values declared: add "
                "blind_phase_hygiene.protected_sha256 to the batch, or this "
                "check is UNCHECKABLE rather than passing"]
    problems = []
    for sha, body in commit_messages(ref, max_commits, repo):
        hit = {d: t for d, t in _token_hashes(body).items() if d in hashes}
        for digest in hit:
            problems.append(
                f"{sha[:9]} commit message states a protected value "
                f"({hashes[digest]}) -- a blind agent given this tree can read "
                f"it with `git log`, which is not a file read and is in no "
                f"blind_from list")
    return problems


def _find_in_batch(batch: str) -> tuple[str | None, list[str]]:
    plans = [p for p in glob.glob(os.path.join(batch, "**", "*.yaml"),
                                  recursive=True)
             if _plan_of(_load(p)) is not None]
    return (plans[0] if plans else None), [batch]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", help="handoff or review_plan YAML")
    parser.add_argument("--reports", nargs="*", default=[],
                        help="report files or directories to scan")
    parser.add_argument("--batch", help="batch directory holding both")
    parser.add_argument("--expected-plan-sha256", metavar="HEX",
                        help="externally pinned SHA-256 of the exact plan file; "
                             "required when the plan uses explicit joint IDs")
    parser.add_argument("--no-addenda", action="store_true",
                        help="check against the plan file alone, ignoring any "
                             "review_plan_addendum beside it (for auditing a "
                             "round against its ORIGINAL setup)")
    parser.add_argument("--blind-history", metavar="REF",
                        help="git ref whose reachable commit messages must not "
                             "state any protected literal")
    parser.add_argument("--protected-from", metavar="BATCH_YAML",
                        help="batch.yaml declaring blind_phase_hygiene."
                             "protected_literals")
    parser.add_argument("--max-commits", type=int, default=500)
    args = parser.parse_args()

    if args.blind_history:
        if not args.protected_from:
            print("--blind-history requires --protected-from", file=sys.stderr)
            return 2
        hashes = protected_hashes(_load(args.protected_from))
        problems = check_blind_history(args.blind_history, hashes,
                                       args.max_commits)
        if problems:
            for problem in problems:
                print(f"FAIL: {problem}")
            print(f"\n{len(problems)} blind-history problem(s) in {args.blind_history}")
            return 1
        print(f"PASS: {args.blind_history} states none of "
              f"{len(hashes)} protected value(s) in its last "
              f"{args.max_commits} reachable commit messages")
        return 0

    plan_path, report_targets = args.plan, list(args.reports)
    if args.batch:
        found, targets = _find_in_batch(args.batch)
        plan_path = plan_path or found
        report_targets = report_targets or targets
    if not plan_path:
        print("no review_plan found; pass --plan or a --batch containing one",
              file=sys.stderr)
        return 2

    # An ID and a plausible statement in the same untrusted plan cannot bind
    # one to the other. Require a digest supplied outside that file before a
    # combined CLI check admits a plan with explicit joint IDs.
    try:
        with open(plan_path, "rb") as handle:
            plan_bytes = handle.read()
        actual_plan_sha256 = hashlib.sha256(plan_bytes).hexdigest()
        plan_text = plan_bytes.decode("utf-8")
    except (OSError, UnicodeError) as error:
        print(f"cannot read review plan {plan_path}: {error}", file=sys.stderr)
        return 2

    try:
        plan = _plan_of(_load(plan_path, content=plan_text))
    except ValueError as error:
        print(f"FAIL: invalid review plan: {error}", file=sys.stderr)
        return 2
    if plan is None:
        print(f"{plan_path}: no review_plan block", file=sys.stderr)
        return 2

    composition: list[str] = []
    if not args.no_addenda:
        try:
            addenda = find_addenda(plan_path)
            if addenda:
                plan, composition = compose_plan(plan, addenda)
        except ValueError as error:
            print(f"FAIL: invalid review-plan addendum: {error}", file=sys.stderr)
            return 2
        if addenda:
            print(f"composed {len(addenda)} addendum/addenda into "
                  f"{_rel(plan_path)}:")
            for path, _ in addenda:
                print(f"  extends: {_rel(path)}")
            for note in composition:
                print(f"  {note}")
            if not composition:
                print("  (no joint added or reassigned)")

    pin_joints = plan.get("joints")
    has_explicit_ids = isinstance(pin_joints, list) and any(
        isinstance(joint, dict) and "id" in joint for joint in pin_joints)
    expected = args.expected_plan_sha256
    if has_explicit_ids and not expected:
        print("FAIL: explicit joint IDs require --expected-plan-sha256 "
              "from a trusted external record", file=sys.stderr)
        return 2
    if expected and (not re.fullmatch(r"[0-9a-f]{64}", expected)
                     or expected != actual_plan_sha256):
        print(f"FAIL: plan SHA-256 mismatch (actual {actual_plan_sha256})",
              file=sys.stderr)
        return 2

    try:
        reports = _collect_reports(report_targets)
    except ValueError as error:
        print(f"FAIL: invalid review report: {error}", file=sys.stderr)
        return 2
    if not reports:
        print("no review_attestation blocks found in the given reports",
              file=sys.stderr)
        return 2

    problems = check(plan, reports)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        print(f"\n{len(problems)} independence problem(s) across "
              f"{len(reports)} report(s)")
        return 1
    print(f"PASS: {len(reports)} report(s), every joint owned and attested, "
          f"blindness respected, controls declared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
