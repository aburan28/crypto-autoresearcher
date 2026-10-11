# SNFS-G1 cyclotomic-trace design audit

Task: `TASK-20261010-8d7af0`  
Idea: `IDEA-20261009-57140c`  
Parent hypothesis: `H-ECDLP-bd1572`  
Idea status: `proposed`; approved: `false`

## Repository evidence and scope

The idea and the directly relevant `EXP-ECDLP-3e8403` experiment/specification
records support treating SNFS-G1 as distinct only for the following additional
objects and certificates: cyclotomic subfields; complete-splitting
certificates; Galois-trace rows; independent trace rank; and certified
`E(K)/E(Q)` rank intervals. The residue-coverage/gamma portion overlaps
`EXP-ECDLP-3e8403`; it must be reused from that work or removed here, not
duplicated. The absence of runs is not a result and supports no inference.

This audit records design requirements only. The repository records above are
not being changed, and no future measurement is implied by this review.

## Minimum repairs before approval

The proposal must add, with reproducible receipts:

- exact fields, subfields, bases, and embeddings;
- explicit curve, rank, torsion, and good-reduction receipts;
- complete-splitting and residue-map certificates for both special and random
  fields;
- the exact trace relation, including torsion handling;
- shared coverage conventions with `EXP-ECDLP-3e8403`;
- reproducible same-`p` random-field controls;
- deterministic height enumeration and explicit censoring rules;
- two-sided rank certification;
- fixed budgets and stopping rules;
- raw artifacts and replay receipts; and
- a finite claim ceiling: no asymptotic conclusion and no ECDLP conclusion.

Approval remains false until these repairs are specified sufficiently for an
independent implementation and replay. Any later observations must be labeled
as measurements with their exact finite scope; they cannot be promoted beyond
that ceiling without separate evidence and review.
