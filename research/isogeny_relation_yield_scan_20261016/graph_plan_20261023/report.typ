#set page(paper: "a4", margin: 18mm)
#set text(font: "Helvetica", size: 9pt)
#set heading(numbering: "1.")
= Study-level graph admission implementation control

2026-10-23, Conductor tasks T-4830, T-4834 and T-4838. This is an executor-admission
and trial-plan implementation control. It records guard behavior; it makes no relation-yield,
rank or ECDLP claim and grants no Coordinator approval.

#image("diagram.svg", width: 100%)

The runner now supports a single study admission binding the complete P29/P37
schedule, both graph commitments and shared roots, frozen source commit and
hashes, collector binaries, and experiment output prefix. Before each arm's
collector starts, the runner replays the schedule row and prepared binding.
Transported-base rows also check their checkpoint, chain manifest and terminal
checkpoint hashes.

Controls rejected candidate status, a non-Coordinator approver, an unknown
schema, and malformed or unauthorized execution stages. The trial adapter
passes the prepared-arm binding to study-admitted arms, and its checker
independently recomputes the admission identity and materializer binding.
Three full-quota P37 vertex-zero prepared inputs continue to pass group-law
replay, including rejection of a modified transport checkpoint. The new
compiler emits 8,206 discovery trials; its plan passes the repository's actual
execution-plan loader, including dependency ordering and source bindings. This
is plan compatibility only. A second full 8,206-row candidate fixture passes
the same loader in candidate-readiness mode and is refused by its default
execution mode. A separate candidate-only path writes a
`candidate-trial-plan.json` for a frozen, unapproved `review_required`
specification. An explicit newest-experiment query reports it ready only when
all rows validate; default selection omits candidates. The execution loader
and public runner refuse candidate plans, and approval requires a fresh
approved plan and dispatch queue. Focused tests exercise readiness and refusal.
Both plan paths bind `stop_on_invalid_output: true`: the supervisor stops on
the first invalid arm certificate while preserving its receipt. Timeouts and
infrastructure failures retain their separate statuses.

Confirmation and finalist solve streams still need independent roots. No
scientific roots, canonical frozen experiment, or relation outputs are present.
