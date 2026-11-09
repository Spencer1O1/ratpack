import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "bootstrap", ROOT / "skills/rp-bootstrap/scripts/bootstrap.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BootstrapTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name)

    def run_bootstrap(self, apply=False):
        with contextlib.redirect_stdout(io.StringIO()):
            MODULE.bootstrap(self.target, apply)

    def test_preview_does_not_create_files_or_directories(self):
        self.run_bootstrap()
        self.assertEqual(list(self.target.iterdir()), [])

    def test_apply_creates_self_contained_project_and_is_idempotent(self):
        self.run_bootstrap(apply=True)
        config = json.loads((self.target / "ratpack.json").read_text())
        self.assertEqual(config["merge_policy"], "designated-integration-owner")
        self.assertNotIn("integration_owner", config)
        self.assertNotIn("implementation_delegation_authorized", config)
        self.assertNotIn("max_implementation_agents", config)
        for path in self.target.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#")[0]).exists())
        before = {p: p.stat().st_mtime_ns for p in self.target.rglob("*")}
        self.run_bootstrap(apply=True)
        self.assertEqual(
            before, {p: p.stat().st_mtime_ns for p in self.target.rglob("*")}
        )

    def test_bootstrap_runs_from_an_individually_installed_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "rp-bootstrap"
            shutil.copytree(ROOT / "skills/rp-bootstrap", package,
                            ignore=shutil.ignore_patterns("__pycache__"))
            spec = importlib.util.spec_from_file_location(
                "standalone_bootstrap", package / "scripts/bootstrap.py"
            )
            standalone = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(standalone)
            with contextlib.redirect_stdout(io.StringIO()):
                standalone.bootstrap(self.target, True)
            self.assertEqual(
                (self.target / "docs/development.md").read_bytes(),
                (package / "references/workflow.md").read_bytes(),
            )
            self.assertEqual(len(list((self.target / ".codex/agents").glob("*.toml"))), 5)
            self.assertFalse((Path(directory) / "rp-coordinate").exists())

    def test_conflict_preserves_existing_content_and_prevents_partial_write(self):
        existing = self.target / "CONTRIBUTING.md"
        existing.write_text("Existing contribution instructions\n")
        with self.assertRaisesRegex(ValueError, "reconcile manually"):
            self.run_bootstrap(apply=True)
        self.assertEqual(existing.read_text(), "Existing contribution instructions\n")
        self.assertEqual(list(self.target.iterdir()), [existing])

    def test_rejects_symlinked_output_directory(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.target / "docs").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.run_bootstrap(apply=True)
            self.assertEqual(list(Path(outside).iterdir()), [])
            self.assertFalse((self.target / "AGENTS.md").exists())

    def test_rejects_file_in_place_of_parent_directory(self):
        (self.target / "docs").write_text("not a directory")
        with self.assertRaisesRegex(ValueError, "not a directory"):
            self.run_bootstrap(apply=True)
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_rejects_missing_project(self):
        with self.assertRaises(ValueError):
            MODULE.prepare(self.target / "missing")


if __name__ == "__main__":
    unittest.main()
