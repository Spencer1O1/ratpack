---
name: rp-bootstrap
description: Adopt Ratpack in a new or existing project by reconciling contributor guidance, roles, and GitHub/Linear setup. Use for setup or an explicit adoption upgrade, not ongoing coordination.
---

# Ratpack Bootstrap

Read [the workflow](references/workflow.md) and the target project's existing
instructions, requirements, ownership, and handoff. Preserve existing policy and
authority until deliberate adoption decisions are made; do not import another
project's names, account identifiers, or production settings.

1. Inspect status, branches, worktrees, remotes, checks, and active ownership.
   Prepare changes in an isolated worktree when the checkout is occupied.
2. Discover existing GitHub/Linear connections, repository, team, projects,
   statuses, labels, and permissions. Resolve missing setup decisions with the
   human, including integration ownership and delegation under the workflow.
3. Reconcile contributor guidance, `ratpack.json`, PR template, and native
   profiles with existing files. Keep one project workflow; merge into its
   owning documents rather than replacing instructions or creating rivals.
4. Configure the agreed branch policy, protections, and tracker conventions
   within actual authorization. Record unsupported settings or pending access.
5. Run local checks and realistic adoption checks. Verify external settings and
   automation separately; generated files alone are not evidence they work.
   Verify native discovery in a trusted fresh/reloaded session before claiming
   activation; preserve global trust, model, and permission settings.
6. Hand setup changes to independent review/integration. Report installed files,
   verified behavior, pending external setup, source revision when known, and
   next owner/action. End at setup handoff rather than starting product work.

The helper previews starter files in an existing directory and refuses to
overwrite differing content or write through symlink output paths:

```bash
python3 scripts/bootstrap.py /path/to/project --owner coordinator-name
```

Run from this skill's directory with Python 3.11+. Add `--apply` to write.
The helper does not change Git or accounts. Reconcile conflicts manually and
fill configuration from the project's actual commands and identifiers.

For an installed copy, pass `--source-revision <commit>` when the pinned source
commit is known. Bootstrap records provenance and generated-file hashes in
`ratpack.lock.json`; unknown provenance stays explicit. The lock is an adoption
baseline, not task state or permission to overwrite project changes.

Read-only checks from this skill's directory:

```bash
python3 scripts/doctor.py /path/to/project
python3 scripts/upgrade.py /path/to/project --source-revision <commit>
```

Use `--json` for structured output. Doctor accepts `--workflow <relative-path>`
for an existing owning document and `--native` to require native profiles. It
does not run configured checks or verify remote integrations. Upgrade only
previews changes against the recorded baseline; reconcile conflicts and preserve
project configuration deliberately. Legacy projects without a baseline need
manual adoption reconciliation.
