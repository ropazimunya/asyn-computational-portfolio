"""Run fixed synthetic suites and persist their actual results without network access."""
from pathlib import Path
import csv,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa_auditor';OUT=QA/'generated'
def main():
    OUT.mkdir(exist_ok=True)
    suites=[('comparison',[QA/'validation/compare_versions.py']),('historical_independent',[QA/'tests/independent_tests.py',QA/'validation']),('hardening',[QA/'tests/additional_hardening_tests.py']),('round4',[QA/'tests/reviewer_round4_tests.py']),('round5',[QA/'tests/reviewer_round5_tests.py']),('round6',[QA/'tests/reviewer_round6_tests.py']),('portfolio_integrity',[QA/'tests/portfolio_integrity_tests.py'])]
    results=[]
    for name,args in suites:
        proc=subprocess.run([sys.executable,'-B',*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=120)
        # Store stdout without absolute host paths; no private input is used.
        (OUT/(name+'.stdout.txt')).write_text(proc.stdout.replace(str(ROOT),'<repository>'),encoding='utf-8')
        (OUT/(name+'.stderr.txt')).write_text(proc.stderr.replace(str(ROOT),'<repository>'),encoding='utf-8')
        results.append({'suite':name,'exit':proc.returncode})
        print(name,'exit',proc.returncode)
    comparison=json.loads((QA/'validation/results/v1_vs_v2_summary.json').read_text())
    with (QA/'validation/results/v1_vs_v2_fault_detection.csv').open(newline='') as stream:rows=list(csv.DictReader(stream))
    independent=json.loads((QA/'tests/results.json').read_text())
    focused=json.loads((OUT/'portfolio_integrity_results.json').read_text())
    checks={'comparison_rows':len(rows)==14 and all(x['v2_status']=='PASS' for x in rows),'comparison_summary':comparison=={'cases':14,'introduced_faults':13,'v1_detected_faults':9,'v2_detected_faults':13,'v2_passes':14},'review_set':{x['id'] for x in independent if x['assessment']=='REVIEW'}=={'C7','C9','F18'},'no_independent_failures':not any(x['assessment']=='FAIL' for x in independent),'focused_assertions':len(focused)==13 and all(x['pass'] for x in focused)}
    result={'python':platform.python_version(),'platform':platform.system(),'suites':results,'assertions':checks,'comparison':comparison,'historical_independent':{v:sum(x['assessment']==v for x in independent) for v in ['PASS','REVIEW','FAIL']},'review_cases':[{'id':x['id'],'expectation':x['expect'],'observed':x['v2']} for x in independent if x['assessment']=='REVIEW'],'all_assertions_passed':all(x['exit']==0 for x in results) and all(checks.values()),'scope':'synthetic demonstrations only; scenarios overlap; REVIEW is not PASS'}
    (OUT/'execution_summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0 if result['all_assertions_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
