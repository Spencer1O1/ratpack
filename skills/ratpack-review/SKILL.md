---
name: ratpack-review
description: Independently review an identified Ratpack commit or PR against project requirements and report findings, checks, and limitations for the exact revision. Use for requested independent review, not implementation or self-approval.
---

# Ratpack Review

Evaluate an identified revision as an independent reviewer. Read the target
project's AGENTS.md, contributor workflow, `ratpack.json`, task acceptance
criteria, and relevant requirements/design documents. The project's adopted
policy governs; installing this skill grants no merge or release authority.

## Establish the review

Resolve the repository, base revision, exact proposed head SHA, task scope,
dependencies, and review destination. Inspect branch, status, worktrees, and
current ownership before touching files. Record reviewer identity and the
session/handoff route in the task where applicable. If the proposed revision or
acceptance criteria cannot be established, report the gap instead of certifying
an unidentified change.

Independence requires a different human or agent from the implementer. An
implementer may prepare evidence but cannot turn self-review into independent
approval by invoking this skill. Use an existing reviewer when assigned. Start
another agent only within explicit delegation authorization and host capacity;
otherwise hand the identified revision and requirements to a separate reviewer.
Human-created peer conversations are valid reviewers: have them explicitly read
the same review brief and project instructions, and record their actual route.

## Inspect and verify

Inspect the actual diff and affected callers, tests, requirements, and contracts.
Evaluate correctness, regressions, acceptance criteria, and meaningful evidence.
Treat author summaries and passing checks as evidence to assess, rather than a
substitute for inspecting the change. Keep optional cleanup separate from defects.

Read-only review may use the owner's checkout. Experiments that alter files,
dependencies, caches, or build outputs require an isolated worktree/copy at the
identified SHA. Never switch, reset, stash, clean, or edit the author's checkout.
Run applicable project checks when feasible and report exact commands, results,
and untested behavior. Do not infer configured protections, production readiness,
or successful external integrations from simulation or generated configuration.

Do not implement fixes on the author's branch. Return actionable findings to
the implementer; proposed repairs remain subject to normal task ownership and
review. Recheck affected behavior after a revision, naming the newly reviewed
SHA. Findings or approval of an older SHA do not cover later changes. Before
handoff, check whether the proposed head advanced; if so, identify the remaining
unreviewed revision clearly.

## Report and hand off

Return the repository/PR, base and exact reviewed head SHA, acceptance coverage,
and either actionable findings or an explicit no-findings result. Each finding
includes severity, path/line, the failing condition, consequence, and supporting
reasoning or reproduction. Distinguish blocking findings from optional cleanup.
List checks/results, unavailable checks, assumptions, and remaining limitations;
no findings means no defects found within that stated scope.

Use the authorized review destination. Preparing a review does not itself grant
permission to post externally. A local report or agent review does not manufacture
a required GitHub approval; only report an approval as recorded when the actual
authorized review submission succeeded. Report missing access or branch-protection
requirements accurately.

Hand findings back to the implementer, or a no-findings result to the project's
integration owner with remaining checks/approvals. Include any review worktree
and its disposition. Do not merge, grant authority, approve a release, or mark
implementation Done merely because review completed.
