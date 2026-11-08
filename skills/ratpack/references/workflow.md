# Ratpack contributor workflow

Humans and agents use the same task, branch, PR, and review process. Linear owns
task state and dependencies; GitHub owns code and review evidence; repository
docs own requirements and design decisions. Link rather than duplicate them.

## Roles and authority

| Role | Responsibility |
| --- | --- |
| Coordinator / integration owner | Planning, product coordination, priorities, task breakdown, delegation, and merges |
| Implementation worker | Implement one assigned task, test it, and submit a PR |
| Independent reviewer | Check the proposed revision and report actionable findings |
| Cleanup contributor | Find and fix maintainability problems through normal tasks and PRs |
| Workflow maintainer | Maintain contributor guidance and tracker/repository coordination |

The coordinator delegates substantial implementation by default when authorized
and supported by the host. Start with at most two workers; use fewer when tasks
share a contract or there is no useful parallel work. The coordinator may also
implement bounded work. Cleanup and workflow are optional supporting roles,
not requirements to run five persistent agents on every project.

Record the current integration owner and delegation limit in `ratpack.json`.
Names are labels; roles define responsibility, not an agent's entire scope.
Independent review is required even for the coordinator's own changes. A
different human or agent reviews; the implementer cannot approve its own work.

Only the designated integration owner merges agent PRs, one at a time. The user
retains final product authority and approves releases. To transfer integration,
the user names a replacement, the old owner stops merging and hands off the
queue, and the assignment record changes before the replacement starts. If the
old owner is unavailable, confirm it will not merge and reconstruct the queue
from GitHub. Renaming a conversation does not transfer authority.

## Task to merge

1. Pick or create a bounded issue. Record the outcome, acceptance criteria,
   owner, dependencies, and relevant design links. Check for existing work first.
2. The coordinator assigns the task and intended files/modules. Agree on shared
   interfaces before parallel work; sequence changes to shared schemas, headers,
   and build files. Each implementation has one owner and its own branch.
3. Branch from current `origin/devel`, using `feature/`, `fix/`, `docs/`, or
   `chore/` plus the real issue ID and a short description when available.
   Concurrent agents use separate worktrees; humans may use a normal checkout.
   Never change another contributor's branch or uncommitted work.
4. Implement one reviewable change with applicable tests and docs. Open a PR
   into `devel`, link the issue, and report exact checks/results and gaps.
5. An independent reviewer checks the current revision for correctness,
   regressions, acceptance criteria, and meaningful test evidence. Put findings
   on the PR; distinguish blockers from optional cleanup. Review experiments
   that modify files/build outputs use an isolated copy. Re-review affected
   behavior after changes; never treat an old approval as approval of new code.
6. The integration owner verifies dependencies, review, and CI, then squash
   merges. Mark the issue Done after merge. Remove branches/worktrees only when
   no remaining work depends on them and their owner has handed them off.

Merge prerequisites before dependents. Update owned branches by merging current
`devel` or transplanting dependent commits; the final PR diff must contain only
the intended change. Repeat affected checks and review after synchronization.

Worker assignments include the issue, outcome, acceptance criteria, owned paths,
dependencies/contracts, checks, reviewer, and handoff destination. Workers do not
expand scope, spawn more workers, or merge without explicit delegation.

At handoff record the branch/worktree, commit/PR, checks/results, open findings,
blocker, and next owner/action. Keep unfinished worktrees until handed off.
Session identifiers belong in task notes when needed for agent coordination;
human contributors do not need session bookkeeping.

## Linear

Reuse existing teams and projects. Start with one team and one project per
bounded milestone. Add current work and near-term dependencies, not every
historical roadmap item. A bounded issue normally corresponds to one PR.

| Status | Meaning |
| --- | --- |
| Backlog | Captured work not ready or selected |
| Ready | Scope, acceptance criteria, and dependencies are clear |
| In Progress | An owner is implementing the task |
| In Review | A ready PR awaits independent review/integration |
| Done | Accepted scope merged into `devel` with required checks passing |
| Canceled | Abandoned, with a reason or replacement |

Ready is Unstarted; In Progress and In Review are Started. Use blocking relations
and name the next unblock action. Start with Bug, Feature, Improvement, and
Documentation labels; documentation follows the same states as other work.
Documentation required by a feature is part of that feature's acceptance.
Use owners, priorities, projects, and dependencies instead of duplicating them
as labels. Cycles and additional labels are optional.

Configure GitHub automation for target `devel`: draft → In Progress, ready/open
PR → In Review, merged → Done. Verify supported events with a real linked PR.
Do not confuse a review-state automation with independent review approval.
If access or automation is unavailable, link the PR and update tasks manually;
reconcile outstanding setup in a task. Keep implementation moving.

## Branches and releases

| Change | Target | Merge method |
| --- | --- | --- |
| Feature, fix, docs, chore | `devel` | Squash |
| Release from `devel` | `main` | Merge commit |
| Hotfix branched from released `main` | `main` | Squash; then merge `main` into `devel` |

Use `devel` as the GitHub default branch. Enable squash and merge commits;
disable rebase merges. Never squash between long-lived branches, rebase shared
`main`/`devel`, or force-push them. After a release, merge `main` into `devel`.
Creating branches never certifies deployment or product readiness.

The user approves the release scope/version. The integration owner checks the
applicable evidence, merges the release PR, and tags its `main` commit. Track
release completion separately from implementation Done. Temporary release
branches may stabilize a release alongside ongoing development.

Configure PR review and required CI protections on both branches when available;
prohibit direct and force pushes. If the host plan prevents protection, disclose
that limitation and enforce the checklist through the integration owner. Do not
change repository visibility or billing to enable protections without approval.

For a brand-new repository, a reviewed initial baseline may initialize `main`
and `devel` at the same commit. Subsequent changes use PRs. Existing repositories
need a reviewed migration plan: preserve history and work, inspect existing
branches/releases, and never relabel an arbitrary commit as a released version.
