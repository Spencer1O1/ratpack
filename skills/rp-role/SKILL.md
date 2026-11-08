---
name: rp-role
description: Create, update, or retire a project's custom Ratpack role and native Codex profile. Use for role lifecycle changes, not ordinary assignment or conversation renaming.
---

# Ratpack Role

Read the project's AGENTS.md, contributor workflow, `ratpack.json`, role files,
and active assignments. Follow its ownership and role-change rules. Resolve the
requested purpose, scope, outputs, and handoff from project context and the human.

1. Reconcile the brief under `custom_roles`. For a new entry use `purpose`,
   `allowed_work`, `expected_outputs`, `handoff`, and `native_agent`; preserve
   existing prose briefs unless deliberately migrating them.
2. Build a matching `.codex/agents/<name>.toml` with `name`, `description`, and
   `developer_instructions`. Keep unique stable `ratpack_` names (for example
   `ratpack_research`) and inherit model/permissions/MCP access. Preserve unrelated
   profiles and configuration; reconcile existing instructions with their owner.
3. Use the bundled [renderer](scripts/render_agent.py), which accepts exactly
   those three fields as JSON on stdin and writes TOML to stdout:

   ```bash
   python3 scripts/render_agent.py < /tmp/role-spec.json > /tmp/role-profile.toml
   ```

4. Review the output before applying it. Parse JSON/TOML, check name/path/brief
   consistency, and run applicable checks (Python 3.11+ for the renderer).
5. For retirement, resolve active assignments and references before removing
   the intended brief/profile. Preserve unrelated entries and local changes.
6. Hand off changed paths, branch/worktree, commit/PR, validation, remaining
   activation gaps, and next owner/action. Verify discovery separately if asked
   to activate the role; a profile file or conversation rename is not activation.
