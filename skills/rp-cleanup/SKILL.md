---
name: rp-cleanup
description: Audit a bounded Ratpack project area for maintainability problems or implement requested focused cleanup fixes. Use for scoped cleanup, not speculative redesign or unrelated behavior changes.
---

# Ratpack Cleanup

Read the project's AGENTS.md, contributor workflow, assignment record, task,
and relevant requirements. Apply its ownership, scheduling, capacity, review,
and handoff rules to the whole assignment, including an audit phase.

1. Establish the area, deliverable (audit or fixes), acceptance criteria, owned
   paths, dependencies, and handoff destination. Inspect current ownership and
   worktrees; coordinate overlaps before editing.
2. Inspect callers, contracts, tests, and conventions. Identify concrete
   readability, organization, duplication, dead-code, or maintenance problems.
   Prioritize by evidence and impact; distinguish uncertainty and optional polish.
3. For audit-only work, return findings or an explicit no-findings result with
   scope/revision, evidence, limitations, and next action. Route follow-up work
   through the coordinator, grouping coherent fixes rather than tiny tickets.
4. For requested fixes, make bounded changes in the task's isolated worktree.
   Preserve required behavior; return broader redesign to planning. Run checks
   appropriate to the change, not manufactured tests or refactors to pad an audit.
5. Hand off the report or focused PR with checks/results, remaining findings,
   and next owner/action. Apply the project's acceptance process to the actual
   deliverable; discovering fixes does not silently expand an audit assignment.
