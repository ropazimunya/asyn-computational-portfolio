#!/usr/bin/env python3
"""Six independent-review-derived CLI regression tests plus a clean control."""
import tempfile, zipfile, json, sys, subprocess
from pathlib import Path
from additional_hardening_tests import fixture, AUDITOR, PREFIX, LOG, CFG, SUMMARY

def apply(case, data):
    if case == 'seed_decimal':
        data['docking/results_wt/probe.log'] = LOG.format(seed='101.5')
    elif case == 'seed_suffix':
        data['docking/results_wt/probe.log'] = LOG.format(seed='101oops')
    elif case == 'nested_ligand':
        data['docking/ligands_pdbqt/nested/probe.pdbqt'] = data.pop('docking/ligands_pdbqt/probe.pdbqt')
    elif case == 'negative_num_modes':
        data['docking/vina_config.txt'] = CFG + 'num_modes = -1\n'
    elif case == 'blank_csv_line':
        data['docking_results_summary.csv'] = SUMMARY + '\n'
    elif case == 'invalid_archive':
        pass

cases = {
    'seed_decimal': ('INVALID_LOG', True),
    'seed_suffix': ('INVALID_LOG', True),
    'nested_ligand': ('UNEXPECTED_LIGAND_PATH', True),
    'negative_num_modes': ('INVALID_CONFIG', True),
    'blank_csv_line': (None, False),
    'invalid_archive': ('INVALID_ARCHIVE', True),
    'clean': (None, False),
}

def main():
    successes = 0
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for name, (expected_type, should_fail) in cases.items():
            data = fixture()
            apply(name, data)
            zip_path = root / f'{name}.zip'
            if name == 'invalid_archive':
                zip_path.write_bytes(b'not a zip')
            else:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                    for path, content in data.items():
                        z.writestr(PREFIX+path, content)
            dest = root / f'{name}_out'
            run = subprocess.run([sys.executable,str(AUDITOR),str(zip_path),str(dest)],capture_output=True,text=True)
            reports = all((dest/f).is_file() for f in ['audit_summary.json','exceptions.csv','run_audit.csv','source_manifest.csv'])
            summary = json.loads((dest/'audit_summary.json').read_text()) if reports else {}
            types = {x['type'] for x in summary.get('failed_checks', [])}
            passed = (run.returncode == (1 if should_fail else 0) and reports and bool(summary.get('failures',0)) == should_fail and (expected_type is None or expected_type in types))
            successes += passed
            print(('PASS' if passed else 'FAIL'), name, 'exit',run.returncode,'reports',reports,'types',sorted(types))
    print('RESULT',successes,'/',len(cases))
    return 0 if successes == len(cases) else 1

if __name__ == '__main__':
    raise SystemExit(main())
