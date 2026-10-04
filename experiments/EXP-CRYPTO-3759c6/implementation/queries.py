"""Safe query parsing, Boolean compilation, and fidelity/leakage classification.

EXP-CRYPTO-3759c6 preparation artifact for TASK-20260907-da9b67. Defines the
non-shell, program-specific argv parser and Boolean/sparse compiler required
by spec.query_extraction and spec.query_compiler. No recorded proposal query
is parsed or executed by this task: every function below is a frozen
interface to be invoked by the future admission pass over real proposal
records, never at import time.

Hard invariants (spec.query_compiler):
  - Parse argv as data with POSIX quoting rules only; no eval, shell, pipes,
    redirections, variable/glob expansion, or command substitution.
  - Program allowlist: rg or grep only.
  - Flag allowlist: -e/--regexp, -F/--fixed-strings, -i/--ignore-case,
    -w/--word-regexp, -x/--line-regexp, -l/--files-with-matches,
    -n/--line-number, --; rg additionally -s/--case-sensitive, --glob/-g.
  - grep -s and --no-messages are rejected (not treated as rg case-sensitive
    mode). Unsupported flags are never silently ignored.
  - No target-derived terms ever (spec.query_extraction.no_target_advice).
"""

from __future__ import annotations

import dataclasses
import shlex
from enum import Enum
from typing import Optional

# ---------------------------------------------------------------------------
# Program / flag allowlist (spec.query_compiler.allowlist)
# ---------------------------------------------------------------------------

ALLOWED_PROGRAMS = frozenset({"rg", "grep"})

_SHARED_FLAGS = frozenset({
    "-e", "--regexp",
    "-F", "--fixed-strings",
    "-i", "--ignore-case",
    "-w", "--word-regexp",
    "-x", "--line-regexp",
    "-l", "--files-with-matches",
    "-n", "--line-number",
    "--",
})
_RG_ONLY_FLAGS = frozenset({"-s", "--case-sensitive", "--glob", "-g"})
_EXPLICITLY_REJECTED = frozenset({"-s", "--no-messages"})  # for grep specifically

RG_VERSION_PINNED = "15.2.0"


class QueryFidelity(str, Enum):
    EXACT = "exact"                    # spec.query_extraction.exact_stratum
    RECONSTRUCTED = "reconstructed"    # spec.query_extraction.reconstructed_stratum
    UNSUPPORTED = "unsupported"        # spec.query_extraction.unsupported_stratum


class ArgvRejectionReason(str, Enum):
    SHELL_METACHARACTER = "shell_metacharacter"
    DISALLOWED_PROGRAM = "disallowed_program"
    DISALLOWED_FLAG = "disallowed_flag"
    GREP_S_REJECTED = "grep_s_rejected"           # not rg case-sensitive mode
    AMBIGUOUS_BOOLEAN_COMPOSITION = "ambiguous_boolean_composition"
    UNRECOVERABLE_COMMAND = "unrecoverable_command"


#: A conservative POSIX shell metacharacter set. Presence of any of these in a
#: raw recorded string (outside of a token that shlex.split treats as a single
#: quoted literal) marks the command UNREPLAYABLE rather than attempting a
#: partial shell-like interpretation.
_SHELL_METACHARACTERS = set("|&;<>()$`\\\n")


@dataclasses.dataclass(frozen=True)
class ParsedArgv:
    program: str
    tokens: tuple[str, ...]                # argv after the program name
    rejected: Optional[ArgvRejectionReason]
    rejection_detail: Optional[str]


def contains_shell_metacharacters(raw_command: str) -> bool:
    """Detect unsupported shell constructs (pipes/redirects/substitution/etc.).

    This is a conservative textual scan, not a shell parser: its purpose is
    to *reject* ambiguous input, never to interpret it.
    """
    return any(ch in _SHELL_METACHARACTERS for ch in raw_command)


