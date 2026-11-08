import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "skills/rp-role/scripts/render_agent.py"
SPEC = importlib.util.spec_from_file_location("render_agent", RENDERER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AgentTest(unittest.TestCase):
    def test_custom_role_round_trips_multiline_unicode_and_quotes(self):
        spec = {
            "name": "ratpack_research",
            "description": 'Research "Lean" proofs 🐀',
            "developer_instructions": 'Find lemmas.\nPreserve \\paths and "quotes".\x7f',
        }
        self.assertEqual(tomllib.loads(MODULE.render_agent(spec)), spec)

    def test_renderer_rejects_missing_fields_and_permission_overrides(self):
        valid = dict(name="ratpack_research", description="Research", developer_instructions="Read only")
        for spec in [
            {}, {**valid, "sandbox_mode": "danger-full-access"},
            {**valid, "name": "../../config"}, {**valid, "name": "reviewer"},
            {**valid, "description": " "}, {**valid, "developer_instructions": False},
        ]:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                MODULE.render_agent(spec)

    def test_cli_reports_invalid_input_without_emitting_profile(self):
        result = subprocess.run(
            [sys.executable, str(RENDERER)], input='{"name":"ratpack_bad"}',
            text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("exactly", result.stderr)

    def test_existing_native_profile_blocks_bootstrap_without_partial_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            profile = target / ".codex/agents/ratpack_reviewer.toml"
            profile.parent.mkdir(parents=True)
            profile.write_text('name = "my-existing-reviewer"\n')
            before = {p: p.read_bytes() for p in target.rglob("*") if p.is_file()}
            result = subprocess.run([
                sys.executable, str(ROOT / "skills/rp-bootstrap/scripts/bootstrap.py"),
                directory, "--owner", "peer-coordinator", "--apply",
            ], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, {p: p.read_bytes() for p in target.rglob("*") if p.is_file()})

    def test_bootstrap_installs_profiles_without_replacing_human_assignments(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            command = [
                sys.executable, str(ROOT / "skills/rp-bootstrap/scripts/bootstrap.py"),
                directory, "--owner", "human-created-coordinator", "--apply",
            ]
            subprocess.run(command, check=True, capture_output=True)
            profiles = list((target / ".codex/agents").glob("*.toml"))
            self.assertEqual(len(profiles), 5)
            names = set()
            for profile in profiles:
                data = tomllib.loads(profile.read_text())
                self.assertEqual(set(data), set(MODULE.FIELDS))
                self.assertTrue(all(isinstance(v, str) and v.strip() for v in data.values()))
                names.add(data["name"])
            self.assertEqual(names, {
                "ratpack_coordinator", "ratpack_implementer", "ratpack_reviewer",
                "ratpack_cleanup", "ratpack_workflow",
            })
            config_path = target / "ratpack.json"
            config = json.loads(config_path.read_text())
            self.assertEqual(config["integration_owner"], "human-created-coordinator")
            self.assertFalse(config["implementation_delegation_authorized"])
            config["custom_roles"]["research"] = {"purpose": "Keep my research role"}
            config_path.write_text(json.dumps(config))
            before = {p: p.read_bytes() for p in target.rglob("*") if p.is_file()}
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, {p: p.read_bytes() for p in target.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
