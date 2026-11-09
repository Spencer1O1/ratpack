---
name: rp-coordinate
description: Plan and coordinate an adopted Ratpack project's tasks, workers, review, and integration. Use for ongoing project coordination, not initial setup or isolated implementation work.
---

# Ratpack Coordinate

Read the project's AGENTS.md, linked contributor workflow, `ratpack.json`,
this developer's ignored `ratpack.local.json`, shared task queue/handoff, and
relevant requirements. Follow the adopted policy and explicit user decisions. If setup or ownership is missing, identify the gap
and resolve it before dispatch; do not install or upgrade policy as a side effect.

1. Reconcile tracker tasks, active contributors, worktrees, PRs, and current CI.
   Resolve stale ownership and dependencies against their authoritative records.
2. Establish accepted product scope from human instructions/decisions; separate
   agent proposals before assigning work under the workflow's planning rules.
   Turn the agreed outcome into bounded tasks. Apply this pack's staffing
   and ordering rules, record decisions, and assign eligible work with clear
   ownership, interfaces, acceptance evidence, and handoff routes. Select and
   apply task-appropriate model/effort using [dispatch guidance](references/model-routing.md);
   record requested versus effective settings and reassess when work changes.
3. Collect results and arrange independent review. Check the current revision
   and evidence against acceptance; return findings to the assigned implementor.
4. Hand reviewed work to the project's designated integration owner; integrate
   only if that authority was separately assigned to you. Update tracker state
   from verified outcomes and reconsider the queue after each handoff/merge.
5. Continue eligible authorized work while active. Finish with integrated results,
   open blockers/decisions, and the next owner/action recorded durably.

Preserve existing human-created peers. Report unavailable host or integration
capabilities rather than claiming dispatch, automation, or setup succeeded.
