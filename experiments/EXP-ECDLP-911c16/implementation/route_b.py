"""Arithmetic route b: cross multiply and Euclidean reduction; no Fraction."""
def pair(a,b):
    if b<=0:
        raise ValueError("positive denominator required")
    x,y=abs(a),b
    while y:
        x,y=y,x%y
    return a//x,b//x
def text(v):
    return f"{v[0]}/{v[1]}"
def compute(inputs):
    M,b=inputs["numeric"]["M"],inputs["numeric"]["b"]
    if min(M,b)<=0:
        raise ValueError("positive domain required")
    lower,good_off,bad_off=pair(M,2*b),pair(M,16*b),pair(M,4*b)
    good,bad=pair(2,16),pair(2,4)
    remain_good,remain_bad=pair(good[1]-2*good[0],good[1]),pair(bad[1]-2*bad[0],bad[1])
    numeric_good=pair(good_off[0]*lower[1],good_off[1]*lower[0])
    numeric_bad=pair(bad_off[0]*lower[1],bad_off[1]*lower[0])
    return {"measurement": {"good_ratio": text(good),"good_remaining":text(remain_good),
        "bad_ratio":text(bad),"bad_remaining":text(remain_bad),
        "numeric_matches_symbolic":numeric_good==good and numeric_bad==bad,
        "bad_label":"does_not_suffice" if remain_bad[0]<=0 else "suffices",
        "numeric_lower":text(lower),"numeric_good_off":text(good_off),"numeric_bad_off":text(bad_off)},
        "witness":{"symbolic_ratio_pairs":[[2,16],[2,4]],"domain":"M>0,b>0; common nonzero monomial M*b cancels without divisibility assumptions"}}

def assess(inputs,m):
    return {"larger_theta_does_not_suffice": m["bad_label"]=="does_not_suffice",
            "positive_domain": inputs["numeric"]["M"]>0 and inputs["numeric"]["b"]>0}, {
        **{key: m[key] == value for key,value in inputs["predicted"].items()},
        "numeric_matches_symbolic": m["numeric_matches_symbolic"]}

