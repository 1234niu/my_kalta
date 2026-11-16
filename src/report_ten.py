"""Build the ten-case document from static evidence and saved model predictions."""
from collections import defaultdict
from statistics import mean, median
import json

import katia
from compare_ten import ARMS, MODEL, REPETITIONS

RESULTS = katia.ROOT / 'results'


def read(path):
    return json.loads(path.read_text())


def report():
    labels = {
        entry['id']: entry['impacted']
        for entry in map(json.loads, (katia.ROOT / 'dataset/processed/evaluation-only.jsonl').read_text().splitlines())
    }
    cases = []
    for row in range(10):
        task = katia.load_task(row)
        case_id = task['id']
        static = read(RESULTS / 'static-seed-diff' / (case_id + '.json'))
        predictions = {}
        for arm, experiment in ARMS.items():
            for variant in ('sp', 'ma'):
                predictions[arm, variant] = [
                    set(read(RESULTS / 'runs' / experiment / variant / case_id / str(rep) / 'prediction.json')['predictions'])
                    for rep in range(REPETITIONS)
                ]
        target = {e['fqn'] for e in labels[case_id]}
        cases.append((task, static, target, predictions))

    lines = [
        '# 10 个案例的静态候选与 SP／MA 对照', '',
        '使用 Constantinople 原始顺序的前 10 行。前三例参与了静态规则设计，后七例用于检验扩展效果。每个案例使用同一个变更前快照、相同种子和问题描述。', '',
        f'模型统一使用 `{MODEL}`，温度 0，关闭 thinking。SP 和 MA 保持现有提示词与编排，每个候选组各重复 {REPETITIONS} 次。原始候选组复用已保存的前三例响应。字段扩展只参加静态对照，模型对照使用原始候选和多跳候选。', '',
        '## 静态候选逐案例比较', '',
        '每组写作“FQN 命中数 / 候选数”。parent 已索引标签使用同一个源码索引核对。未索引可能来自新增实体或解析、签名映射缺口。', '',
        '| 样本 | 仓库 | 标签数 | parent 已索引 | JAR 一跳 | 加字段 | 加多跳 | 加两跳调用 | 加 diff 与重写 |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for task, static, target, _ in cases:
        values = [f"{len(static['metrics'][mode]['hits'])} / {static['metrics'][mode]['candidate_count']}"
                  for mode in ('baseline', 'fields', 'multihop', 'two_hop_calls', 'diff_and_override')]
        lines.append(f"| {task['id']} | {task['repo']} | {len(target)} | {len(static['indexed_targets'])} | " + ' | '.join(values) + ' |')
    subsets = [('前三例', cases[:3]), ('后七例', cases[3:]), ('全部十例', cases)]
    lines += ['', '| 样本范围 | 组别 | 全部 FQN 命中 / 标签 | parent 已索引命中 / 已索引标签 | 候选总数 |',
              '| --- | --- | ---: | ---: | ---: |']
    for label, subset in subsets:
        total = sum(len(target) for _, _, target, _ in subset)
        indexed_total = sum(len(static['indexed_targets']) for _, static, _, _ in subset)
        for mode, name in [('baseline','JAR 一跳'),('fields','加字段'),('multihop','加多跳'),
                           ('two_hop_calls','加两跳调用'),('diff_and_override','加 diff 与重写')]:
            hits = indexed_hits = candidates = 0
            for _, static, _, _ in subset:
                metrics = static['metrics'][mode]
                hits += len(metrics['hits'])
                indexed_hits += len(set(metrics['hits']) & set(static['indexed_targets']))
                candidates += metrics['candidate_count']
            lines.append(f'| {label} | {name} | {hits}/{total} | {indexed_hits}/{indexed_total} | {candidates} |')
    lines += ['', '两跳调用在 003 找回 `VfsResource.normalize(String)`。新增调用签名推断、字段写入和重写关系再补回 11 个标签。000–009 都曾用于分析或设计当前规则，独立对照见 [20 例静态结果](twenty-case-static.md)。',
              '', '009 的 parent 归档含一个脚本测试目录的符号链接。提取时跳过了该链接，Java 源目录中的链接仍会触发显式检查。']
    lines += ['', '## SP／MA 逐案例比较', '',
              '每格依次列三次运行的“FQN 命中数 / 输出数”。模型表保留当时的原始候选与加多跳候选对照。最新静态组尚未接入这次模型对照。', '',
              '| 样本 | 标签数 | SP 原始 | SP 多跳 | MA 原始 | MA 多跳 |',
              '| --- | ---: | --- | --- | --- | --- |']
    order = [(arm, variant) for variant in ('sp', 'ma') for arm in ARMS]
    for task, _, target, predictions in cases:
        values = [', '.join(f'{len(run & target)}/{len(run)}' for run in predictions[key]) for key in order]
        lines.append(f"| {task['id']} | {len(target)} | " + ' | '.join(values) + ' |')
    lines += ['', '每项指标先取单案例三次运行的中位数，再对案例作宏平均。', '',
              '| 范围 | 模型阶段 | 候选组 | FQN P / R / F1 | CE P / R / F1 |',
              '| --- | --- | --- | --- | --- |']
    for label, subset in subsets:
        for key in order:
            cells = []
            for mode in ('FQN', 'CE'):
                values = defaultdict(list)
                for _, _, target, predictions in subset:
                    scores = [katia.score(run, target, mode) for run in predictions[key]]
                    for metric in ('precision', 'recall', 'f1'):
                        values[metric].append(median(score[metric] for score in scores))
                cells.append(' / '.join(f'{mean(v):.1%}' for v in values.values()))
            lines.append(f'| {label} | {key[1].upper()} | {key[0]} | ' + ' | '.join(cells) + ' |')
    lines += ['', '## 逐实体命中和误报', '',
              '按 FQN 核对。模型列中的数字为三次中命中的次数。各案例的静态 JSON 包含完整候选与扩展证据。']
    for task, static, target, predictions in cases:
        case_id = task['id']
        lines += ['', f"### {case_id} · {task['repo']}", '',
                  f"[静态候选和源码路径](../results/static-seed-diff/{case_id}.json)", '',
                  '| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |',
                  '| --- | --- | --- | --- |']
        for entity in sorted(target):
            found = '/'.join('✓' if entity in static['candidates'][arm] else '—'
                             for arm in ('baseline','fields','multihop','two_hop_calls','diff_and_override'))
            counts = [sum(entity in run for run in predictions[key]) for key in order]
            lines.append(f'| `{entity}` | {found} | {counts[0]}/{counts[1]} | {counts[2]}/{counts[3]} |')
        extras = set().union(*(run for runs in predictions.values() for run in runs)) - target
        if extras:
            lines += ['', '| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |', '| --- | --- | --- |']
            for entity in sorted(extras):
                counts = [sum(entity in run for run in predictions[key]) for key in order]
                lines.append(f'| `{entity}` | {counts[0]}/{counts[1]} | {counts[2]}/{counts[3]} |')
    lines += ['', '## 复跑', '', '```bash',
              'python src/static_compare.py --seed-diff-overlay --cross-class-calls --rows 0,1,2,3,4,5,6,7,8,9',
              'python src/compare_ten.py --env-file ../work/ripple/.env.ripple100',
              'python src/report_ten.py', '```']
    out = katia.ROOT / 'docs/ten-case-comparison.md'
    out.write_text('\n'.join(lines) + '\n')
    print(out)


if __name__ == '__main__':
    report()
