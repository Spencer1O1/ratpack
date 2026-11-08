#!/usr/bin/env python3
"""Preview or add Ratpack starter files without overwriting project content."""

import argparse
import json
from pathlib import Path
import sys


SKILL = Path(__file__).resolve().parents[1]


def prepare(target, owner):
    """Preflight every output, including parent paths, before any writes."""
    target = Path(target).resolve()
    if not target.is_dir():
        raise ValueError("Target must be an existing project directory")
    if not owner.strip():
        raise ValueError("An integration owner is required")
    assets = SKILL / "assets/project"
    outputs = {
        path.relative_to(assets): path.read_bytes()
        for path in assets.rglob("*") if path.is_file()
    }
    config = json.loads(outputs[Path("ratpack.json")])
    config["integration_owner"] = owner.strip()
    outputs[Path("ratpack.json")] = (
        json.dumps(config, indent=2) + "\n"
    ).encode()
    outputs[Path("docs/development.md")] = (
        SKILL / "references/workflow.md"
    ).read_bytes()
    pending = []
    for relative, content in sorted(outputs.items()):
        path = target / relative
        for parent in [path, *path.parents]:
            if parent == target:
                break
            if parent.is_symlink():
                raise ValueError(f"Refusing symlink path: {relative}")
            if parent != path and parent.exists() and not parent.is_dir():
                raise ValueError(f"Parent is not a directory: {relative}")
        if path.exists():
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError(
                    f"Existing content differs: {relative}; reconcile manually"
                )
        else:
            pending.append((path, content))
    return target, pending


def bootstrap(target, owner, apply=False):
    target, pending = prepare(target, owner)
    for path, content in pending:
        print(f"{'ADD' if apply else 'WOULD ADD'} {path.relative_to(target)}")
        if apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation also prevents overwriting a concurrent writer.
            with path.open("xb") as handle:
                handle.write(content)
    if not pending:
        print("Starter files already match; no changes")
    elif not apply:
        print("Preview only; add --apply to write these files")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        bootstrap(args.target, args.owner, args.apply)
    except (OSError, ValueError) as error:
        print(f"Ratpack: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
