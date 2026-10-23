"""Finite shadow-level crosscheck for THM-COMMUTATOR-KERNEL1 Lemma 2(b)."""
from itertools import product


def observed(B, d):
    out = set()
    words = 0
    for length in range(d + 1):
        for word in product(range(B + 1), repeat=length):
            words += 1
            neg_right = 0
            counts = [0] * B
            for letter in reversed(word):
                if letter == B:
                    neg_right += 1
                else:
                    counts[letter] += -1 if neg_right % 2 else 1
            out.add((-1 if neg_right % 2 else 1, tuple(counts)))
    return out, words


def predicted(B, d):
    out = set()
    for a in product(range(-d, d + 1), repeat=B):
        weight = sum(abs(x) for x in a)
        for e in (1, -1):
            penalty = 1 if e == -1 else 0 if all(x >= 0 for x in a) else 2
            if weight + penalty <= d:
                out.add((e, a))
    return out


def main():
    total_words = 0
    total_cases = 0
    for B in range(4):
        for d in range(7):
            got, words = observed(B, d)
            want = predicted(B, d)
            missing, extra = want - got, got - want
            assert not missing and not extra, (B, d, sorted(missing), sorted(extra))
            print(f"B={B} d={d} words={words} shadows={len(got)} missing=0 extra=0")
            total_words += words
            total_cases += 1
    print(f"PASS: {total_cases} (B,d) cases, {total_words} exhaustive word evaluations, 0 shadow mismatches")


if __name__ == "__main__":
    main()
