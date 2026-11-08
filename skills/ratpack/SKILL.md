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
   and existing authorization. Starting a Ratpack does not silently grant
   spawning, publishing, or release authority. If the user explicitly permits
   implementation delegation, record the worker limit (default two) and use
   bounded tasks; do not request the same permission again within that scope.
4. Prepare `ratpack.json`, contributor/agent guidance, and a short PR template.
   The helper below previews or installs starter files only when they will not
   overwrite different content. With existing docs, reconcile manually into
   their owning files and retain one canonical workflow. Do not replace a
   project's entire AGENTS.md or create a competing contributor guide.
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

Add `--apply` to write the previewed files. Python 3.10+ is required. The helper
does not change Git state or accounts. Complete `checks` and connection fields
in `ratpack.json` using the project's actual commands and identifiers. Generated
docs describe the adopted workflow, not proof of configured services.

## Coordinate an existing Ratpack

Read the project's own instructions and assignment record; its adopted version
and explicit user changes take precedence over newer upstream defaults. Plan
atomic tasks before dispatching workers. Freeze shared contracts and assign one
writer per overlapping area. Delegate useful implementation within the recorded
authorization; if the host lacks subagents, give equivalent briefs to existing
contributors and report the limitation.

Keep Linear tasks and PR evidence current, including the exact reviewed commit.
Route PRs to the independent reviewer and sole integration owner. Respect manual
tracking while integrations are pending. Finish with a durable handoff; do not
mark work Done because a worker returned successfully or a branch passed CI.
