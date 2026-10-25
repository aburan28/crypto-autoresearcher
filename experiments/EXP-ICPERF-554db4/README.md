# Binary m8 sorted-input diagnostic

The experiment remains `review_required`, with `approved_by: null`,
`execution_authorized: false`, and `frozen: false`.

Read the [2026-10-19 review correction](review-corrections/20261019-sorted-exception.md)
with the current [specification](specification.yaml). A valid unsorted witness
can acquire an unrepresentable intermediate point after sorting. The current
specification restricts the eligible domain and records that unrestricted
witness preservation is false. The two planned positive controls still pass
their static checks; their solver feasibility remains unmeasured.

The design and implementation snapshot receipts bind their original commits.
Those receipts and the archived hypothesis remain unchanged. Review plans that
pin the earlier specification require a new Coordinator binding before dispatch.
