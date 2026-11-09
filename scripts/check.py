#!/usr/bin/env python3
"""Check packaged resources, Markdown links, and the project assignment file."""

from pathlib import Path
import re
import runpy
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
    adoption = runpy.run_path(str(Path(__file__).resolve().parents[1] / "skills/rp-bootstrap/scripts/adoption.py"))
    for relative in ("ratpack.json", "skills/rp-bootstrap/assets/project/ratpack.json"):
        try:
            adoption["validate_shared"](adoption["parse_json"]((ROOT / relative).read_bytes()))
        except ValueError as error:
            errors.append(f"{relative}: {error}")
    local_template = ROOT / "skills/rp-bootstrap/assets/local/ratpack.local.json"
    try:
        local = adoption["parse_json"](local_template.read_bytes())
        # A distributable template must not contain a real local identity.
        if not isinstance(local, dict) or local.get("coordinator") is not None:
            raise ValueError("Local template must be an object without an identity")
        adoption["validate_local"]({**local, "coordinator": "template-validation"})
    except (OSError, ValueError) as error:
        errors.append(str(error))
    if (ROOT / "skills/rp-bootstrap/assets/project/ratpack.local.json").exists():
        errors.append("Local configuration must not be packaged as shared project content")
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
