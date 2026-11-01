"""Focused CLI expectations with independent fixture construction and report assertions."""
import csv,hashlib,json,re,subprocess,sys,tempfile,zipfile
from pathlib import Path
BASE='asyn-cryptic-pocket-screening-main/'
AUDITOR=Path(__file__).resolve().parents[1]/'validation/audit_workflow_v2.py'
P='docking/results_wt/auditprobe.log';POSE='docking/results_wt/auditprobe_out.pdbqt'
def fixture():
    d={'docking/vina_config.txt':'center_x = 3\ncenter_y = -2\ncenter_z = 9\nsize_x = 18\nsize_y = 22\nsize_z = 26\nexhaustiveness = 12\nnum_modes = 3\n','run_docking.sh':'vina --receptor r.pdbqt --ligand auditprobe.pdbqt\n','docking/ligands_pdbqt/auditprobe.pdbqt':'REMARK SYNTHETIC\n','docking_results_summary.csv':'Compound,WT_Affinity_kcal_mol,A53T_Affinity_kcal_mol\nauditprobe,-5.250,-6.750\n'}
    for g,score,seed in [('wt','-5.250',719),('a53t','-6.750',823)]:
        d[f'docking/results_{g}/auditprobe.log']=f'AutoDock Vina v1.2.7\nGrid center: X 3 Y -2 Z 9\nGrid size : X 18 Y 22 Z 26\nExhaustiveness: 12\nPerforming docking (random seed: {seed}) ...\n   1 {score} 0 0\n'
        d[f'docking/results_{g}/auditprobe_out.pdbqt']=f'REMARK VINA RESULT: {score} 0 0\n'
    return d
def append(d,line):d[P]+=line+'\n'
CASES=[
('clean',lambda d:None,0,None,2),
('T01_bad_repeated_top_score',lambda d:append(d,'   1 -99oops 0 0'),1,'INVALID_LOG',1),
('T02_empty_repeated_version',lambda d:append(d,'AutoDock Vina v'),1,'INVALID_LOG',1),
('T03_empty_repeated_exhaustiveness',lambda d:append(d,'Exhaustiveness:'),1,'INVALID_LOG',1),
('T04_empty_repeated_seed',lambda d:append(d,'Performing docking (random seed: ) ...'),1,'INVALID_LOG',1),
('T05_invalid_secondary_pose',lambda d:d.__setitem__(POSE,d[POSE]+'REMARK VINA RESULT: -9oops 0 0\n'),1,'INVALID_POSE',1),
('T06_comment_text',lambda d:d.__setitem__('run_docking.sh','# vina --receptor x --seed 5\n'),0,None,2),
('T07_empty_ligand_presence_only',lambda d:d.__setitem__('docking/ligands_pdbqt/auditprobe.pdbqt',''),0,None,2),
('T08_crlf_clean',lambda d:d.update({k:v.replace('\n','\r\n') for k,v in d.items()}),0,None,2),
('T09_malformed_csv',lambda d:d.__setitem__('docking_results_summary.csv',d['docking_results_summary.csv']+'"unclosed'),1,'INVALID_CSV',0),
('T10_duplicate_member',lambda d:None,1,'DUPLICATE_ARCHIVE_MEMBER',1),
('T11_corrupt_archive',lambda d:None,1,'INVALID_ARCHIVE',0),
('T12_duplicate_summary_header',lambda d:d.__setitem__('docking_results_summary.csv','Compound,WT_Affinity_kcal_mol,WT_Affinity_kcal_mol,A53T_Affinity_kcal_mol\nauditprobe,-99,-5.250,-6.750\n'),1,'DUPLICATE_CSV_HEADER',2),
]
def main():
    results=[]
    with tempfile.TemporaryDirectory() as td:
        for name,mutate,expected,kind,verified in CASES:
            f=Path(td)/name;f.mkdir();arc=f/'input.zip';out=f/'reports';d=fixture();mutate(d)
            with zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED) as z:
                for k,v in d.items():z.writestr(BASE+k,v)
                if name=='T10_duplicate_member':
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore');z.writestr(BASE+P,d[P])
            if name=='T11_corrupt_archive':arc.write_bytes(b'not a zip')
            proc=subprocess.run([sys.executable,'-B',str(AUDITOR),str(arc),str(out)],capture_output=True,text=True,timeout=30)
            try:
                assert proc.returncode==expected,(proc.returncode,proc.stderr)
                assert all((out/n).is_file() for n in ['audit_summary.json','run_audit.csv','exceptions.csv','source_manifest.csv'])
                summary=json.loads((out/'audit_summary.json').read_text(encoding='utf-8'))
                with (out/'exceptions.csv').open(encoding='utf-8',newline='') as stream: exceptions=list(csv.DictReader(stream))
                assert exceptions==summary['failed_checks']
                assert summary['failures']==len(exceptions)
                assert bool(summary['failures'])==bool(expected)
                kinds=sorted({x['type'] for x in exceptions})
                if kind:assert kind in kinds
                assert summary['verified_primary_runs']==verified,summary['verified_primary_runs']
                if not summary.get('terminal_error'):
                    assert summary['source_archive_sha256']==hashlib.sha256(arc.read_bytes()).hexdigest()
                    with (out/'source_manifest.csv').open(encoding='utf-8',newline='') as stream:
                        manifest=list(csv.DictReader(stream))
                    with zipfile.ZipFile(arc) as z:
                        infos=[x for x in z.infolist() if not x.is_dir()]
                        assert len(manifest)==len(infos)
                        for row,info in zip(manifest,infos):
                            assert row['sha256']==hashlib.sha256(z.read(info)).hexdigest()
                            assert int(row['bytes'])==len(z.read(info))
                    with (out/'run_audit.csv').open(encoding='utf-8',newline='') as stream:runs=list(csv.DictReader(stream))
                    assert sum(x['run_disposition']=='PASS' for x in runs)==verified
                    if name.startswith(('T01','T02','T03','T04','T05')):
                        assert next(x for x in runs if x['system']=='wt')['run_disposition']=='FAIL'
                    if name=='clean':
                        assert [float(x['best_score']) for x in runs]==[-5.25,-6.75]
                    if name=='T06_comment_text':
                        assert summary['script_contains_vina_invocation_text'] is True
                        assert summary['script_contains_seed_option_text'] is True
                        assert 'script_uses_external_binaries' not in summary
                        assert 'script_contains_fixed_seed' not in summary
                passed=True;detail=''
            except Exception as exc:
                passed=False;detail=repr(exc);kinds=[];summary={}
            results.append({'case':name,'expected_exit':expected,'observed_exit':proc.returncode,'expected_issue':kind,'observed_issues':kinds,'verified_primary_runs':summary.get('verified_primary_runs'),'pass':passed,'detail':detail})
            print(('PASS' if passed else 'FAIL'),name,detail)
    dest=Path(__file__).resolve().parents[1]/'generated';dest.mkdir(exist_ok=True)
    (dest/'portfolio_integrity_results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print('RESULT',sum(x['pass'] for x in results),'/',len(results))
    return 0 if all(x['pass'] for x in results) else 1
if __name__=='__main__':raise SystemExit(main())
