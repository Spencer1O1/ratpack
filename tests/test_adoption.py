import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills/rp-bootstrap"
SHA = "1234567890abcdef1234567890abcdef12345678"


def load_script(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


class AdoptionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source_root = self.root / "source"
        self.skill = self.source_root / "skills/rp-bootstrap"
        shutil.copytree(SOURCE, self.skill, ignore=shutil.ignore_patterns("__pycache__"))
        self.target = self.root / "project"
        self.target.mkdir()
        self.bootstrap = load_script(self.skill / "scripts/bootstrap.py")
        self.upgrade = load_script(self.skill / "scripts/upgrade.py")
        self.adoption = self.bootstrap.adoption

    def install(self, revision=SHA):
        with contextlib.redirect_stdout(io.StringIO()):
            self.bootstrap.bootstrap(self.target, "human-coordinator", True, revision)

    def lock(self):
        return json.loads((self.target / "ratpack.lock.json").read_text())

    def write_lock(self, manifest):
        (self.target / "ratpack.lock.json").write_text(json.dumps(manifest))

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.source_root), *args],
                              check=True, capture_output=True, text=True).stdout.strip()

    def commit_source(self):
        self.git("init", "--quiet")
        (self.source_root / ".gitignore").write_text("__pycache__/\n*.pyc\n")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "--quiet", "-m", "Source fixture")
        return self.git("rev-parse", "HEAD")

    def test_manifest_records_exact_generated_bytes_and_supplied_origin(self):
        self.install()
        manifest = self.lock()
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["source_revision"], SHA)
        self.assertEqual(manifest["source_revision_origin"], "supplied")
        self.assertEqual(manifest["upstream_repository"], self.adoption.UPSTREAM)
        files = {str(p.relative_to(self.target)) for p in self.target.rglob("*") if p.is_file()}
        self.assertEqual(set(manifest["files"]), files - {"ratpack.lock.json"})
        for name, digest in manifest["files"].items():
            self.assertEqual(digest, hashlib.sha256((self.target / name).read_bytes()).hexdigest())

    def test_standalone_source_is_unknown_unless_revision_supplied(self):
        self.install(revision=None)
        self.assertIsNone(self.lock()["source_revision"])
        self.assertEqual(self.lock()["source_revision_origin"], "unknown")
        before = snapshot(self.target)
        # A matching rerun preserves the original record even if source metadata changes.
        with patch.object(self.adoption, "source_provenance", return_value=(SHA, "git-verified")):
            with contextlib.redirect_stdout(io.StringIO()):
                self.bootstrap.bootstrap(self.target, "human-coordinator", True)
        self.assertEqual(before, snapshot(self.target))
        self.assertIn("unknown", " ".join(self.upgrade.preview(self.target)["warnings"]))

    def test_only_clean_actual_source_git_can_be_verified(self):
        head = self.commit_source()
        self.assertEqual(self.adoption.source_provenance(self.skill), (head, "git-verified"))
        workflow = self.skill / "references/workflow.md"
        # Even a modification hidden from git status cannot claim exact source provenance.
        self.git("update-index", "--assume-unchanged", "skills/rp-bootstrap/references/workflow.md")
        workflow.write_text(workflow.read_text() + "\nLocal source customization\n")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.adoption.source_provenance(self.skill), (None, "unknown"))
        self.assertEqual(self.adoption.source_provenance(self.skill, SHA), (SHA, "supplied"))

    def test_unrelated_enclosing_git_repository_is_not_source_provenance(self):
        self.commit_source()
        installed = self.source_root / "plugins/rp-bootstrap"
        shutil.copytree(self.skill, installed, ignore=shutil.ignore_patterns("__pycache__"))
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "--quiet", "-m", "Installed copy")
        self.assertEqual(self.adoption.source_provenance(installed), (None, "unknown"))

    def test_invalid_revision_and_legacy_adoption_do_not_write(self):
        for revision in ["main", "a" * 39, "g" * 40]:
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                self.bootstrap.prepare(self.target, "owner", revision)
        self.assertEqual(list(self.target.iterdir()), [])
        (self.target / "ratpack.json").write_text('{"integration_owner":"existing"}')
        before = snapshot(self.target)
        with self.assertRaisesRegex(ValueError, "baseline unknown"):
            self.install()
        self.assertEqual(before, snapshot(self.target))

    def test_rerun_cannot_relabel_adoption_or_write_through_symlinked_lock(self):
        self.install()
        before = snapshot(self.target)
        with self.assertRaisesRegex(ValueError, "provenance differs"):
            self.bootstrap.prepare(self.target, "human-coordinator", "f" * 40)
        self.assertEqual(before, snapshot(self.target))
        lock = self.target / "ratpack.lock.json"
        outside = self.root / "outside-manifest.json"
        outside.write_bytes(lock.read_bytes())
        lock.unlink()
        lock.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.bootstrap.prepare(self.target, "human-coordinator", SHA)
        self.assertEqual(outside.read_bytes(), before["ratpack.lock.json"][0])

    def test_three_way_preview_classifies_changes_and_preserves_project(self):
        self.install()
        # Upstream-only, local-only, conflicting, removed, added, and unchanged files.
        upstream = self.skill / "assets/project/CONTRIBUTING.md"
        upstream.write_text(upstream.read_text() + "\nUpstream addition\n")
        local = self.target / "AGENTS.md"
        local.write_text(local.read_text() + "\nProject policy\n")
        workflow = self.skill / "references/workflow.md"
        workflow.write_text(workflow.read_text() + "\nNew shared policy\n")
        development = self.target / "docs/development.md"
        development.write_text(development.read_text() + "\nProject workflow\n")
        removed = self.skill / "assets/project/.codex/agents/ratpack_cleanup.toml"
        removed.unlink()
        (self.skill / "assets/project/new.md").write_text("A newly packaged file\n")
        unknown = self.target / "private-project-notes.txt"
        unknown.write_text("Keep unknown files untouched\n")
        before = snapshot(self.target)
        report = self.upgrade.preview(self.target, SHA)
        self.assertEqual(before, snapshot(self.target))
        records = {r["path"]: r for r in report["files"]}
        expected = {
            "CONTRIBUTING.md": "upstream-only", "AGENTS.md": "local-only",
            "docs/development.md": "conflict", "new.md": "added",
            ".codex/agents/ratpack_cleanup.toml": "removed", "ratpack.json": "unchanged",
        }
        for name, status in expected.items():
            self.assertEqual(records[name]["status"], status, name)
        self.assertNotIn(unknown.name, records)
        self.assertIn("+Upstream addition", records["CONTRIBUTING.md"]["diff"])
        self.assertIn("-Project workflow", records["docs/development.md"]["diff"])
        self.assertIn("+New shared policy", records["docs/development.md"]["diff"])
        self.assertIn("--- current/new.md", records["new.md"]["diff"])
        self.assertIn("+++ candidate/", records[removed.relative_to(self.skill / "assets/project").as_posix()]["diff"])

    def test_local_deletion_upstream_removal_and_new_file_collisions(self):
        self.install()
        (self.target / "AGENTS.md").unlink()
        (self.target / "CONTRIBUTING.md").unlink()
        upstream = self.skill / "assets/project/CONTRIBUTING.md"
        upstream.write_text(upstream.read_text() + "Upstream change\n")
        removed = ".codex/agents/ratpack_cleanup.toml"
        (self.skill / "assets/project" / removed).unlink()
        (self.target / removed).write_text("Locally modified retired profile\n")
        (self.skill / "assets/project/collision.md").write_text("upstream\n")
        (self.target / "collision.md").write_text("local\n")
        statuses = {r["path"]: r["status"] for r in self.upgrade.preview(self.target)["files"]}
        self.assertEqual(statuses["AGENTS.md"], "local-only")
        self.assertEqual(statuses["CONTRIBUTING.md"], "conflict")
        self.assertEqual(statuses[removed], "conflict")
        self.assertEqual(statuses["collision.md"], "conflict")

    def test_custom_configuration_survives_and_requires_manual_reconciliation(self):
        self.install()
        path = self.target / "ratpack.json"
        config = json.loads(path.read_text())
        config.update(integration_owner="new-human-owner", max_implementation_agents=7,
                      custom_roles={"research": "Project research role"}, private_setting={"keep": True})
        path.write_text(json.dumps(config, indent=4) + "\n")
        template = self.skill / "assets/project/ratpack.json"
        defaults = json.loads(template.read_text())
        defaults["new_upstream_default"] = False
        template.write_text(json.dumps(defaults))
        before = snapshot(self.target)
        report = self.upgrade.preview(self.target)
        self.assertEqual(before, snapshot(self.target))
        record = next(r for r in report["files"] if r["path"] == "ratpack.json")
        self.assertEqual(record["status"], "conflict")
        self.assertTrue(record["manual_reconciliation"])
        self.assertTrue(any("retain owner, worker count, custom roles" in warning for warning in report["warnings"]))
        self.assertEqual(json.loads(path.read_text()), config)

    def test_missing_manifest_never_guesses_a_baseline(self):
        self.install()
        (self.target / "ratpack.lock.json").unlink()
        before = snapshot(self.target)
        report = self.upgrade.preview(self.target)
        self.assertIsNone(report["adopted_source_revision"])
        self.assertTrue(all(r["status"] == "unknown" for r in report["files"]))
        self.assertTrue(any("manual adoption required" in w for w in report["warnings"]))
        self.assertEqual(before, snapshot(self.target))

    def test_unsafe_manifest_paths_and_malformed_records_reject_before_content_reads(self):
        self.install()
        valid = self.lock()
        bad_records = [
            {**valid, "schema_version": True}, {**valid, "schema_version": 2},
            {**valid, "source_revision": "main"}, {**valid, "files": []},
            {**valid, "files": {"AGENTS.md": "not-sha256"}},
            {**valid, "source_revision_origin": "unknown"},
        ]
        for name in ["../secret", "/tmp/secret", "a/../../secret", "a//b", "./a", "a/", "a\\b", "C:/secret", "ratpack.lock.json"]:
            bad_records.append({**valid, "files": {name: "0" * 64}})
        for manifest in bad_records:
            with self.subTest(manifest=manifest):
                self.write_lock(manifest)
                before = snapshot(self.target)
                with self.assertRaises(ValueError):
                    self.upgrade.preview(self.target)
                self.assertEqual(before, snapshot(self.target))
        (self.target / "ratpack.lock.json").write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.upgrade.preview(self.target)

    def test_symlink_manifest_file_and_parent_paths_are_rejected(self):
        self.install()
        lock = self.target / "ratpack.lock.json"
        original = lock.read_bytes()
        outside = self.root / "outside"
        outside.mkdir()
        secret = outside / "secret"
        secret.write_text("Must never read or overwrite\n")
        for relative in ["escape/secret", "linked-file", "ratpack.lock.json"]:
            with self.subTest(relative=relative):
                if relative == "ratpack.lock.json":
                    lock.unlink()
                    lock.symlink_to(secret)
                    link = lock
                else:
                    manifest = json.loads(original)
                    manifest["files"][relative] = "0" * 64
                    self.write_lock(manifest)
                    link = self.target / relative.split("/")[0]
                    link.symlink_to(outside if "/" in relative else secret)
                original_read = Path.read_bytes
                def guarded_read(path):
                    self.assertFalse(path.is_symlink(), f"Attempted symlink content read: {path}")
                    self.assertFalse(path.is_relative_to(outside))
                    return original_read(path)
                with patch.object(Path, "read_bytes", guarded_read):
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        self.upgrade.preview(self.target)
                link.unlink()
                lock.write_bytes(original)
        self.assertEqual(secret.read_text(), "Must never read or overwrite\n")

    def test_upgrade_json_cli_is_read_only_and_has_no_apply_mode(self):
        self.install()
        before = snapshot(self.target)
        cli = self.skill / "scripts/upgrade.py"
        result = subprocess.run([sys.executable, str(cli), str(self.target), "--source-revision", SHA, "--json"],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["preview_only"])
        self.assertEqual(report["candidate_source_revision_origin"], "supplied")
        self.assertTrue(all(r["status"] == "unchanged" for r in report["files"]))
        denied = subprocess.run([sys.executable, str(cli), str(self.target), "--apply"],
                                text=True, capture_output=True)
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(before, snapshot(self.target))

    def test_cli_preview_does_not_create_source_bytecode_or_project_outputs(self):
        for cache in self.skill.rglob("__pycache__"):
            shutil.rmtree(cache)
        before_source = snapshot(self.skill)
        result = subprocess.run([
            sys.executable, str(self.skill / "scripts/upgrade.py"), str(self.target), "--json",
        ], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before_source, snapshot(self.skill))
        self.assertEqual(list(self.target.iterdir()), [])
        self.assertFalse(list(self.skill.rglob("__pycache__")))


if __name__ == "__main__":
    unittest.main()
