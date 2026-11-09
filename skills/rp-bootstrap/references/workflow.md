# Ratpack contributor workflow

Humans and agents share one task, branch, PR, and review process. Linear owns
task state, ownership, and dependencies; GitHub owns code and review evidence;
repository documents own requirements and design. Use the adopted project
workflow and explicit user decisions; upstream changes require deliberate adoption.

## Shared project and developer packs

Each developer may run a separate pack: a coordinator and its agents working
within the repository's shared rules. Coordinate assignments through the shared
tracker so packs do not duplicate or overwrite each other's work.

| File | Scope and version control |
| --- | --- |
| `ratpack.json` | Commit shared checks, reusable roles, repository/tracker references, and merge policy |
| `ratpack.lock.json` | Commit the adopted upstream revision and shared-file baseline hashes; it is provenance, not a running-agent lock |
| `ratpack.local.json` | Ignore developer-local coordinator identity and approved implementor count |

Keep personal model preferences and agent sessions local or in assignment notes,
not in shared project configuration. Never put local pack files or their hashes
in the adoption lock. Another developer joining an adopted project initializes
only their local pack; shared config, policy, profiles, and lock stay unchanged.
A worker in another worktree remains part of its assigning pack: include the
pack coordinator/local-config path and relevant settings in its assignment. Do
not bootstrap another coordinator or commit local settings for each worktree.
A local file cannot grant repository integration authority. Legacy mixed configs
need deliberate separation, preserving agreed merge authority and project facts;
do not blindly copy one developer's coordinator or staffing into another pack.

## Roles and authority

| Role | General agent name | Responsibility and handoff |
| --- | --- | --- |
| Coordinator | `crd-rat` | Plan product work, prioritize tasks, assign owners, resolve dependencies, and collect results |
| Implementation | `imp-rat` | Build one assigned change with tests/docs; hand off a commit or PR and validation |
| Independent review | `rev-rat` | Evaluate the exact proposed revision; return actionable findings or no findings, with checks and limitations |
| Cleanup | `cln-rat` | Audit a bounded area for maintainability problems; report findings or implement scoped fixes |
| Workflow | `wfl-rat` | Maintain contributor guidance and tracker/repository setup; report changes, verified behavior, and setup gaps |

Each pack's coordinator is its persistent developer conversation by default.
Adopting Ratpack authorizes it to create and manage task-scoped helpers, including
independent reviewers, where the host supports them. It delegates substantial
implementation and may implement bounded work itself. Cleanup and workflow are
optional support, not permanent staffing requirements. Every assignment names
the outcome, acceptance criteria, owned paths, dependencies/contracts, checks,
and handoff destination.

The shared `merge_policy` is `designated-integration-owner`: only the project's
human-designated integration owner merges, one PR at a time. Record that shared
assignment and handoff route in the tracker or the human's explicit instructions.
A pack coordinator organizes its developer's work; it merges only if separately
assigned integration authority. Other packs submit reviewed PRs to that owner.
The user retains product and release authority. To transfer integration, the
human names a replacement, the old owner stops and hands off the queue, and the
shared assignment changes before the new owner merges. If the old owner is
unavailable, confirm it will not merge and reconstruct the queue from GitHub.
Conversation names, local config, and role selection do not confer authority.

Authority is repository-specific: a conversation may coordinate one project
and contribute to another without carrying merge rights or project context
between them. Worker assignments do not permit scope expansion or recursive
spawning; additional spawning authority must be explicitly delegated.

### Staffing and contributors

There is no separate delegation enable/disable step. At bootstrap, leave
`ratpack.local.json`'s `max_implementation_agents` null unless that developer
already chose a count. When implementation is ready to start, the coordinator proposes a useful concurrent
implementor count and concrete task split; the human approves or chooses another.
Record that pack's count in its local `max_implementation_agents`. Null means
the count has not been chosen; zero records an explicit choice to work without implementation
helpers. Do not dispatch implementors before a positive count is approved.
Reuse approval until changed; suggest an increase when growing implementation
work justifies it, and wait before exceeding the approved count.

