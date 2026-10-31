#!/usr/bin/env python3
"""Offline, synthetic fault-injection evaluation of the previously written Vina auditor.

Creates synthetic logs and PDBQT remarks for parser testing only: NO docking,
no molecular structures, no source research data or artifacts are used.
"""
from pathlib import Path
import sys, csv, io, json, zipfile, tempfile

HERE = Path(__file__).resolve().parent
from audit_workflow import main as audit_v1, BASE

CFG = 'center_x = 0.19\ncenter_y = -19.5\ncenter_z = 10.55\nsize_x = 24\nsize_y = 24\nsize_z = 24\nexhaustiveness = 8\nnum_modes = 9\n'

def log(score, seed, version='1.2.7', center=(0.19,-19.5,10.55), size=(24,24,24), exhaustive=8, include_seed=True, include_score=True):
    parts=[f'AutoDock Vina v{version}', f'Grid center: X {center[0]} Y {center[1]} Z {center[2]}',
       f'Grid size  : X {size[0]} Y {size[1]} Z {size[2]}', f'Exhaustiveness: {exhaustive}']
    if include_seed: parts.append(f'Performing docking (random seed: {seed}) ...')
    if include_score: parts.append(f'   1       {score:.3f}          0          0')
    return '\n'.join(parts)+'\n'

def fixture():
    data={'docking/vina_config.txt':CFG, 'run_docking.sh':'vina --receptor receptor.pdbqt --ligand ligand.pdbqt\n'}
    for lig in ('ligand_a','ligand_b'):
        data[f'docking/ligands_pdbqt/{lig}.pdbqt']='REMARK SYNTHETIC LIGAND IDENTIFIER\n'
    rows=[]
    for i,lig in enumerate(('ligand_a','ligand_b')):
        wt=-4.2-i*0.3; a53t=-4.8-i*0.3
        rows.append({'Compound':lig, 'WT_Affinity_kcal_mol':f'{wt:.3f}', 'A53T_Affinity_kcal_mol':f'{a53t:.3f}'})
        for j,(g,score) in enumerate((('wt',wt),('a53t',a53t))):
            data[f'docking/results_{g}/{lig}.log']=log(score,100+i*2+j)
            data[f'docking/results_{g}/{lig}_out.pdbqt']=f'REMARK VINA RESULT: {score:.3f} 0.000 0.000\n'
    f=io.StringIO(); w=csv.DictWriter(f,fieldnames=['Compound','WT_Affinity_kcal_mol','A53T_Affinity_kcal_mol']);w.writeheader();w.writerows(rows)
    data['docking_results_summary.csv']=f.getvalue()
    return data

def write_zip(path,data):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for key,value in sorted(data.items()):z.writestr(BASE+key,value)

TARGET='docking/results_wt/ligand_a.log'
POSE='docking/results_wt/ligand_a_out.pdbqt'

def alter_score_log(d):d[TARGET]=d[TARGET].replace('-4.200','-8.200')
def alter_pose_score(d):d[POSE]=d[POSE].replace('-4.200','-8.200')
def alter_summary(d):d['docking_results_summary.csv']=d['docking_results_summary.csv'].replace('-4.200','-8.200')
def alter_center(d):d[TARGET]=d[TARGET].replace('X 0.19 Y -19.5','X 1.19 Y -19.5')
def alter_size(d):d[TARGET]=d[TARGET].replace('X 24 Y 24 Z 24','X 25 Y 24 Z 24')
def alter_exhaust(d):d[TARGET]=d[TARGET].replace('Exhaustiveness: 8','Exhaustiveness: 4')
def remove_log(d):del d[TARGET]
def remove_pose(d):del d[POSE]
def remove_score(d):d[TARGET]=d[TARGET].replace('   1       -4.200          0          0\n','')
def remove_seed(d):d[TARGET]=d[TARGET].replace('Performing docking (random seed: 100) ...\n','')
def alter_version(d):d[TARGET]=d[TARGET].replace('AutoDock Vina v1.2.7','AutoDock Vina v0.0.0')
def alter_seed(d):d[TARGET]=d[TARGET].replace('random seed: 100','random seed: 101')
def remove_ligand(d):del d['docking/ligands_pdbqt/ligand_a.pdbqt']

