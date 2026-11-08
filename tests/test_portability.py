"""Exercise one local project layout under three contributor arrangements.

These are actual CLI/file checks, not host spawning or human participation tests.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/rp-bootstrap/scripts'


class PortabilityTest(unittest.TestCase):
    def test_same_project_supports_native_peer_and_manual_arrangements(self):
        workflow_bytes = None
        with tempfile.TemporaryDirectory() as directory:
            for mode in ('native', 'peers', 'manual'):
                with self.subTest(mode=mode):
                    project = Path(directory) / mode
                    project.mkdir()
                    subprocess.run([sys.executable, str(SCRIPTS / 'bootstrap.py'), str(project),
                                    '--owner', 'coordinator', '--apply'], check=True, capture_output=True)
                    for args in (('init', '-b', 'main'),
                                 ('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                                  '-c', 'commit.gpgsign=false', 'commit', '--allow-empty', '-m', 'Fixture'),
                                 ('branch', 'devel')):
                        subprocess.run(['git', '-C', str(project), *args], check=True, capture_output=True)
                    config_path = project / 'ratpack.json'
                    config = json.loads(config_path.read_text())
                    marker = project / 'must-not-execute'
                    config['checks'] = [f'touch {marker}']
                    if mode != 'manual':
                        config['max_implementation_agents'] = 4
                        config['implementation_delegation_authorized'] = mode == 'native'
                        config['github_repository'] = 'example/project'
                        config['linear_team'] = 'TEAM'
                    if mode != 'native':
                        shutil.rmtree(project / '.codex/agents')
                    config_path.write_text(json.dumps(config))
                    current_workflow = (project / 'docs/development.md').read_bytes()
                    if workflow_bytes is None:
                        workflow_bytes = current_workflow
                    self.assertEqual(current_workflow, workflow_bytes)
                    def snapshot():
                        return {p.relative_to(project).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                                for p in project.rglob('*') if p.is_file()}
                    before = snapshot()
                    command = [sys.executable, str(SCRIPTS / 'doctor.py'), str(project), '--json']
                    if mode == 'native':
                        command.append('--native')
                    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
                    result = subprocess.run(command, capture_output=True, text=True, env=env)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    report = json.loads(result.stdout)
                    self.assertTrue(report['ok'])
                    statuses = {c['name']: c['status'] for c in report['checks']}
                    self.assertEqual(statuses['profiles.files'], 'pass' if mode == 'native' else 'warn')
                    for name in ('profiles.runtime', 'integration.protections', 'integration.github',
                                 'integration.linear', 'configuration.checks'):
                        self.assertEqual(statuses[name], 'unverified')
                    self.assertEqual(before, snapshot())
                    self.assertFalse(marker.exists())
