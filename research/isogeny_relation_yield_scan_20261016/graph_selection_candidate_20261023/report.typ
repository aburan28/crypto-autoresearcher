#set page(paper: "a4", margin: 20mm)
#set text(font: "Helvetica", size: 10pt)
= Discovery selector implementation control

2026-10-22. This candidate code nominates confirmation vertices only after
every scheduled discovery arm has a hash-bound supervisor receipt and the
independent checker succeeded. It checks prepared curve identity and paired
target coefficients across arms. An incomplete or tampered run stops selection.

#image("selection_flow.svg", width: 100%)

Three synthetic tests passed: full schedule shape, tie breaking and coverage;
and one supervisor receipt with an altered raw result rejected. These tests do not supply
scientific yield, confirmation intervals, or ECDLP costs. The Coordinator
must freeze the implementation and control-index root commitment in an
approved runnable contract before the fixed discovery stream is collected.
