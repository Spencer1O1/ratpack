---
name: ratpack
description: Bootstrap or coordinate the Ratpack workflow for projects using implementation agents, independent review, Linear, and GitHub with devel/main branches. Use when asked to set up or run a Ratpack, not for unrelated coding or generic Git questions.
---

# Ratpack

Read [the shared workflow](references/workflow.md). It is the human-facing
policy to install in the project. Roles are generic; never import another
project's names, account identifiers, requirements, or production settings.

## Bootstrap

1. Inspect the target repository's instructions, status, worktrees, branches,
   remotes, checks, and current task ownership. Preserve existing work. Use an
   isolated branch/worktree for setup in an occupied repository.
2. Reuse existing GitHub/Linear connections. Discover the actual repository,
   team, projects, statuses, labels, and issues before creating anything. Ask
   only for missing decisions you cannot discover. Do not assume a connection
   can edit every setting; record unavailable operations accurately.
3. Agree on the integration owner and delegation scope from the user's request
   and existing authorization, including support/review agents. Starting a
   Ratpack does not silently grant spawning, publishing, or release authority.
   If the user explicitly permits delegation, record the implementation worker
   limit (default two) and use bounded assignments from the workflow's role
   briefs. Respect host capacity; do not request permission again within the
   already authorized scope.
4. Prepare `ratpack.json`, contributor/agent guidance, a short PR template, and
   the five native Codex profiles under `.codex/agents/`.
   The helper below previews or installs starter files only when they will not
   overwrite different content. With existing docs, reconcile manually into
   their owning files and retain one canonical workflow. Do not replace a
   project's entire AGENTS.md or create a competing contributor guide. Existing
   native profiles also require deliberate reconciliation; never overwrite them
   merely to adopt Ratpack.
5. Require `devel` for integration and `main` for releases. Prepare any necessary
   migration without rewriting history. New repository initialization and
   external writes follow the user's actual authorization. Configure default
   branch, merge options, protections, and Linear conventions where supported.
   Never claim unavailable protections or untested automation are enabled.
6. Validate links, check commands, assignments, and applicable CI. Hand setup
   changes to independent review and the integration owner. Report what is
   installed, what is verified, and the specific remaining external setup.

From this skill's directory, preview starter files in an existing project:

```bash
python3 scripts/bootstrap.py /path/to/project --owner coordinator-name
```

Add `--apply` to write the previewed files. Python 3.11+ is required. The helper
does not change Git state or accounts. Complete `checks` and connection fields
in `ratpack.json` using the project's actual commands and identifiers. Generated
docs describe the adopted workflow, not proof of configured services.

Codex discovers the profiles in a trusted project. Use a fresh/reloaded session
and verify available native agent names before claiming runtime activation;
TOML parsing alone is not evidence of discovery or successful spawning. Profiles
inherit the parent's model, sandbox/approval settings, and MCP access. Do not
silently change global trust, permissions, or model settings to activate them.

Human-created conversations remain valid. Have a peer explicitly read the same
role file and project instructions for its assignment; naming the conversation
does not activate a native profile or confer merge authority.

## Coordinate an existing Ratpack

Read the project's own instructions and assignment record; its adopted version
and explicit user changes take precedence over newer upstream defaults. Plan
atomic tasks before dispatching workers. Use the shared workflow's hierarchy and
role briefs: coordinator as the persistent root, implementation/review subagents,
cleanup/workflow support as needed. Preserve existing peer conversations when
they already fill these roles. Freeze shared contracts and assign one
writer per overlapping area. Delegate useful implementation within the recorded
authorization; if the host lacks subagents, give equivalent briefs to existing
contributors and report the limitation.

Apply the shared workflow's [request-ordering rules](references/workflow.md#requests-and-ordering)
to every role. Create/reuse a bounded task for actual work, record its start
condition, and turn relative requests such as "after current tickets" into an
explicit snapshot of IDs. Use tracker dependencies; do not let future tickets
silently extend the snapshot. Check ownership, prerequisites, authorization,
and capacity before dispatch. "Now" is a priority request, not a bypass.

Reconcile the queue after handoffs/merges and on resume. Continue authorized
ready work while active; do not mark queued work started or complete. A stopped
coordinator is not awakened by a tracker relation alone. Honor deferred scope
for audits, research, docs, and custom roles as well as implementation. Report
concrete blockers, missing tracking access, or any unconfigured time automation.
Non-code deliverables need explicit acceptance; repository changes still need
review, checks, and merge before Done.

Keep role and merge assignments scoped to the target repository. When the human
defines a new role, record its purpose, scope, outputs/evidence, and handoff in
the project's `custom_roles` record before assignment. Use that brief within
existing authorization; a new role name does not grant merge/spawn authority.
Do not inject unrelated projects' agent identities or upstream planning into
the project's working context.

Keep Linear tasks and PR evidence current, including the exact reviewed commit.
Route PRs to the independent reviewer and sole integration owner. Respect manual
tracking while integrations are pending. Finish with a durable handoff; do not
mark work Done because a worker returned successfully or a branch passed CI.