def parse_argv(raw_command: str) -> ParsedArgv:
    """Parse a recorded command as data using POSIX quoting rules only.

    No eval, no shell, no pipes/redirections/expansion/substitution. Rejects
    shell metacharacter operations rather than running them
    (spec.query_compiler.parser). This function is a pure parser; it does not
    execute rg/grep and is not invoked by this preparation task against a
    real recorded command.
    """
    if contains_shell_metacharacters(raw_command):
        return ParsedArgv(
            program="",
            tokens=(),
            rejected=ArgvRejectionReason.SHELL_METACHARACTER,
            rejection_detail=raw_command,
        )
    try:
        tokens = shlex.split(raw_command, comments=False, posix=True)
    except ValueError as exc:
        return ParsedArgv(
            program="",
            tokens=(),
            rejected=ArgvRejectionReason.UNRECOVERABLE_COMMAND,
            rejection_detail=str(exc),
        )
    if not tokens:
        return ParsedArgv(
            program="",
            tokens=(),
            rejected=ArgvRejectionReason.UNRECOVERABLE_COMMAND,
            rejection_detail="empty command",
        )
    program = tokens[0]
    if program not in ALLOWED_PROGRAMS:
        return ParsedArgv(
            program=program,
            tokens=tuple(tokens[1:]),
            rejected=ArgvRejectionReason.DISALLOWED_PROGRAM,
            rejection_detail=program,
        )
    return ParsedArgv(program=program, tokens=tuple(tokens[1:]), rejected=None, rejection_detail=None)


def validate_flags(parsed: ParsedArgv) -> Optional[ArgvRejectionReason]:
    """Check every flag token against the allowlist for the parsed program.

    grep -s / --no-messages are explicitly rejected rather than silently
    accepted or reinterpreted as rg's case-sensitive mode
    (spec.query_compiler.allowlist). Interface only: not invoked here.
    """
    if parsed.rejected is not None:
        return parsed.rejected
    allowed = set(_SHARED_FLAGS)
    if parsed.program == "rg":
        allowed |= _RG_ONLY_FLAGS
    for token in parsed.tokens:
        if not token.startswith("-") or token == "--":
            continue  # positional term / path / end-of-flags marker
        if parsed.program == "grep" and token in _EXPLICITLY_REJECTED:
            return ArgvRejectionReason.GREP_S_REJECTED
        if token not in allowed:
            return ArgvRejectionReason.DISALLOWED_FLAG
    return None


# ---------------------------------------------------------------------------
# Boolean compilation (spec.query_compiler.logic)
# ---------------------------------------------------------------------------

class BooleanOp(str, Enum):
    OR = "or"     # repeated -e patterns
    AND = "and"   # structured all_of: each component matches the document, not necessarily the same line
    LITERAL = "literal"


@dataclasses.dataclass(frozen=True)
class CompiledPredicate:
    op: BooleanOp
    terms: tuple[str, ...]
    fixed_string: bool
    case_insensitive: bool
    word_boundary: bool
    path_filters: tuple[str, ...]           # rg glob semantics, corpus-relative only
    fidelity: QueryFidelity
    empty_query: bool                       # truly absent/empty structured query
    rejection: Optional[ArgvRejectionReason]


def compile_boolean(parsed: ParsedArgv, structured: Optional[dict] = None) -> CompiledPredicate:
    """Compile validated argv (or a structured all_of/any_of expression) into
    a CompiledPredicate. Repeated -e patterns are OR; a structured all_of list
    is AND across file predicates; any_of is OR; nesting only when explicitly
    recorded. Negative expressions require explicit supported syntax or are
    unreplayable (spec.query_compiler.logic). Frozen interface; not invoked
    against a real recorded query by this preparation task.
    """
    raise NotImplementedError(
        "compile_boolean is a frozen interface for the future admission pass; "
        "no query compilation occurs in TASK-20260907-da9b67."
    )


def reconstruct_summary_terms(term_list: list[str]) -> CompiledPredicate:
    """Explicit summary term lists with no command compile as case-insensitive
    fixed-string OR (spec.query_extraction.precedence). Marked RECONSTRUCTED,
    never pooled into primary exact replay. Frozen interface; not invoked.
    """
    raise NotImplementedError(
        "reconstruct_summary_terms is a frozen interface for the future "
        "admission pass; not invoked by TASK-20260907-da9b67."
    )


def classify_fidelity(parsed: ParsedArgv, flag_rejection: Optional[ArgvRejectionReason]) -> QueryFidelity:
    """Exact / reconstructed / unsupported per spec.query_extraction strata."""
    if parsed.rejected is not None or flag_rejection is not None:
        return QueryFidelity.UNSUPPORTED
    return QueryFidelity.EXACT


# ---------------------------------------------------------------------------
# Leakage / contamination checker (spec.query_extraction.contamination)
# ---------------------------------------------------------------------------