cases=[
 ('baseline_clean',lambda d:None,False,'Clean control'),
 ('log_score_changed',alter_score_log,True,'Score inconsistent with pose and summary'),
 ('pose_score_changed',alter_pose_score,True,'Pose score inconsistent with log'),
 ('summary_score_changed',alter_summary,True,'Summary inconsistent with log'),
 ('grid_center_changed',alter_center,True,'Grid center mismatch'),
 ('grid_size_changed',alter_size,True,'Grid size mismatch'),
 ('exhaustiveness_changed',alter_exhaust,True,'Exhaustiveness mismatch'),
 ('log_missing',remove_log,True,'Missing primary execution log'),
 ('pose_missing',remove_pose,True,'Missing pose file'),
 ('log_best_score_missing',remove_score,True,'Unparsable best score'),
 ('seed_missing',remove_seed,True,'Missing execution seed'),
 ('version_changed',alter_version,True,'Unexpected application version'),
 ('seed_duplicated',alter_seed,True,'Identical seeds across two runs'),
 ('ligand_file_missing',remove_ligand,True,'Missing ligand input silently reduces expected run count'),
]

def run_all():
    out=HERE/'results'; out.mkdir(exist_ok=True)
    records=[]
    with tempfile.TemporaryDirectory(prefix='qc_synthetic_') as td:
        tmp=Path(td)
        for case,mutate,should_alert,why in cases:
            d=fixture(); mutate(d)
            archive=tmp/(case+'.zip');write_zip(archive,d)
            folder=tmp/(case+'_results')
            try:
                r=audit_v1(archive,folder)
                details=sorted({f['detail'] for f in r['failed_checks']})
                detected=r['failures']>0
                err=''
                status='PASS' if (detected==should_alert) else 'FAIL'
                records.append(dict(case=case,expected_alert=should_alert,detected_alert=detected,status=status,
                     failure_count=r['failures'],verified_primary_runs=r['verified_primary_runs'],
                     expected_primary_runs=r['expected_primary_runs'],details='; '.join(details),exception=err,description=why))
            except Exception as e:
                records.append(dict(case=case,expected_alert=should_alert,detected_alert=False,status='ERROR',
                     failure_count='',verified_primary_runs='',expected_primary_runs='',details='',exception=repr(e),description=why))
    with (out/'fault_injection_results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    positives=[r for r in records if r['expected_alert']]
    tp=sum(r['detected_alert'] for r in positives)
    fn=len(positives)-tp
    neg=[r for r in records if not r['expected_alert']]
    fp=sum(r['detected_alert'] for r in neg)
    tn=len(neg)-fp
    stats={'total_cases':len(records),'positive_fault_cases':len(positives),'true_positives':tp,'false_negatives':fn,
           'negative_control_cases':len(neg),'true_negatives':tn,'false_positives':fp,
           'sensitivity_on_designed_faults':tp/len(positives),'specificity_on_clean_controls':tn/len(neg),
           'important_note':'Synthetic single-fault demonstration, not field sensitivity/specificity or scientific validation of docking.'}
    (out/'validation_summary.json').write_text(json.dumps(stats,indent=2)+'\n')
    for r in records:print(f"{r['case']:<26} {'ALERT' if r['detected_alert'] else 'SILENT':<7} {r['status']:<5} {r['details']}")
    print('\n',json.dumps(stats,indent=2))
    return records,stats

if __name__=='__main__':
    records, stats = run_all()
    sys.exit(1 if any(row['status'] != 'PASS' for row in records) else 0)
