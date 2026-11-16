"""Run paired baseline/multihop DeepSeek experiments on the first ten rows."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import socket
import time
from urllib.error import HTTPError, URLError

import katia

MODEL = 'deepseek-v4.1-flash-1017'
REPETITIONS = 3
EXTRA = {'thinking': {'type': 'disabled'}, 'max_tokens': 4096}
ARMS = {'baseline': 'deepseek-pilot', 'multihop': 'deepseek-static-multihop-10'}
LATEST_ARM = 'diff_and_override'
LATEST_EXPERIMENT = 'deepseek-diff-override-20'


def candidate_fingerprint(static_fingerprint, candidates):
    return hashlib.sha256(
        static_fingerprint.encode() + b'\0' + json.dumps(candidates).encode()
    ).hexdigest()


def run_case(task, variant, arm, static, env_file):
    folder = 'static-seed-diff' if arm == LATEST_ARM else 'static-compare'
    experiment = LATEST_EXPERIMENT if arm == LATEST_ARM else ARMS[arm]
    comparison_path = katia.ROOT / 'results' / folder / (task['id'] + '.json')
    candidates = json.loads(comparison_path.read_text())['candidates'][arm]
    initial = dict(static, candidates=candidates)
    if arm != 'baseline':
        initial['fingerprint'] = candidate_fingerprint(static['fingerprint'], candidates)
    for attempt in range(3):
        try:
            return katia.run(task, variant, MODEL, REPETITIONS, live=True, env_file=env_file,
                             extra=EXTRA, experiment=experiment, initial=initial,
                             timeout_seconds=45 if arm == LATEST_ARM else 180)
        except (URLError, TimeoutError, socket.timeout) as error:
            if attempt == 2 or isinstance(error, HTTPError) and error.code not in {408, 429, 500, 502, 503, 504}:
                raise
            time.sleep(3 * (attempt + 1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', required=True)
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--rows')
    parser.add_argument('--latest', action='store_true', help='Run the current static candidate arm')
    parser.add_argument('--variant', choices=('sp', 'ma'), help='Resume a single model variant')
    args = parser.parse_args()
    rows = [int(row) for row in args.rows.split(',')] if args.rows else range(20 if args.latest else 10)
    if len(set(rows)) != len(rows) or any(row < 0 or row >= 263 for row in rows):
        parser.error('Specify distinct row positions from 0 to 262')
    tasks = [katia.load_task(row) for row in rows]
    arms = (LATEST_ARM,) if args.latest else ARMS
    variants = (args.variant,) if args.variant else ('sp', 'ma')
    static_by_id = {task['id']: katia.static(task) for task in tasks}
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {}
        for variant in variants:
            for task in tasks:
                for arm in arms:
                    job = pool.submit(run_case, task, variant, arm, static_by_id[task['id']], args.env_file)
                    jobs[job] = (task['id'], arm, variant)
        for job in as_completed(jobs):
            label = jobs[job]
            try:
                job.result()
                print(*label, 'complete', flush=True)
            except Exception as error:
                print(*label, type(error).__name__, str(error)[:200], flush=True)
                failures.append(label)
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
