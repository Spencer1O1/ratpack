---
name: rp-role
description: Create, update, or retire a project's custom Ratpack role and its native Codex agent profile. Use for role lifecycle changes, not ordinary task assignment or conversation renaming.
---

# Ratpack Role

Maintain a portable role brief in the target project's `ratpack.json` and a
matching native Codex profile in `.codex/agents/<name>.toml`. Read that project's
AGENTS.md, contributor workflow, assignment record, and relevant requirements
first. Its adopted policy and explicit user changes govern; installing this
skill does not upgrade project policy or grant delegation or merge authority.

## Scope and ownership

Inspect branch, status, worktrees, active assignments, and existing role files.
Coordinate with current owners before changing shared files. Use an isolated
branch/worktree for implementation in an occupied repository. Record the actual
owner, session/handoff route, and owned paths in the task; preserve unrelated
configuration, assignments, and uncommitted work.

Resolve the requested role's purpose, allowed work, expected outputs/evidence,
and handoff destination from the request and project guidance. Ask only for
missing decisions that materially affect scope. Keep native names stable and
unique with a `ratpack_` prefix (for example `ratpack_research`); do not
repurpose an existing profile merely because its name is useful.

## Create or update

1. Record the brief under `custom_roles` in the project's `ratpack.json`, using
   `purpose`, `allowed_work`, `expected_outputs`, `handoff`, and `native_agent`
   for a new entry. Keep existing prose/string briefs readable; migrate an entry
   only as part of its deliberate update. Preserve unrelated records, fields,
   and conventions. A role definition is separate from contributor assignments.
2. Build `developer_instructions` from that brief, including repository-scoped
   authority, owned scope, evidence, and handoff requirements. Native profiles
   require `name`, `description`, and `developer_instructions`; inherit the
   spawning parent's model, permissions, and MCP access. Do not add model,
   sandbox, permission, or account overrides.
3. Use the bundled [renderer](scripts/render_agent.py) to produce a standalone
   TOML document from JSON on stdin with exactly those three fields. It writes
   only stdout; review its output before applying it to the intended profile.
   From this skill's directory, for example:

   ```bash
   python3 scripts/render_agent.py < /tmp/role-spec.json > /tmp/role-profile.toml
   ```

4. Compare any existing destination before editing. Reconcile deliberate updates
   with its owner and preserve local instructions; do not blindly overwrite an
   unrelated or modified file. Keep the brief and native instructions consistent.
   Preserve unrelated `.codex/config.toml` settings if configuration changes are
   actually required; a role request is not permission to replace that file.
5. Parse the resulting JSON and TOML (for example with Python's `json` and
   `tomllib` on Python 3.11+) and verify required fields, name consistency, and
   intended paths. Run the project's applicable checks and inspect the final
   diff for unrelated changes. Report validation gaps accurately.

## Retire and activate deliberately

Before retirement, inspect assignments and dependencies. Hand off active work,
resolve references to the role, and agree the next owner/action before removing
its custom-role record or profile. Preserve unrelated assignments and locally
modified profiles; reconcile ownership rather than deleting them blindly.

Creating a profile does not spawn an agent, transfer integration ownership, or
authorize merges. Use the native agent name only when a separately authorized
assignment is dispatched through a host that supports it. If the host cannot
discover the profile, report that limitation and provide the same brief to an
existing human or peer conversation. Explicitly have a peer session read the
same role file and project instructions; renaming a conversation alone does not
activate the profile. Record the actual contributor and handoff route.

Finish with branch/worktree, changed role and profile paths, commit/PR when
available, checks/results, outstanding activation or ownership gaps, and the
next reviewer/integration owner action. Follow project review and release rules.
