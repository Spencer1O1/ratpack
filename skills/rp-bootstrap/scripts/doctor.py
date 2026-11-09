#!/usr/bin/env python3
"""Inspect an adopted Ratpack project without writing files or contacting services."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import runpy
import subprocess
import sys
import tomllib


ADOPTION = runpy.run_path(str(Path(__file__).with_name("adoption.py")))


PROFILES = (
    "ratpack_coordinator", "ratpack_implementor", "ratpack_reviewer",
    "ratpack_cleanup", "ratpack_workflow",
)


def project_path(root, relative):
    """Accept portable project-relative paths and refuse symlink traversal."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("expected a nonempty relative POSIX path")
    parts = PurePosixPath(relative).parts
    if PurePosixPath(relative).is_absolute() or any(p in (".", "..") for p in relative.split("/")):
        raise ValueError("path must stay inside the project")
    if not parts or ":" in parts[0]:
        raise ValueError("path must stay inside the project")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("symlink paths are not inspected")
    return path


def check_configuration(root, add):
    try:
        config = ADOPTION["parse_json"](project_path(root, "ratpack.json").read_bytes())
        if not isinstance(config, dict):
            raise ValueError("expected an object")
    except (OSError, UnicodeError, ValueError):
        add("configuration", "fail", "ratpack.json must be a readable JSON object inside the project.")
        config = None
    if config is not None:
        version = config.get("schema_version")
        if type(version) is int and version == 1:
            add("configuration.schema", "warn", "Legacy shared schema 1: reconcile owner and staffing into local settings deliberately; no files were rewritten.")
            owner = config.get("integration_owner")
            add("configuration.owner", "pass" if isinstance(owner, str) and owner.strip() else "fail",
                "Legacy integration owner is recorded; reconcile current merge authority deliberately." if isinstance(owner, str) and owner.strip()
                else "Legacy integration_owner is absent or invalid; reconcile shared/local configuration deliberately.")
            count = config.get("max_implementation_agents")
            count_valid = "max_implementation_agents" in config and (count is None or type(count) is int and count >= 0)
            if not count_valid:
                add("configuration.staffing", "fail", "Use a nonnegative integer or null implementation worker count.")
            elif count is None:
                add("configuration.staffing", "warn", "Propose an implementor count when implementation is ready to start.")
            elif count == 0:
                add("configuration.staffing", "pass", "No implementation helpers are requested; independent review remains part of the workflow.")
            else:
                add("configuration.staffing", "pass", "An implementation worker limit is recorded; human approval was not independently verified.")
        else:
            try:
                ADOPTION["validate_shared"](config)
            except ValueError as error:
                add("configuration.schema", "fail", str(error))
            else:
                add("configuration.schema", "pass", "Shared schema 2 records project policy; merge authority requires explicit designation.")
        if "implementation_delegation_authorized" in config:
            add("configuration.legacy_delegation", "warn", "Retired delegation flag found; reconcile with explicit human instructions when adopting the current workflow.")
        commands = config.get("checks")
        if not isinstance(commands, list) or any(not isinstance(c, str) or not c.strip() for c in commands):
            add("configuration.checks", "fail", "checks must be a list of nonempty command strings.")
        elif not commands:
            add("configuration.checks", "warn", "No project check commands are configured.")
        else:
            add("configuration.checks", "unverified", "Project check commands are configured but were not executed.")
        roles = config.get("custom_roles")
        valid_roles = isinstance(roles, dict) and all(
            isinstance(k, str) and k.strip() and (
                isinstance(v, str) and v.strip() or isinstance(v, dict) and bool(v)
            ) for k, v in roles.items()
        )
        add("configuration.roles", "pass" if valid_roles else "fail",
            "Custom role records have supported container types; role semantics were not evaluated."
            if valid_roles else "custom_roles must map nonempty names to nonempty briefs or objects.")
        for key, label in (("github_repository", "GitHub"), ("linear_team", "Linear")):
            value = config.get(key)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                add("configuration." + key, "fail", key + " must be a nonempty string or null.")
            else:
                add("integration." + label.lower(), "unverified",
                    label + (" reference is configured; service access and automation were not checked."
                             if value else " is not configured; manual tracking remains possible."))
    add("integration.protections", "unverified", "Remote branch protections, required approvals, and CI results were not checked.")


def check_local(root, add):
    try:
        path = ADOPTION["checked_path"](root, ADOPTION["LOCAL"])
        if not path.exists():
            add("local.configuration", "warn", "No local pack configured; join with bootstrap.py TARGET --local --coordinator NAME.")
            return
        ADOPTION["validate_local"](ADOPTION["parse_json"](path.read_bytes()))
        ADOPTION["require_safe_ignore"](root)
        add("local.configuration", "pass", "Local coordinator and staffing are valid and ignored; these settings grant no merge authority.")
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError) as error:
        add("local.configuration", "fail", str(error))


