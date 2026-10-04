# Received text (verbatim)

Provenance: pasted into a Claude Code session by the repository owner on
2026-09-08. No author, publisher, URL, or date was supplied with it. The bytes
below are frozen exactly as received, with no editing, reflowing, or
correction. The trailing sentence is truncated in the source as received.

---

We used a system of coordinating agents powered by our internal model. The agents had access to tools such as the ability to read from a cached version of the internet and the ability to run code. Agents were subdivided into groups with the ability to communicate within the group. The groups varied in size, and the group that produced the Navier–Stokes resolution involved on the order of 10,000 concurrent agents. At all times we maintained the same strict safeguards that we apply to all our frontier model evaluations, including monitoring and isolation.
For each problem, we prompted different groups of agents with different variants of the problem statement, covering all variants of the problem. For the Navier–Stokes problem, we suggested versions “A” and “B” (particular forms of the Navier–Stokes problem which would result in a proof) and versions “C” and “D” (which would result in a disproof) to separate groups of agents.
In addition to the full Millennium Prize problems, we asked our multiagent system to try a set of “easier” problems. One of these problems was a similar blowup question for the limit of the Navier–Stokes problem with the viscosity term removed. This is known as the regularity problem for the Euler equations, and our agents surprised us by resolving this question. The specific variant of the question that they resolved was the unforced version, where no external force is applied to the fluid. Nearly 100 agents worked together for approximately 50 hours to produce our Euler regularity disproof.1
Once we saw the Euler solution, we thought that Navier–Stokes was the most promising problem to work on. Thus, we decided to devote our resources to Navier–Stokes. To do so, we shifted agents away from the other Millennium Problems and prompted these agents with the Euler resolution. When a further trained version of our internal model became available over the course of the effort, we updated our agents to that model.
We encouraged different groups of agents to explore a diversity of approaches. After some time, we cross-pollinated the agent groups by using Codex to consolidate the most useful insights from each agent group. These follow-up prompts drew on the agents’ own intermediate results. The group that found the solution to Navier–Stokes was guided in such a way.
The agents arrived at their resolution on Saturday, September 5, about 88 hours after the first agents were launched. Lean formalization and verification took an additional 17 hours via GPT‑6 Astra.
Across all attempted problems, the agents sent 4.9 million messages and used about 300 billion output tokens. In the process of resolving the Navier–Stokes problem, the agents sent 2.7 million messages and used approximately 130 billion output token
