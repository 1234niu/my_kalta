"""Evaluate the fresh 20-case run with the katIA paper's per-commit macro metrics."""
import json
from statistics import mean, median

import katia
from compare_ten import MODEL, REPETITIONS, candidate_fingerprint
from run_full_fields import ARM, EXPERIMENT, MA, STATIC

ROOT = katia.ROOT
VARIANTS = {
    'before': '改进前静态', 'static': '改进后静态', 'sp': 'SP',
    'ma': '新版 MA · 确认＋待核查', 'confirmed': '新版 MA · 仅确认',
}


def read(path):
    return json.loads(path.read_text())


def load_cases():
    selection = read(MA / EXPERIMENT / 'selection.json')
    if len(selection['cases']) != 20 or len({r['id'] for r in selection['cases']}) != 20:
        raise ValueError('The comparison expects 20 distinct cases')
    labels = {r['id']: {e['fqn'] for e in r['impacted']} for r in map(
        json.loads, (ROOT / 'dataset/processed/evaluation-only.jsonl').read_text().splitlines())}
    cases = []
    for row, selected in zip(selection['rows'], selection['cases']):
        task = katia.load_task(row)
        case = task['id']
        if selected != {k: task[k] for k in selected}:
            raise ValueError(f'Selection mismatch for {case}')
        static = read(STATIC / f'{case}.json')['candidates']
        base = read(ROOT / 'results/static' / case / 'candidates.json')
        fingerprint = candidate_fingerprint(base['fingerprint'], static[ARM])
        runs = {'before': [set(static['diff_and_override'])], 'static': [set(static[ARM])],
                'sp': [], 'ma': [], 'confirmed': []}
        model_turns, tool_counts, query_breakdown, exhausted = [], [], [], []
        for rep in range(REPETITIONS):
            sp = read(ROOT / 'results/runs' / EXPERIMENT / 'sp' / case / str(rep) / 'prediction.json')
            if (sp['id'], sp['variant'], sp['model'], sp['repeat'], sp['static_fingerprint']) != (
                    case, 'sp', MODEL, rep, fingerprint):
                raise ValueError(f'SP metadata mismatch for {case} repetition {rep}')
            path = MA / EXPERIMENT / f'repeat-{rep}' / case
            ma = read(path / 'result.json')
            if (ma['id'], ma['model'], ma['parent_commit'], ma['static']) != (
                    case, MODEL, task['parent_commit'], static[ARM]):
                raise ValueError(f'MA metadata mismatch for {case} repetition {rep}')
            queries = ma['queries']
            explore = sum(queries[k] for k in ('initial', 'ranked', 'analyze'))
            turns = sum(stage['model_turns'] for stage in ma['usage'].values())
            evidence = read(path / 'evidence.json')
            if not (explore <= 12 and queries['review'] <= 6 and turns <= 19
                    and explore + queries['review'] == len(evidence)):
                raise ValueError(f'Budget or evidence mismatch for {case} repetition {rep}')
            model_turns.append(turns)
            tool_counts.append((explore, queries['review']))
            query_breakdown.append(queries)
            exhausted.extend((rep + 1, name) for name, data in ma['usage'].items() if data.get('exhausted'))
            runs['sp'].append(set(sp['predictions']))
            runs['ma'].append({fqn for fqn, item in ma['decisions'].items() if item['status'] != 'contradicted'})
            runs['confirmed'].append({fqn for fqn, item in ma['decisions'].items() if item['status'] == 'confirmed'})
        cases.append(dict(id=case, repo=task['repo'], gold=labels[case], runs=runs,
                          model_turns=model_turns, tool_counts=tool_counts, query_breakdown=query_breakdown, exhausted=exhausted))
    return cases


def case_scores(runs, gold, mode):
    results = [katia.score(run, gold, mode) for run in runs]
    return {key: median(result[key] for result in results) for key in ('precision', 'recall', 'f1')}


def summarize(cases):
    report = {}
    for variant in VARIANTS:
        metrics = {}
        for mode in ('FQN', 'CE'):
            scores = [case_scores(case['runs'][variant], case['gold'], mode) for case in cases]
            metrics[mode] = {key: mean(item[key] for item in scores) for key in ('precision', 'recall', 'f1')}
        report[variant] = dict(metrics=metrics,
            fqn_hits=sum(median(len(run & case['gold']) for run in case['runs'][variant]) for case in cases),
            candidates=sum(median(len(run) for run in case['runs'][variant]) for case in cases),
            set_consistent=sum(all(run == case['runs'][variant][0] for run in case['runs'][variant]) for case in cases))
    return report


