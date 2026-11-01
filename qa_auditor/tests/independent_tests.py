#!/usr/bin/env python3
"""Independent reviewer-origin tests bundled as historical regression coverage.
Own fixture generator (3 ligands, different grid/seed/scores than the repo's fixture).
Usage: python independent_tests.py <path to qa_auditor/validation>   (stdlib only; writes tests/results.json in the repository)
Each case: expected behaviour is stated BEFORE running; the actual result is recorded.
Outcomes per auditor: ALERT(n) | SILENT | CRASH(ExcType) ; plus whether exceptions.csv was written.
"""
import sys, io, csv, zipfile, tempfile, warnings, time, re, json
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO))
import audit_workflow as A1
import audit_workflow_v2 as A2
BASE = A1.BASE

CFG = ('center_x = -3.5\ncenter_y = 12.25\ncenter_z = 7\n'
       'size_x = 20\nsize_y = 22\nsize_z = 18\nexhaustiveness = 16\nnum_modes = 9\n')
LIGS = ['cmpd1', 'cmpd2', 'cmpd3']

def log_text(score, seed, version='1.2.7', center=('-3.5', '12.25', '7'),
             size=('20', '22', '18'), exh=16, seed_line=True, ver_line=True, exh_line=True, crlf=False,
             score_fmt='{:.3f}'):
    p = []
    if ver_line: p.append(f'AutoDock Vina v{version}')
    p.append(f'Grid center: X {center[0]} Y {center[1]} Z {center[2]}')
    p.append(f'Grid size  : X {size[0]} Y {size[1]} Z {size[2]}')
    if exh_line: p.append(f'Exhaustiveness: {exh}')
    if seed_line: p.append(f'Performing docking (random seed: {seed}) ...')
    p.append('   1       ' + score_fmt.format(score) + '          0          0')
    s = '\n'.join(p) + '\n'
    return s.replace('\n', '\r\n') if crlf else s

def fixture(**kw):
    d = {'docking/vina_config.txt': CFG, 'run_docking.sh': 'vina --receptor r.pdbqt --ligand l.pdbqt\n'}
    rows = []
    for i, lig in enumerate(LIGS):
        d[f'docking/ligands_pdbqt/{lig}.pdbqt'] = 'REMARK SYNTH\n'
        wt, a = -6.1 - 0.4 * i, -7.3 - 0.4 * i
        rows.append({'Compound': lig, 'WT_Affinity_kcal_mol': f'{wt:.3f}', 'A53T_Affinity_kcal_mol': f'{a:.3f}'})
        for j, (g, sc) in enumerate((('wt', wt), ('a53t', a))):
            d[f'docking/results_{g}/{lig}.log'] = log_text(sc, 5000 + i * 7 + j * 3, **kw)
            d[f'docking/results_{g}/{lig}_out.pdbqt'] = f'REMARK VINA RESULT: {sc:.3f} 0.000 0.000\n'
    d['docking_results_summary.csv'] = rows_to_csv(rows)
    return d

def rows_to_csv(rows, fields=('Compound', 'WT_Affinity_kcal_mol', 'A53T_Affinity_kcal_mol'), bom=False, eol='\n'):
    f = io.StringIO(newline='')
    w = csv.DictWriter(f, fieldnames=list(fields), lineterminator=eol); w.writeheader(); w.writerows(rows)
    return ('\ufeff' if bom else '') + f.getvalue()

def parse_rows(d):
    return list(csv.DictReader(io.StringIO(d['docking_results_summary.csv'])))

def write_zip(path, d, dup=None):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            for k, v in sorted(d.items()):
                z.writestr(BASE + k, v)
            if dup:  # second member with identical name
                z.writestr(BASE + dup[0], dup[1])

def run(mod, arc, out):
    try:
        r = mod.main(arc, out)
        ex_written = (out / 'exceptions.csv').exists()
        return (f"ALERT({r['failures']})" if r['failures'] else 'SILENT'), ex_written, sorted({f['type'] + ':' + f['detail'] if f['type'] == 'CHECK_FAILED' else f['type'] for f in r['failed_checks']})
    except Exception as e:
        return f'CRASH({type(e).__name__})', (out / 'exceptions.csv').exists(), []

cases = []
def case(cid, desc, expect, mut=None, dup=None, **fx):
    cases.append((cid, desc, expect, mut, dup, fx))

# ---------------- clean controls (expect SILENT) ----------------
case('C1', 'Clean, 3 ligands, different grid/exhaustiveness/seeds', 'SILENT')
case('C2', 'Clean, CRLF line endings in logs', 'SILENT', crlf=True)
case('C3', 'Clean, seed value 0 and negative seed', 'SILENT',
     mut=lambda d: (d.__setitem__('docking/results_wt/cmpd1.log', log_text(-6.1, 0)),
                    d.__setitem__('docking/results_a53t/cmpd1.log', log_text(-7.3, -42))))
