# Successive-lift software validation

Three fixtures with six, six and eight Boolean variables completed a dense degree-three seed followed by native lifts to degrees four and five. All nine maps passed the original independent checker, and their checked codimensions matched independent direct dense calculations at the corresponding degrees. See `cascade-20261029-v2/receipt.json` for artifact and instrument hashes and individual stage transcripts.

The complete campaign driver also completed descent, fresh exact count, D3 production/check, D4 lift/check and D5 lift/check on the retained `cascade-pipeline-20261029` control. Its exact solution count and all checked codimensions equal one, and it correctly emitted no LFD lower bound.

The initial fixture had only four Boolean variables and was refused at the D4-to-D5 transition because the seed degree equalled the variable count. That attempt remains in `cascade-20261029`; the corrected fixtures have enough variables. No producer guard was relaxed.

These are software controls, not frontier measurements, asymptotic bounds or timing evidence. Frontier science is governed separately by `../cascade-protocol.json`.
