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

Assignments and authority apply to a specific repository. The same conversation
may coordinate one project and contribute to another; merge authority does not
carry between them. Projects adopting Ratpack use their own assignment record
and policy version. Their contributors do not need upstream Ratpack development
context unless an adopted change affects their work.

The coordinator delegates substantial implementation by default when authorized
and supported by the host. There is no fixed Ratpack worker count. The coordinator
proposes as many concurrent implementation workers as useful, with a brief task
split and reason. The human may approve that count or choose a different one;
wait for an answer before dispatching beyond existing authorization. Record the
approved concurrent limit in `ratpack.json`. Reuse that approval until the human
changes it; request an increase when useful rather than asking for every spawn.
Use fewer workers when tasks overlap or there is no useful parallel work, and
respect the host's actual capacity even if the approved count is higher.
Human-created implementation peers count toward the same limit. The coordinator
may also implement bounded work. Cleanup and workflow are optional supporting roles,
not requirements to run five persistent agents on every project.

### Agent hierarchy

The default is one persistent coordinator as the main project conversation.
When authorized, it spawns implementation and independent review subagents for
bounded tasks, collects their handoffs, and retains integration responsibility.
Cleanup and workflow agents are started only when useful. They can be subagents
too; they do not each need a permanent conversation.

A reviewer may share a coordinator with the implementer. Independence means a
different agent or human evaluates the actual change; the implementer does not
review its own work. Give reviewers the requirements, diff/commit, and evidence,
not an instruction to rubber-stamp the implementer's conclusions.

The human is not required to create separate agents for any role. They may
create a separate conversation for any role at any time and tell the
coordinator its assignment. The coordinator registers that contributor, agrees
on ownership/handoffs, and avoids spawning duplicate work. Existing separate
conversations or humans may fill any role; mixed setups are supported. Record
the actual owner and handoff route rather than pretending a peer conversation
is a child agent. Respect host capacity and user scope; the implementation
limit is not permission for unlimited support agents. Non-coordinator agents
do not recursively create agents unless explicitly delegated that authority.

### Role briefs

Every assignment states the issue/outcome, acceptance criteria, owned paths,
dependencies/contracts, checks, and handoff destination. These briefs define
behavior. Bootstrap also installs the native Codex types described below.

- **Coordinator:** turn user goals into priorities and bounded tasks, assign
  owners, settle dependencies, and dispatch useful work. Collect implementation
  and independent review handoffs, check the latest revision/CI, and serialize
  merges. Return integrated results, open decisions, and the next plan to the
  user. Preserve human product and release authority.
- **Implementation:** build the assigned behavior within its ownership boundary,
  with applicable tests and docs. Return a commit/PR, acceptance results, exact
  checks, and remaining gaps. Stop at review handoff; do not merge or expand the
  task into unrelated work.
- **Review:** inspect the identified PR head against acceptance criteria,
  correctness, regressions, and test evidence. Return the reviewed commit and
  actionable findings with severity, location, and reasoning, or an explicit
  no-findings result plus checks and limitations. Keep optional cleanup separate;
  do not modify the author's branch or merge. Return fixes to the implementer
  and recheck affected changes when requested.
- **Cleanup:** inspect a bounded area for readability, organization, duplication,
  or technical debt. Return concrete, prioritized findings. Implement selected
  fixes as small tasks/PRs within the assigned scope; broader redesign returns
  to planning. Cleanup changes receive independent review like other changes.
- **Workflow:** inspect contributor guidance, assignments, task states, and
  repository/tracker coordination. Return concise docs/configuration changes,
  what was actually verified, and outstanding setup. Reuse existing objects and
  preserve project conventions; do not change product scope or merge authority.

### Project-specific roles

The five roles above are defaults, not a closed list. The human may add, change,
or retire a role at any time by telling the coordinator. Record its brief under
`custom_roles` in the project's `ratpack.json`: purpose, allowed work, expected
outputs/evidence, and handoff destination. A brief may link existing project
guidance rather than duplicate it. Assignments still identify the actual owner.

For example: "Add a research role to investigate Lean proof approaches. Return
sources, candidate lemmas, and unresolved questions to the coordinator; do not
edit implementation files." The coordinator records the role and assigns a
bounded research task when useful. A role does not require a permanent agent.

Custom roles follow the shared isolation, review, and handoff rules. Role
creation alone grants neither spawning nor merge authority. A research role is
read-only unless its assignment authorizes edits; implementation changes still
go through independent review. Changing the sole integration owner requires
the existing transfer procedure. If a role changes during active work, update
its assignment and handoff before dispatching conflicting work.

### Native Codex types and peer conversations

Bootstrap supplies `.codex/agents/ratpack_coordinator.toml`,
`ratpack_implementer.toml`, `ratpack_reviewer.toml`, `ratpack_cleanup.toml`, and
`ratpack_workflow.toml`. Each defines a native name, selection description, and
developer instructions. A trusted, fresh/reloaded Codex session can discover
these types for spawning. Verify discovery rather than assuming new files have
changed an already-open session's tools. The coordinator remains the main
conversation by default; spawning a coordinator type does not make that child
the project's integration owner.

