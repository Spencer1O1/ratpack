import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/rp-bootstrap/scripts/doctor.py"
SPEC = importlib.util.spec_from_file_location("ratpack_doctor", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DoctorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        self.project.mkdir()
        for relative in ("AGENTS.md", "CONTRIBUTING.md", "docs/development.md"):
            path = self.project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Project guidance\n")
        self.config = dict(
            schema_version=1, integration_owner="human coordinator",
            max_implementation_agents=None,
            custom_roles={"research": "Investigate proofs"}, checks=[],
            github_repository=None, linear_team=None,
        )
        self.write_config()

    def write_config(self):
        (self.project / "ratpack.json").write_text(json.dumps(self.config))

    def result(self, **kwargs):
        report = MODULE.inspect_project(self.project, **kwargs)
        self.assertEqual(set(report), {"ok", "checks"})
        for item in report["checks"]:
            self.assertEqual(set(item), {"name", "status", "detail"})
            self.assertIn(item["status"], {"pass", "fail", "warn", "unverified"})
        return report, {item["name"]: item for item in report["checks"]}

    def snapshot(self):
        return {str(p.relative_to(self.project)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.project.rglob("*") if p.is_file()}

    def git(self, *args, project=None):
        return subprocess.run(["git", "-C", str(project or self.project), *args],
                              check=True, capture_output=True, text=True).stdout.strip()

    def initialize_git(self):
        self.git("init", "-b", "main")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "Fixture")
        self.git("branch", "devel")
        self.git("switch", "-c", "feature/test")

    def manifest(self, files=None, revision="a" * 40):
        if files is None:
            files = {"docs/development.md": hashlib.sha256(
                (self.project / "docs/development.md").read_bytes()).hexdigest()}
        data = dict(schema_version=1, source_revision=revision, files=files,
                    upstream_repository="https://github.com/ratpack-workflow/ratpack",
                    source_revision_origin="git-verified" if revision else "unknown")
        (self.project / "ratpack.lock.json").write_text(json.dumps(data))

    def test_manual_peer_project_and_unapproved_staffing_are_supported(self):
        report, checks = self.result()
        self.assertTrue(report["ok"])
        self.assertEqual(checks["configuration.staffing"]["status"], "warn")
        self.assertEqual(checks["configuration.checks"]["status"], "warn")
        self.assertEqual(checks["profiles.files"]["status"], "warn")
        self.assertEqual(checks["adoption"]["status"], "unverified")
        self.assertEqual(checks["git.repository"]["status"], "warn")

    def test_configured_commands_are_not_executed_or_integrations_certified(self):
        marker = self.project / "executed"
        self.config.update(checks=[f"touch {marker}"], max_implementation_agents=8,
                           github_repository="example/project", linear_team="TEAM")
        self.write_config()
        before = self.snapshot()
        report, checks = self.result()
        self.assertTrue(report["ok"])
        self.assertEqual(before, self.snapshot())
        self.assertFalse(marker.exists())
        for key in ("configuration.checks", "integration.github", "integration.linear",
                    "integration.protections", "profiles.runtime"):
            self.assertEqual(checks[key]["status"], "unverified")

    def test_explicit_zero_and_retired_flag_preserve_read_only_compatibility(self):
        self.config.update(max_implementation_agents=0,
                           implementation_delegation_authorized=False)
        self.write_config()
        before = self.snapshot()
        report, checks = self.result()
        self.assertTrue(report["ok"])
        self.assertEqual(checks["configuration.staffing"]["status"], "pass")
        self.assertEqual(checks["configuration.legacy_delegation"]["status"], "warn")
        self.assertEqual(before, self.snapshot())

    def test_invalid_configuration_is_reported_without_traceback(self):
        cases = (
            dict(schema_version=True), dict(integration_owner=" "),
            dict(max_implementation_agents=True), dict(max_implementation_agents=-1),
            dict(checks="make test"), dict(checks=[""]), dict(custom_roles=[]),
            dict(custom_roles={"research": False}), dict(github_repository=[]),
        )
        original = self.config.copy()
        for changes in cases:
            with self.subTest(changes=changes):
                self.config = {**original, **changes}
                self.write_config()
                report, _ = self.result()
                self.assertFalse(report["ok"])
        for content in ("{", "[]", "null"):
            with self.subTest(content=content):
                (self.project / "ratpack.json").write_text(content)
                report, checks = self.result()
                self.assertFalse(report["ok"])
                self.assertEqual(checks["configuration"]["status"], "fail")

    def test_missing_fields_and_missing_project_files_fail(self):
        for key in ("schema_version", "max_implementation_agents"):
            with self.subTest(key=key):
                config = self.config.copy()
                config.pop(key)
                (self.project / "ratpack.json").write_text(json.dumps(config))
                self.assertFalse(self.result()[0]["ok"])
        self.write_config()
        (self.project / "AGENTS.md").unlink()
        self.assertEqual(self.result()[1]["instructions"]["status"], "fail")

    def test_workflow_override_and_unsafe_paths(self):
        (self.project / "docs/development.md").rename(self.project / "docs/contributing.md")
        self.assertFalse(self.result()[0]["ok"])
        self.assertTrue(self.result(workflow="docs/contributing.md")[0]["ok"])
        for relative in ("../secret", "/etc/passwd", "C:/secret", "docs/../../secret"):
            with self.subTest(relative=relative):
                self.assertEqual(self.result(workflow=relative)[1]["workflow"]["status"], "fail")

    def test_git_feature_branch_and_worktree_are_read_only(self):
        self.initialize_git()
        before = self.snapshot()
        report, checks = self.result()
        self.assertTrue(report["ok"])
        self.assertEqual(checks["git.main"]["status"], "pass")
        self.assertEqual(checks["git.devel"]["status"], "pass")
        self.assertEqual(self.git("branch", "--show-current"), "feature/test")
        self.assertEqual(before, self.snapshot())
        worktree = Path(self.temp.name) / "worktree"
        self.git("worktree", "add", "-b", "feature/peer", str(worktree))
        for relative in ("AGENTS.md", "CONTRIBUTING.md", "docs/development.md", "ratpack.json"):
            destination = worktree / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.project / relative, destination)
        self.assertTrue(MODULE.inspect_project(worktree)["ok"])
        self.assertEqual(self.git("branch", "--show-current", project=worktree), "feature/peer")

    def test_missing_required_git_ref_fails_without_creating_it(self):
        self.initialize_git()
        self.git("branch", "-D", "devel")
        report, checks = self.result()
        self.assertFalse(report["ok"])
        self.assertEqual(checks["git.devel"]["status"], "fail")
        self.assertNotIn("devel", self.git("branch", "--format=%(refname:short)").splitlines())

    def test_no_git_or_subprocess_execution_other_than_local_inspection(self):
        real_run = MODULE.subprocess.run
        commands = []
        def observed(command, **kwargs):
            commands.append(command)
            return real_run(command, **kwargs)
        with patch.object(MODULE.subprocess, "run", side_effect=observed):
            self.result()
        self.assertTrue(commands)
        for command in commands:
            self.assertEqual(command[0], "git")
            self.assertIn(command[4], {"rev-parse", "show-ref"})
            self.assertNotIn("fetch", command)

    def test_native_mode_requires_profiles_but_does_not_claim_activation(self):
        self.assertFalse(self.result(native=True)[0]["ok"])
        source = ROOT / "skills/rp-bootstrap/assets/project/.codex/agents"
        shutil.copytree(source, self.project / ".codex/agents")
        report, checks = self.result(native=True)
        self.assertTrue(report["ok"])
        self.assertEqual(checks["profiles.files"]["status"], "pass")
        self.assertEqual(checks["profiles.runtime"]["status"], "unverified")
        (self.project / ".codex/agents/custom.toml").write_text('name = "ratpack_reviewer"\n')
        self.assertFalse(self.result()[0]["ok"])

    def test_manifest_baseline_drift_and_revision_are_not_overstated(self):
        self.manifest()
        report, checks = self.result()
        self.assertTrue(report["ok"])
        self.assertEqual(checks["adoption.files"]["status"], "pass")
        self.assertEqual(checks["adoption.source"]["status"], "unverified")
        (self.project / "docs/development.md").write_text("Local project policy\n")
        before = self.snapshot()
        report, checks = self.result()
        self.assertTrue(report["ok"])
        self.assertEqual(checks["adoption.files"]["status"], "warn")
        self.assertEqual(before, self.snapshot())
        self.manifest(revision=None)
        self.assertEqual(self.result()[1]["adoption.source"]["status"], "unverified")

    def test_doctor_and_upgrade_reject_the_same_malformed_adoption_record(self):
        self.manifest()
        manifest_path = self.project / "ratpack.lock.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.pop("source_revision")
        manifest_path.write_text(json.dumps(manifest))
        self.assertEqual(self.result()[1]["adoption"]["status"], "fail")
        result = subprocess.run([sys.executable, str(SCRIPT.with_name("upgrade.py")),
                                 str(self.project), "--json"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source_revision", result.stderr)

    def test_unsafe_manifest_entries_are_rejected_before_hashing(self):
        outside = Path(self.temp.name) / "secret"
        outside.write_text("private")
        (self.project / "link").symlink_to(outside)
        for relative in ("../secret", str(outside), "link", "C:/secret", "docs/../secret"):
            with self.subTest(relative=relative):
                self.manifest(files={relative: "0" * 64})
                with patch.object(MODULE.hashlib, "sha256", side_effect=AssertionError("must not hash")):
                    report, checks = self.result()
                self.assertFalse(report["ok"])
                self.assertEqual(checks["adoption"]["status"], "fail")
        before = outside.read_bytes()
        self.assertEqual(outside.read_bytes(), before)

    def test_symlinked_documents_profiles_and_manifest_are_not_followed(self):
        outside = Path(self.temp.name) / "external"
        outside.mkdir()
        (outside / "profile.toml").write_text('name = "secret"')
        profiles = self.project / ".codex/agents"
        profiles.parent.mkdir()
        profiles.symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.result()[1]["profiles.files"]["status"], "fail")
        (self.project / "ratpack.lock.json").symlink_to(outside / "profile.toml")
        self.assertEqual(self.result()[1]["adoption"]["status"], "fail")
        (self.project / "AGENTS.md").unlink()
        (self.project / "AGENTS.md").symlink_to(outside / "profile.toml")
        self.assertEqual(self.result()[1]["instructions"]["status"], "fail")

    def test_cli_json_exit_status_and_missing_target(self):
        before = self.snapshot()
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.project), "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)["ok"])
        self.assertEqual(result.stderr, "")
        self.assertEqual(before, self.snapshot())
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.project / "missing"), "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
