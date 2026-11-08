# Ratpack

A workflow for humans and agents building projects with Linear and GitHub.
One coordinator organizes work; independent reviewers check changes; one
integration owner merges. Feature branches integrate into `devel`; releases
promote `devel` to `main`.

## Start

Give your agent this request:

> Use `skills/rp-bootstrap/SKILL.md` from https://github.com/Spencer1O1/ratpack
> to set up Ratpack in this project.

If the skills are already installed, use `$rp-bootstrap` for setup and
`$rp-coordinate` for ongoing work. To install them, use your skill installer
with the selected paths below from this repository, pinned to a chosen commit.
Each skill can be installed separately.

| Skill path | Procedure |
| --- | --- |
| [skills/rp-bootstrap](skills/rp-bootstrap/SKILL.md) | Adopt Ratpack and verify setup |
| [skills/rp-coordinate](skills/rp-coordinate/SKILL.md) | Plan and coordinate project work |
| [skills/rp-review](skills/rp-review/SKILL.md) | Independently review a revision |
| [skills/rp-cleanup](skills/rp-cleanup/SKILL.md) | Audit maintainability and make scoped fixes |
| [skills/rp-role](skills/rp-role/SKILL.md) | Create, update, or retire a custom role |

## Workflow

The [contributor workflow](skills/rp-bootstrap/references/workflow.md) owns the
shared rules. Bootstrap installs it into the project; contributors follow that
adopted copy. Updating this repository does not change existing projects.

Roles define responsibility; skills provide procedures. A new role does not
require a new skill. Ratpack supports both coordinator-spawned subagents and
human-created conversations, and includes native Codex role profiles.

Ratpack supplies instructions and helpers. Spawning requires host support;
repository protections and integrations must be configured and verified during
setup. No dedicated Ratpack server is required.

See [CONTRIBUTING.md](CONTRIBUTING.md) to develop Ratpack. Licensed under [MIT](LICENSE).
