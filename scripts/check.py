#!/usr/bin/env python3
"""Check packaged resources, Markdown links, and the project assignment file."""

import json
from pathlib import Path
import re
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    for path in ROOT.rglob("*.md"):
        # Asset links refer to generated project files, checked in bootstrap tests.
        if "assets" in path.relative_to(ROOT).parts:
            continue
        text = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
        for link in re.findall(r"\]\(([^)]+)\)", text):
            link = link.strip("<>")
            if re.match(r"[a-zA-Z]+:", link) or link.startswith("#"):
                continue
            target = path.parent / unquote(link.split("#")[0])
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing {link}")
    for relative in [
        "ratpack.json", "skills/ratpack/assets/project/ratpack.json"
    ]:
        config = json.loads((ROOT / relative).read_text())
        if config["schema_version"] != 1:
            errors.append(f"{relative}: unsupported schema version")
        limit = config["max_implementation_agents"]
        if type(limit) is not int or limit < 1:
            errors.append(f"{relative}: worker limit must be a positive integer")
        if type(config["implementation_delegation_authorized"]) is not bool:
            errors.append(f"{relative}: delegation authorization must be boolean")
        if not all(isinstance(c, str) and c for c in config["checks"]):
            errors.append(f"{relative}: checks must contain command strings")
    skill = (ROOT / "skills/ratpack/SKILL.md").read_text()
    if not skill.startswith("---\nname: ratpack\ndescription:"):
        errors.append("Skill frontmatter missing name/description")
    if errors:
        raise SystemExit("\n".join(errors))
    print("Packaged resources, local links, and configuration checks pass")


if __name__ == "__main__":
    check()