Use fewer workers for overlapping tasks and respect actual host capacity.
Human-created implementation peers and cleanup/custom roles that edit repository
content consume the same worker capacity. Independent review and other support
helpers are part of the adopted workflow, scoped to actual tasks and host
capacity; they do not require a separate enablement question. Honor explicit
human restrictions on helpers and preserve existing staffing decisions during
adoption upgrades. The retired `implementation_delegation_authorized` field is
not used by this workflow; reconcile it against the human's actual instructions
before removing it from an older project's configuration. Existing shared
staffing is legacy information, not an approval for every developer's pack.

The human may create a separate conversation for any role. Register its actual
owner and handoff route, have it read the project instructions and role brief,
and avoid duplicate assignments. Peers remain human-accessible; they need not
become subagents. Humans do not need agent session bookkeeping.

Use the role table's general names for reusable agents; projects may choose
other names. Reuse suitable general agents across assignments. Add a task suffix
only when it distinguishes concurrent or specialized workers, such as
`imp-rat-storage`. Adapt punctuation to host constraints: `imp_rat_storage` when
internal names require underscores. Each assignment still has its own bounded
brief and ownership record.

### Model and reasoning effort

Choose model and reasoning effort for each assignment, including review and
support, rather than inheriting an expensive coordinator setting by accident.
Use the lightest host-available setting likely to meet the task's acceptance
criteria, considering ambiguity, failure impact, context needs, and validation.
Role names do not select a model. Honor explicit human model choices and project
constraints; do not change global defaults or other conversations to optimize one
task. Routine selection within those constraints needs no new permission prompt.

| Assignment | Starting choice |
| --- | --- |
| Mechanical edits, extraction, or a scoped fix with strong checks | Efficient model, low or medium effort |
| Nontrivial implementation or analysis with clear boundaries | Balanced model, medium effort |
| Ambiguous design, difficult debugging, or consequential changes with weak checks | Stronger model and/or higher effort |

These are starting points, not a universal ranking or measured savings. Select
review settings from the change's risk independently of its author's model; a
small diff can have serious consequences. If reasoning, checks, or review expose
a capability gap, narrow the task or escalate model/effort rather than repeatedly
retrying an inadequate setting. Fix environmental failures as environmental
failures, not automatic model upgrades. Preserve independent review and acceptance
criteria when using a cheaper model.

Record requested model/effort and a brief reason in the task assignment; record
effective settings only when the host exposes evidence, otherwise mark them
unverified. For existing peers, preserve the human's settings and explain any
recommended change. If the host cannot choose a suitable setting, disclose the
fallback and continue only when it can meet acceptance; do not claim a switch.
Compare quality, rework, and time on representative tasks, plus usage/cost only
when available, before claiming an optimization. Keep temporary measurements in
the tracker, personal preferences local, and agreed project-wide model constraints
in shared `ratpack.json`.

### Custom roles and native profiles

The human may add, change, or retire a role through the coordinator at any time.
Record its purpose, allowed work, expected outputs/evidence, and handoff under
`custom_roles`. Reconcile active assignments before changing or retiring a role.
A definition grants no new authority and does not require a permanent agent or
another skill; use the role procedure when maintaining a native definition.

Bootstrap supplies `ratpack_coordinator`, `ratpack_implementor`,
`ratpack_reviewer`, `ratpack_cleanup`, and `ratpack_workflow` profiles in
`.codex/agents/`. Profiles select these role briefs; skills provide procedures.
Packaged profiles leave model/effort unpinned so dispatch can select them;
otherwise the host's inheritance/defaults apply. Sandbox/approvals and MCP access
follow the parent. Behavioral read-only instructions are not a separate sandbox. Verify discovery in a trusted,
fresh/reloaded session before claiming activation; another host may use the same
briefs without native discovery. Renaming a conversation does not activate a profile.

## Planning and product scope

The coordinator plans from the human's agreed outcomes and constraints. Agents
may suggest new capabilities, operator actions, or materially different behavior,
but present their benefit, cost, and tradeoffs as proposals and wait for human
acceptance before dispatching implementation. Creating a ticket, writing a
requirements document, or another agent approving it does not grant product
approval. Distinguish accepted scope from proposals in the existing task/design
record and link the human decision when needed; no separate approval ledger is
required. Reuse approval already given in the conversation or accepted plan.

