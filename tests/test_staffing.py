import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    'ratpack_check', Path(__file__).resolve().parents[1] / 'scripts/check.py'
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class StaffingTest(unittest.TestCase):
    def validate(self, limit, authorized):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = dict(
                schema_version=1, max_implementation_agents=limit,
                implementation_delegation_authorized=authorized, checks=[],
            )
            for relative in ('ratpack.json', 'skills/ratpack/assets/project/ratpack.json'):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(config))
            with patch.object(MODULE, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                MODULE.check()

    def test_unapproved_and_approved_counts_including_more_than_two(self):
        for limit, authorized in ((None, False), (2, True), (8, True)):
            with self.subTest(limit=limit, authorized=authorized):
                self.validate(limit, authorized)

    def test_invalid_counts_and_approval_without_count_are_rejected(self):
        for limit, authorized in ((None, True), (0, True), (-1, False), (True, True), ('8', True)):
            with self.subTest(limit=limit, authorized=authorized), self.assertRaises(SystemExit):
                self.validate(limit, authorized)