def check_git(root, add):
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")

    def git(*args):
        return subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                              capture_output=True, text=True, env=env, timeout=10)

    try:
        repo = git("rev-parse", "--show-toplevel")
        if repo.returncode:
            add("git.repository", "warn", "No local Git worktree found; branch setup remains unconfigured.")
        else:
            add("git.repository", "pass", "Local Git worktree found; the current checkout need not be devel.")
            for branch in ("main", "devel"):
                local = git("show-ref", "--verify", "--quiet", "refs/heads/" + branch)
                remote = git("show-ref", "--verify", "--quiet", "refs/remotes/origin/" + branch)
                if local.returncode == 0 or remote.returncode == 0:
                    add("git." + branch, "pass", "Branch ref exists locally; remote freshness was not checked.")
                else:
                    add("git." + branch, "fail", "Required main/devel branch ref is absent locally; no fetch was attempted.")
    except (OSError, subprocess.TimeoutExpired):
        add("git.repository", "warn", "Git inspection is unavailable; branch setup was not verified.")


def check_profiles(root, native, add):
    try:
        directory = project_path(root, ".codex/agents")
        if directory.exists() and not directory.is_dir():
            raise ValueError("profile path is not a directory")
        paths = sorted(directory.glob("*.toml")) if directory.is_dir() else []
        found = set()
        for path in paths:
            relative = path.relative_to(root).as_posix()
            profile = tomllib.loads(project_path(root, relative).read_text())
            fields = ("name", "description", "developer_instructions")
            if not all(isinstance(profile.get(f), str) and profile[f].strip() for f in fields):
                raise ValueError("profile missing fields")
            if profile["name"] in found:
                raise ValueError("duplicate native names")
            found.add(profile["name"])
        missing = set(PROFILES) - found
        if native and missing:
            add("profiles.files", "fail", "Native mode is missing required profiles: " + ", ".join(sorted(missing)) + ". Preview adoption changes before reconciling profile names.")
        elif paths:
            add("profiles.files", "pass", "Present native profile files parse and have unique names and required strings.")
        else:
            add("profiles.files", "warn", "No native profiles configured; human-created peers/manual contributors are supported.")
    except (OSError, UnicodeError, ValueError, tomllib.TOMLDecodeError):
        add("profiles.files", "fail", "Native profile files must be safe, valid TOML with unique names and required strings.")
    add("profiles.runtime", "unverified", "Native runtime discovery, trust, permissions, and successful spawning were not checked.")


def check_adoption(root, add):
    try:
        manifest = ADOPTION["load_manifest"](root)
        if manifest is None:
            add("adoption", "unverified", "No adoption record found; legacy project provenance is unknown.")
            return
        changed = sum(
            not (path := project_path(root, name)).is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
            for name, digest in manifest["files"].items()
        )
        add("adoption.files", "warn" if changed else "pass",
            str(changed) + " adopted files differ or are missing; inspect customization/drift before upgrade."
            if changed else "Adopted file bytes match their recorded baseline hashes.")
        add("adoption.source", "unverified",
            "A source revision is recorded; this command does not verify its historical or remote provenance."
            if manifest["source_revision"] else "The adoption source revision is unknown.")
    except (OSError, UnicodeError, ValueError):
        add("adoption", "fail", "Adoption record must contain supported schema, revision, and safe project-relative SHA256 file entries.")


def inspect_project(target, workflow="docs/development.md", native=False):
    root = Path(target).resolve()
    checks = []

    def add(name, status, detail):
        checks.append(dict(name=name, status=status, detail=detail))

    def finish():
        return dict(ok=not any(c["status"] == "fail" for c in checks), checks=checks)

    if not root.is_dir():
        add("project", "fail", "Project must be an existing directory.")
        return finish()

    for name, relative in (("instructions", "AGENTS.md"), ("contributors", "CONTRIBUTING.md"),
                           ("workflow", workflow)):
        try:
            path = project_path(root, relative)
            if not path.is_file():
                raise ValueError("required file is missing")
            with path.open("rb") as stream:
                if not stream.read(1):
                    raise ValueError("required file is empty")
        except (OSError, ValueError):
            add(name, "fail", "Required project file is missing, empty, unreadable, or unsafe.")
        else:
            add(name, "pass", "Required project file exists; policy semantics were not evaluated.")

    check_configuration(root, add)
    check_local(root, add)
    check_git(root, add)
    check_profiles(root, native, add)
    check_adoption(root, add)
    return finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--workflow", default="docs/development.md", help="project-relative workflow path")
    parser.add_argument("--native", action="store_true", help="require all five native profile files")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    args = parser.parse_args()
    report = inspect_project(args.project, args.workflow, args.native)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for item in report["checks"]:
            print(f'{item["status"].upper()} {item["name"]}: {item["detail"]}')
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
