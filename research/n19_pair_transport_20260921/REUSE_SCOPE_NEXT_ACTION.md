# Next cost question: reuse within one cold target job

This is a proposed follow-up design boundary, not a new experiment or a timing result.

P8 measures a single point-decomposition query in a fresh native process, including a newly built pair table. A cold single-target IC job can build its factor base and pair table once, then reuse them across the relation attempts needed for that same target. That is legitimate reuse within the cold job, even though reuse across independent targets would be a different cost model.

For a frozen list of M public synthetic point-decomposition queries, the relevant accounting is

    total = startup + base construction + representation preparation
            + table construction
            + sum over M of (query + canonicalization + witness transport + verification)
            + final output.

The P8 construction advantage therefore cannot be multiplied by M. Conversely, per-query canonicalization and transport are paid on every attempt and must be summed. Separate medians of stages or of different arms do not determine this total or its crossover.

A useful next contract should freeze a target-independent finite query list, a same-base expanded comparator and the exact job boundary before any timings. Each fresh job constructs its own table once and processes the whole list in the same order. Record one-query and repeated-query regimes separately; retain every no-decomposition decision, exact witness, construction cost, memory measurement and process overhead. Technical replicates must not be counted as new targets. A larger field/base should be selected for a concrete integration question, not by extrapolating the N19 percentage.

This follow-up would test whether the new representation remains useful under the reuse pattern of cold single-target relation collection. It still would not measure full IC versus rho unless the complete relation-generation, linear algebra, target determination and matched comparator are included in a separately approved experiment. The previous IC/rho result remains unchanged.

Provenance: internal cost-model reasoning from the frozen P8 measurement definition and prior cold IC decomposition of setup and query costs. The Coordinator chooses the next contract after independent P8 review; no new runs or official state changes are authorized here.
