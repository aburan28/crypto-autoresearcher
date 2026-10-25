"""Public norm-column projection. No discrete-log routine or truth table."""
from relations import Rank


def projection(context,scalars):
    known={};derivations=[]
    # These exact public scalar inputs are part of the frozen experiment,
    # including failed source lifts. Matching their public images is allowed;
    # no other scalar enumeration is performed to learn base logs.
    for scalar in scalars:
        point=context.e.mul(scalar,context.P)
        for j,atom in enumerate(context.base):
            for sign in (1,-1):
                image=atom if sign==1 else context.e.neg(atom)
                if point==image:
                    value=sign*scalar%context.r
                    if j in known and known[j]!=value:
                        raise ArithmeticError('inconsistent public anchor')
                    if j not in known:
                        known[j]=value;derivations.append({'column':j,'scalar':value,
                            'derived_from_public_source_scalar':scalar,'sign':sign})
    unknown=[j for j in range(len(context.base)) if j not in known]
    return {'known':known,'unknown_columns':unknown,'public_derivations':derivations}


def row_project(row,projected,r):
    coefficients=row['coefficients']
    rhs=(row['source_scalar']-sum(coefficients[j]*x for j,x in projected['known'].items()))%r
    return [coefficients[j] for j in projected['unknown_columns']],rhs


def certificate(rows,projected,r):
    rank=Rank(len(projected['unknown_columns']),r)
    indices=[]
    for i,row in enumerate(rows):
        if rank.add(*row_project(row,projected,r)):indices.append(i)
    return {'U':rank.columns,'rank':len(rank.pivots),'augmented_rank':len(rank.pivots),
            'independent_row_indices':indices,'pivots':rank.pivots,
            'solution':rank.solve(),'matrix_operation_units':rank.ops,
            'public_derivations':projected['public_derivations'],
            'unknown_columns':projected['unknown_columns'],
            'all_columns_publicly_known':rank.columns==0}
