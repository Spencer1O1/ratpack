---
name: rp-bootstrap
description: Adopt Ratpack in a new or existing project by reconciling contributor instructions, roles, GitHub/Linear setup, and devel/main branches. Use for initial setup or an explicit adoption upgrade, not routine task coordination.
---

# Ratpack Bootstrap

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
   Propose a useful concurrent implementation worker count and brief task split;
   the user may approve it or choose a different number. Record the approved
   count; there is no default of two. Until approval, keep any existing authorized
   limit and do not exceed it. A null limit means no approved count. Use bounded
   assignments from the workflow's role briefs, respect host capacity, and reuse
   existing approval. Request an increase only when useful.
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

Add `--apply` to write the previewed files. Python 3.11+ is required. The
helper does not change Git state or accounts. Complete `checks` and connection
fields in `ratpack.json` using the project's actual commands and identifiers.
Generated docs describe the adopted workflow, not proof of configured services.

Codex discovers the profiles in a trusted project. Use a fresh/reloaded session
and verify available native agent names before claiming runtime activation;
TOML parsing alone is not evidence of discovery or successful spawning.
Profiles inherit the parent's model, sandbox/approval settings, and MCP access.
Do not silently change global trust, permissions, or model settings to activate
them.

Human-created conversations remain valid. Have a peer explicitly read the same
role file and project instructions for its assignment; naming the conversation
does not activate a native profile or confer merge authority.

Finish when setup changes are reviewed/integrated and the handoff names what is
installed, what was verified, any outstanding external setup, and the next
owner/action. Do not expand setup into product implementation. Ongoing work
uses the project's adopted workflow; `rp-coordinate` provides that procedure
when available. Installing a newer skill does not upgrade an existing project.
