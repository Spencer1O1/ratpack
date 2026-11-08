#!/usr/bin/env python3
"""Export blind workflow prompts or grade structured decisions; no model calls."""
import argparse
import json
from pathlib import Path
import sys


CASES = Path(__file__).resolve().parents[1] / 'tests/scenarios/workflow.json'


def load_cases(path=CASES):
    data = json.loads(Path(path).read_text())
    if data.get('schema_version') != 1 or not isinstance(data.get('cases'), list):
        raise ValueError('Unsupported scenario document')
    cases = data['cases']
    ids = [c['id'] for c in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ValueError('Scenarios need unique identifiers')
    for case in cases:
        if not isinstance(case.get('expected'), dict) or not case['expected']:
            raise ValueError('Each scenario needs expected decision fields')
        if not isinstance(case.get('request'), str) or not isinstance(case.get('context'), dict):
            raise ValueError('Each scenario needs a request and context')
    return cases


def prompts(cases):
    return {
        'instructions': 'Use the project workflow and coordination procedure to decide each case. '
        'Return one JSON object keyed by case ID, with the requested decision fields and a '
        'nonempty reason for each. Do not dispatch agents, edit projects, or contact services. '
        'For occupied-checkout, next_action must be one of assign, coordinate_handoff, '
        'merge, or request_staffing. ID lists are unordered.',
        'cases': [{k: c[k] for k in ('id', 'request', 'context')} for c in cases],
    }


def equal(expected, actual):
    if type(expected) is not type(actual):
        return False
    if isinstance(expected, list) and all(isinstance(x, str) for x in expected + actual):
        return sorted(expected) == sorted(actual)
    return expected == actual


def grade(cases, responses):
    failures = []
    if not isinstance(responses, dict):
        raise ValueError('Responses must be an object keyed by case ID')
    known = {c['id'] for c in cases}
    for unknown in responses.keys() - known:
        failures.append({'case': unknown, 'field': 'id', 'error': 'unknown case'})
    passed = 0
    for case in cases:
        answer = responses.get(case['id'])
        errors = []
        if not isinstance(answer, dict):
            errors.append({'field': 'response', 'error': 'missing decision object'})
        else:
            if not isinstance(answer.get('reason'), str) or not answer['reason'].strip():
                errors.append({'field': 'reason', 'error': 'missing reasoning'})
            for field, expected in case['expected'].items():
                if field not in answer or not equal(expected, answer[field]):
                    errors.append({'field': field, 'expected': expected, 'actual': answer.get(field)})
        if not errors:
            passed += 1
        failures.extend({'case': case['id'], **error} for error in errors)
    return {'passed': passed, 'total': len(cases), 'failures': failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prompts', action='store_true', help='export requests without expected answers')
    mode.add_argument('--grade', type=Path, metavar='RESPONSES_JSON')
    args = parser.parse_args()
    try:
        cases = load_cases()
        result = prompts(cases) if args.prompts else grade(cases, json.loads(args.grade.read_text()))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    return 0 if args.prompts or not result['failures'] else 1


if __name__ == '__main__':
    sys.exit(main())
