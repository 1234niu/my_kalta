"""Independent katIA reconstruction. Inference never opens evaluation-only.jsonl."""
import argparse
import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import tarfile
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
JAR = ROOT / 'vendor/katia/StaticCodeAnalysis-1.0-SNAPSHOT-jar-with-dependencies.jar'


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def prepare():
    raw = ROOT / 'dataset/raw/constantinople.csv'
    manifest = json.loads((ROOT / 'dataset/provenance/dataset-manifest.json').read_text())
    if digest(raw) != manifest['sha256']:
        raise ValueError('Original dataset checksum mismatch')
    inputs, gold, counts = [], [], collections.Counter()
    with raw.open() as f:
        for r in csv.DictReader(f):
            seeds = json.loads(r['seed_changes_with_diff_json'])
            impacted = json.loads(r['impacted_entities_json'])
            unrelated = json.loads(r['non_related_entities_json'])
            for key, entities, label in [('seed_count', seeds, 'seed'), ('impact_count', impacted, 'impact'), ('non_related_count', unrelated, 'non_related')]:
                if len(entities) != int(r[key]):
                    raise ValueError('Count mismatch: ' + r['index'])
                counts[label] += len(entities)
            task_id = 'constantinople-' + r['index'].zfill(3)
            inputs.append(dict(id=task_id, repo=r['repo'], parent_commit=r['parent_commit'],
                jira_title=r['jira_summary'], jira_description=r['jira_description'],
                seed_changes=[{k: e[k] for k in ('type', 'fqn', 'file', 'parent_line', 'git_diff_hunk')} for e in seeds]))
            gold.append(dict(id=task_id, commit=r['commit'], impacted=impacted, non_related=unrelated))
    if len(inputs) != 263 or len({x['id'] for x in inputs}) != 263:
        raise ValueError('Unexpected dataset IDs/count')
    for name, records in [('inputs', inputs), ('evaluation-only', gold)]:
        (ROOT / f'dataset/processed/{name}.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
    summary = dict(tasks=len(inputs), repositories=len({r['repo'] for r in inputs}), entity_counts=dict(counts),
                   input_sha256=digest(ROOT/'dataset/processed/inputs.jsonl'))
    dump(ROOT/'dataset/provenance/preparation.json', summary)
    return summary


def load_task(row):
    return json.loads((ROOT/'dataset/processed/inputs.jsonl').read_text().splitlines()[row])


def source(task):
    """Fetch only the immutable parent archive; never the labeled target commit."""
    repo, commit = task['repo'], task['parent_commit']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Invalid source identity')
    dest = ROOT/'dataset/sources'/repo/commit
    marker = dest/'.katia-source.json'
    if marker.exists():
        record = json.loads(marker.read_text())
        if record['repo'] != repo or record['parent_commit'] != commit:
            raise ValueError('Source identity mismatch')
        return dest
    if dest.exists():
        raise ValueError('Unverified source directory: ' + str(dest))
    archive = ROOT/'dataset/archives'/f'{repo.replace("/", "--")}-{commit}.tar.gz'
    archive.parent.mkdir(parents=True, exist_ok=True)
    url = f'https://codeload.github.com/{repo}/tar.gz/{commit}'
    if not archive.exists():
        partial = archive.with_suffix('.partial')
        with urllib.request.urlopen(url, timeout=180) as r, partial.open('wb') as f:
            while chunk := r.read(1024 * 1024):
                f.write(chunk)
        partial.replace(archive)
    dest.parent.mkdir(parents=True, exist_ok=True)
    skipped_links = []
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        tmp = Path(tmp)
        with tarfile.open(archive) as tar:
            members = []
            for member in tar.getmembers():
                target = (tmp/member.name).resolve()
                if not target.is_relative_to(tmp.resolve()):
                    raise ValueError('Unsafe archive member: ' + member.name)
                if member.issym() or member.islnk():
                    relative = '/' + '/'.join(Path(member.name).parts[1:]) + '/'
                    if '/src/main/java/' in relative or '/src/java/' in relative:
                        raise ValueError('Linked Java source needs inspection: ' + member.name)
                    skipped_links.append(member.name)
                    continue
                if not (member.isfile() or member.isdir()):
                    raise ValueError('Unsafe archive member: ' + member.name)
                members.append(member)
            tar.extractall(tmp, members=members)
        roots = list(tmp.iterdir())
        if len(roots) != 1 or not roots[0].is_dir():
            raise ValueError('Unexpected archive layout')
        roots[0].rename(dest)
    dump(marker, dict(repo=repo, parent_commit=commit, url=url, archive_sha256=digest(archive),
                      skipped_non_source_links=skipped_links))
    return dest


def java_path():
    if os.environ.get('KATIA_JAVA'):
        return os.environ['KATIA_JAVA']
    candidates = sorted({p.resolve() for p in (ROOT/'.tools').glob('**/bin/java')})
    if len(candidates) != 1:
        raise ValueError('Set KATIA_JAVA to Java 24+ executable')
    return str(candidates[0])


def jar_seed(project, seed, output):
    """JAR appends: each invocation gets its own fresh output file."""
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([java_path(), '-jar', str(JAR), str(project), seed['type'].upper(), seed['fqn'], str(output)],
                          text=True, capture_output=True, timeout=300)
    output.with_suffix('.log').write_text(proc.stdout + '\n' + proc.stderr)
    if proc.returncode:
        raise RuntimeError('Static analysis failed; see ' + str(output.with_suffix('.log')))
    relations = json.loads(output.read_text())
    if not isinstance(relations, dict) or not all(isinstance(k, str) and isinstance(v, list) for k,v in relations.items()):
        raise ValueError('Unexpected JAR schema')
    return relations


def static(task):
    project = source(task)
    out = ROOT/'results/static'/task['id']
    key = hashlib.sha256((json.dumps(task, sort_keys=True)+digest(JAR)).encode()).hexdigest()
    cached = out/'candidates.json'
    if cached.exists():
        result = json.loads(cached.read_text())
        if result['fingerprint'] != key:
            raise ValueError('Static cache mismatch; use a fresh result directory')
        return result
    seeds, candidates = [], set()
    # Temporary invocation directory avoids stale append output after interrupted attempts.
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        for n, seed in enumerate(task['seed_changes']):
            raw = Path(tmp)/f'seed-{n}.json'
            relations = jar_seed(project, seed, raw)
            (out/f'seed-{n}.json').write_text(raw.read_text())
            (out/f'seed-{n}.log').write_text(raw.with_suffix('.log').read_text())
            candidates.update(relations)
            seeds.append(dict(fqn=seed['fqn'], type=seed['type'], relations=relations,
                resolution='relations_found' if relations else 'empty_unresolved_or_no_relations'))
    candidates.difference_update(e['fqn'] for e in task['seed_changes'])
    result = dict(id=task['id'], fingerprint=key, jar_sha256=digest(JAR),
                  parent_commit=task['parent_commit'], candidates=sorted(candidates), seeds=seeds)
    dump(cached, result)
    return result


def prompt_values(task, candidates):
    # Whitelist: no gold, target diff, target commit message or full candidate source.
    return dict(jira_title=task['jira_title'], jira_description=task['jira_description'],
        seed_changes=json.dumps([dict(fqn=e['fqn'], git_diff_hunk=e['git_diff_hunk']) for e in task['seed_changes']], ensure_ascii=False),
        static_impact_set=json.dumps(candidates, ensure_ascii=False))


def messages(variant, task, candidates, stage=0, previous=''):
    import yaml
    from jinja2 import Environment, StrictUndefined
    values = prompt_values(task, candidates)
    if variant == 'sp':
        template = (ROOT/'vendor/katia/baseline.j2').read_text()
        return [dict(role='user', content=Environment(undefined=StrictUndefined).from_string(template).render(**values))]
    agents = yaml.safe_load((ROOT/'vendor/katia/agents.yaml').read_text())
    tasks = yaml.safe_load((ROOT/'vendor/katia/tasks.yaml').read_text())
    ak = ['bug_and_seed_change_analyzer_agent','impact_set_refinement_agent','impact_set_reporting_agent'][stage]
    tk = ['analyze_seed_changes','refine_impact_set','report_final_impact_set'][stage]
    agent, spec = agents[ak], tasks[tk]
    system = '\n'.join(agent[k] for k in ('role','goal','backstory'))
    prompt = spec['description'].format(**values)+'\nExpected output:\n'+spec['expected_output']
    if stage:
        prompt += '\nPrevious task output:\n' + previous
    return [dict(role='system', content=system), dict(role='user', content=prompt)]


def parse_prediction(text):
    value = json.loads(text.strip())
    if not isinstance(value,list) or any(not isinstance(x,str) or not x.strip() for x in value):
        raise ValueError('Expected JSON array of nonempty FQN strings')
    return sorted(set(value))


def credentials(path=None):
    env = dict(os.environ)
    if path:
        for line in Path(path).read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                k,v=line.split('=',1); env[k.strip()]=v.strip().strip('"').strip("'")
    base = env.get('KATIA_API_BASE') or env.get('RIPPLE_API_BASE')
    key = env.get('KATIA_API_KEY') or env.get('RIPPLE_API_KEY')
    if not base or not key:
        raise ValueError('Set KATIA_API_BASE and KATIA_API_KEY, or provide Ripple env file')
    return base.rstrip('/'), key


def run(task, variant, model, repetitions, live=False, env_file=None, extra=None, experiment='pilot', *, initial=None,
        timeout_seconds=180):
    if initial is None:
        initial = static(task)
    for repeat in range(repetitions):
        previous = ''
        for stage in range(1 if variant == 'sp' else 3):
            payload = dict(model=model, temperature=0, messages=messages(variant,task,initial['candidates'],stage,previous))
            if set(extra or {}) & {'messages', 'model', 'temperature'}:
                raise ValueError('Cannot override messages/model/temperature')
            payload.update(extra or {})
            if payload['model'] != model or payload['temperature'] != 0:
                raise ValueError('Model/temperature override is not allowed')
            fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
            out=ROOT/'results/runs'/experiment/variant/task['id']/str(repeat)
            record_path=out/f'stage-{stage}.json'
            if record_path.exists():
                record=json.loads(record_path.read_text())
                if record['request_sha256'] != fingerprint:
                    raise ValueError('Request cache mismatch; select another --experiment')
            elif not live:
                dump(out/f'stage-{stage}.request.json',payload)
                if variant=='ma':
                    break  # Later stages require actual preceding responses.
                continue
            else:
                base,key=credentials(env_file)
                request=urllib.request.Request(base+'/chat/completions', data=json.dumps(payload).encode(),
                    headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
                start=time.monotonic()
                with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                    body=json.load(response)
                record=dict(request_sha256=fingerprint, request=payload, response=body,
                            seconds=time.monotonic()-start, endpoint=base)
                dump(record_path,record)
            choice=record['response']['choices'][0]
            if choice.get('finish_reason') != 'stop':
                raise ValueError('Incomplete model output; excluded from evaluation')
            previous=choice['message']['content']
            if stage == (0 if variant=='sp' else 2):
                pred=parse_prediction(previous)
                excluded=sorted(set(pred)&{e['fqn'] for e in task['seed_changes']})
                pred=sorted(set(pred)-set(excluded))
                dump(out/'prediction.json',dict(id=task['id'],variant=variant,model=model,repeat=repeat,
                    predictions=pred, excluded_seeds=excluded, static_fingerprint=initial['fingerprint'],
                    reconstruction='author templates; custom sequential orchestration'))
    return dict(id=task['id'],variant=variant,candidates=len(initial['candidates']),live=live)


def ce(fqn):
    return '.'.join(fqn.split('(',1)[0].split('.')[-2:])


def score(pred, gold, mode):
    transform = ce if mode=='CE' else lambda x:x
    p,g={transform(x) for x in pred},{transform(x) for x in gold}
    tp=len(p&g); precision=tp/len(p) if p else 0.; recall=tp/len(g) if g else 0.
    return dict(precision=precision,recall=recall,f1=2*tp/(len(p)+len(g)) if p or g else 0.)


def evaluate(experiment, variant, rows, repetitions):
    gold={r['id']:r for r in map(json.loads,(ROOT/'dataset/processed/evaluation-only.jsonl').read_text().splitlines())}
    tasks=[load_task(row) for row in rows]; per_case=[]
    for task in tasks:
        task_id=task['id']; target=[e['fqn'] for e in gold[task_id]['impacted']]
        if variant=='static':
            runs=[json.loads((ROOT/'results/static'/task_id/'candidates.json').read_text())['candidates']]
        else:
            runs=[json.loads((ROOT/'results/runs'/experiment/variant/task_id/str(rep)/'prediction.json').read_text())['predictions'] for rep in range(repetitions)]
        metrics={mode:{k:statistics.median(score(p,target,mode)[k] for p in runs) for k in ('precision','recall','f1')} for mode in ('FQN','CE')}
        per_case.append(dict(id=task_id,metrics=metrics,consistent=all(set(p)==set(runs[0]) for p in runs)))
    result=dict(experiment=experiment, variant=variant, commits=len(per_case), repetitions=1 if variant=='static' else repetitions,
        aggregation='per-commit metric median over repetitions, then macro mean; zero-division=0',
        metrics={mode:{k:statistics.mean(c['metrics'][mode][k] for c in per_case) for k in ('precision','recall','f1')} for mode in ('FQN','CE')},
        per_case=per_case, complete_benchmark=len(per_case)==263 and (variant=='static' or repetitions==3))
    dump(ROOT/'results/evaluation'/f'{experiment}-{variant}.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['prepare','static','run','evaluate'])
    p.add_argument('--rows',default='0,1,2',help='CSV row positions, comma-separated; all for full dataset')
    p.add_argument('--variant',choices=['sp','ma','static'],default='sp')
    p.add_argument('--model',default='google/gemini-2.5-flash')
    p.add_argument('--repetitions',type=int,default=3)
    p.add_argument('--live',action='store_true',help='Permit API requests; default only creates/replays requests')
    p.add_argument('--env-file'); p.add_argument('--extra-json',default='{}')
    p.add_argument('--experiment',default='pilot')
    a=p.parse_args()
    if a.repetitions<1 or not re.fullmatch(r'[A-Za-z0-9_-]+',a.experiment):
        p.error('Positive repetitions and safe experiment name required')
    if a.command=='prepare': print(json.dumps(prepare())); return
    rows=list(range(263)) if a.rows=='all' else [int(x) for x in a.rows.split(',')]
    if not rows or len(rows)!=len(set(rows)) or any(x<0 or x>=263 for x in rows): p.error('Invalid rows')
    if a.command=='evaluate': print(json.dumps(evaluate(a.experiment,a.variant,rows,a.repetitions))); return
    for row in rows:
        task=load_task(row)
        if a.command=='static': result=static(task); print(json.dumps(dict(id=task['id'],candidates=len(result['candidates']))),flush=True)
        else:
            if a.variant=='static': p.error('Use static command for static baseline')
            print(json.dumps(run(task,a.variant,a.model,a.repetitions,a.live,a.env_file,json.loads(a.extra_json),a.experiment)),flush=True)

if __name__=='__main__': main()
