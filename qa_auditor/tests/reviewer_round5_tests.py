#!/usr/bin/env python3
"""External-review round 5: strict numeric-token CLI regression checks.

Uses synthetic fixtures. Confirms exit status, all four reports, and issue type.
"""
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from additional_hardening_tests import fixture, AUDITOR, PREFIX

TESTS = (
    ('clean_control', None, False, None),
    ('malformed_coordinate_suffix', 'coordinate', True, 'CHECK_FAILED'),
    ('malformed_pose_score_suffix', 'pose', True, 'INVALID_POSE'),
)


def main():
    passed = 0
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name, mutation, expect_failure, expected_type in TESTS:
            items = fixture()
            if mutation == 'coordinate':
                path = 'docking/results_wt/probe.log'
                items[path] = items[path].replace('Z 2\n', 'Z 2oops\n', 1)
            elif mutation == 'pose':
                path = 'docking/results_wt/probe_out.pdbqt'
                items[path] = items[path].replace('-6.000 0 0', '-6.000oops 0 0', 1)
            archive = root / (name + '.zip')
            out = root / (name + '_results')
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
                for member, content in items.items():
                    z.writestr(PREFIX + member, content)
            proc = subprocess.run([sys.executable, str(AUDITOR), str(archive), str(out)],
                                  capture_output=True, text=True)
            reports = ['audit_summary.json', 'exceptions.csv', 'run_audit.csv', 'source_manifest.csv']
            complete = all((out / filename).is_file() for filename in reports)
            summary = json.loads((out / 'audit_summary.json').read_text(encoding='utf-8')) if complete else {}
            failures = summary.get('failures', 0)
            kinds = {item['type'] for item in summary.get('failed_checks', [])}
            ok = (proc.returncode == (1 if expect_failure else 0)
                  and complete and bool(failures) == expect_failure
                  and (expected_type is None or expected_type in kinds))
            print(('PASS' if ok else 'FAIL'), name, 'exit', proc.returncode,
                  'reports', complete, 'findings', sorted(kinds))
            passed += ok
    print('RESULT', passed, '/', len(TESTS))
    return 0 if passed == len(TESTS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
