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
