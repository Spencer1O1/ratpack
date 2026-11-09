#!/usr/bin/env python3
"""Preview adoption changes against recorded byte hashes; never apply changes."""

import argparse
import difflib
import importlib.util
import json
from pathlib import Path
import sys


SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ratpack_adoption", Path(__file__).with_name("adoption.py"))
adoption = importlib.util.module_from_spec(SPEC)
# Avoid creating bytecode files as a side effect of a read-only preview.
exec(compile(Path(SPEC.origin).read_bytes(), SPEC.origin, "exec"), adoption.__dict__)


def classify(baseline, current, candidate):
    """Three-way comparison, including upstream/local deletions and collisions."""
    current_hash = adoption.digest(current) if current is not None else None
    candidate_hash = adoption.digest(candidate) if candidate is not None else None
    if baseline is None:
        if current is None:
            return "added"
        return "unchanged" if current == candidate else "conflict"
    if candidate is None:
        return "removed" if current_hash in (None, baseline) else "conflict"
    if current == candidate:
        return "unchanged"
    if current_hash == baseline:
        return "upstream-only"
    if candidate_hash == baseline:
        return "local-only"
    return "conflict"


def difference(name, current, candidate):
    if current == candidate:
        return ""
    try:
        before = (current or b"").decode("utf-8").splitlines(keepends=True)
        after = (candidate or b"").decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError:
        return None
    # Keep unterminated lines readable without concealing their difference.
    lines = difflib.unified_diff(before, after, fromfile=f"current/{name}", tofile=f"candidate/{name}")
    return "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n" for line in lines)


def preview(target, source_revision=None):
    target = adoption.project_root(target)
    manifest = adoption.load_manifest(target)
    warnings = []
    if manifest is None:
        warnings.append("No adoption manifest: baseline unknown; manual adoption required; no three-way classification")
    elif manifest["source_revision"] is None:
        warnings.append("Adopted upstream revision unknown; comparisons use recorded byte hashes only")
    elif manifest.get("source_revision_origin") != "git-verified":
        warnings.append("Adopted source revision is not recorded as Git-verified")
    revision, origin = adoption.source_provenance(SKILL, source_revision)
    if origin == "unknown":
        warnings.append("Candidate upstream revision unknown; no clean source Git provenance available")
    elif origin == "supplied":
        warnings.append("Candidate source revision supplied; not verified against source Git bytes")

    config_path = adoption.checked_path(target, "ratpack.json")
    if config_path.exists():
        try:
            config = adoption.parse_json(config_path.read_bytes())
            adoption.validate_shared(config)
        except ValueError as error:
            warnings.append(f"Manual configuration reconciliation required: {error}; existing configuration and manifest are preserved")
    candidate = adoption.render_outputs(SKILL)
    baseline = manifest["files"] if manifest is not None else {}
    names = sorted(set(baseline) | set(candidate))
    paths = {name: adoption.checked_path(target, name) for name in names}
    records = []
    for name, path in paths.items():
        current = path.read_bytes() if path.exists() else None
        proposed = candidate.get(name)
        status = classify(baseline.get(name), current, proposed) if manifest else "unknown"
        record = {
            "path": name, "status": status,
            "baseline_sha256": baseline.get(name),
            "current_sha256": adoption.digest(current) if current is not None else None,
            "candidate_sha256": adoption.digest(proposed) if proposed is not None else None,
            "diff": difference(name, current, proposed),
        }
        if name == "ratpack.json" and (status != "unchanged" or manifest is None):
            record["manual_reconciliation"] = True
            warnings.append("ratpack.json needs manual configuration reconciliation: retain owner, worker count, custom roles, and other legacy/project settings during deliberate shared/local reconciliation; local settings confer no merge authority; the diff compares upstream defaults, not a replacement plan. Hashes cannot recover old field-level defaults.")
        if record["diff"] is None:
            warnings.append(f"{name}: binary content differs; text diff unavailable")
        records.append(record)
    return {
        "preview_only": True,
        "adopted_source_revision": manifest["source_revision"] if manifest else None,
        "candidate_source_revision": revision,
        "candidate_source_revision_origin": origin,
        "upstream_repository": adoption.UPSTREAM,
        "warnings": warnings,
        "files": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--source-revision", help="Supplied upstream SHA (40 hex; not Git-verified)")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable preview")
    args = parser.parse_args()
    try:
        report = preview(args.project, args.source_revision)
    except (OSError, ValueError) as error:
        print(f"Ratpack: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Preview only; no files or settings will be changed")
        print(f"Adopted source: {report['adopted_source_revision'] or 'unknown'}")
        print(f"Candidate source: {report['candidate_source_revision'] or 'unknown'} ({report['candidate_source_revision_origin']})")
        for warning in report["warnings"]:
            print(f"WARNING: {warning}")
        for record in report["files"]:
            print(f"{record['status'].upper()} {record['path']}")
            if record["diff"]:
                print(record["diff"], end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
