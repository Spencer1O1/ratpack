# Model selection at dispatch

Follow the adopted workflow's model policy and explicit project/user constraints.
Apply this to each assignment, not to a role permanently. Do not install policy
into an existing project as a side effect of ordinary coordination.

1. Inspect the current host's available models, supported effort levels, and
   spawn controls. Read the selected native profile for model/effort pins; a
   profile or host default can change the effective request. Prefer the current
   host inventory to stale model names. If comparison is needed, consult
   [official model guidance](https://developers.openai.com/api/docs/guides/model-selection).
2. Choose a model and effort together from the workflow's task criteria. On a
   host advertising them, `gpt-6-luna` at low/medium is a candidate for routine
   work, `gpt-6.1-sol` at medium for nontrivial implementation, and stronger
   available settings for demanding work. These are replaceable examples, not
   a required provider, benchmark result, or reason to force every task through
   the cheapest model first. Explicit user choices take precedence.
3. Apply the choice through the actual spawn parameters where supported. Merely
   writing a model name in a prompt does not change the model. If the host requires
   a fresh agent rather than a full-history fork for overrides, provide a bounded
   brief with ownership, requirements, source paths/revisions, checks, authority,
   and handoff route. Keep packaged role profiles model-neutral; preserve custom
   profile pins and disclose any conflict rather than silently editing them.
4. Record the requested choice/reason with the assignment. Use host runtime
   metadata to verify the effective model/effort when exposed; an agent's own
   assertion is not verification. If unsupported, keep it explicitly unverified.
   For human-created peers or an existing agent without a switch control, suggest
   settings in the handoff and retain its actual settings/ownership. Do not claim
   a follow-up message changed its model or replace it without a safe handoff.
5. Evaluate the deliverable and checks. On a capability failure, reassign/escalate
   with the failed evidence and remaining scope; maintain one active owner and
   repeat affected validation/review. Do not use a stronger model to bypass a
   missing credential, broken environment, or approval. Record available quality,
   repair/time and usage evidence on representative tasks; distinguish measured
   savings from an expected efficiency improvement.

For Codex, pass both model and effort when controlling both. Unspecified values
can inherit defaults; native profile pins may take precedence over spawn values.
Check the [current subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
and actual tool schema. If the tool cannot express or confirm the intended
settings, report that limitation without editing global configuration.
