import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('scenarios', Path(__file__).resolve().parents[1] / 'scripts/scenarios.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ScenarioTest(unittest.TestCase):
    def setUp(self):
        self.cases = MODULE.load_cases()
        self.answers = {c['id']: {**copy.deepcopy(c['expected']), 'reason': 'Reasoned against the adopted workflow.'} for c in self.cases}

    def test_export_does_not_expose_expected_answers(self):
        exported = MODULE.prompts(self.cases)
        for case in exported['cases']:
            self.assertEqual(set(case), {'id', 'request', 'context'})
        self.assertEqual(len(exported['cases']), len(self.cases))

    def test_correct_answers_and_unordered_task_ids_pass(self):
        self.answers['fixed-batch']['blocker_ids'].reverse()
        result = MODULE.grade(self.cases, self.answers)
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['passed'], len(self.cases))

    def test_unsafe_merge_and_missing_cases_fail(self):
        self.answers['changed-review-head']['merge'] = True
        del self.answers['transfer-owner']
        result = MODULE.grade(self.cases, self.answers)
        failed_ids = {x['case'] for x in result['failures']}
        self.assertEqual(failed_ids, {'changed-review-head', 'transfer-owner'})

    def test_missing_reason_wrong_types_and_unknown_cases_fail(self):
        self.answers['staffing-and-host-capacity']['new_starts'] = True
        self.answers['deferred-audit']['reason'] = ''
        self.answers['unknown'] = {}
        result = MODULE.grade(self.cases, self.answers)
        self.assertEqual({x['case'] for x in result['failures']}, {'staffing-and-host-capacity', 'deferred-audit', 'unknown'})