def report_text(cases, report):
    labels = sum(len(c['gold']) for c in cases)
    count_repos = len({c['repo'] for c in cases})
    lines = [
        '# 新 20 例静态、SP 与新版 MA 对照', '',
        f'选取 {len(cases)} 个此前未运行的案例，覆盖 {count_repos} 个仓库。这些仓库没有出现在静态规则开发用的原 000–019 中。'
        '按数据集原顺序在仓库间轮询，排除已有实验或尝试的案例及重复 parent 快照，选定后再运行。', '',
        f'静态分析每例运行一次。SP 和新版 MA 使用同一份改进静态候选，'
        f'使用 `{MODEL}`、温度 0、关闭思考模式，每例各跑 {REPETITIONS} 次。'
        'MA 主结果包含确认和待核查，保留未被明确排除的静态候选。', '',
        '## 论文口径的宏平均', '',
        'FQN 严格匹配完整名称和签名。CE 保留声明类和成员名并去重。先逐提交算集合精确率、召回率、F1，'
        '模型组每项指标取三次中位数，最后对提交取宏平均。零分母按实验实现记为零。'
        '候选和 FQN 命中数按案例相加，模型组先取各案例三次计数的中位数。'
        '计算口径见 [katIA §V-A](https://arxiv.org/html/2611.10958v1#S5.SS1)。', '',
        '| 方法 | FQN 精确率 / 召回率 / F1 | CE 精确率 / 召回率 / F1 | FQN 命中 / 标签 | 候选数 |',
        '| --- | --- | --- | ---: | ---: |',
    ]
    for key, label in VARIANTS.items():
        row = report[key]
        metrics = [' / '.join(f'{v:.2%}' for v in row['metrics'][mode].values()) for mode in ('FQN', 'CE')]
        lines.append(f'| {label} | ' + ' | '.join(metrics) + f' | {row["fqn_hits"]:g}/{labels} | {row["candidates"]:g} |')
    lines += ['', '## 逐案例 FQN 命中', '',
              '预测格为命中数 / 输出数。SP、MA 的三次结果按运行顺序排列。', '',
              '| 案例 | 仓库 | 标签 | 改进前静态 | 改进后静态 | SP 三次 | MA 三次 | MA 仅确认三次 |',
              '| --- | --- | ---: | ---: | ---: | --- | --- | --- |']
    for case in cases:
        gold, runs = case['gold'], case['runs']
        cells = [', '.join(f'{len(run & gold)}/{len(run)}' for run in runs[v]) for v in VARIANTS]
        lines.append(f'| {case["id"][-3:]} | {case["repo"]} | {len(gold)} | ' + ' | '.join(cells) + ' |')
    lines += ['', '## 召回和用量', '']
    static_new = []
    for case in cases:
        g, r = case['gold'], case['runs']
        static_new.extend((case['id'], fqn) for fqn in sorted((r['static'][0] - r['before'][0]) & g))
    lines.append(f'- 静态改进在本组补回 {len(static_new)} 个严格匹配标签，分布在 {len({c for c, _ in static_new})} 个案例。')
    for case, fqn in static_new:
        lines.append(f'  - {case[-3:]} · `{fqn}`')
    for variant in ('sp', 'ma'):
        available = sum(len(case['runs']['static'][0] & case['gold']) for case in cases)
        kept = sum(len(case['runs']['static'][0] & case['gold'] &
                       {fqn for run in case['runs'][variant] for fqn in run
                        if sum(fqn in p for p in case['runs'][variant]) >= 2}) for case in cases)
        new = sum(len({fqn for fqn in case['gold'] - case['runs']['static'][0]
                       if sum(fqn in run for run in case['runs'][variant]) >= 2}) for case in cases)
        lines.append(f'- {VARIANTS[variant]} 以三次中至少两次命中为阈值，保留静态命中 {kept}/{available} 个，'
                     f'另找到 {new} 个静态候选以外的标签。预测集合三次完全一致的案例为 '
                     f'{report[variant]["set_consistent"]}/{len(cases)}。')
    counts = [sum(count) for case in cases for count in case['tool_counts']]
    turns = [t for case in cases for t in case['model_turns']]
    limits = [(case['id'][-3:], rep, stage) for case in cases for rep, stage in case['exhausted']]
    lines.append(f'- MA 每次运行最多 18 次工具查询及 19 个模型轮次。实际查询中位数 {median(counts):g}、最高 {max(counts)}。'
                 f'模型轮次中位数 {median(turns):g}、最高 {max(turns)}。SP 每次运行一个模型轮。')
    stages = [record for case in cases for record in case['query_breakdown']]
    counts_by_stage = {stage: sum(record[stage] for record in stages)
                       for stage in ('initial', 'ranked', 'analyze', 'review')}
    lines.append('- MA 查询总量按阶段拆分为初探 {initial} 次、排名后补查 {ranked} 次、'
                 'Analyze 自主追加 {analyze} 次、复检 {review} 次。'.format(**counts_by_stage))
    if limits:
        lines.append('- 模型阶段未在轮次上限内返回有效结果，程序按既定规则保留可用候选的记录：'
                     + '、'.join(f'{c} 第 {rep} 次 {stage}' for c, rep, stage in limits) + '。')
    lines += ['', '## 标签级命中与漏检', '',
              '静态列显示旧版 → 新版是否命中。模型列为三次运行中出现的次数，0/3 表示三次都漏检。', '',
              '| 案例 | 数据集标签 FQN | 静态前 → 后 | SP | MA | MA 仅确认 |',
              '| --- | --- | --- | ---: | ---: | ---: |']
    for case in cases:
        r = case['runs']
        for fqn in sorted(case['gold']):
            static = ' → '.join('是' if fqn in r[v][0] else '否' for v in ('before', 'static'))
            frequency = ' | '.join(f'{sum(fqn in run for run in r[v])}/{REPETITIONS}'
                                   for v in ('sp', 'ma', 'confirmed'))
            lines.append(f'| {case["id"][-3:]} | `{fqn}` | {static} | {frequency} |')
    return '\n'.join(lines) + '\n'


def main():
    cases = load_cases()
    report = summarize(cases)
    destination = ROOT / 'results/evaluation' / f'{EXPERIMENT}.json'
    katia.dump(destination, dict(cases=len(cases), repetitions=REPETITIONS, summary=report, per_case=[
        dict(id=c['id'], repo=c['repo'], gold=sorted(c['gold']), scores={
            v: {mode: case_scores(r, c['gold'], mode) for mode in ('FQN', 'CE')} for v, r in c['runs'].items()},
            model_turns=c['model_turns'], tool_counts=c['tool_counts'], query_breakdown=c['query_breakdown'],
             exhausted=c['exhausted'])
        for c in cases]))
    (ROOT / 'docs/full-fields-new20.md').write_text(report_text(cases, report))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