case('C4', 'Clean, numerically-equal formatting (log prints 24.0 / -3.50 vs config 20 / -3.5)', 'SILENT',
     center=('-3.50', '12.250', '7.0'), size=('20.0', '22.0', '18.0'))
case('C5', 'Clean, config file has an inline comment on one line', 'SILENT',
     mut=lambda d: d.__setitem__('docking/vina_config.txt', CFG.replace('exhaustiveness = 16', 'exhaustiveness = 16  # standard')))
case('C6', 'Clean, summary CSV saved by Excel (UTF-8 BOM)', 'SILENT',
     mut=lambda d: d.__setitem__('docking_results_summary.csv', '\ufeff' + d['docking_results_summary.csv']))
case('C7', 'Clean data but run produced with Vina v1.2.5 (legit different version)', 'SILENT (policy-dependent)', version='1.2.5')
case('C8', 'Clean, log prints 1 decimal (-6.1) while pose/summary print 3 (-6.100)', 'SILENT', score_fmt='{:.1f}')

# ---------------- new faults (expect ALERT) ----------------
def f_orphan(d):
    d['docking/results_wt/cmpd9.log'] = log_text(-5.0, 9999)
    d['docking/results_wt/cmpd9_out.pdbqt'] = 'REMARK VINA RESULT: -5.000 0 0\n'
case('F1', 'Orphan result files (cmpd9) with no input and no summary row', 'ALERT', mut=f_orphan)

def f_dup_row(d):
    rows = parse_rows(d); rows.append(dict(rows[0], WT_Affinity_kcal_mol='-9.900'))
    d['docking_results_summary.csv'] = rows_to_csv(rows)
case('F2', 'Duplicate summary row for cmpd1 with CONFLICTING score (appended after correct row)', 'ALERT', mut=f_dup_row)

def f_dup_row2(d):
    rows = parse_rows(d); rows.insert(0, dict(rows[0], WT_Affinity_kcal_mol='-9.900'))
    d['docking_results_summary.csv'] = rows_to_csv(rows)
case('F2b', 'Same, but conflicting row placed BEFORE the correct row', 'ALERT', mut=f_dup_row2)

def f_empty_cell(d):
    rows = parse_rows(d); rows[1]['A53T_Affinity_kcal_mol'] = ''
    d['docking_results_summary.csv'] = rows_to_csv(rows)
case('F3', 'Empty score cell in summary CSV', 'ALERT (graceful)', mut=f_empty_cell)

def f_nonnum(d):
    rows = parse_rows(d); rows[1]['WT_Affinity_kcal_mol'] = 'N/A'
    d['docking_results_summary.csv'] = rows_to_csv(rows)
case('F4', 'Non-numeric score ("N/A") in summary CSV', 'ALERT (graceful)', mut=f_nonnum)

case('F5', 'Summary CSV missing the A53T column', 'ALERT (graceful)',
     mut=lambda d: d.__setitem__('docking_results_summary.csv', rows_to_csv(
         [{k: v for k, v in r.items() if k != 'A53T_Affinity_kcal_mol'} for r in parse_rows(d)],
         fields=('Compound', 'WT_Affinity_kcal_mol'))))

case('F6', 'Pose file: model 1 mismatches log, model 2 equals log', 'ALERT',
     mut=lambda d: d.__setitem__('docking/results_wt/cmpd1_out.pdbqt',
                                  'REMARK VINA RESULT: -9.000 0 0\nREMARK VINA RESULT: -6.100 1.2 2.1\n'))

def f_swap(d):
    a, b = 'docking/results_wt/cmpd1_out.pdbqt', 'docking/results_wt/cmpd2_out.pdbqt'
    d[a], d[b] = d[b], d[a]
case('F7', 'Pose files swapped between cmpd1 and cmpd2 (different scores)', 'ALERT', mut=f_swap)

def f_no_a53t(d):
    for k in [k for k in d if k.startswith('docking/results_a53t/')]: del d[k]
case('F8', 'Entire results_a53t folder missing', 'ALERT', mut=f_no_a53t)

def f_no_logs(d):
    for k in [k for k in d if k.endswith('.log')]: del d[k]
case('F9', 'ALL logs missing (nothing auditable) -> should report exceptions, not crash', 'ALERT (graceful)', mut=f_no_logs)

case('F10', 'Version line absent from one log', 'ALERT',
     mut=lambda d: d.__setitem__('docking/results_wt/cmpd2.log', log_text(-6.5, 5007, ver_line=False)))
case('F11', 'Exhaustiveness line absent from one log', 'ALERT',
     mut=lambda d: d.__setitem__('docking/results_wt/cmpd2.log', log_text(-6.5, 5007, exh_line=False)))
case('F12', 'Grid center X/Z transposed in one log', 'ALERT',
     mut=lambda d: d.__setitem__('docking/results_wt/cmpd2.log', log_text(-6.5, 5007, center=('7', '12.25', '-3.5'))))
case('F13', 'Config missing exhaustiveness key', 'ALERT (graceful)',
     mut=lambda d: d.__setitem__('docking/vina_config.txt', CFG.replace('exhaustiveness = 16\n', '')))
