#!/usr/bin/env python3
"""Read-only QA audit of an archived Vina workflow; no docking is executed."""
from pathlib import Path
import zipfile, csv, io, re, json, hashlib, argparse
from collections import Counter

BASE = 'asyn-cryptic-pocket-screening-main/'

def parse_config(text):
    d={}
    for line in text.splitlines():
        m=re.match(r'^\s*([A-Za-z_]+)\s*=\s*([-+\d.]+)\s*$',line)
        if m: d[m.group(1)]=float(m.group(2))
    return d

def parse_log(text):
    v=re.search(r'AutoDock Vina v([\d.]+)',text)
    center=re.search(r'Grid center:\s*X\s*([-\d.]+)\s*Y\s*([-\d.]+)\s*Z\s*([-\d.]+)',text)
    size=re.search(r'Grid size\s*:\s*X\s*([-\d.]+)\s*Y\s*([-\d.]+)\s*Z\s*([-\d.]+)',text)
    ex=re.search(r'Exhaustiveness:\s*(\d+)',text)
    seed=re.search(r'random seed:\s*(-?\d+)',text)
    mode=re.search(r'^\s*1\s+(-?\d+(?:\.\d+)?)\s+0(?:\.0+)?\s+0(?:\.0+)?\s*$',text,re.M)
    return {'version':v.group(1) if v else None,'center':tuple(map(float,center.groups())) if center else None,
            'size':tuple(map(float,size.groups())) if size else None,'exhaustiveness':int(ex.group(1)) if ex else None,
            'seed':int(seed.group(1)) if seed else None,'best_score':float(mode.group(1)) if mode else None}

def main(archive, out):
    out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        names=set(z.namelist())
        def get(p):return z.read(BASE+p).decode('utf-8',errors='replace')
        cfg=parse_config(get('docking/vina_config.txt'))
        script=get('run_docking.sh')
        entries=[]; failures=[]
        rows=list(csv.DictReader(io.StringIO(get('docking_results_summary.csv'))))
        csv_by={r['Compound']:r for r in rows}
        ligs=sorted(Path(x).stem for x in names if x.startswith(BASE+'docking/ligands_pdbqt/') and x.endswith('.pdbqt') and not x.endswith('_out.pdbqt'))
        # File presence is reported separately from scientific validity.
        for group in ['wt','a53t']:
            for ligand in ligs:
                logname=f'docking/results_{group}/{ligand}.log'
                posename=f'docking/results_{group}/{ligand}_out.pdbqt'
                if BASE+logname not in names:
                    failures.append({'type':'MISSING_LOG','sample':f'{group}/{ligand}','detail':logname});continue
                log=parse_log(get(logname))
                pose_present=BASE+posename in names
                pose_score=None
                if pose_present:
                    pose=re.search(r'^REMARK VINA RESULT:\s*(-?[\d.]+)',get(posename),re.M)
                    if pose: pose_score=float(pose.group(1))
                col='WT_Affinity_kcal_mol' if group=='wt' else 'A53T_Affinity_kcal_mol'
                csvscore=float(csv_by[ligand][col]) if ligand in csv_by else None
                expected_center=tuple(cfg[f'center_{x}'] for x in 'xyz')
                expected_size=tuple(cfg[f'size_{x}'] for x in 'xyz')
                check={'config_center':log['center']==expected_center,
                       'config_size':log['size']==expected_size,
                       'exhaustiveness':log['exhaustiveness']==int(cfg['exhaustiveness']),
                       'log_vs_pose_score':pose_score is not None and log['best_score'] is not None and abs(log['best_score']-pose_score)<0.001,
                       'log_vs_summary_score':csvscore is not None and log['best_score'] is not None and abs(log['best_score']-csvscore)<0.001,
                       'pose_exists':pose_present}
                for k,ok in check.items():
                    if not ok:failures.append({'type':'CHECK_FAILED','sample':f'{group}/{ligand}','detail':k})
                entries.append({'system':group,'ligand':ligand,'version':log['version'],'best_score':log['best_score'],
                                'pose_score':pose_score,'summary_score':csvscore,'seed':log['seed'],
                                **{k:('PASS' if v else 'FAIL') for k,v in check.items()}})
        with (out/'run_audit.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(entries[0]));w.writeheader();w.writerows(entries)
        with (out/'exceptions.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['type','sample','detail']);w.writeheader();w.writerows(failures)
        fullmanifest=[]
        for n in sorted(names):
            if n.endswith('/'):continue
            raw=z.read(n)
            fullmanifest.append({'file':n[len(BASE):] if n.startswith(BASE) else n,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        with (out/'source_manifest.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['file','bytes','sha256']);w.writeheader();w.writerows(fullmanifest)
        summary={'source_archive':archive.name,'source_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
                 'archive_files':len(fullmanifest),'ligands':len(ligs),'expected_primary_runs':len(ligs)*2,
                 'verified_primary_runs':len(entries),'failures':len(failures),'failed_checks':failures,
                 'version_counts':dict(Counter(str(x['version']) for x in entries)),
                 'distinct_seeds':len(set(x['seed'] for x in entries)),
                 'config':cfg,'script_uses_external_binaries':'vina --receptor' in script,
                 'script_contains_fixed_seed':'--seed' in script,
                 'csv_rows':len(rows), 'archive_contains_duplicate_out_log':BASE+'docking/results_wt/anle138b_out.log' in names}
        (out/'audit_summary.json').write_text(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(main(args.archive,args.output),indent=2))
