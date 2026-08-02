# Mandatory Regression Suite Substitution

The independent Red Team replaced all 26 artifact-supplied mandatory controls
with 26 copies of a trivial unknown-record rejection. The unchanged verifier
still reported 26/26 passes because it does not pin regression IDs, operations,
or expected reasons independently.

```text
artifact: e0061d15975d2532435c8a991af51ea8113f242fdb13994e81facb28f8dbe3d5
receipt:  92e92566908ebece8ee04c03cf8a7c3ac69ee4f36428f701973fda0cf557cc62
```
