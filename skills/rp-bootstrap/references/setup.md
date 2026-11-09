# Setup guidance

Use this when discovering connections, resolving setup decisions, or reporting a
setup blocker. The [workflow](workflow.md) owns authority and staffing policy.

## Questions people can answer

Recommend a concrete setup based on the repository and explain its consequence.
Infer facts from available tools before asking; reuse prior answers. For a new local pack, propose this conversation as its coordinator. Inspect
the repository's existing integration assignment separately; joining a project
must not claim or replace its merger. If that assignment is missing, resolve it
with the human before integration. Do not ask the user to select internal JSON fields,
enable delegation, or choose an implementor count during bootstrap. Explain
that the coordinator arranges helpers and independent review; implementation
staffing is proposed when there is actual implementation ready to assign.

For GitHub settings, name the repository, proposed changes, and any decision
that affects the human. Follow the workflow's default of independent agent
review, passing CI, and designated-owner integration with no GitHub approval click.
Explain any existing GitHub approval requirement and its available approvers;
do not invent that requirement during setup. If an
approval system rejects the action, explain its reason and request the specific
approval needed; do not retry around the rejection or silently weaken protections.

## Missing Linear connection in Codex

Distinguish Codex access to Linear from Linear's GitHub integration; connecting
one does not configure the other. If current tools cannot reach the intended
workspace, give the repair steps immediately, alongside any question about the
destination. Do not make the user discover the commands themselves.

1. Have the user create or identify the intended Linear workspace. Reuse an
   existing connection if it reaches that workspace. Never send project work to
   another workspace just because its tools are available.
2. For Codex CLI, provide copyable commands with an unused, project-specific
   server name. For a project named `example`:

   ```bash
   codex mcp add linear_example --url https://mcp.linear.app/mcp
   codex mcp login linear_example
   ```

   If that server is already configured, skip `add`; retry login only when
   authentication needs repair. Have the user select the intended workspace in
   browser authorization. Do not overwrite another project's connection or
   change global credentials automatically.
3. If the current conversation still lacks the tools, have the user reload or
   reopen it, then verify the actual workspace/team before writing tasks. A
   configured server alone is not proof of access. For another client, give its
   supported connection steps instead of assuming it has the Codex CLI.
4. Continue independent local preparation while access is pending. Keep pending
   decisions and handoff evidence in the conversation until a tracker is
   available; then record them in its setup task, not a repo setup-status section.

See [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp) and
[Linear's MCP documentation](https://linear.app/docs/mcp) for current setup.

## Reconcile the Linear team

After verifying workspace/team access, inspect the team's issue statuses and
applicable issue labels, including workspace labels available to that team.
Compare them with the workflow's [Linear conventions](workflow.md#linear).
Reuse equivalent existing names and IDs; do not recreate them for each project
or confuse issue labels with project labels. Create only missing issue labels
through supported tools and read them back. For missing statuses or unsupported
label edits, direct the user to Settings > Teams > the actual team > Issue
statuses, or that team's issue Labels settings. Name each missing value and its
status category from the workflow; confirm the resulting values before claiming setup.
Keep documentation work in the same status workflow, not a separate docs state.

## Linear's GitHub integration

1. Inspect the workspace's Settings > Integrations > GitHub connection and
   repository access. If UI access is required, tell the user to enable the
   integration there, select the intended GitHub owner/repository, complete
   authorization, and return to Linear. A Codex MCP connection does not prove
   this integration exists. If GitHub shows an existing installation but Linear
   shows no connection, inspect the return flow and which workspace owns the
   installation before recommending changes. Preserve other projects' access.
2. Inspect this team's Automations > Pull request automations. Reconcile against
   the workflow's [event mapping](workflow.md#linear). When tools cannot inspect
   or change these settings, provide a numbered UI checklist with the team's
   actual name, each event and destination, and the following branch steps.
   Ask the user to confirm the saved settings or inspect their screenshot;
   do not claim configuration from a successful GitHub connection alone.
3. Under Branch-specific rules, use Add branch for target `devel`, or edit the
   existing matching rule. Apply the canonical mapping there; do not create
   duplicate rules or overwrite the team's defaults or unrelated branch rules.
   Explain that the target is where a PR merges, not its feature branch. Check
   for broader rules that would interfere. Team rules affect all its projects;
   resolve incompatible conventions with existing owners before changing them.
4. Exercise a real task PR with a closing reference such as `Fixes TEAM-123`.
   Observe automatic attachment and draft/ready/review/merge behavior separately
   from manual edits. A draft already In Progress is not proof of a draft-triggered
   transition. Record what was inspected, observed, and remains unverified in the
   setup task; keep work moving with manual updates if needed. Prefer the next
   real task over manufacturing a code change just to exercise an event.

Follow [Linear's official GitHub setup](https://linear.app/docs/github) and
[issue properties documentation](https://linear.app/docs/issue-properties-home)
for current UI and workspace restrictions rather than guessing from permissions.
