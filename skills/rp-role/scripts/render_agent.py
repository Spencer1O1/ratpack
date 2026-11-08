#!/usr/bin/env python3
"""Render a Codex custom-agent definition from JSON stdin; never modify files."""

import json
import re
import sys
import tomllib


FIELDS = ("name", "description", "developer_instructions")


def render_agent(spec):
    if not isinstance(spec, dict) or set(spec) != set(FIELDS):
        raise ValueError("Provide exactly name, description, developer_instructions")
    if any(not isinstance(spec[k], str) or not spec[k].strip() for k in FIELDS):
        raise ValueError("Agent fields must be nonempty strings")
    if not re.fullmatch(r"ratpack_[a-z][a-z0-9_]*", spec["name"]):
        raise ValueError("Use a name like ratpack_research (lowercase snake_case)")
    lines = []
    for key in FIELDS:
        value = json.dumps(spec[key], ensure_ascii=False).replace("\x7f", "\\u007f")
        lines.append(f"{key} = {value}\n")
    rendered = "".join(lines)
    if tomllib.loads(rendered) != spec:
        raise ValueError("Agent definition did not round-trip as TOML")
    return rendered


def main():
    try:
        rendered = render_agent(json.load(sys.stdin))
    except (ValueError, UnicodeError) as error:
        print(f"Ratpack role: {error}", file=sys.stderr)
        return 1
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
