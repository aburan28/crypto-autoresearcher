"""Arithmetic route a: exact Fraction substitution and coefficient cancellation."""
from fractions import Fraction
def compute(inputs):
    M,b = inputs["numeric"]["M"],inputs["numeric"]["b"]
    if M<=0 or b<=0:
        raise ValueError("positive M,b required")
    lower = Fraction(M,2*b)
    good_off,bad_off = Fraction(M,16*b),Fraction(M,4*b)
    good,bad = Fraction(2,16),Fraction(2,4)
    fmt = lambda x: f"{x.numerator}/{x.denominator}"
    measurement = {"good_ratio": fmt(good), "good_remaining": fmt(1-2*good),
        "bad_ratio": fmt(bad), "bad_remaining": fmt(1-2*bad),
        "numeric_matches_symbolic": good_off/lower==good and bad_off/lower==bad,
        "bad_label": "does_not_suffice" if 1-2*bad<=0 else "suffices",
        "numeric_lower": fmt(lower), "numeric_good_off": fmt(good_off), "numeric_bad_off": fmt(bad_off)}
    return {"measurement": measurement, "witness": {"symbolic_ratio_pairs": [[2,16],[2,4]],
        "domain": "M>0,b>0; common nonzero monomial M*b cancels without divisibility assumptions"}}

def assess(inputs,m):
    return {"larger_theta_does_not_suffice": m["bad_label"]=="does_not_suffice",
            "positive_domain": inputs["numeric"]["M"]>0 and inputs["numeric"]["b"]>0}, {
        **{key: m[key] == value for key,value in inputs["predicted"].items()},
        "numeric_matches_symbolic": m["numeric_matches_symbolic"]}

