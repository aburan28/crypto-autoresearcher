"""Streaming two-endpoint incidence reduction; imports run no calculation."""
import heapq


class WitnessDAG:
    def __init__(self, modulus):
        self.modulus = modulus
        self.nodes = []

    def leaf(self, index):
        self.nodes.append({"input": index})
        return len(self.nodes) - 1

    def combine(self, terms):
        terms = [[c % self.modulus, node] for c, node in terms
                 if c % self.modulus]
        self.nodes.append({"terms": terms})
        return len(self.nodes) - 1

    def expand(self, node):
        # Descending node order accumulates every parent before a child is
        # visited. No dense vector is cached at every internal DAG node.
        coefficients, queued = {node: 1}, {node}
        heap, answer = [-node], {}
        while heap:
            current = -heapq.heappop(heap)
            queued.remove(current)
            scale = coefficients.pop(current, 0) % self.modulus
            if not scale:
                continue
            record = self.nodes[current]
            if "input" in record:
                at = record["input"]
                answer[at] = (answer.get(at, 0) + scale) % self.modulus
            else:
                for factor, child in record["terms"]:
                    assert child < current
                    coefficients[child] = (coefficients.get(child, 0) +
                                           scale * factor) % self.modulus
                    if child not in queued:
                        heapq.heappush(heap, -child)
                        queued.add(child)
        return {i: c for i, c in answer.items() if c}


class SparseReducer:
    """Column reduction with sparse pivots and exact row-combination DAGs."""
    def __init__(self, modulus):
        self.modulus = modulus
        self.pivots = {}
        self.dag = WitnessDAG(modulus)
        self.outputs = []
        self.processed = 0
        self.reductions = 0
        self.max_support = 0
        self.trace = []

    def append(self, outside):
        modulus, index = self.modulus, self.processed
        vector = {str(k): int(c) % modulus for k, c in outside.items()
                  if int(c) % modulus}
        if len(vector) > 2:
            raise ValueError("More than two aggregated outside endpoints")
        expression = self.dag.leaf(index)
        while any(k in self.pivots for k in vector):
            vertex = min(k for k in vector if k in self.pivots)
            factor = vector[vertex]
            pivot, witness = self.pivots[vertex]
            for key, value in pivot.items():
                vector[key] = (vector.get(key, 0) - factor * value) % modulus
                if vector[key] == 0:
                    vector.pop(key)
            expression = self.dag.combine([(1, expression), (-factor, witness)])
            self.reductions += 1
            assert len(vector) <= 2
        self.max_support = max(self.max_support, len(vector))
        if vector:
            vertex = min(vector)
            inverse = pow(vector[vertex], -1, modulus)
            vector = {k: c * inverse % modulus for k, c in vector.items()}
            expression = self.dag.combine([(inverse, expression)])
            self.pivots[vertex] = (vector, expression)
            assert all(k >= vertex for k in vector)
            emitted = False
        else:
            self.outputs.append(expression)
            emitted = True
        self.processed += 1
        self.trace.append({"input": index, "outside_rank": len(self.pivots),
                           "kernel_dimension": len(self.outputs),
                           "emitted": emitted, "reductions": self.reductions})

    def result(self):
        witnesses = [self.dag.expand(node) for node in self.outputs]
        for witness in witnesses:
            assert witness[max(witness)] == 1
        return {"input_rows": self.processed,
                "outside_rank": len(self.pivots),
                "kernel_dimension": len(witnesses),
                "witnesses": witnesses,
                "output_nodes": list(self.outputs),
                "dag": self.dag.nodes,
                "trace": self.trace,
                "stats": {"reductions": self.reductions,
                          "dag_nodes": len(self.dag.nodes),
                          "dag_arcs": sum(len(n.get("terms", []))
                                          for n in self.dag.nodes),
                          "active_pivot_entries": sum(len(v)
                              for v, _ in self.pivots.values()),
                          "max_pivot_nonzeros": self.max_support,
                          "expanded_witness_terms": sum(map(len, witnesses))}}


def combine_rows(rows, coefficients, modulus):
    answer = {}
    for index, factor in coefficients.items():
        for key, value in rows[int(index)].items():
            answer[key] = (answer.get(key, 0) + factor * value) % modulus
    return {key: value for key, value in answer.items() if value}


def centered_lift(coefficients, modulus):
    return {int(i): int(c) if int(c) <= modulus // 2 else int(c) - modulus
            for i, c in coefficients.items()}


def reduce_rows(rows, base, modulus):
    base = set(base)
    reducer = SparseReducer(modulus)
    for row in rows:
        reducer.append({key: c for key, c in row.items() if key not in base})
    result = reducer.result()
    outside = sorted({key for row in rows for key in row if key not in base})
    cancelled, quotients = [], []
    for witness in result["witnesses"]:
        value = combine_rows(rows, witness, modulus)
        assert all(key in base for key in value)
        cancelled.append(value)
        lift = centered_lift(witness, modulus)
        integer_sums = {key: sum(c * rows[i].get(key, 0)
                                for i, c in lift.items()) for key in outside}
        assert all(value % modulus == 0 for value in integer_sums.values())
        quotients.append({key: value // modulus
                          for key, value in integer_sums.items() if value})
    result.update(outside_columns=outside, base_columns=sorted(base),
                  cancelled_rows=cancelled,
                  outside_integer_lift_quotients=quotients)
    return result
