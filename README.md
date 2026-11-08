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
> You may spawn up to two implementation workers for bounded tasks in this
> project, plus independent review and occasional cleanup/workflow agents as
> useful within the host's capacity. Use our existing GitHub repository and
> Linear team; ask only for
> missing information you cannot discover. Releases still need my approval.

For a local checkout, give the agent the absolute path to
`skills/ratpack/SKILL.md`. To install it for reuse, ask Codex's skill installer
to install `skills/ratpack` from `Spencer1O1/ratpack`, then invoke `$ratpack`.
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
authority. The workflow includes reusable briefs for all five roles.

Linear tracks ownership and dependencies. GitHub holds code, PRs, checks, and
releases. Project documentation owns requirements and technical decisions.
Until app approvals or automation are ready, link PRs and update tasks manually.

Ratpack supplies instructions, templates, and a bootstrap helper. Agent spawning
still needs host support and authorization; merge restrictions need repository
permissions and protections to be enforced technically. Existing Linear and
GitHub tools are sufficient to start; Ratpack does not require its own server.

## Develop Ratpack

See [CONTRIBUTING.md](CONTRIBUTING.md). Run with Python 3.10 or newer:

```bash
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

The bootstrap helper uses only the Python standard library and makes no Git,
GitHub, Linear, or account-setting changes. Those are coordinated by the agent.

Licensed under [MIT](LICENSE).
