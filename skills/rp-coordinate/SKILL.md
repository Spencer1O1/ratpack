---
name: rp-coordinate
description: Run an adopted Ratpack project through task planning, staffing proposals, authorized delegation, dependency management, review, and integration. Use for ongoing coordination, not initial setup or unrelated coding tasks.
---

# Ratpack Coordinate

Coordinate within the target project's adopted policy and actual authority.
This skill does not install starter files, configure accounts, or silently
upgrade project policy. If required workflow or ownership records are missing,
identify the setup gap before dispatch; use `rp-bootstrap` for requested setup
when available, or reconcile the project's existing instructions explicitly. No
sibling skill is required to coordinate an already configured project.

Read the project's AGENTS.md, linked contributor workflow, `ratpack.json`,
current tasks/handoff, and relevant requirements. Its adopted version and
explicit user changes take precedence over newer upstream defaults. Propose a
useful concurrent implementation count and task split when approval is missing
or an increase would help; the human approves or adjusts it. Record the answer
and reuse existing authorization within host capacity. A null count is
unapproved, not unlimited. Plan atomic tasks before dispatching workers. Use
the project's hierarchy and role briefs: coordinator as the persistent root,
implementation/review subagents, cleanup/workflow support as needed. Preserve
existing peer conversations when they already fill these roles. Freeze shared
contracts and assign one writer per overlapping area. Delegate useful
implementation within the recorded authorization; if the host lacks subagents,
give equivalent briefs to existing contributors and report the limitation.

Apply the project's adopted request-ordering rules to every role. Create/reuse
a bounded task for actual work, record its start condition, and turn relative
requests such as "after current tickets" into an explicit snapshot of IDs. Use
tracker dependencies; do not let future tickets silently extend the snapshot.
Check ownership, prerequisites, authorization, and capacity before dispatch.
"Now" is a priority request, not a bypass.

Reconcile the queue after handoffs/merges and on resume. Continue authorized
ready work while active; do not mark queued work started or complete. A stopped
coordinator is not awakened by a tracker relation alone. Honor deferred scope
for audits, research, docs, and custom roles as well as implementation. Report
concrete blockers, missing tracking access, or any unconfigured time
automation. Non-code deliverables need explicit acceptance; repository changes
still need review, checks, and merge before Done.

Keep role and merge assignments scoped to the target repository. When the human
defines a new role, record its purpose, scope, outputs/evidence, and handoff in
the project's `custom_roles` record before assignment. Use that brief within
existing authorization; a new role name does not grant merge/spawn authority.
Do not inject unrelated projects' agent identities or upstream planning into
the project's working context.

Follow the project's communication rules: normal word spacing, exact
identifiers, linked authoritative records, and acknowledgment of ownership or
authority transfers. Resolve ambiguous/truncated messages against their source
before acting; a forwarded summary is not verification.

Keep Linear tasks and PR evidence current, including the exact reviewed commit.
Route PRs to the independent reviewer and sole integration owner. Respect
manual tracking while integrations are pending. Finish with a durable handoff;
do not mark work Done because a worker returned successfully or a branch passed
CI.
