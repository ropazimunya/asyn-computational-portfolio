#!/usr/bin/env python3
"""Round-six independent-review-derived malformed/duplicate field regressions."""
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from additional_hardening_tests import fixture, AUDITOR, PREFIX

CASES = (
    ('clean', None, False, None),
    ('valid_then_malformed_center', 'center_duplicate_bad', True, 'INVALID_LOG'),
    ('valid_then_valid_center', 'center_duplicate_good', True, 'INVALID_LOG'),
    ('malformed_single_size', 'size_bad', True, 'INVALID_LOG'),
    ('valid_then_malformed_size', 'size_duplicate_bad', True, 'INVALID_LOG'),
)

def main():
    successes = 0
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name, change, should_fail, expected_type in CASES:
            data = fixture()
            path = 'docking/results_wt/probe.log'
            text = data[path]
            center = next(line for line in text.splitlines() if line.startswith('Grid center'))
            size = next(line for line in text.splitlines() if line.startswith('Grid size'))
            if change == 'center_duplicate_bad':
                text += center.rsplit(' ', 1)[0] + ' 2oops\n'
            elif change == 'center_duplicate_good':
                text += center + '\n'
            elif change == 'size_bad':
                text = text.replace(size, size.rsplit(' ', 1)[0] + ' 20oops', 1)
            elif change == 'size_duplicate_bad':
                text += size.rsplit(' ', 1)[0] + ' 20oops\n'
            data[path] = text
            arc, out = root / f'{name}.zip', root / f'{name}_out'
            with zipfile.ZipFile(arc, 'w', zipfile.ZIP_DEFLATED) as z:
                for member, content in data.items():
                    z.writestr(PREFIX + member, content)
            proc = subprocess.run([sys.executable, str(AUDITOR), str(arc), str(out)], capture_output=True, text=True)
            filenames = ('audit_summary.json', 'exceptions.csv', 'run_audit.csv', 'source_manifest.csv')
            complete = all((out / filename).is_file() for filename in filenames)
            summary = json.loads((out / 'audit_summary.json').read_text(encoding='utf-8')) if complete else {}
            findings = {item['type'] for item in summary.get('failed_checks', [])}
            good = (proc.returncode == int(should_fail) and complete and
                    bool(summary.get('failures', 0)) == should_fail and
                    (expected_type is None or expected_type in findings))
            print(('PASS' if good else 'FAIL'), name, 'exit', proc.returncode,
                  'reports', complete, 'findings', sorted(findings))
            successes += good
    print(f'RESULT {successes}/{len(CASES)}')
    return 0 if successes == len(CASES) else 1

if __name__ == '__main__':
    raise SystemExit(main())
