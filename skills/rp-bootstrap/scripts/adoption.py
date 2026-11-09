"""Shared rendering, provenance, and project-path checks for adoption helpers."""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess


LOCK = "ratpack.lock.json"
LOCAL = "ratpack.local.json"
UPSTREAM = "https://github.com/ratpack-workflow/ratpack"
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


def render_outputs(skill):
    assets = skill / "assets/project"
    outputs = {}
    for path in assets.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Refusing symlink source asset: {path}")
        if path.is_file():
            relative = path.relative_to(assets).as_posix()
            relative_path(relative)
            if relative == LOCAL:
                raise ValueError("Local configuration must not be a shared asset")
            outputs[relative] = path.read_bytes()
    config = parse_json(outputs["ratpack.json"])
    outputs["ratpack.json"] = encode_json(config)
    outputs["docs/development.md"] = (skill / "references/workflow.md").read_bytes()
    return outputs


def source_provenance(skill, supplied=None):
    """Do not mistake an installed skill's enclosing project for its source."""
    if supplied is not None:
        if not isinstance(supplied, str) or not REVISION.fullmatch(supplied):
            raise ValueError("Source revision must be exactly 40 hexadecimal characters")
        return supplied.lower(), "supplied"

    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    git_command = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false"]

    def git(*args):
        return subprocess.run(
            [*git_command, "-C", str(skill), *args], check=True, capture_output=True,
            text=True, timeout=10, env=env,
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
                [*git_command, "-C", str(root), "show", f"{revision}:{path.relative_to(root).as_posix()}"],
                check=True, capture_output=True, timeout=10, env=env,
            ).stdout
            if committed != path.read_bytes():
                return None, "unknown"
        if REVISION.fullmatch(revision):
            return revision.lower(), "git-verified"
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return None, "unknown"


def make_manifest(outputs, revision, origin):
    if LOCAL in outputs:
        raise ValueError("Local configuration cannot be included in an adoption manifest")
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
        if name in (LOCK, LOCAL) or not isinstance(value, str) or not DIGEST.fullmatch(value):
            raise ValueError(f"Malformed adoption manifest file: {name}")
    for name in files:
        checked_path(target, name)
    return manifest


def validate_shared(config):
    if not isinstance(config, dict) or type(config.get("schema_version")) is not int or config["schema_version"] != 2:
        raise ValueError("Shared configuration requires schema_version 2; reconcile legacy configuration deliberately")
    if config.get("merge_policy") != "designated-integration-owner":
        raise ValueError("merge_policy must be designated-integration-owner")
    if any(key in config for key in ("integration_owner", "max_implementation_agents", "coordinator", "model_preferences")):
        raise ValueError("Personal owner/staffing fields do not belong in shared configuration")
    commands = config.get("checks")
    if not isinstance(commands, list) or any(not isinstance(c, str) or not c.strip() for c in commands):
        raise ValueError("checks must be a list of nonempty command strings")
    roles = config.get("custom_roles")
    if not isinstance(roles, dict) or not all(isinstance(k, str) and k.strip() and (
            isinstance(v, str) and v.strip() or isinstance(v, dict) and bool(v)) for k, v in roles.items()):
        raise ValueError("custom_roles must map names to nonempty briefs or objects")
    for key in ("github_repository", "linear_team"):
        if key not in config or config[key] is not None and (not isinstance(config[key], str) or not config[key].strip()):
            raise ValueError(key + " must be a nonempty string or null")


def validate_local(config):
    if not isinstance(config, dict) or type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ValueError("Local configuration requires schema_version 1")
    if not isinstance(config.get("coordinator"), str) or not config["coordinator"].strip():
        raise ValueError("Local coordinator must be nonempty")
    count = config.get("max_implementation_agents")
    if "max_implementation_agents" not in config or not (count is None or type(count) is int and count >= 0):
        raise ValueError("Local max_implementation_agents must be null or a nonnegative integer")
    if "model_preferences" in config and not isinstance(config["model_preferences"], dict):
        raise ValueError("Local model_preferences must be an object")
    if set(config) - {"schema_version", "coordinator", "max_implementation_agents", "model_preferences"}:
        raise ValueError("Unsupported local configuration fields")


def require_safe_ignore(target):
    path = checked_path(target, ".gitignore")
    guidance = "Add /ratpack.local.json at the end of the root .gitignore manually, then rerun; existing ignore content is preserved"
    if not path.exists():
        raise ValueError(guidance)
    lines = path.read_text().splitlines()
    rules = [line for line in lines if line.strip() and not line.startswith("#")]
    if "/ratpack.local.json" not in rules:
        raise ValueError(guidance)
    last = len(rules) - 1 - rules[::-1].index("/ratpack.local.json")
    if any(line.startswith("!") for line in rules[last + 1:]):
        raise ValueError(guidance + "; later negation rules cannot be verified safely")
    require_untracked_local(target)


def require_untracked_local(target):
    # Ignoring a path cannot protect a file already tracked in Git.
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    env["LC_ALL"] = "C"
    command = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(target)]
    repository = subprocess.run([*command, "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True, env=env, timeout=10)
    if repository.returncode:
        # Exit 128 also reports unreadable repositories and unsafe ownership.
        # Accept only Git's ordinary non-repository diagnostic, with no existing
        # repository metadata that could conceal an inaccessible index. Empty
        # .git directories (including temporary-directory discovery guards) do
        # not constitute repository metadata.
        diagnostic = repository.stderr.strip()
        ordinary_nonrepo = diagnostic == (
            "fatal: not a git repository (or any of the parent directories): .git") or bool(re.fullmatch(
                r"fatal: not a git repository \(or any parent up to mount point [^\n]+\)\n"
                r"Stopping at filesystem boundary \(GIT_DISCOVERY_ACROSS_FILESYSTEM not set\)\.", diagnostic))
        if ordinary_nonrepo:
            for parent in (target, *target.parents):
                marker = parent / ".git"
                try:
                    marker.lstat()
                except FileNotFoundError:
                    continue
                if marker.is_symlink() or not marker.is_dir() or any(marker.iterdir()):
                    ordinary_nonrepo = False
                    break
        if ordinary_nonrepo:
            return
        raise ValueError("Unable to verify whether local configuration is tracked; Git repository inspection failed")
    if repository.stdout.strip() != "true":
        raise ValueError("Local configuration requires a Git worktree or a directory outside Git")
    result = subprocess.run([*command, "ls-files", "--", LOCAL],
                            capture_output=True, text=True, env=env, timeout=10)
    if result.returncode:
        raise ValueError("Unable to verify whether local configuration is tracked; Git index inspection failed")
    if result.stdout.strip():
        raise ValueError("ratpack.local.json is already tracked; reconcile and untrack it deliberately before joining")
