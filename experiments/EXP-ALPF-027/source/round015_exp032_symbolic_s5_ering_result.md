# EXP-032 Result: symbolic S5 e-ring true degree

Verdict: **inconclusive**

meter_self_validated: False

## Fixtures

- POS-A: {'fires': False, 'gate_meaningful': False, 'd_ff': None, 'D_reg': 4, 'expect_fire': True, 'expect_gate_meaningful': True, 'ok': False}
- NEG-1: {'fires': False, 'gate_meaningful': False, 'd_ff': None, 'D_reg': 3, 'expect_fire': False, 'expect_gate_meaningful': False, 'ok': True}
- e-ring-m3: {'fires': False, 'gate_meaningful': False, 'd_ff': None, 'D_reg': None, 'expect_fire': True, 'expect_gate_meaningful': False, 'ok': False}
- POS-C-WeilS3: {'fires': False, 'gate_meaningful': False, 'd_ff': None, 'D_reg': None, 'expect_fire': True, 'expect_gate_meaningful': True, 'ok': False}

## S5 genuineness

- s5_genuine (vanishes on real 5-tuples summing to O): None
- true per-variable degree: None (expected 8 = 2^(m-1), m=4)
- total degree: None

## e-ring leading form

```
None
```

## Gated meter at true degree

- meter: None
- crossbred admissible D<D_reg cuts: None
- any gate_meaningful fall: None

## Does NR-027 hold at true degree?

- nr027_holds_at_true_degree: None

Meter did not self-validate; cannot trust downstream meter readings.

## Notes

- Meter failed inline self-validation on >=1 of 4 fixtures -> INCONCLUSIVE per protocol.

elapsed_sec: 4.67
