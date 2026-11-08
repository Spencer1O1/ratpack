# Setup guidance

Use this when discovering connections, resolving setup decisions, or reporting a
setup blocker. The [workflow](workflow.md) owns authority and staffing policy.

## Questions people can answer

Recommend a concrete setup based on the repository and explain its consequence.
Infer facts from available tools before asking; reuse prior answers. If no owner
exists, propose this conversation as coordinator and sole PR merger, then get
that assignment confirmed. Do not ask the user to select internal JSON fields,
enable delegation, or choose an implementor count during bootstrap. Explain
that the coordinator arranges helpers and independent review; implementation
staffing is proposed when there is actual implementation ready to assign.

For GitHub settings, name the repository, proposed changes, and any decision
that affects the human. Follow the workflow's default of independent agent
review, passing CI, and coordinator integration with no GitHub approval click.
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

## Linear's GitHub integration

Guide the user through the workspace's Settings > Integrations > GitHub, then
the team's Automations page. Explain that GitHub repository access and a
workspace connection must both complete. If GitHub shows an existing installation
but Linear shows no connection, inspect the return flow and which workspace owns
the installation before recommending changes. Preserve other projects' access.

For the workflow's `devel` automation, use Branch-specific rules > Add branch on
the team Automations page. Verify linking and transitions against a real PR and
report manual updates separately. Follow [Linear's official GitHub setup](https://linear.app/docs/github)
for current UI and workspace restrictions rather than guessing from app permissions.
