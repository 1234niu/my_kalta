"""Run paired SP and planned MA with the combined field candidate set."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
from urllib.error import HTTPError, URLError

import katia
import ma_evidence
import ma_planned
from compare_ten import MODEL, EXTRA, REPETITIONS, candidate_fingerprint

EXPERIMENT = 'full-fields-new20'
ARM = 'combined_field_paths'
STATIC = katia.ROOT / 'results/static-field-ablation'
MA = katia.ROOT / 'results/ma-evidence'


def retry(operation):
    for attempt in range(3):
        try:
            return operation()
        except (URLError, TimeoutError) as exc:
            if attempt == 2 or isinstance(exc, HTTPError) and exc.code not in {408, 429, 500, 502, 503, 504}:
                raise
            time.sleep(3 * (attempt + 1))


def run_sp(task, env_file, experiment):
    case = task['id']
    record = json.loads((STATIC / f'{case}.json').read_text())
    candidates = record['candidates'][ARM]
    initial = dict(katia.static(task))
    initial.update(candidates=candidates, fingerprint=candidate_fingerprint(initial['fingerprint'], candidates))
    return retry(lambda: katia.run(task, 'sp', MODEL, REPETITIONS, live=True, env_file=env_file,
                                   extra=EXTRA, experiment=experiment, initial=initial, timeout_seconds=70))


def run_ma(task, connection, experiment, rep, arm, workflow):
    folder = f'{experiment}/repeat-{rep}'
    output = MA / folder / task['id'] / 'result.json'
    static_path = STATIC / f'{task["id"]}.json'
    static = json.loads(static_path.read_text())['candidates'][arm]
    if output.exists():
        record = json.loads(output.read_text())
        actual = record.get('static')
        if workflow == 'bounded':
            planner_request = json.loads((output.parent / 'planner-0.json').read_text())['request']
            actual = json.loads(planner_request['messages'][1]['content'])['static_candidates']
        if (record['id'], record['model'], record['parent_commit'], actual) != (
                task['id'], MODEL, task['parent_commit'], static):
            raise ValueError(f'Cached MA result differs: {output}')
        return
    base, key = connection
    if workflow == 'bounded':
        return retry(lambda: ma_evidence.run_case(task, MODEL, base, key, folder, static, arm))
    return retry(lambda: ma_planned.run_case(task, MODEL, base, key, folder, static_arm=arm,
                                      static_path=static_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', required=True)
    parser.add_argument('--experiment', default=EXPERIMENT)
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--variant', choices=('sp', 'ma'))
    parser.add_argument('--ma-static-arm', choices=('diff_and_override', ARM), default=ARM)
    parser.add_argument('--ma-workflow', choices=('planned', 'bounded'), default='planned')
    args = parser.parse_args()
    if args.workers < 1 or not args.experiment or not all(c.isalnum() or c in '_-' for c in args.experiment):
        parser.error('Expected a positive worker count and a safe experiment name')
    selection = json.loads((MA / args.experiment / 'selection.json').read_text())
    tasks = [katia.load_task(row) for row in selection['rows']]
    connection = katia.credentials(args.env_file)
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {}
        for task in tasks:
            if args.variant != 'ma':
                jobs[pool.submit(run_sp, task, args.env_file, args.experiment)] = (task['id'], 'SP')
        if args.variant != 'sp':
            for rep in range(REPETITIONS):
                for task in tasks:
                    jobs[pool.submit(run_ma, task, connection, args.experiment, rep, args.ma_static_arm, args.ma_workflow)] = (task['id'], 'MA', rep + 1)
        for job in as_completed(jobs):
            label = jobs[job]
            try:
                job.result()
                print(*label, 'complete', flush=True)
            except Exception as exc:
                failures.append(label)
                print(*label, type(exc).__name__, str(exc)[:250], flush=True)
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
