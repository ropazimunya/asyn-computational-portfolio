#!/usr/bin/env python3
"""Run identical synthetic datasets through baseline and enhanced auditors."""
import csv, json, tempfile, sys
from pathlib import Path
from validate_injected_faults import cases, fixture, write_zip
from audit_workflow import main as v1
from audit_workflow_v2 import main as v2
HERE=Path(__file__).resolve().parent
rows=[]
with tempfile.TemporaryDirectory() as td:
    t=Path(td)
    for name,mutate,expected,description in cases:
        d=fixture(); mutate(d)
        arc=t/(name+'.zip');write_zip(arc,d)
        r1=v1(arc,t/(name+'_v1'));r2=v2(arc,t/(name+'_v2'))
        detected1=r1['failures']>0;detected2=r2['failures']>0
        rows.append(dict(case=name,expected_alert=expected,v1_detected=detected1,v2_detected=detected2,
                         v1_failures=r1['failures'],v2_failures=r2['failures'],v2_types=';'.join(sorted(set(x['type'] for x in r2['failed_checks']))),
                         v2_status='PASS' if expected==detected2 else 'FAIL'))
for r in rows:print(r['case'], 'v1',r['v1_detected'],'v2',r['v2_detected'],r['v2_status'])
out=HERE/'results'
out.mkdir(parents=True, exist_ok=True)
with (out/'v1_vs_v2_fault_detection.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'cases':len(rows),'introduced_faults':sum(r['expected_alert'] for r in rows),
         'v1_detected_faults':sum(r['v1_detected'] and r['expected_alert'] for r in rows),
         'v2_detected_faults':sum(r['v2_detected'] and r['expected_alert'] for r in rows),
         'v2_passes':sum(r['v2_status']=='PASS' for r in rows)}
(out/'v1_vs_v2_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

if any(row['v2_status'] != 'PASS' for row in rows):
    sys.exit(1)
