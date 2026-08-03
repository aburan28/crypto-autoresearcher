"""Tokenization shared by the chunker and the sparse retriever.

The identifier handling here is the reason hybrid retrieval works on this
corpus. A plain word tokenizer turns ``EXP-GGM-001`` into ``exp``, ``ggm``,
``001`` and ``F_{p^n}`` into ``f``, ``p``, ``n`` -- after which no exact-lookup
query can distinguish that experiment from any other. Identifiers are emitted
whole *and* decomposed, so exact queries hit the whole form (rare, hence high
IDF) while looser queries still match the parts.
"""

from __future__ import annotations

import re

#: Whole-token identifier shapes seen in this corpus:
#: EXP-GGM-001, P-256, KN-LIT-001, F_{p^n}, S_4, 2026/1486, 4.3, GF(2)
_IDENTIFIER = re.compile(
    r"""
      [A-Za-z]+_\{[^}\s]+\}          # F_{p^n}
    | [A-Za-z]+\^\{[^}\s]+\}         # p^{1/3}
    | [A-Za-z]+_[A-Za-z0-9]+         # S_4
    | [A-Za-z]{2,}\([A-Za-z0-9^,\s]+\)  # GF(2)
    | [A-Za-z0-9]+(?:-[A-Za-z0-9]+)+ # EXP-GGM-001, P-256
    | \d{4}/\d{3,5}                  # ePrint 2026/1486
    | \d+(?:\.\d+)+                  # Theorem 4.3
    """,
    re.VERBOSE,
)

_WORD = re.compile(r"[A-Za-z]+|\d+")

#: Approximate-token pattern. Deliberately not a BPE tokenizer: chunk bounds
#: must be reproducible years from now without pinning a tokenizer package, and
#: a systematic estimate is fine for enforcing size bands. Empirically this
#: runs within ~15% of GPT/Claude-family counts on technical English, which is
#: well inside the slack between the nominal and maximum chunk sizes.
_TOKENISH = re.compile(r"[A-Za-z]+|\d+|[^\sA-Za-z\d]")

_STOPWORDS = frozenset(
    """
    a an and are as at be by for from has have in into is it its of on or that the
    to was were will with this these those we our they their there than then such
    can could may might not but if when which while also been being do does did
    """.split()
)


def count_tokens(text: str) -> int:
    """Approximate model-token count. Monotone in length; used for size bands."""
    return len(_TOKENISH.findall(text))


def identifiers(text: str) -> list[str]:
    """Whole identifier forms found in ``text``, lowercased."""
    found = []
    for match in _IDENTIFIER.finditer(text):
        token = match.group(0).lower()
        if len(token) > 1:
            found.append(token)
    return found


def search_terms(text: str, keep_stopwords: bool = False) -> list[str]:
    """Terms for sparse retrieval: identifiers whole, plus decomposed words."""
    terms: list[str] = []
    spans: list[tuple[int, int]] = []
    for match in _IDENTIFIER.finditer(text):
        token = match.group(0).lower()
        if len(token) > 1:
            terms.append(token)
            spans.append(match.span())
        # Decompose too, so "semaev p-256" still matches a chunk that only
        # writes "P256" or spells the parts separately.
        terms.extend(w.lower() for w in _WORD.findall(match.group(0)))

    covered = set()
    for start, end in spans:
        covered.update(range(start, end))
    for match in _WORD.finditer(text):
        if match.start() in covered:
            continue
        word = match.group(0).lower()
        if not keep_stopwords and word in _STOPWORDS:
            continue
        terms.append(word)
    return [t for t in terms if t]


#: How much of a term's weight a decomposed identifier part carries. The whole
#: form (``kn-open-001``) is the precise term; the parts (``kn``, ``open``,
#: ``001``) exist so a loosely-spelled query still matches. At equal weight the
#: parts drown the whole: every open-problem note contains ``kn``, ``open`` and
#: some ``001``, so the query "KN-OPEN-001" scored dozens of documents as
#: highly as the one it names. Measured on the evaluation set: exact-identifier
#: recall@5 0.89 -> 1.00.
IDENTIFIER_PART_WEIGHT = 0.3


def weighted_terms(text: str, part_weight: float = IDENTIFIER_PART_WEIGHT) -> dict[str, float]:
    """Terms with weights: whole identifiers and words at 1, ID parts lower."""
    weights: dict[str, float] = {}
    spans: list[tuple[int, int]] = []

    for match in _IDENTIFIER.finditer(text):
        token = match.group(0).lower()
        if len(token) > 1:
            weights[token] = weights.get(token, 0.0) + 1.0
            spans.append(match.span())
        for word in _WORD.findall(match.group(0)):
            key = word.lower()
            weights[key] = weights.get(key, 0.0) + part_weight

    covered: set[int] = set()
    for start, end in spans:
        covered.update(range(start, end))
    for match in _WORD.finditer(text):
        if match.start() in covered:
            continue
        word = match.group(0).lower()
        if word in _STOPWORDS:
            continue
        weights[word] = weights.get(word, 0.0) + 1.0
    return weights


def char_ngrams(text: str, n: int = 4) -> list[str]:
    """Character n-grams over a whitespace-normalized string.

    Gives the dense hashing embedder robustness to the morphological variation
    ("Semaev", "Semaev's", "summation polynomial(s)") that a pure word-hash
    model misses.
    """
    normalized = " " + " ".join(text.lower().split()) + " "
    if len(normalized) <= n:
        return [normalized]
    return [normalized[i : i + n] for i in range(len(normalized) - n + 1)]


def truncate_tokens(text: str, max_tokens: int) -> str:
    """Trim to at most ``max_tokens`` on a whitespace boundary."""
    if count_tokens(text) <= max_tokens:
        return text
    words = text.split()
    low, high = 0, len(words)
    while low < high:
        mid = (low + high + 1) // 2
        if count_tokens(" ".join(words[:mid])) <= max_tokens:
            low = mid
        else:
            high = mid - 1
    return " ".join(words[:low])


def tail_tokens(text: str, max_tokens: int) -> str:
    """The last ``max_tokens`` of ``text``, sentence-aligned where possible."""
    if count_tokens(text) <= max_tokens:
        return text
    words = text.split()
    low, high = 0, len(words)
    while low < high:
        mid = (low + high + 1) // 2
        if count_tokens(" ".join(words[-mid:])) <= max_tokens:
            low = mid
        else:
            high = mid - 1
    tail = " ".join(words[-low:]) if low else ""
    # Prefer starting at a sentence boundary so the overlap reads as prose.
    match = re.search(r"(?<=[.!?])\s+", tail)
    if match and count_tokens(tail[match.end() :]) >= max_tokens // 2:
        return tail[match.end() :]
    return tail


def split_sentences(text: str) -> list[str]:
    """Sentence split good enough for prose; does not break on ``e.g.``/``Fig.``."""
    # The sentinel must be a real NUL in the replacement, not the two-character
    # escape a raw string would produce -- `re` rejects `\x` in a replacement.
    protected = re.sub(
        r"\b(e\.g|i\.e|cf|Fig|Eq|Thm|Alg|Def|Prop|Sec|vs|approx)\.", "\\1\x00", text
    )
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[$\\])", protected)
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]
