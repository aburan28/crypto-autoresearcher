"""Independent checker: rational-pair determinants normalized with math.gcd."""
from math import gcd
def canonical(a,b):
    g=gcd(a,b)
    return f"{a//g}/{b//g}"
def compute(inputs):
    m=inputs["numeric"]["M"]; b=inputs["numeric"]["b"]
    if b<=0 or m<=0:
        raise ValueError("outside positive domain")
    ratios=[]; remains=[]; matches=[]
    for factor in (16,4):
        numerator,denominator=m*(2*b),(factor*b)*m
        ratios.append(canonical(numerator,denominator))
        remains.append(canonical(denominator-2*numerator,denominator))
        # Equality of coefficients times the SAME symbolic monomial M*b.
        matches.append(numerator*factor==denominator*2)
    return {"measurement":{"good_ratio":ratios[0],"good_remaining":remains[0],
        "bad_ratio":ratios[1],"bad_remaining":remains[1],"numeric_matches_symbolic":all(matches),
        "bad_label":"does_not_suffice" if 4-2*2<=0 else "suffices",
        "numeric_lower":canonical(m,2*b),"numeric_good_off":canonical(m,16*b),"numeric_bad_off":canonical(m,4*b)},
        "witness":{"symbolic_ratio_pairs":[[2,16],[2,4]],"domain":"M>0,b>0; common nonzero monomial M*b cancels without divisibility assumptions"}}
def assess(inputs,m):
    controls=dict(larger_theta_does_not_suffice=(m["bad_label"]=="does_not_suffice"),
                  positive_domain=(min(inputs["numeric"].values())>0))
    predictions={}
    for name,anticipated in inputs["predicted"].items():
        predictions[name]=anticipated==m[name]
    predictions["numeric_matches_symbolic"]=m["numeric_matches_symbolic"]
    return controls,predictions

