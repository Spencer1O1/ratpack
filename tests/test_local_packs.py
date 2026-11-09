"""Exercise independent local packs without changing shared adoption state."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_adoption import load_script, snapshot, SHA, SOURCE


BOOTSTRAP = load_script(SOURCE / 'scripts/bootstrap.py')
UPGRADE = load_script(SOURCE / 'scripts/upgrade.py')
DOCTOR = load_script(SOURCE / 'scripts/doctor.py')


def quiet(function, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args, **kwargs)


class LocalPacksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.project.mkdir()

    def adopt(self):
        quiet(BOOTSTRAP.bootstrap, self.project, apply=True, source_revision=SHA)

    def git(self, target, *args):
        return subprocess.run(['git', '--no-optional-locks', '-C', str(target), *args], check=True,
                              text=True, capture_output=True).stdout

    def statuses(self):
        return {c['name']: c['status'] for c in DOCTOR.inspect_project(self.project)['checks']}

    def test_two_independent_clones_join_without_shared_or_lock_changes(self):
        self.adopt()
        self.git(self.project, 'init', '-b', 'main')
        self.git(self.project, 'add', '.')
        self.git(self.project, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-m', 'Shared adoption')
        self.git(self.project, 'branch', 'devel')
        shared = {name: data[0] for name, data in snapshot(self.project).items() if not name.startswith('.git/')}
        clones = []
        for name, limit in [('alice', 0), ('bob', 8)]:
            clone = self.root / name
            self.git(self.root, 'clone', '--quiet', str(self.project), str(clone))
            before = snapshot(clone)
            quiet(BOOTSTRAP.join_local, clone, name, apply=False, max_implementation_agents=limit)
            self.assertEqual(before, snapshot(clone))
            quiet(BOOTSTRAP.join_local, clone, name, apply=True, max_implementation_agents=limit)
            after = snapshot(clone)
            self.assertEqual(set(after) - set(before), {'ratpack.local.json'})
            self.assertTrue(all(after[path] == content for path, content in before.items()))
            self.assertEqual(json.loads((clone / 'ratpack.local.json').read_text())['coordinator'], name)
            self.assertEqual(self.git(clone, 'status', '--porcelain'), '')
            self.assertTrue(all((clone / path).read_bytes() == content for path, content in shared.items()))
            quiet(BOOTSTRAP.join_local, clone, name, apply=True, max_implementation_agents=limit)
            self.assertEqual(after, snapshot(clone))
            manifest = json.loads((clone / 'ratpack.lock.json').read_text())
            self.assertNotIn('ratpack.local.json', manifest['files'])
            self.assertNotIn('ratpack.local.json', {f['path'] for f in UPGRADE.preview(clone)['files']})
            clones.append(clone)
        self.assertEqual((clones[0] / 'ratpack.lock.json').read_bytes(), (clones[1] / 'ratpack.lock.json').read_bytes())

    def test_existing_ignore_is_preserved_or_refused_with_actionable_guidance(self):
        ignore = self.project / '.gitignore'
        ignore.write_text('build/\n!important.txt\n')
        before = snapshot(self.project)
        with self.assertRaisesRegex(ValueError, 'Add /ratpack.local.json at the end'):
            self.adopt()
        self.assertEqual(before, snapshot(self.project))
        ignore.write_text(ignore.read_text() + '/ratpack.local.json\n')
        content = ignore.read_bytes()
        self.adopt()
        self.assertEqual(ignore.read_bytes(), content)
        quiet(BOOTSTRAP.bootstrap, self.project, apply=True, source_revision=SHA)
        ignore.write_text(ignore.read_text() + '!ratpack.local.json\n')
        before = snapshot(self.project)
        with self.assertRaisesRegex(ValueError, 'negation'):
            quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        self.assertEqual(before, snapshot(self.project))

    def test_local_conflicts_symlinks_and_tracked_files_are_preserved(self):
        self.adopt()
        local = self.project / 'ratpack.local.json'
        quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        before = snapshot(self.project)
        with self.assertRaisesRegex(ValueError, 'settings differ'):
            quiet(BOOTSTRAP.join_local, self.project, 'bob', apply=True)
        self.assertEqual(before, snapshot(self.project))
        self.git(self.project, 'init', '-b', 'main')
        self.git(self.project, 'add', '-f', 'ratpack.local.json')
        with self.assertRaisesRegex(ValueError, 'already tracked'):
            quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        self.git(self.project, 'rm', '--cached', 'ratpack.local.json')
        outside = self.root / 'private'
        outside.write_bytes(local.read_bytes())
        local.unlink()
        local.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        self.assertEqual(outside.read_bytes(), before['ratpack.local.json'][0])
        local.unlink()
        ignore = self.project / '.gitignore'
        ignore.unlink()
        ignore.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)

    def test_shared_adoption_refuses_already_tracked_local_file_without_ignore(self):
        self.git(self.project, 'init', '-b', 'main')
        local = self.project / 'ratpack.local.json'
        local.write_text('{"private":"keep"}')
        self.git(self.project, 'add', 'ratpack.local.json')
        before = snapshot(self.project)
        with self.assertRaisesRegex(ValueError, 'already tracked'):
            self.adopt()
        self.assertEqual(before, snapshot(self.project))

    def test_legacy_configuration_and_manifest_survive_all_previews(self):
        self.adopt()
        config = self.project / 'ratpack.json'
        legacy = json.loads(config.read_text())
        legacy.pop('merge_policy')
        legacy.update(schema_version=1, integration_owner='legacy-owner', max_implementation_agents=7)
        config.write_text(json.dumps(legacy))
        before = snapshot(self.project)
        self.assertEqual(self.statuses()['configuration.schema'], 'warn')
        report = UPGRADE.preview(self.project)
        self.assertTrue(any('deliberately' in w for w in report['warnings']))
        self.assertTrue(next(f for f in report['files'] if f['path'] == 'ratpack.json')['manual_reconciliation'])
        with self.assertRaisesRegex(ValueError, 'schema_version 2'):
            quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        with self.assertRaisesRegex(ValueError, 'differs'):
            quiet(BOOTSTRAP.bootstrap, self.project, apply=True)
        self.assertEqual(before, snapshot(self.project))

    def test_doctor_optional_and_malformed_local_settings(self):
        self.adopt()
        self.assertEqual(self.statuses()['local.configuration'], 'warn')
        quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        self.assertEqual(self.statuses()['local.configuration'], 'pass')
        local = self.project / 'ratpack.local.json'
        valid = json.loads(local.read_text())
        for change in ({'coordinator': ''}, {'schema_version': True}, {'max_implementation_agents': True},
                       {'max_implementation_agents': -1}, {'max_implementation_agents': '2'}):
            with self.subTest(change=change):
                local.write_text(json.dumps({**valid, **change}))
                self.assertEqual(self.statuses()['local.configuration'], 'fail')
        local.write_text('{"coordinator":"a","coordinator":"b"}')
        self.assertEqual(self.statuses()['local.configuration'], 'fail')

    def test_join_rerun_preserves_local_count_and_advisory_model_preferences(self):
        self.adopt()
        quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        local = self.project / 'ratpack.local.json'
        config = json.loads(local.read_text())
        config.update(max_implementation_agents=8, model_preferences={'implementation': 'developer-choice'})
        local.write_text(json.dumps(config, indent=4))
        before = snapshot(self.project)
        quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        self.assertEqual(before, snapshot(self.project))
        self.assertEqual(self.statuses()['local.configuration'], 'pass')
        with self.assertRaisesRegex(ValueError, 'settings differ'):
            quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True, max_implementation_agents=2)
        self.assertEqual(before, snapshot(self.project))
        config['model_preferences'] = 'invalid'
        local.write_text(json.dumps(config))
        self.assertEqual(self.statuses()['local.configuration'], 'fail')

    def test_local_join_requires_valid_shared_schema_and_safe_configuration_paths(self):
        self.adopt()
        config = self.project / 'ratpack.json'
        valid = json.loads(config.read_text())
        for change in ({'schema_version': True}, {'merge_policy': 'anyone'},
                       {'integration_owner': 'alice'}, {'max_implementation_agents': 2},
                       {'checks': ['']}, {'model_preferences': {}}, {'custom_roles': []}, {'github_repository': False}):
            with self.subTest(change=change):
                config.write_text(json.dumps({**valid, **change}))
                before = snapshot(self.project)
                with self.assertRaises(ValueError):
                    quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
                self.assertEqual(before, snapshot(self.project))
                self.assertEqual(self.statuses()['configuration.schema'], 'fail')
        config.write_text(json.dumps(valid))
        outside = self.root / 'shared-config'
        config.rename(outside)
        config.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            quiet(BOOTSTRAP.join_local, self.project, 'alice', apply=True)
        self.assertFalse((self.project / 'ratpack.local.json').exists())

    def test_retired_owner_and_invalid_local_cli_write_nothing(self):
        cli = SOURCE / 'scripts/bootstrap.py'
        for args in (['--owner', 'alice', '--apply'], ['--local', '--apply'],
                     ['--coordinator', 'alice', '--apply'],
                     ['--local', '--coordinator', 'alice', '--source-revision', SHA]):
            result = subprocess.run([sys.executable, str(cli), str(self.project), *args],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(self.project.iterdir()), [])
        self.assertIn('--owner is retired', subprocess.run(
            [sys.executable, str(cli), str(self.project), '--owner', 'alice'],
            capture_output=True, text=True).stderr)
