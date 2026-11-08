# Ratpack

A small workflow for humans and agents building projects with Linear and
GitHub. One coordinator plans and delegates, independent reviewers
check the work, and one integration owner merges.

**Feature branches → `devel` by squash merge → `main` by release merge.**
This branch arrangement is required for Ratpack projects.

## Start a Ratpack

Point your coordinator at this repository:

> Read the Ratpack skill at `skills/ratpack/SKILL.md` in
> https://github.com/Spencer1O1/ratpack and bootstrap Ratpack in this project.
> Preserve existing instructions. You are the coordinator and integration owner.
> Propose how many concurrent implementation workers would help and why; I will
> approve that number or choose another. You may use independent review and
> occasional cleanup/workflow agents within the host's capacity. Use our existing GitHub repository and
> Linear team; ask only for
> missing information you cannot discover. Releases still need my approval.

For a local checkout, give the agent the absolute path to
`skills/ratpack/SKILL.md`. To install the complete set for reuse, ask Codex's
skill installer to install `skills/ratpack`, `skills/ratpack-role`,
`skills/ratpack-review`, and `skills/ratpack-cleanup` from `Spencer1O1/ratpack`
at the chosen revision.
Then invoke `$ratpack` to bootstrap a project.
Pin the source commit when adopting a version; fetching the URL does not itself
install a skill or activate instructions in another conversation.

The [bootstrap skill](skills/ratpack/SKILL.md) inspects the project, prepares
local contributor guidance, records assignments and checks, and reconciles the
tracker and repository settings within the user's authorization. Its optional
Python helper previews files first and refuses to overwrite existing content.
Existing projects can adopt the same workflow through small manual edits.

## How it works

Read the [shared workflow](skills/ratpack/references/workflow.md) for roles,
delegation, branch policy, review, and handoffs. The project keeps its own
`ratpack.json` assignment record and contributor guide; changes to this upstream
repository do not silently change an existing project's policy.

The default is one persistent coordinator spawning bounded implementation and
review subagents. Cleanup and workflow agents are used as needed. Separate
human-directed conversations can fill the same roles; names do not grant
authority. The workflow includes reusable briefs for all five roles. There is
no fixed implementation-agent count: the coordinator proposes a count, the
human approves or adjusts it, and that approval remains valid until changed.
Host capacity may restrict how many can actually run at once.

Bootstrap installs five native Codex definitions in the target project's
`.codex/agents/`: `ratpack_coordinator`, `ratpack_implementer`,
`ratpack_reviewer`, `ratpack_cleanup`, and `ratpack_workflow`. Trusted Codex
sessions discover these names for spawning. Reload an existing session and
verify discovery before claiming activation. The coordinator normally remains
the main conversation; selecting a type does not transfer merge authority.

Human-created peers can explicitly read the same role file and follow its
instructions for their assignment. They remain directly accessible to the
human; they do not need to become subagents or acquire a particular name.

| Skill | Use |
| --- | --- |
| [ratpack](skills/ratpack/SKILL.md) | Bootstrap and coordinate the project |
| [ratpack-role](skills/ratpack-role/SKILL.md) | Create, update, or retire a custom brief and native definition |
| [ratpack-review](skills/ratpack-review/SKILL.md) | Independently review a specific revision and report evidence |
| [ratpack-cleanup](skills/ratpack-cleanup/SKILL.md) | Audit a bounded area and implement requested maintainability fixes |

Task ordering is generic: ask for implementation, documentation, research,
cleanup, or any custom-role work now, next, or after specific tickets. The
coordinator records scope and explicit dependencies; "after current tickets"
captures a fixed batch rather than a growing backlog. Deferred tasks survive
conversation restarts in the tracker. They run while the coordinator is active
or on resume; dependencies alone do not wake a stopped agent. See
[requests and ordering](skills/ratpack/references/workflow.md#requests-and-ordering).

Roles are extensible: tell the coordinator to add a project-specific role such
as research, with its scope and expected output. The coordinator records the
brief in that project's `ratpack.json`. The same agent may hold different roles
in different repositories; authority stays scoped to each repository.

Linear tracks ownership and dependencies. GitHub holds code, PRs, checks, and
releases. Project documentation owns requirements and technical decisions.
Until app approvals or automation are ready, link PRs and update tasks manually.

Ratpack supplies instructions, templates, and a bootstrap helper. Agent spawning
still needs host support and authorization; merge restrictions need repository
permissions and protections to be enforced technically. Existing Linear and
GitHub tools are sufficient to start; Ratpack does not require its own server.

Native profiles inherit the parent's model and permissions. A reviewer's
read-only instructions do not create a separate sandbox. See the
[Codex custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Develop Ratpack

See [CONTRIBUTING.md](CONTRIBUTING.md). Run with Python 3.11 or newer
(the role tooling uses the standard-library TOML parser):

```bash
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

The bootstrap helper uses only the Python standard library and makes no Git,
GitHub, Linear, or account-setting changes. Those are coordinated by the agent.

Licensed under [MIT](LICENSE).
