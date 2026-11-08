---
name: ratpack-cleanup
description: Audit a bounded Ratpack project area for maintainability problems or implement requested, focused cleanup fixes. Use for scoped cleanup work, not speculative redesign or unrelated behavior changes.
---

# Ratpack Cleanup

Read the target project's AGENTS.md, contributor workflow, `ratpack.json`, task
brief, and relevant requirements/design documents. Follow its adopted policy,
task order, and coordinator assignments. Do not begin a deferred audit or its
fixes before the recorded start condition is satisfied. This skill grants no
new spawning, merge, release, or repository authority.

## Establish the assignment

Resolve the bounded area, expected deliverable, acceptance criteria, owned
paths, dependencies, checks, and handoff destination from the request and task.
An audit-only assignment ends with findings; a cleanup assignment may include
reasonable bounded fixes within its authorized scope without asking again for
each small edit. Keep redesign, new features, and unrelated behavior changes
outside that scope and return them to the coordinator.

Inspect branch, status, worktrees, and existing task ownership before work.
Coordinate overlapping paths with their owners and preserve their uncommitted
work. Code-writing cleanup consumes implementation capacity: coordinate the
project's worker limit and assignment before editing, rather than treating the
cleanup role as extra capacity. Human-created cleanup peers are valid owners;
record the actual contributor and handoff route, and have the peer explicitly
read the same role/task brief and project instructions. Record agent identity
and session route in task notes where applicable; do not spawn duplicate work.

## Inspect and prioritize

Inspect the assigned area's callers, contracts, tests, and local conventions.
Prefer concrete evidence of confusing structure, duplication, dead paths, or
maintenance cost over personal style preferences or hypothetical future needs.
For each meaningful finding, identify its location, evidence, impact, priority,
and a bounded improvement. Distinguish confirmed problems from uncertainty and
optional polish. A report with no findings is a valid result within its stated
scope and limitations.

Reuse an existing task when it covers the work. Route meaningful follow-up work
through the coordinator and the project's tracker process; group related
findings into coherent tasks rather than opening a ticket for every tiny smell.
When integrations are unavailable, hand off the findings and tracking gap
accurately instead of claiming tasks were created. Findings do not silently
expand the current assignment or bypass its scheduling constraints.

## Implement and verify when requested

Use a separate implementation branch/worktree and keep one implementation task
active at a time. Read-only inspection may use the owner's checkout; experiments
that change files or build outputs need an isolated copy. Never switch, reset,
stash, clean, or stage unrelated work in another contributor's checkout.

Make coherent, small changes that preserve required behavior and project
conventions. Keep broader discoveries in the handoff rather than growing the
diff. Run checks appropriate to the touched behavior and project requirements;
record exact commands, results, and unverified areas. Do not manufacture tests
or broad refactors merely to give an audit a code artifact.

## Hand off

For an audit, report the inspected scope/revision, prioritized findings or an
explicit no-findings result, evidence, checks, limitations, and next owner/action.
The accepted report can complete an audit/report-only task; fixes discovered by
the audit remain separately tracked work.

For changes, hand off branch/worktree, commit/PR, scope, checks/results, remaining
findings, and the next reviewer/integration owner action. Use a focused PR into
`devel` under the project's workflow. Independent review by a different human or
agent is required; a cleanup author cannot approve their own implementation.
Only the assigned integration owner merges. Repository-change tasks become
Done after merge with required evidence, not when the cleanup worker finishes.