Derive acceptance criteria from the agreed outcome without adding independent
product scope. Routine implementation choices, necessary tests, and useful
behavior-preserving cleanup remain autonomous within the assignment. Cleanup
that changes product behavior or adds operator obligations needs the same scope
check as a feature. A safety or reliability concern is grounds to explain the
problem and suggest options, not to invent a mandatory product requirement.
Continue independent authorized work while a proposal awaits a decision.

Before dispatch and integration, check that material requirements have human
support. If an existing agent-written requirement's authority is unclear, check
its source and ask about the disputed scope rather than treating the document
as approval. Reviewers flag unsupported scope even when code matches its written
requirements; coordinators resolve it with the human before merging that scope.

## Task to merge

For normal repository changes; release/hotfix routing is specified below.

1. Create or reuse a bounded tracker task for actual work, not hypothetical
   discussion. Record scope, acceptance evidence, owner or pending assignment,
   dependencies, start condition, next action, and relevant design links.
2. Assign one owner and an independent reviewer. Agree shared interfaces before
   parallel work; sequence overlapping schemas, headers, and build files.
3. Branch from current `origin/devel` using `feature/`, `fix/`, `docs/`, or
   `chore/` plus the real task ID and short description when available.
   Each implementation task gets its own branch/worktree; humans may use a
   normal checkout. Inspect status, branches, and worktrees first. Never switch,
   reset, stash, clean, or stage unrelated work in another owner's checkout.
4. Implement one reviewable change with applicable tests/docs. Open a PR into
   `devel`, link the task, and report checks/results and gaps.
5. A different human or agent reviews the exact head for requirements,
   correctness, regressions, and test evidence, including coordinator-authored
   changes. Record severity, location, reasoning/evidence for findings; separate
   blockers from optional polish. The reviewer does not edit the author's branch.
   Experiments that modify files/build outputs use an isolated copy. Re-review
   affected changes after updates; old review does not approve a new revision.
6. The integration owner verifies prerequisites, current review, required GitHub
   approvals, and CI, then squash merges. Agent review does not manufacture a
   GitHub approval. Mark repository-change tasks Done only after accepted merge.

Merge prerequisites before dependents. Synchronize owned branches with current
`devel` by merge or transplanting dependent commits; retain only the intended
diff and repeat affected checks/review. Keep one implementation task active per
worker. Occupied worktrees remain until their owner hands them off; remove them
only when no remaining work depends on them.

## Requests and ordering

Capture actual requests as bounded tracker tasks for every role, including
audits, research, docs, and custom work; hypothetical discussion creates none.
Record relative requests as explicit start conditions in the task.

Use conversation and project context to identify the owning project. Update an
existing task for a clarification or related scope; capture independent work
as a new or existing task in that project's queue. Resolve genuine project
ambiguity before tracker writes or dispatch. Route work outside your project or
assigned role to the appropriate coordinator without taking over its authority.

An unscheduled request is capture and triage, not implicit cancellation or
preemption. Continue active assignments; schedule new work through existing
priorities, prerequisites, and capacity. Clarifications needed to finish the
current task belong on that task. Reprioritize when the human clearly requests
it, coordinating a safe handoff where needed. Acknowledge the captured task and
next action; creating a ticket is not dispatch or completion.

| Request | Start condition |
| --- | --- |
| No timing specified | Capture/update the project task and schedule within existing priorities, dependencies, and capacity |
| Now | Next eligible opportunity within authority, ownership, dependencies, and capacity |
| Next / when free | Next suitable slot with prerequisites intact |
| After named tasks | Those exact IDs and their accepted deliverables |
| After current tickets | Fixed snapshot of In Progress/In Review IDs at request time, unless the user names another batch |

Acknowledge the snapshot IDs; future tickets do not join it. If the batch is
empty, say so and treat the condition as met. Resolve an unclear batch before
dispatch. Use tracker blocking relations, exclude the target itself, and check
for cycles: required review cannot wait for its own implementation to be Done.
Reassess canceled/replaced prerequisites and record the decision or replacement.

Deferred work stays Backlog until its condition is met, then Ready; mark it
In Progress only when it starts. The whole task is deferred, including its audit
phase, unless the human explicitly separates audit-now from fixes-later. Urgency
does not bypass prerequisites or justify disrupting another owner's checkout;
coordinate a safe handoff for preemption and report any blocker/next action.

