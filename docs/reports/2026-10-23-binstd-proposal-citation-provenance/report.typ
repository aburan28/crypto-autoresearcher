#set page(width: 210mm, height: 297mm, margin: 18mm)
#set text(font: "DejaVu Sans", size: 10pt)

= BINSTD proposal citation provenance correction

Two archived adaptation proposals cited the internal card KR-IC-73db3f as
``recalled``. The complete card was read on 2026-10-23. It labels its
small-product-space statement a heuristic and lists four upstream sources
read only at abstract level.

#image("citation-graph.svg", width: 100%)

The additive replacements for IDEA-20261003-94078e and
IDEA-20261003-c9c6c3 change only citation 4. They identify the card as an
internal source, name Codex as reader, and restrict the claim to the card's
heuristic scope. The archived originals, experiments, measurements and
decisions are unchanged. A focused parsed-field and SHA-256 comparison passed.

A complete-tree validator comparison on parent f7408a231b and corrected head
6c08b90468 reported 120 to 118 unsuppressed errors in the same 36 paths.
Only the two cited proposal errors disappeared; none was added. Both runs
exited 1 and the 1,210-entry legacy baseline was unchanged.

The full ledger gate is still open. This correction does not establish a
published theorem or any solver performance gain. No prior canonical graph
mentioned either proposal or the card; the diagram above is the new derived
view of this provenance correction.
