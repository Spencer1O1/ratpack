---
name: rp-review
description: Independently review an identified Ratpack commit or PR against requirements and report findings, checks, and limitations for the exact revision. Use for requested review, not implementation or self-approval.
---

# Ratpack Review

Read the project's AGENTS.md, contributor workflow, assignment record, task
acceptance criteria, and relevant requirements/design. Apply its independence,
isolation, authority, and handoff rules; invoking this skill does not make the
implementer an independent reviewer.

1. Establish the repository, base, exact proposed head SHA, task scope,
   dependencies, and review destination. Report missing identity or acceptance
   criteria rather than certifying an unidentified change.
2. Inspect the diff and affected callers, tests, and contracts. Evaluate
   correctness, regressions, requirements, and evidence instead of relying on
   the author's summary. Keep optional cleanup separate from defects.
3. Run applicable checks when feasible. Use an isolated copy at the reviewed SHA
   for experiments that write files, caches, or build outputs. Report unavailable
   checks and distinguish simulation from actual integration/production evidence.
4. Return exact base/head, acceptance coverage, checks/limitations, and findings
   with severity, path/line, failing condition, consequence, and evidence—or an
   explicit no-findings result within the stated scope.
5. Check whether the head advanced. Return findings to the implementer and
   identify remaining unreviewed changes; recheck affected behavior on request.
   Route the final report to the integration owner at the authorized destination.

Record an external review or GitHub approval only if its actual submission
succeeded. Include any review worktree and its disposition in the handoff.
