# Ratpack repository instructions

Follow [CONTRIBUTING.md](CONTRIBUTING.md). This repository maintains the reusable
workflow; adopting projects retain their own product plans and configuration.

- Shared policy belongs in `skills/rp-bootstrap/references/workflow.md`.
  Skills describe procedures; native profiles select role briefs; the README
  is an entry point. Link policy instead of copying it between these layers.
- Keep repository authority, staffing, and custom roles in that repository's
  `ratpack.json`; keep task ownership and dependencies in its tracker.
- Keep packaged profiles and this repository's `.codex/agents/` copies aligned.
  Bootstrap changes must preserve preview, idempotence, and conflict protection.
- Keep credentials and adopting projects' private data out of this public repo.
  Initial publication is authorized; releases still require user approval.
