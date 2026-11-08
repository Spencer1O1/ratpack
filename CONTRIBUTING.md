# Contributing to Ratpack

Follow the [contributor workflow](skills/rp-bootstrap/references/workflow.md).
Agents also read [AGENTS.md](AGENTS.md).

Run with Python 3.11 or newer; the helpers use only the standard library:

```bash
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

For skill or template changes, also exercise the affected procedure in an
isolated adoption scenario, including existing files and unavailable
integrations. Report what was tested and what remains unverified.

Workflow changes also use the cases in `tests/scenarios/workflow.json`. Export
blind prompts with `python3 scripts/scenarios.py --prompts`, have an independent
evaluator use the project workflow and relevant skill, then grade its saved JSON
with `python3 scripts/scenarios.py --grade /path/to/responses.json`. Keep expected
answers out of the evaluator's context. Review the reasons as well as the grade.
This checks policy interpretation; helper tests exercise actual local behavior.
Cases include subagent, human-created-peer, and manual-tracking arrangements.
