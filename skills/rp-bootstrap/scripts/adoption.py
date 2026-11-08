"""Shared rendering, provenance, and project-path checks for adoption helpers."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


LOCK = "ratpack.lock.json"
UPSTREAM = "https://github.com/Spencer1O1/ratpack"
REVISION = re.compile(r"[0-9a-fA-F]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def digest(content):
    return hashlib.sha256(content).hexdigest()


def project_root(target):
    target = Path(target)
    if target.is_symlink():
        raise ValueError("Refusing symlink project directory")
    target = target.resolve()
    if not target.is_dir():
        raise ValueError("Target must be an existing project directory")
    return target


def relative_path(value):
    """Accept only canonical relative POSIX names, including hidden files."""
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        raise ValueError(f"Unsafe managed path: {value!r}")
    path = PurePosixPath(value)
    if (path.is_absolute() or path.as_posix() != value
            or any(part in (".", "..") or ":" in part for part in value.split("/"))):
        raise ValueError(f"Unsafe managed path: {value!r}")
    return path


def checked_path(target, relative):
    relative = relative_path(str(relative))
    path = target
    for index, part in enumerate(relative.parts):
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Refusing symlink path: {relative}")
        if path.exists():
            if index < len(relative.parts) - 1 and not path.is_dir():
                raise ValueError(f"Parent is not a directory: {relative}")
            if index == len(relative.parts) - 1 and not path.is_file():
                raise ValueError(f"Managed path is not a file: {relative}")
    return path


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(content):
    return json.loads(content, object_pairs_hook=_unique_object)


def encode_json(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def render_outputs(skill, owner=None):
    assets = skill / "assets/project"
    outputs = {}
    for path in assets.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Refusing symlink source asset: {path}")
        if path.is_file():
            relative = path.relative_to(assets).as_posix()
            relative_path(relative)
            outputs[relative] = path.read_bytes()
    config = parse_json(outputs["ratpack.json"])
    if owner is not None:
        config["integration_owner"] = owner
    outputs["ratpack.json"] = encode_json(config)
    outputs["docs/development.md"] = (skill / "references/workflow.md").read_bytes()
    return outputs


def source_provenance(skill, supplied=None):
    """Do not mistake an installed skill's enclosing project for its source."""
    if supplied is not None:
        if not isinstance(supplied, str) or not REVISION.fullmatch(supplied):
            raise ValueError("Source revision must be exactly 40 hexadecimal characters")
        return supplied.lower(), "supplied"

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(skill), *args], check=True, capture_output=True,
            text=True, timeout=10,
        ).stdout.strip()

    try:
        root = Path(git("rev-parse", "--show-toplevel")).resolve()
        if skill.resolve() != root / "skills/rp-bootstrap":
            return None, "unknown"
        if git("status", "--porcelain", "--untracked-files=all"):
            return None, "unknown"
        inputs = [path for path in (skill / "assets/project").rglob("*") if path.is_file()]
        inputs += [skill / "references/workflow.md"]
        inputs += list((skill / "scripts").glob("*.py"))
        git("ls-files", "--error-unmatch", "--", *[
            path.relative_to(skill).as_posix() for path in inputs
        ])
        revision = git("rev-parse", "HEAD")
        # Git status can hide assume-unchanged files; verify actual input bytes.
        for path in inputs:
            committed = subprocess.run(
                ["git", "-C", str(root), "show", f"{revision}:{path.relative_to(root).as_posix()}"],
                check=True, capture_output=True, timeout=10,
            ).stdout
            if committed != path.read_bytes():
                return None, "unknown"
        if REVISION.fullmatch(revision):
            return revision.lower(), "git-verified"
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return None, "unknown"


def make_manifest(outputs, revision, origin):
    return {
        "schema_version": 1,
        "source_revision": revision,
        "upstream_repository": UPSTREAM,
        "source_revision_origin": origin,
        "files": {path: digest(content) for path, content in sorted(outputs.items())},
    }


def load_manifest(target):
    path = checked_path(target, LOCK)
    if not path.exists():
        return None
    manifest = parse_json(path.read_bytes())
    if not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int:
        raise ValueError("Malformed adoption manifest schema_version")
    if manifest["schema_version"] != 1:
        raise ValueError("Unsupported adoption manifest schema_version")
    revision = manifest.get("source_revision")
    if "source_revision" not in manifest or (revision is not None and (
            not isinstance(revision, str) or not REVISION.fullmatch(revision))):
        raise ValueError("Malformed adoption manifest source_revision")
    upstream = manifest.get("upstream_repository")
    if not isinstance(upstream, str) or not upstream.strip():
        raise ValueError("Malformed adoption manifest upstream_repository")
    origin = manifest.get("source_revision_origin")
    if origin is not None and origin not in ("supplied", "git-verified", "unknown"):
        raise ValueError("Malformed adoption manifest source_revision_origin")
    if (origin == "unknown" and revision is not None) or (
            origin in ("supplied", "git-verified") and revision is None):
        raise ValueError("Inconsistent adoption manifest provenance")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Malformed adoption manifest files")
    # Validate all names before inspecting any managed content.
    for name, value in files.items():
        relative_path(name)
        if name == LOCK or not isinstance(value, str) or not DIGEST.fullmatch(value):
            raise ValueError(f"Malformed adoption manifest file: {name}")
    for name in files:
        checked_path(target, name)
    return manifest
