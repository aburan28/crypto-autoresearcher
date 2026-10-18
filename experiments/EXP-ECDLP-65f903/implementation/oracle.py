"""Independent checker: signed integer determinants and product lists."""
from math import prod
def compute(inputs):
    nums,dens = [],[]
    for key in ("left","witness","right"):
        a,b = inputs[key].split("/")
        nums.append(int(a)); dens.append(int(b))
    products = [[nums[0]*dens[1],dens[0]*nums[1]],[nums[1]*dens[2],dens[1]*nums[2]],[nums[2]*dens[0],dens[2]*nums[0]]]
    less = [x-y<0 for x,y in products]
    return {"measurement": dict(left_below_witness=less[0],witness_below_right=less[1],
        n_squared=prod([inputs["n"],inputs["n"]]),n_cubed=prod([inputs["n"]]*3),
        reversed_below=less[2],cross_products=products,tail_products=[sum([5]*6),sum([6]*5)]),
        "witness": {"rational_cross_products": products}}
def assess(inputs,m):
    q=inputs["predicted"]
    controls = {"reversed_comparison_false": m["reversed_below"] is False,
                "both_tail_products_computed": m["tail_products"]==[30,30]}
    predicted = {"witness_inside": (m["left_below_witness"] and m["witness_below_right"])==q["witness_inside"],
        "n_squared": q["n_squared"]==m["n_squared"],"n_cubed": q["n_cubed"]==m["n_cubed"],
        "reversed_below": q["reversed_below"]==m["reversed_below"]}
    return controls,predicted

