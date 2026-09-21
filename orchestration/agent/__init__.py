"""The `api_direct` runtime: role contracts executed through a LangGraph loop.

Claude Code and the Codex CLI bring their own tool loop; this package is the
one for everything else, so a role can run against any backend in
`orchestration/model-bindings.yaml`.

Requires `langgraph` and `langchain-core` (see `requirements-agent.txt`). The
adapter core does not -- resolution, transport, and manifests stay dependency
free, and importing this package is the only thing that pulls LangGraph in.
"""
