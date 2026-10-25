# Insight: lazy Coordinator import preserves control execution

The phased wrapper module loaded `study_admission` before checking whether the
trial was in control mode. A dedicated control environment with `psutil` and
`sympy` but without PyYAML therefore stopped before input verification. Moving
the import into the scientific study-admission branch let the same eight-target
control complete without weakening the scientific gate. The checked retry
matched the independent ordered-count output and retained zero useful targets
for this fixed eight-target input. No scientific yield inference follows.
