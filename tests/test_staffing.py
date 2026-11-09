from pathlib import Path
import runpy
import unittest


class StaffingTest(unittest.TestCase):
    def validate(self, limit):
        adoption = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'skills/rp-bootstrap/scripts/adoption.py'))
        adoption['validate_local'](dict(schema_version=1, coordinator="local-coordinator", max_implementation_agents=limit))

    def test_unapproved_and_approved_counts_including_more_than_two(self):
        for limit in (None, 0, 2, 8):
            with self.subTest(limit=limit):
                self.validate(limit)

    def test_invalid_counts_are_rejected(self):
        for limit in (-1, True, '8'):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.validate(limit)