import unicodedata


def normalize_for_contamination_check(text: str) -> str:
    """NFC + casefold + collapse whitespace to one ASCII space, strip outer
    whitespace. Diagnostic-only normalization; never applied to actual
    replay corpus/query bytes (spec.query_extraction.contamination_normalization).
    """
    nfc = unicodedata.normalize("NFC", text)
    folded = nfc.casefold()
    collapsed = " ".join(folded.split())
    return collapsed


@dataclasses.dataclass(frozen=True)
class LeakageCheck:
    contaminated: bool
    matching_bytes: Optional[str]
    reason: Optional[str]   # "target_id" | "target_doi" | "target_full_title"


def check_leakage(
    compiled_query_terms: tuple[str, ...],
    target_id: str,
    target_doi: Optional[str],
    target_title: str,
) -> LeakageCheck:
    """A separate checker run before scoring, comparing the extracted query
    with the referenced target's literal ID/DOI and normalized full title.
    ID/DOI matching is literal case-sensitive token equality; title matching
    uses the diagnostic normalization above. Annotators/query extractors do
    not receive this diagnostic (spec.query_extraction.contamination). This
    is a pure function; it is not invoked against a real query/target pair
    by this preparation task, and it must never be used to source query
    terms (spec.query_extraction.no_target_advice) — it is read-only
    diagnostics, called strictly after extraction.
    """
    for term in compiled_query_terms:
        if term == target_id:
            return LeakageCheck(True, term, "target_id")
        if target_doi is not None and term == target_doi:
            return LeakageCheck(True, term, "target_doi")
    normalized_title = normalize_for_contamination_check(target_title)
    joined = normalize_for_contamination_check(" ".join(compiled_query_terms))
    if normalized_title and normalized_title in joined:
        return LeakageCheck(True, normalized_title, "target_full_title")
    return LeakageCheck(False, None, None)


# ---------------------------------------------------------------------------
# BM25 query term extraction (spec.query_compiler.bm25_query)
# ---------------------------------------------------------------------------

def extract_bm25_terms(compiled: CompiledPredicate) -> Optional[tuple[str, ...]]:
    """Concatenate positive literal term texts from the compiled query,
    preserving multiplicity. Fixed-string terms are literal; regex terms are
    accepted only if they are an entire unescaped literal or an alternation
    of entire literals with no other metacharacters. More complex admitted
    Boolean regex may remain replayable for grep but BM25-unrepresentable —
    returns None in that case rather than inventing words
    (spec.query_compiler.bm25_query). AND/OR constraints filter Boolean
    results but are never added as BM25 operators. Frozen interface; not
    invoked by this preparation task.
    """
    raise NotImplementedError(
        "extract_bm25_terms is a frozen interface for the future admission "
        "pass; not invoked by TASK-20260907-da9b67."
    )


def union_multi_search(compiled_queries: list[CompiledPredicate]) -> CompiledPredicate:
    """If a proposal has multiple recorded searches with no declared
    composition, the proposal result is the union of individually compiled
    returned sets (multi_search_union), retaining constituent results as an
    inherited search reconstruction, not a union of competing retrieval arms
    (spec.query_extraction.precedence, spec.query_compiler.ranking_union).
    Frozen interface; not invoked by this preparation task.
    """
    raise NotImplementedError(
        "union_multi_search is a frozen interface for the future admission "
        "pass; not invoked by TASK-20260907-da9b67."
    )


# ---------------------------------------------------------------------------
# Path filters (spec.query_compiler.paths)
# ---------------------------------------------------------------------------

def apply_path_filters(
    corpus_relative_paths: tuple[str, ...],
    admitted_paths: tuple[str, ...],
    path_filters: tuple[str, ...],
) -> tuple[str, ...]:
    """Match only an explicit sorted list of admitted corpus-relative paths;
    apply recorded corpus-local path/glob filters with rg 15.2.0 glob
    semantics. Reject paths outside the corpus. A target excluded by a path
    filter is reported separately as a real failure of an otherwise
    replayable query (spec.query_compiler.paths). Frozen interface; not
    invoked against real paths by this preparation task.
    """
    raise NotImplementedError(
        "apply_path_filters is a frozen interface for the future admission "
        "pass; not invoked by TASK-20260907-da9b67."
    )