case('F14', 'Three runs share one seed', 'ALERT',
     mut=lambda d: [d.__setitem__(f'docking/results_{g}/{l}.log', log_text(sc, 777))
                    for g, l, sc in (('wt', 'cmpd1', -6.1), ('wt', 'cmpd2', -6.5), ('a53t', 'cmpd3', -8.1))])
case('F15', 'Duplicate ZIP member: second copy of cmpd1.log (altered score) appended', 'ALERT', dup=('docking/results_wt/cmpd1.log', log_text(-1.0, 5000)))
case('F16', 'Score tolerance: log differs from pose by 0.0009 (within 0.001)', 'SILENT',
     mut=lambda d: d.__setitem__('docking/results_wt/cmpd1.log', log_text(-6.1009, 5000, score_fmt='{:.4f}')))
case('F17', 'Score tolerance: log differs from pose by 0.0020', 'ALERT',
     mut=lambda d: d.__setitem__('docking/results_wt/cmpd1.log', log_text(-6.102, 5000, score_fmt='{:.4f}')))

def f_consistent(d):
    d['docking/results_wt/cmpd1.log'] = log_text(-9.0, 5000)
    d['docking/results_wt/cmpd1_out.pdbqt'] = 'REMARK VINA RESULT: -9.000 0 0\n'
    rows = parse_rows(d); rows[0]['WT_Affinity_kcal_mol'] = '-9.000'
    d['docking_results_summary.csv'] = rows_to_csv(rows)
case('F18', 'KNOWN LIMIT: score altered identically in log+pose+summary (consistent tampering)', 'SILENT (by design)', mut=f_consistent)

case('F15b', 'Duplicate ZIP member: TAMPERED copy first, clean copy last (zipfile returns last)', 'ALERT',
     mut=lambda d: d.__setitem__('docking/results_wt/cmpd1.log', log_text(-1.0, 5000)),
     dup=('docking/results_wt/cmpd1.log', log_text(-6.1, 5000)))

def c9(d):
    d['docking/results_wt/cmpd1.log'] = log_text(-6.147, 5000, score_fmt='{:.1f}')
    d['docking/results_wt/cmpd1_out.pdbqt'] = 'REMARK VINA RESULT: -6.147 0 0\n'
    rows = parse_rows(d); rows[0]['WT_Affinity_kcal_mol'] = '-6.147'
    d['docking_results_summary.csv'] = rows_to_csv(rows)
case('C9', 'Clean: log prints 1 decimal (-6.1) vs pose/summary 3 decimals (-6.147) [CONDITIONAL: unverified vs real Vina]', 'SILENT', mut=c9)

def main():
    print(f'{"ID":<4}{"v1":<14}{"v2":<14}{"exc.csv(v1/v2)":<16}description')
    results = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for cid, desc, expect, mut, dup, fx in cases:
            d = fixture(**fx)
            if mut: mut(d)
            arc = td / f'{cid}.zip'; write_zip(arc, d, dup)
            r1 = run(A1, arc, td / f'{cid}_1'); r2 = run(A2, arc, td / f'{cid}_2')
            results.append(dict(id=cid, desc=desc, expect=expect, v1=r1[0], v2=r2[0], v1_exc=r1[1], v2_exc=r2[1], v2_detail=r2[2]))
            print(f'{cid:<4}{r1[0]:<14}{r2[0]:<14}{str(r1[1])[0]+"/"+str(r2[1])[0]:<16}{desc}  [expected: {expect}]')
    output = Path(__file__).resolve().parent / 'results.json'
    output.write_text(json.dumps(results, indent=1) + '\n')
    failures=[]
    for rec in results:
        expected=rec['expect']
        observed=rec['v2']
        if rec['id'] in ('C7', 'C9'):
            passed=None
        elif expected.startswith('ALERT'):
            passed=observed.startswith('ALERT(') and rec['v2_exc']
        elif expected == 'SILENT':
            passed=observed == 'SILENT'
        else:
            # Version-policy and score-rounding cases need deliberate reviewer decisions.
            passed=None
        rec['assessment']='PASS' if passed else ('REVIEW' if passed is None else 'FAIL')
        if passed is False:
            failures.append(rec['id'])
    output.write_text(json.dumps(results, indent=1) + '\n')
    print('INDEPENDENT TEST ASSESSMENT:', {k:sum(r['assessment']==k for r in results) for k in ('PASS','REVIEW','FAIL')})
    if failures:
        raise SystemExit('Failed independent cases: '+', '.join(failures))

    # ---- performance probe of v2 parser ----
    print('\nparse_log() timing on a log padded with N whitespace-only lines (no match present):')
    for n in (5_000, 10_000, 20_000, 40_000):
        txt = 'AutoDock Vina v1.2.7\n' + ('\n' * n) + 'end\n'
        t = time.perf_counter(); A2.parse_log(txt); dt = time.perf_counter() - t
        print(f'  N={n:>6}  {dt:7.3f} s')

if __name__ == '__main__':
    main()