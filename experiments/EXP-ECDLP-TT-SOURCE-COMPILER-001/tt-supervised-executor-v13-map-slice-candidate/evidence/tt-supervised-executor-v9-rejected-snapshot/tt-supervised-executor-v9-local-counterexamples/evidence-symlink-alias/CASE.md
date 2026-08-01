# Intermediate Evidence Symlink Alias

The independent Red Team rewrote evidence resolution through an in-bundle
intermediate symlink alias. The unchanged verifier accepted the alias and
returned:

```text
artifact: d86c360e83d3e1ec8defcd2320962becad9f60cc23980a700a2acd91c018fb22
receipt:  7e5958c18be596420b911da83eec8d39483afe25b2df25f627cb2352e1c6bf16
```

The mutation script reproduces the filesystem alias on a fresh mutable V9 copy.
