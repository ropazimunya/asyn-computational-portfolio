#!/usr/bin/env python3
"""Synthetic demonstration auditor for archived Vina-style records.

Not a validated scientific or GxP quality system. No docking performed.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import re
import zipfile
from pathlib import PurePosixPath
from collections import Counter
from pathlib import Path

BASE = 'asyn-cryptic-pocket-screening-main/'  # Synthetic test fixture root
GROUPS = ('wt', 'a53t')
FIELDS = ('type', 'sample', 'detail')
FLOAT = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'


def parse_config(text):
    """Parse a single unambiguous set of finite configuration values."""
    config = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.partition('#')[0].strip()
        if not line:
            continue
        match = re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(' + FLOAT + r')', line)
        if not match:
            raise ValueError(f'invalid config assignment at line {lineno}: {line!r}')
        key = match.group(1)
        if key in config:
            raise ValueError(f'duplicate config key {key!r} at line {lineno}')
        number = float(match.group(2))
        if not math.isfinite(number):
            raise ValueError(f'nonfinite config value for {key}')
        if key in ('exhaustiveness', 'num_modes') and (number < 1 or not number.is_integer()):
            raise ValueError(f'{key} must be a positive integer')
        if key.startswith('size_') and number <= 0:
            raise ValueError(f'{key} must be positive')
        config[key] = int(number) if key in ('exhaustiveness', 'num_modes') else number
    return config


def parse_log(text):
    """Identify recognized fields before validating complete values."""
    lines=text.splitlines()
    def one(label, candidates, pattern):
        if len(candidates)>1:
            raise ValueError(f'multiple {label} fields found in one log')
        if not candidates: return None
        match=re.fullmatch(pattern,candidates[0])
        if match is None: raise ValueError(f'malformed {label} field')
        return match
    def xyz(label):
        candidates=[x for x in lines if re.match(r'^'+label+r'(?:[ \t:]|$)',x)]
        m=one(label,candidates,label+r'[ \t]*:[ \t]*X[ \t]*('+FLOAT+r')[ \t]+Y[ \t]*('+FLOAT+r')[ \t]+Z[ \t]*('+FLOAT+r')[ \t]*')
        vals=tuple(map(float,m.groups())) if m else None
        if vals is not None and not all(map(math.isfinite,vals)): raise ValueError('nonfinite '+label)
        return vals
    version=one('version',[x for x in lines if x.startswith('AutoDock Vina')],r'AutoDock Vina v([^ \t]+)[ \t]*')
    exhaust=one('exhaustiveness',[x for x in lines if re.match(r'^Exhaustiveness(?:[ \t:]|$)',x)],r'Exhaustiveness:[ \t]*([0-9]+)[ \t]*')
    seed=one('seed',[x for x in lines if 'random seed' in x],r'.*random seed:[ \t]*(-?[0-9]+)[ \t]*\).*')
    mode=one('top score',[x for x in lines if re.match(r'^[ \t]*1(?:[ \t]|$)',x)],r'[ \t]*1[ \t]+('+FLOAT+r')[ \t]+0(?:\.0+)?[ \t]+0(?:\.0+)?[ \t]*')
    ex=int(exhaust[1]) if exhaust else None
    if ex is not None and ex<1: raise ValueError('nonpositive exhaustiveness')
    score=float(mode[1]) if mode else None
    if score is not None and not math.isfinite(score): raise ValueError('nonfinite score')
    return {'version':version[1] if version else None,'center':xyz('Grid center'),
            'size':xyz('Grid size'),'exhaustiveness':ex,'seed':int(seed[1]) if seed else None,'best_score':score}


def hash_archive_streaming(archive):
    h = hashlib.sha256()
    with archive.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_terminal_error(out, archive, exc):
    out.mkdir(parents=True, exist_ok=True)
    issue = {'type': 'INVALID_ARCHIVE', 'sample': archive.name,
             'detail': f'{type(exc).__name__}: {exc}'}
    with (out / 'exceptions.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(issue)
    with (out / 'run_audit.csv').open('w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(['system', 'ligand', 'version', 'best_score', 'pose_score', 'summary_score', 'seed'])
    with (out / 'source_manifest.csv').open('w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(['file', 'bytes', 'sha256'])
    result = {'source_archive': archive.name, 'failures': 1, 'failed_checks': [issue], 'verified_primary_runs': 0, 'terminal_error': True}
    (out / 'audit_summary.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def main(archive, out, expected_version='1.2.7'):
    """Audit archive; return summary and persist both passing and failing records."""
    archive, out = Path(archive), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    failures, entries, warnings = [], [], []
    manifest = []
    rows = []
    cfg = {}
    script = ""
    ligs = []
    observed_seeds = {}

    def issue(kind, sample, detail):
        failures.append({'type': kind, 'sample': str(sample), 'detail': str(detail)})

    with zipfile.ZipFile(archive) as z:
        infos = [info for info in z.infolist() if not info.is_dir()]
        counts = Counter(info.filename for info in infos)
        for name, count in sorted(counts.items()):
            if count > 1:
                issue('DUPLICATE_ARCHIVE_MEMBER', name, f'{count} entries with same path')
        names = set(counts)
        MAX_MEMBER_BYTES = 32 * 1024 * 1024
        MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
        if sum(info.file_size for info in infos) > MAX_ARCHIVE_BYTES:
            raise ValueError('archive exceeds 256 MiB uncompressed safety limit')
        for info in infos:
            parts = PurePosixPath(info.filename)
            if (parts.is_absolute() or '..' in parts.parts or '\\' in info.filename
                    or not info.filename.startswith(BASE)):
                issue('UNSAFE_ARCHIVE_PATH', info.filename, 'unexpected or unsafe member name')
        for info in infos:
            # Stream in bounded chunks, including duplicate members; no extraction.
            if info.file_size > MAX_MEMBER_BYTES:
                issue('OVERSIZE_ARCHIVE_MEMBER', info.filename, 'member exceeds 32 MiB limit')
                continue
            h = hashlib.sha256()
            total = 0
            with z.open(info) as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    h.update(chunk)
            manifest.append({'file': info.filename[len(BASE):] if info.filename.startswith(BASE) else info.filename,
                             'bytes': total, 'sha256': h.hexdigest()})

        def get(path, required=True):
            full = BASE + path
            if full not in names:
                if required:
                    issue('MISSING_REQUIRED_FILE', path, 'not present')
                return None
            try:
                if counts[full] > 1:
                    issue('AMBIGUOUS_ARCHIVE_MEMBER', path, 'duplicate entries; content not trusted')
                    return None
                if z.getinfo(full).file_size > MAX_MEMBER_BYTES:
                    issue('OVERSIZE_ARCHIVE_MEMBER', path, 'cannot read oversized member')
                    return None
                return z.read(full).decode('utf-8-sig', errors='strict')
            except (OSError, ValueError, RuntimeError, UnicodeError, zipfile.BadZipFile) as exc:
                issue('UNREADABLE_FILE', path, type(exc).__name__)
                return None

        config_text = get('docking/vina_config.txt')
        try:
            cfg = parse_config(config_text or '')
        except ValueError as exc:
            issue('INVALID_CONFIG', 'docking/vina_config.txt', str(exc))
            cfg = {}
        script = get('run_docking.sh') or ''
        required_config = [f'{name}_{axis}' for name in ('center', 'size') for axis in 'xyz'] + ['exhaustiveness']
        for key in required_config:
            if key not in cfg:
                issue('MISSING_CONFIG_FIELD', 'docking/vina_config.txt', key)

        csvtext = get('docking_results_summary.csv')
        rows = []
        csv_by = {}
        if csvtext is not None:
            try:
                parsed_csv = list(csv.reader(io.StringIO(csvtext), strict=True))
                if not parsed_csv:
                    raise ValueError('missing header row')
                header = parsed_csv[0]
                if len(header) != len(set(header)):
                    issue('DUPLICATE_CSV_HEADER', 'docking_results_summary.csv', repr(header))
                for i, vals in enumerate(parsed_csv[1:], 2):
                    if not vals or (len(vals) == 1 and not vals[0].strip()):
                        continue
                    if len(vals) != len(header):
                        issue('INVALID_CSV_ROW_WIDTH', i, f'expected {len(header)} cells; got {len(vals)}')
                reader = csv.DictReader(io.StringIO(csvtext), strict=True)
                colnames = ['Compound', 'WT_Affinity_kcal_mol', 'A53T_Affinity_kcal_mol']
                for col in colnames:
                    if col not in (reader.fieldnames or []):
                        issue('MISSING_CSV_COLUMN', 'docking_results_summary.csv', col)
                rows = [r for r in reader if any((str(v).strip() if v is not None else '') for v in r.values())]
                for i, row in enumerate(rows, start=2):
                    lig = (row.get('Compound') or '').strip()
                    if not lig:
                        issue('INVALID_SUMMARY_ROW', i, 'blank ligand name')
                        continue
                    if lig in csv_by:
                        issue('DUPLICATE_SUMMARY_ROW', lig, f'duplicate row {i}')
                    else:
                        csv_by[lig] = row
            except (csv.Error, ValueError) as exc:
                issue('INVALID_CSV', 'docking_results_summary.csv', str(exc))

        ligand_prefix = BASE + 'docking/ligands_pdbqt/'
        present_ligs = {PurePosixPath(n).stem for n in names
                        if n.startswith(ligand_prefix) and n.endswith('.pdbqt')
                        and len(PurePosixPath(n[len(ligand_prefix):]).parts) == 1}
        for n in sorted(names):
            if n.startswith(ligand_prefix) and n.endswith('.pdbqt') \
                    and len(PurePosixPath(n[len(ligand_prefix):]).parts) != 1:
                issue('UNEXPECTED_LIGAND_PATH', n, 'ligand must be a direct child of ligands_pdbqt')
        expected_ligs = set(csv_by)
        ligs = sorted(present_ligs | expected_ligs)
        for lig in sorted(expected_ligs - present_ligs):
            issue('MISSING_LIGAND_INPUT', lig, 'summary row exists but ligand input missing')
        for lig in sorted(present_ligs - expected_ligs):
            issue('MISSING_SUMMARY_ROW', lig, 'ligand input exists but summary row missing')
        for n in sorted(names):
            for group in GROUPS:
                prefix = BASE + f'docking/results_{group}/'
                if n.startswith(prefix) and (n.endswith('.log') or n.endswith('_out.pdbqt')):
                    filename = n[len(prefix):]
                    lig = filename[:-4] if filename.endswith('.log') else filename[:-10]
                    if lig not in ligs:
                        issue('ORPHAN_RESULT', f'{group}/{lig}', filename)

        expected_center = tuple(cfg.get('center_' + x) for x in 'xyz')
        expected_size = tuple(cfg.get('size_' + x) for x in 'xyz')
        observed_seeds = {}

        for group in GROUPS:
            for ligand in ligs:
                ident = f'{group}/{ligand}'
                logname = f'docking/results_{group}/{ligand}.log'
                posename = f'docking/results_{group}/{ligand}_out.pdbqt'
                logtext = get(logname, required=False)
                posetext = get(posename, required=False)
                if logtext is None:
                    issue('MISSING_LOG', ident, logname)
                if posetext is None:
                    issue('MISSING_POSE', ident, posename)
                try:
                    log = parse_log(logtext or '')
                except (ValueError, OverflowError) as exc:
                    issue('INVALID_LOG', ident, str(exc))
                    log = {'version': None, 'center': None, 'size': None,
                           'exhaustiveness': None, 'seed': None, 'best_score': None}
                pose_lines = [line for line in (posetext or '').splitlines()
                              if line.startswith('REMARK VINA RESULT:')]
                pose_scores = []
                for pose_line in pose_lines:
                    posematch = re.fullmatch(
                        r'REMARK VINA RESULT:[\t ]*(' + FLOAT + r')[\t ]+(' + FLOAT +
                        r')[\t ]+(' + FLOAT + r')[\t ]*', pose_line)
                    if posematch is None:
                        issue('INVALID_POSE', ident, f'malformed Vina result remark: {pose_line[:150]!r}')
                        continue
                    try:
                        values = [float(value) for value in posematch.groups()]
                        if not all(math.isfinite(value) for value in values):
                            raise ValueError('nonfinite pose result')
                        pose_scores.append(values[0])
                    except ValueError as exc:
                        issue('INVALID_POSE', ident, str(exc))
                pose_score = pose_scores[0] if pose_scores else None
                col = 'WT_Affinity_kcal_mol' if group == 'wt' else 'A53T_Affinity_kcal_mol'
                raw_score = (csv_by.get(ligand) or {}).get(col)
                try:
                    csvscore = float(raw_score) if raw_score not in (None, '') else None
                    if csvscore is None or not math.isfinite(csvscore):
                        raise ValueError('missing/nonfinite')
                except (TypeError, ValueError):
                    csvscore = None
                    issue('INVALID_SUMMARY_SCORE', ident, f'{col}: {raw_score!r}')
                if log['seed'] is not None:
                    observed_seeds.setdefault(log['seed'], []).append(ident)

                def eq_xyz(a, b):
                    return a is not None and all(v is not None for v in b) and all(
                        math.isclose(x, y, rel_tol=1e-8, abs_tol=1e-6) for x, y in zip(a, b))
                def eq_score(a, b):
                    return a is not None and b is not None and abs(a - b) <= 0.00100001
                check = {
                    'version_expected': log['version'] == expected_version,
                    'seed_present': log['seed'] is not None,
                    'config_center': eq_xyz(log['center'], expected_center),
                    'config_size': eq_xyz(log['size'], expected_size),
                    'exhaustiveness': log['exhaustiveness'] is not None and 'exhaustiveness' in cfg and log['exhaustiveness'] == cfg['exhaustiveness'],
                    'log_vs_pose_score': eq_score(log['best_score'], pose_score),
                    'log_vs_summary_score': eq_score(log['best_score'], csvscore),
                    'pose_exists': posetext is not None,
                }
                for key, passed in check.items():
                    if not passed and (logtext is not None or posetext is not None):
                        issue('CHECK_FAILED', ident, key)
                entries.append({'system': group, 'ligand': ligand, 'version': log['version'],
                                'best_score': log['best_score'], 'pose_score': pose_score,
                                'summary_score': csvscore, 'seed': log['seed'],
                                **{key: 'PASS' if passed else 'FAIL' for key, passed in check.items()}})

        for seed, ids in sorted(observed_seeds.items()):
            if len(ids) > 1:
                # Flagged for review; reuse may be intentional, not a scientific defect.
                issue('DUPLICATE_SEED_REVIEW', ';'.join(ids), seed)

        for entry in entries:
            ident=entry['system']+'/'+entry['ligand']
            related=[f for f in failures if f['sample']==entry['ligand'] or ident in f['sample'].split(';')]
            check_keys=('version_expected','seed_present','config_center','config_size','exhaustiveness','log_vs_pose_score','log_vs_summary_score','pose_exists')
            entry['run_disposition']='PASS' if all(entry[k]=='PASS' for k in check_keys) and not related else 'FAIL'

        if not entries:
            issue('NO_AUDITABLE_RUNS', archive.name, 'No input ligands or summary compounds detected')
        with (out / 'run_audit.csv').open('w', newline='', encoding='utf-8') as f:
            fieldnames = list(entries[0]) if entries else ['system', 'ligand', 'version', 'best_score', 'pose_score', 'summary_score', 'seed']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries)
        with (out / 'exceptions.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(failures)
        with (out / 'source_manifest.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['file', 'bytes', 'sha256'])
            writer.writeheader()
            writer.writerows(manifest)

        summary = {'source_archive': archive.name, 'source_archive_sha256': hash_archive_streaming(archive),
                   'expected_version': expected_version, 'archive_files': len(manifest),
                   'ligands': len(ligs), 'expected_primary_runs': len(ligs) * len(GROUPS),
                   'verified_primary_runs': sum(x['run_disposition']=='PASS' for x in entries),
                   'failures': len(failures), 'failed_checks': failures,
                   'version_counts': dict(Counter(str(x['version']) for x in entries)),
                   'distinct_seeds': len(observed_seeds), 'config': cfg,
                   'script_contains_vina_invocation_text': 'vina --receptor' in script,
                   'script_contains_seed_option_text': '--seed' in script,
                   'csv_rows': len(rows)}
        (out / 'audit_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path, help='ZIP with the documented synthetic archive layout')
    p.add_argument('output', type=Path, help='Output folder for the audit reports')
    p.add_argument('--expected-version', default='1.2.7', help='Expected Vina version, default 1.2.7')
    args = p.parse_args()
    try:
        result = main(args.archive, args.output, expected_version=args.expected_version)
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile, ValueError, RuntimeError, EOFError) as exc:
        result = write_terminal_error(args.output, args.archive, exc)
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result['failures'] else 0)
