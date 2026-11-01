#!/usr/bin/env python3
"""Independent-style malformed-input CLI regression tests for synthetic Vina records.

No docking, MD, network, or real research data used.
Run from the repository root: python3 qa_auditor/tests/additional_hardening_tests.py
"""
from pathlib import Path
import csv
import io
import json
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
AUDITOR = HERE.parent / 'validation' / 'audit_workflow_v2.py'
PREFIX = 'asyn-cryptic-pocket-screening-main/'
CFG = ('center_x = 0\ncenter_y = 1\ncenter_z = 2\nsize_x = 20\nsize_y = 20\n'
       'size_z = 20\nexhaustiveness = 8\n')
LOG = ('AutoDock Vina v1.2.7\nGrid center: X 0 Y 1 Z 2\n'
       'Grid size  : X 20 Y 20 Z 20\nExhaustiveness: 8\n'
       'Performing docking (random seed: {seed}) ...\n'
       '   1       -6.000          0          0\n')
SUMMARY = 'Compound,WT_Affinity_kcal_mol,A53T_Affinity_kcal_mol\nprobe,-6.000,-6.000\n'

def fixture():
    d = {'docking/vina_config.txt': CFG,
         'run_docking.sh': 'vina --receptor r.pdbqt --ligand l.pdbqt\n',
         'docking_results_summary.csv': SUMMARY,
         'docking/ligands_pdbqt/probe.pdbqt': 'REMARK SYNTHETIC\n'}
    for group, seed in [('wt', 101), ('a53t', 202)]:
        d[f'docking/results_{group}/probe.log'] = LOG.format(seed=seed)
        d[f'docking/results_{group}/probe_out.pdbqt'] = 'REMARK VINA RESULT: -6.000 0 0\n'
    return d

def cases():
    yield 'clean_control', lambda d: None, False, None
    yield 'fractional_exhaustiveness', lambda d: d.__setitem__('docking/vina_config.txt', CFG.replace('= 8', '= 8.9')), True, 'INVALID_CONFIG'
    yield 'nonfinite_exhaustiveness', lambda d: d.__setitem__('docking/vina_config.txt', CFG.replace('= 8', '= 1e999')), True, 'INVALID_CONFIG'
    yield 'extra_csv_cell', lambda d: d.__setitem__('docking_results_summary.csv', SUMMARY.replace('probe,-6.000,-6.000', 'probe,-6.000,-6.000,UNEXPECTED')), True, 'INVALID_CSV_ROW_WIDTH'
    yield 'duplicate_csv_header', lambda d: d.__setitem__('docking_results_summary.csv', 'Compound,WT_Affinity_kcal_mol,WT_Affinity_kcal_mol,A53T_Affinity_kcal_mol\nprobe,-99,-6,-6\n'), True, 'DUPLICATE_CSV_HEADER'
    yield 'conflicting_config', lambda d: d.__setitem__('docking/vina_config.txt', 'size_x = 999\n' + CFG), True, 'INVALID_CONFIG'
    yield 'concatenated_log', lambda d: d.__setitem__('docking/results_wt/probe.log', LOG.format(seed=101) + LOG.format(seed=999)), True, 'INVALID_LOG'
    yield 'invalid_utf8', lambda d: d.__setitem__('docking/vina_config.txt', CFG.encode('utf-8') + b'\n# invalid: \xff\n'), True, 'UNREADABLE_FILE'
    yield 'custom_version', lambda d: d.__setitem__('docking/results_wt/probe.log', LOG.format(seed=101).replace('v1.2.7', 'v1.2.7-custom')), True, 'CHECK_FAILED'
    yield 'unsafe_zip_member', lambda d: d.__setitem__('../../escape.txt', 'NOT EXTRACTED'), True, 'UNSAFE_ARCHIVE_PATH'


def main():
    outcomes = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        for i, (name, modify, expected_problem, expected_type) in enumerate(cases()):
            data = fixture()
            modify(data)
            archive = base / f'{i:02d}_{name}.zip'
            reports = base / f'{i:02d}_{name}_out'
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
                for path, content in data.items():
                    z.writestr(PREFIX + path if path != '../../escape.txt' else PREFIX + path, content)
            proc = subprocess.run([sys.executable, str(AUDITOR), str(archive), str(reports)], capture_output=True, text=True)
            report_files = ['audit_summary.json', 'exceptions.csv', 'run_audit.csv', 'source_manifest.csv']
            written = all((reports / f).is_file() for f in report_files)
            summary = json.loads((reports / 'audit_summary.json').read_text()) if written else {}
            types = {x['type'] for x in summary.get('failed_checks', [])}
            okay = (proc.returncode == (1 if expected_problem else 0)
                    and written
                    and bool(summary.get('failures', 0)) == expected_problem
                    and (expected_type is None or expected_type in types))
            outcomes.append({'case': name, 'pass': okay, 'exit': proc.returncode,
                             'reports': written, 'failure_types': sorted(types)})
            print(('PASS' if okay else 'FAIL'), name, 'exit=', proc.returncode,
                  'reports=', written, 'types=', sorted(types))
            if not okay:
                print(proc.stderr[-1200:])
    print('RESULT:', sum(x['pass'] for x in outcomes), '/', len(outcomes))
    return 0 if all(x['pass'] for x in outcomes) else 1

if __name__ == '__main__':
    raise SystemExit(main())
