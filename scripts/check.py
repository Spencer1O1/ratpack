#!/usr/bin/env python3
"""Check packaged resources, Markdown links, and the project assignment file."""

import json
from pathlib import Path
import re
import tomllib
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
        "ratpack.json", "skills/rp-bootstrap/assets/project/ratpack.json"
    ]:
        config = json.loads((ROOT / relative).read_text())
        if config["schema_version"] != 1:
            errors.append(f"{relative}: unsupported schema version")
        limit = config["max_implementation_agents"]
        if limit is not None and (type(limit) is not int or limit < 0):
            errors.append(f"{relative}: worker limit must be null or a nonnegative integer")
        if not all(isinstance(c, str) and c for c in config["checks"]):
            errors.append(f"{relative}: checks must contain command strings")
    for path in (ROOT / "skills").glob("*/SKILL.md"):
        if not path.read_text().startswith(f"---\nname: {path.parent.name}\ndescription:"):
            errors.append(f"{path}: skill frontmatter missing name/description")
    assets = ROOT / "skills/rp-bootstrap/assets/project/.codex/agents"
    for path in assets.glob("*.toml"):
        profile = tomllib.loads(path.read_text())
        fields = ("name", "description", "developer_instructions")
        if not all(isinstance(profile.get(k), str) and profile[k].strip() for k in fields):
            errors.append(f"{path}: native profile missing required strings")
        local = ROOT / ".codex/agents" / path.name
        if not local.exists() or local.read_bytes() != path.read_bytes():
            errors.append(f"{local}: differs from packaged native profile")
    if errors:
        raise SystemExit("\n".join(errors))
    print("Packaged resources, local links, and configuration checks pass")


if __name__ == "__main__":
    check()
