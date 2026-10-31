"""Combinatorial coverage of LSB-first prefix cylinders, without enumeration.

This module does NOT verify polynomial refutations, models, or SAT transcripts.
A caller must discharge those obligations before interpreting coverage as a
completeness certificate. An uncovered assignment need not be an arithmetic
solution. No solver is imported or invoked.
"""


def _integer(value, name):
    if type(value) is not int:
        raise ValueError(name + " must be an integer, not bool")
    return value


def verify_cover(n, prefixes, projected_bits=None, aux_bound=None):
    """Cover assignments b with cylinders b % 2**depth == prefix.

    If aux_bound is given, the domain additionally requires
    b >> projected_bits < aux_bound. Unassigned bits may be set to zero:
    their value cannot lower the auxiliary integer. This makes it possible
    to return a valid gap immediately at a missing trie child.

    At most 1 + sum(depth) nodes are allocated; traversal visits only nodes
    and their missing children. Input processing and arbitrary-precision
    integer costs are additional to this node bound. No recursion or loop
    over the Boolean assignment space is used.
    """
    n = _integer(n, "n")
    if n < 0:
        raise ValueError("negative n")
    m = n if projected_bits is None else _integer(projected_bits, "projected_bits")
    if not 0 <= m <= n:
        raise ValueError("projected_bits outside [0,n]")
    if aux_bound is not None:
        _integer(aux_bound, "aux_bound")
        if not 0 <= aux_bound <= 1 << (n - m):
            raise ValueError("aux_bound outside representable range")
    try:
        entries = iter(prefixes)
    except TypeError as error:
        raise ValueError("prefixes must be iterable") from error

    # Each node stores child zero, child one, and terminal coverage.
    nodes = [[-1, -1, False]]
    for entry in entries:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise ValueError("prefix entry must be a pair")
        depth, prefix = (_integer(entry[0], "depth"), _integer(entry[1], "prefix"))
        if not 0 <= depth <= n or prefix < 0 or prefix.bit_length() > depth:
            raise ValueError("noncanonical prefix")
        index = 0
        for bit in range(depth):
            if nodes[index][2]:
                break
            value = (prefix >> bit) & 1
            child = nodes[index][value]
            if child == -1:
                child = len(nodes)
                nodes[index][value] = child
                nodes.append([-1, -1, False])
            index = child
        nodes[index][2] = True

    stack = [(0, 0, 0)]
    while stack:
        index, depth, prefix = stack.pop()
        if aux_bound is not None and prefix >> m >= aux_bound:
            continue
        if index == -1:
            return {"covered": False, "uncovered": prefix,
                    "trie_nodes": len(nodes), "arithmetic_verified": False}
        if nodes[index][2]:
            continue
        if depth == n:
            return {"covered": False, "uncovered": prefix,
                    "trie_nodes": len(nodes), "arithmetic_verified": False}
        stack.append((nodes[index][1], depth + 1, prefix | (1 << depth)))
        stack.append((nodes[index][0], depth + 1, prefix))
    return {"covered": True, "uncovered": None,
            "trie_nodes": len(nodes), "arithmetic_verified": False}