Use the role skill to create/update/retire a custom brief and corresponding
native profile, and the review skill for the repeatable independent-review
procedure. A profile defines the agent's role; a skill defines a procedure it
may use. Neither automatically assigns a task or transfers authority.

Human-created conversations can perform any of these roles without becoming
subagents. Tell that conversation to read the same role file and follow its
instructions plus project guidance for the assignment; register its actual
owner and handoff route. A conversation rename alone does not activate a native
profile. This preserves a direct human channel while the coordinator manages
shared ownership and dependencies.

Native types inherit their parent's model, sandbox/approvals, and MCP servers.
Read-only reviewer instructions are behavioral rules, not a separate read-only
sandbox. Keep permission boundaries explicit in the hosting session. Another
host can use the same role briefs without claiming Codex-native discovery.

Record the current integration owner and approved concurrent worker limit in
`ratpack.json`. `max_implementation_agents: null` means no count has been
approved, not unlimited capacity. Spawning implementation workers requires both
`implementation_delegation_authorized: true` and a positive approved count.
Existing numeric limits remain valid; this policy does not silently increase
a project's authorization. Support/review spawning still needs its own agreed
scope and available host capacity.
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

Implementation assignments also name the independent reviewer. Workers do not
expand scope, spawn more workers, or merge without explicit delegation.

At handoff record the branch/worktree, commit/PR, checks/results, open findings,
blocker, and next owner/action. Keep unfinished worktrees until handed off.
Session identifiers belong in task notes when needed for agent coordination;
human contributors do not need session bookkeeping.

## Agent communication

Write messages in ordinary readable language, with normal spaces and line
breaks. Do not concatenate words or compress prose into shorthand to save
tokens. Keep identifiers, paths, commands, and quoted evidence exact; do not
normalize their internal whitespace.

Messages coordinate work; tasks, PRs, commits, and repository documents retain
the authoritative state. Link those records rather than repeatedly paraphrasing
requirements or forwarding an entire conversation. A handoff names the task,
exact commit/PR, checks and limitations, and next owner/action. Distinguish a
request, an acknowledgment, and verified completion.

For a transfer of ownership or authority, the recipient acknowledges the scope
and next action before conflicting work begins. If a message looks truncated,
ambiguous, or inconsistent with its source, read the linked record or ask the
sender before acting on the disputed detail. Do not treat an unacknowledged
message as an accepted handoff or a summary as proof that checks passed.

## Requests and ordering

These rules apply to every task: implementation, documentation, research,
review, cleanup, and custom roles. The coordinator converts an actual work
request into a new or existing bounded task in the project's tracker. Discussion
and hypothetical examples do not create work. Reuse related tasks rather than
opening duplicate tickets or one ticket per tiny finding.

Record the outcome/scope, acceptance evidence, requested order, explicit start
condition, owner or pending assignment, and next action. Resolve relative
phrases while their context is available and acknowledge the captured IDs.

| Request | Start condition |
| --- | --- |
| Now | Prioritize eligible work within existing authority, ownership, and capacity |
| Next / when free | Queue it for the next suitable slot, keeping prerequisites intact |
| After named tasks | Block on those exact task IDs and their accepted deliverables |
| After current tickets | Snapshot active In Progress/In Review IDs at request time, unless the user names a different batch |

The snapshot is fixed: later tickets do not silently join it. If no tasks are
active, say so and treat the condition as already met. If the intended batch or
start condition cannot be determined, resolve that uncertainty before dispatch;
do not leave a promise depending on "later" only in conversation memory.

Use blocking relations for dependencies. Deferred work stays Backlog until its
start condition is met; then make it Ready and dispatch when eligible. Mark
In Progress only when work actually starts. Use the team's available statuses
with these meanings rather than claiming unsupported states were created.
Exclude the target task itself and check for dependency cycles. If the new work
is required to finish a proposed blocker, resolve the intended phase or scope
instead of creating a circular wait (for example, a required review cannot wait
for its own implementation issue to be Done).

Now does not bypass prerequisites, another contributor's checkout/ownership,
permissions, or worker limits. Cleanup or any custom role that edits repository
content uses implementation capacity too. If work needs preemption, coordinate
a safe handoff; never reset or stash someone else's work to make room. Report
the concrete blocker and next action when immediate dispatch is impossible.

The order applies to the whole requested task, including its audit/research
phase. Do not start deferred work early under a different role name. If the
human explicitly asks for an audit now and fixes later, record separate bounded
tasks or phase conditions so the permitted early scope is clear.

Completion follows the task's acceptance contract. Repository changes require
independent review, passing checks, and merge into `devel`. Report-only research,
audits, or reviews finish when the agreed artifact is delivered and accepted by
its recipient, with required evidence retained or linked in the task. A worker's
return alone is not acceptance.
Reassess canceled, duplicate, or replaced prerequisites against the request and
record the replacement/decision; neither assume success nor leave a stale block.

Recheck pending work on new requests, worker handoffs, merges, and resume. While
active and authorized, continue into eligible follow-up work rather than treating
queue creation as completion. Tracker dependencies preserve order; they do not
start a stopped coordinator. Calendar-based execution needs a separately
requested and verified automation; do not claim a timer or wake-up exists merely
because a task has a date or blocker.

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
| Done | Accepted deliverable complete; repository changes merged into `devel` with required checks passing |
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
