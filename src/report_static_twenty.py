"""Summarize the frozen static rules on rows 0–19."""
import argparse
import json
from statistics import mean, median

import katia
from compare_ten import LATEST_ARM, LATEST_EXPERIMENT, MODEL, REPETITIONS, candidate_fingerprint

ARMS = {
    'baseline': '作者 JAR',
    'fields': '加字段',
    'multihop': '加多跳',
    'two_hop_calls': '加两跳调用',
    'diff_and_override': '加 diff 与重写',
}


def model_table(rows, allow_incomplete=False):
    predictions = {}
    for task, result in rows:
        case_id = task['id']
        metrics = result['metrics'][LATEST_ARM]
        gold = set(metrics['hits']) | set(metrics['misses'])
        candidates = result['candidates'][LATEST_ARM]
        baseline_path = katia.ROOT / 'results/static' / case_id / 'candidates.json'
        fingerprint = candidate_fingerprint(json.loads(baseline_path.read_text())['fingerprint'], candidates)
        variants = {'static': [set(candidates)]}
        for variant in ('sp', 'ma'):
            runs = []
            for rep in range(REPETITIONS):
                path = (katia.ROOT / 'results/runs' / LATEST_EXPERIMENT / variant
                        / case_id / str(rep) / 'prediction.json')
                if not path.exists() and allow_incomplete:
                    runs.append(None)
                    continue
                record = json.loads(path.read_text())
                if (record['id'], record['variant'], record['model'], record['repeat']) != (
                    case_id, variant, MODEL, rep
                ) or record['static_fingerprint'] != fingerprint:
                    raise ValueError(f'Prediction metadata mismatch: {path}')
                runs.append(set(record['predictions']))
            variants[variant] = runs
        predictions[case_id] = (gold, variants)

    completed = {
        variant: sum(run is not None for _, variants in predictions.values() for run in variants[variant])
        for variant in ('sp', 'ma')
    }
    expected = len(rows) * REPETITIONS
    lines = ['## SP／MA 逐案例对照', '',
             f'两组均使用最新静态候选、`{MODEL}`、温度 0，每例重复 {REPETITIONS} 次。SP 单次调用，MA 三个阶段。每格依次列三次运行的 FQN 命中数 / 输出数。', '',
             f"已完成的预测轮次为 SP {completed['sp']}/{expected}、MA {completed['ma']}/{expected}。短横线表示未完成的运行。", '',
             '| 案例 | 标签数 | 最新静态命中 | SP 三次 | MA 三次 |',
             '| --- | ---: | ---: | --- | --- |']
    for task, result in rows:
        case_id = task['id']
        gold, variants = predictions[case_id]
        cells = [', '.join(f'{len(run & gold)}/{len(run)}' if run is not None else '—' for run in variants[variant])
                 for variant in ('sp', 'ma')]
        hits = len(result['metrics'][LATEST_ARM]['hits'])
        lines.append(f"| {case_id[-3:]} | {len(gold)} | {hits} | " + ' | '.join(cells) + ' |')

    lines += ['', '模型指标只使用三次均完成的案例，先取每例中位数，再跨案例取宏平均。P、R、F1 分别为精确率、召回率和 F1。覆盖案例数不同的行仅作进度记录。', '',
              '| 范围 | 阶段 | 完整案例 | FQN P / R / F1 | CE P / R / F1 |',
              '| --- | --- | ---: | --- | --- |']
    values = list(predictions.values())
    for label, subset in [('000–009', values[:10]), ('010–019', values[10:]), ('全部 20 例', values)]:
        for variant in ('static', 'sp', 'ma'):
            eligible = [(gold, variants) for gold, variants in subset
                        if all(run is not None for run in variants[variant])]
            title = '最新静态候选' if variant == 'static' else variant.upper()
            if not eligible:
                lines.append(f'| {label} | {title} | 0/{len(subset)} | — | — |')
                continue
            metrics = []
            for mode in ('FQN', 'CE'):
                cases = [[katia.score(run, gold, mode) for run in variants[variant]]
                         for gold, variants in eligible]
                metrics.append(' / '.join(
                    f'{mean(median(repeat[key] for repeat in case) for case in cases):.1%}'
                    for key in ('precision', 'recall', 'f1')))
            lines.append(f'| {label} | {title} | {len(eligible)}/{len(subset)} | ' + ' | '.join(metrics) + ' |')

    lines += ['', '## 模型逐实体命中、漏报和误报', '',
              '每列用 n/m 记录该实体在 m 次已完成运行中的出现次数。短横线表示该方法没有已完成的运行。额外输出按严格 FQN 计。', '']
    for task, result in rows:
        case_id = task['id']
        gold, variants = predictions[case_id]
        observed = {v: [run for run in variants[v] if run is not None] for v in ('sp', 'ma')}
        extras = set().union(*observed['sp'], *observed['ma']) - gold
        static = set(result['candidates'][LATEST_ARM])
        lines += [f'### {case_id}', '',
                  '| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |',
                  '| --- | --- | --- | ---: | ---: |']
        for entity in sorted(gold) + sorted(extras):
            counts = [f'{sum(entity in run for run in runs)}/{len(runs)}' if runs else '—'
                      for runs in observed.values()]
            label = '受影响' if entity in gold else '额外输出'
            found = '是' if entity in static else '否'
            safe_entity = entity.replace('|', '&#124;').replace('\n', ' ').replace('`', '&#96;')
            lines.append(f'| `{safe_entity}` | {label} | {found} | {counts[0]} | {counts[1]} |')
        lines.append('')
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--with-models', action='store_true', help='Include completed SP and MA runs')
    parser.add_argument('--allow-incomplete', action='store_true', help='Mark missing model runs explicitly')
    args = parser.parse_args()
    path = katia.ROOT / 'results/static-seed-diff'
    rows = []
    for index in range(20):
        task = katia.load_task(index)
        case_id = task['id']
        result = json.loads((path / f'{case_id}.json').read_text())
        if result['id'] != case_id or not ARMS.keys() <= result['metrics'].keys():
            raise ValueError(f'Missing or mismatched static arms for {case_id}')
        rows.append((task, result))

    lines = [
        '# 20 个案例的静态候选对照', '',
        '000–009 是用于分析规则的原 10 例。010–019 是 Constantinople 按原顺序选取的下一批 10 例，沿用同一套静态规则。完整 FQN 命中包含对新增实体的签名推断。', '',
        '## 汇总', '',
        '| 范围 | 静态组 | FQN 命中 / 标签 | 召回率 | 候选总数 |',
        '| --- | --- | ---: | ---: | ---: |',
    ]
    for label, subset in [('000–009', rows[:10]), ('010–019', rows[10:]), ('全部 20 例', rows)]:
        labels = sum(len(r['indexed_targets']) + len(r['unindexed_targets']) for _, r in subset)
        for arm, title in ARMS.items():
            hits = sum(len(r['metrics'][arm]['hits']) for _, r in subset)
            candidates = sum(r['metrics'][arm]['candidate_count'] for _, r in subset)
            lines.append(f'| {label} | {title} | {hits} / {labels} | {hits/labels:.1%} | {candidates} |')

    lines += ['', '统计按实体累加得出。下表每格为命中数 / 候选数。', '',
              '## 逐案例对照', '',
              '| 案例 | 仓库 | 标签 | ' + ' | '.join(ARMS.values()) + ' |',
              '| --- | --- | ---: |' + ' ---: |' * len(ARMS)]
    for task, result in rows:
        case_id = task['id']
        label_count = len(result['indexed_targets']) + len(result['unindexed_targets'])
        scores = [f"{len(result['metrics'][arm]['hits'])} / {result['metrics'][arm]['candidate_count']}" for arm in ARMS]
        link = f"[{case_id[-3:]}](../results/static-seed-diff/{case_id}.json)"
        lines.append(f"| {link} | {task['repo']} | {label_count} | " + ' | '.join(scores) + ' |')

    if args.with_models:
        lines += [''] + model_table(rows, args.allow_incomplete)
    lines += ['', '## 新 10 例的命中和漏报', '']
    for task, result in rows[10:]:
        latest = result['metrics']['diff_and_override']
        previous = result['metrics']['two_hop_calls']
        added = set(latest['hits']) - set(previous['hits'])
        lines += [f"### {task['id']} · {task['jira_title']}", '',
                  '| 类别 | 完整签名 |', '| --- | --- |']
        for category, entities in [
            ('两跳组已命中', previous['hits']),
            ('diff 或重写补回', sorted(added)),
            ('最新组仍漏报', latest['misses']),
        ]:
            for entity in entities:
                lines.append(f'| {category} | `{entity}` |')
        lines.append('')

    lines += ['## 复跑', '', '```bash',
              'python src/static_compare.py --seed-diff-overlay --cross-class-calls --rows 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19',
              'python src/compare_ten.py --latest --env-file ../work/ripple/.env.ripple100',
              'python src/report_static_twenty.py --with-models', 'python src/report_ten.py', '```', '',
              '此前的原始候选与多跳候选模型对照见 [十案例报告](ten-case-comparison.md)。', '']
    report = katia.ROOT / 'docs/twenty-case-static.md'
    report.write_text('\n'.join(lines), encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()