Report-only work finishes when its agreed artifact is delivered and accepted
by the recipient, with evidence linked in the task. A worker's return alone
is not acceptance. Reuse coherent tasks rather than creating a ticket per tiny
finding. Recheck the queue on new requests, handoffs, merges, and resume; continue
authorized ready work while active. Tracker relations do not wake a stopped
coordinator; calendar execution needs separately requested, verified automation.

## Communication and handoffs

Use readable language with normal spaces and line breaks; preserve exact
identifiers, commands, paths, and quoted evidence. Link authoritative records
rather than repeatedly forwarding summaries or whole conversations. Resolve
truncated or ambiguous messages against their source before acting.

A handoff records task, branch/worktree, exact commit/PR, checks/results,
limitations/open findings, and next owner/action. Include agent identity and
session route in task notes when needed. Ownership/authority transfers require
recipient acknowledgment before conflicting work starts. Distinguish requests,
acknowledgments, and verified completion; summaries are not proof of passed checks.

## Linear

Reuse existing teams/projects. Start with one team and one project per bounded
milestone; track current work and near-term dependencies rather than the entire
historical roadmap. A code-change task normally corresponds to one PR.

| Status | Meaning |
| --- | --- |
| Backlog | Captured work not ready or selected |
| Ready | Scope, acceptance criteria, dependencies, and start condition permit work |
| In Progress | An owner is doing the task |
| In Review | A ready PR awaits review/integration, or a report awaits acceptance |
| Done | Accepted deliverable complete; repository changes satisfy Task to merge |
| Canceled | Abandoned with a reason or replacement |

Use the team's available statuses with these meanings: Ready is Unstarted;
In Progress/In Review are Started. Start with Bug, Feature, Improvement, and
Documentation labels; docs use the same states. Feature-required docs belong
in that feature's acceptance. Prefer owners, priorities, projects, and blocking
relations over redundant labels. Extra labels and cycles are optional.

Configure supported GitHub automation for PRs targeting `devel`:

| Event | Destination |
| --- | --- |
| Draft PR opened | In Progress |
| PR opened / marked ready | In Review |
| Review requested or review activity | In Review |
| PR ready for merge | No action |
| PR merged | Done |

`devel` accepts implementation; promotion to `main` is a separately approved
release. Passing checks or review alone does not complete a task. Team settings
are shared by its projects: preserve unrelated branch rules and coordinate any
change affecting other repositories. Verify linking and transitions with a real
closing-linked PR; state changes are not independent approval. If access or
automation is unavailable, give the exact setup steps, link evidence and update
manually, track pending setup, and keep work moving. Distinguish settings that
were inspected from automatic events that were actually observed.

## Branches and releases

| Change | Target | Merge method |
| --- | --- | --- |
| Feature, fix, docs, chore | `devel` | Squash |
| Release from `devel` | `main` | Merge commit |
| Hotfix from released `main` | `main` | Squash, then merge `main` into `devel` |

Use `devel` as default branch. Enable squash/merge commits and disable rebase
merges. Never squash between long-lived branches, rebase shared `main`/`devel`,
or force-push them. The user approves release scope/version; the integration
owner verifies evidence, merges the release PR, and tags its `main` commit.
Merge `main` back into `devel` after release. Track release completion separately
from implementation; temporary release branches may stabilize a release.

Protect both branches with PRs and CI where available; prohibit direct/force
pushes. The default is independent agent review followed by the integration
owner's merge after passing CI, with zero required GitHub approving reviews.
Do not ask the human to sign in with a second GitHub account to approve agents'
PRs. Require GitHub approvals only when the human requests them or existing
repository policy requires them; an approving account must differ from the PR
author's. Preserve existing protections;
relaxing them requires explicit human approval. Disclose unavailable protections
and apply the checklist manually; visibility/billing changes need user approval. A branch is not proof
of deployment or product readiness.

For a new repository, a reviewed baseline may initialize `main` and `devel` at
the same commit. Existing repositories need a reviewed migration preserving
history and occupied work; never relabel arbitrary code as a released version.
