#!/usr/bin/env python3
"""Compute QR-UOV rejection-sampling tau constants without libgsl."""

import argparse
import math


DEFAULT_Q = 127
DEFAULT_L = 3
DEFAULT_V = 156
DEFAULT_M = 54
TAIL_SUM_CUTOFF = 1e-17


def rejection_probability(q: int) -> float:
    """Probability that one masked byte/word is rejected.

    Rejection sampling first maps a uniform integer modulo the next power of two
    into {0, ..., 2^k-1}. Values >= q are rejected. For q in {7,31,127}, this is
    1/8, 1/32, and 1/128 respectively.
    """
    sample_space = 1 << (q - 1).bit_length()
    return (sample_space - q) / sample_space


def binomial_upper_tail_log(trials: int, lower: int, p: float) -> float:
    """Return log Pr[Binomial(trials, p) >= lower].

    tau failure is most naturally counted by rejections, not acceptances. If
    tau = target + extra, failure means more than extra rejections:

        R ~ Binomial(tau, p_reject),  failure = Pr[R >= extra + 1].

    This tail is tiny but near the left side of the distribution for QR-UOV, so
    we compute the first term with lgamma and then walk the tail by recurrence:

        P(X=k+1) / P(X=k) = (n-k)/(k+1) * p/(1-p).

    The recurrence avoids summing thousands of accepted-sample lower-tail terms
    and keeps the values aligned with the existing tau table.
    """
    if lower <= 0:
        return 0.0
    if lower > trials:
        return -math.inf

    # If lower is at or below the mode, the upper tail is not small. Returning
    # log(1) is enough for the binary-search predicate and avoids needless work.
    if lower <= math.floor((trials + 1) * p):
        return 0.0

    log_term = (
        math.lgamma(trials + 1)
        - math.lgamma(lower + 1)
        - math.lgamma(trials - lower + 1)
        + lower * math.log(p)
        + (trials - lower) * math.log1p(-p)
    )

    rel = 1.0
    rel_sum = 1.0
    odds = p / (1.0 - p)
    for k in range(lower, trials):
        rel *= ((trials - k) / (k + 1)) * odds
        rel_sum += rel
        if rel <= rel_sum * TAIL_SUM_CUTOFF:
            break

    return log_term + math.log(rel_sum)


def tau(q: int, lambda_: int, target: int) -> int:
    """Return minimal tau with failure probability <= 2^-lambda."""
    p_reject = rejection_probability(q)
    log_bound = -lambda_ * math.log(2.0)

    def ok(extra: int) -> bool:
        trials = target + extra
        min_rejections_for_failure = extra + 1
        return binomial_upper_tail_log(trials, min_rejections_for_failure, p_reject) <= log_bound

    # Search in the natural variable: extra random samples beyond target.
    low = -1
    high = 1
    while not ok(high):
        high *= 2

    while high - low > 1:
        mid = (low + high) // 2
        if ok(mid):
            high = mid
        else:
            low = mid

    return target + high


def parameter_lengths(L: int, v: int, m: int) -> tuple[int, int, int, int]:
    V = v // L
    M = m // L
    return (
        L * V * (V + 1) // 2,  # P1 coefficients per equation
        L * V * M,             # P2/S coefficients
        L * V,                 # vinegar vector
        L * M,                 # oil/hash vector
    )


def print_tau_defines(lambda_: int, q: int, L: int, v: int, m: int, directive: str) -> None:
    lengths = parameter_lengths(L, v, m)
    tau_values = [tau(q, lambda_, length) for length in lengths]

    print(
        f"#{directive} (QRUOV_q == {q})"
        f" && (QRUOV_L == {L})"
        f" && (QRUOV_v == {v})"
        f" && (QRUOV_m == {m})"
    )
    labels = (
        ("QRUOV_tau_n1", "QRUOV_n1 = L*V*(V+1)/2"),
        ("QRUOV_tau_n2", "QRUOV_n2 = L*V*M      "),
        ("QRUOV_tau_v ", "QRUOV_v  = L*V        "),
        ("QRUOV_tau_m ", "QRUOV_m  = L*M        "),
    )
    for (name, desc), value, length in zip(labels, tau_values, lengths):
        print(f"#define {name} {value:7d} // {desc} : {length:7d}")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute QR-UOV rejection-sampling tau constants.",
        epilog="example: ./find_tau.py 128 127 10 540 60 if",
    )
    parser.add_argument("lambda_", nargs="?", type=positive_int, default=256, metavar="lambda")
    parser.add_argument("q", nargs="?", type=positive_int, default=DEFAULT_Q)
    parser.add_argument("L", nargs="?", type=positive_int, default=DEFAULT_L)
    parser.add_argument("v", nargs="?", type=positive_int, default=DEFAULT_V)
    parser.add_argument("m", nargs="?", type=positive_int, default=DEFAULT_M)
    parser.add_argument("directive", nargs="?", default="elif")
    args = parser.parse_args(argv)

    if args.v % args.L != 0:
        parser.error("v must be divisible by L")
    if args.m % args.L != 0:
        parser.error("m must be divisible by L")

    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    print_tau_defines(args.lambda_, args.q, args.L, args.v, args.m, args.directive)


if __name__ == "__main__":
    main()
