"""Reusable target-polynomial operators for a fixed Dickson fibre.

The frozen S4 expressions have target-x degree at most four. Linearity gives
M(t)=sum(t**j*M_j). Charge setup for every M_j and subsequent query matrices,
kernel/extraction/recovery. No measured advantage or P-256 run is claimed.
"""
import ast
from collections import Counter
from math import comb

import core
import exterior
from crypto_autoresearcher.index_calculus.curve import Curve, is_probable_prime


def target_degree(text):
    def degree(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return 0
        if isinstance(node, ast.Name) and node.id in ('a','b','t'):
            return int(node.id == 't')
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return degree(node.operand)
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub)):
                return max(degree(node.left), degree(node.right))
            if isinstance(node.op, ast.Mult):
                return degree(node.left)+degree(node.right)
            if (isinstance(node.op, ast.Pow) and isinstance(node.right, ast.Constant) and
                    type(node.right.value) is int and 0 <= node.right.value <= 12):
                return degree(node.left)*node.right.value
        raise ValueError('unsupported frozen coefficient expression')
    return degree(ast.parse(text, mode='eval').body)


def lagrange_columns(nodes, p):
    columns=[]
    for x in nodes:
        coefficients, denominator=[1],1
        for y in nodes:
            if x==y:
                continue
            following=[0]*(len(coefficients)+1)
            for j,c in enumerate(coefficients):
                following[j]=(following[j]-y*c)%p
                following[j+1]=(following[j+1]+c)%p
            coefficients=following
            denominator=denominator*(x-y)%p
        inverse=pow(denominator,-1,p)
        columns.append([c*inverse%p for c in coefficients])
    return columns


class OperatorFamily:
    def __init__(self,parameters,depth,terminal,name,*,max_dimension=560):
        if type(depth) is not int or depth<1:
            raise ValueError('positive integer depth required')
        size=1<<depth
        dimension={'distinct':comb(size,3),'twoequal':size*size,'allequal':size}[name]
        if dimension>max_dimension:
            raise core.ExtractionUnknown('operator-family dimension exceeds configured resource guard')
        p=parameters['p']
        if p<=5 or not is_probable_prime(p):
            raise ValueError('prime field greater than interpolation degree required')
        Curve(p,parameters['a'],parameters['b'])
        if not 0<=terminal<p or terminal in (2,p-2):
            raise ValueError('separable canonical fibre required')
        import json
        from flint import fmpz_mod_ctx
        source=json.loads((core.OLD/'baseline/s4-symmetric.json').read_text())
        self.degree=max(target_degree(text) for _,text in source['terms'])
        if self.degree>=p:
            raise ValueError('not enough distinct field interpolation nodes')
        nodes=list(range(self.degree+1))
        slots={'distinct':(0,1,2),'twoequal':(0,0,1),'allequal':(0,0,0)}[name]
        polynomials=[core.relation_polynomial(parameters,x,slots)[0] for x in nodes]
        weights=lagrange_columns(nodes,p)
        coefficients=[]
        for j in range(self.degree+1):
            poly={}
            for i,value in enumerate(polynomials):
                poly=core.poly_add(poly,core.poly_scale(value,weights[i][j],p),p)
            coefficients.append(poly)
        context=fmpz_mod_ctx(p)
        scalar=exterior.scalar_columns(depth,terminal,p)
        counters=Counter()
        self.operators=[]
        self.basis=None
        for polynomial in coefficients:
            operator,basis=exterior.tensor_operator(polynomial,max(slots)+1,name=='distinct',
                                                     scalar,context,p,counters)
            if self.basis is not None and self.basis!=basis:
                raise ArithmeticError('coefficient operators use different bases')
            self.basis=basis
            self.operators.append(operator)
        self.p=p
        self.dimension=dimension
        self.setup_counters=dict(counters)
        self.setup_scope='All coefficient operators; no FLINT-internal field count or complete-cost claim.'

    def evaluate(self,target_x):
        if type(target_x) is not int:
            raise ValueError('integer target coordinate required')
        result=self.operators[-1]
        for operator in reversed(self.operators[:-1]):
            result=(target_x%self.p)*result+operator
        return result
