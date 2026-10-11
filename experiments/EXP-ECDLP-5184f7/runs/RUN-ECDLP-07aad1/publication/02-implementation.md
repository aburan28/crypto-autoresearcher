Add the frozen sampler, exact PARI curve-order audits, subgroup matching, instrumented native/opaque Pollard rho, independent 32-adding walk and memory-accounted BSGS for the Solinas-versus-random-prime comparison. Synthetic ground-truth scalars are validation-only and never enter public kernel jobs; setup, search and verification costs are separate.

Base: `run/solinas-number-fields-20261011`. Head: `run/solinas-prime-resistance-implementation-20261011`. The source freezes are fa315f9ef and 054f1988e.

Validation: 96 instrument jobs, 36 exact sham/replay/transport checks, scalar and collision-equation validation, and 10,050 modular-fold agreement cases passed. The arithmetic implementation is a Python prototype, not a production reduction-speed claim.
