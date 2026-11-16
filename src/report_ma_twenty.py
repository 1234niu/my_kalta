"""Compare the bounded evidence MA experiment with the existing 20-case runs."""
import json
from statistics import mean, median

import katia
from compare_ten import LATEST_ARM, LATEST_EXPERIMENT, MODEL, REPETITIONS, candidate_fingerprint
from ma_evidence import PHASE_QUERY_LIMITS

EXPERIMENT = 'bounded-20'
LABELS = {
    'static': '静态候选', 'sp': '旧 SP', 'ma': '旧 MA',
    'recall': '新 MA · 确认＋待核查', 'confirmed': '新 MA · 仅确认',
}


def read(path):
    return json.loads((katia.ROOT / path).read_text())


def load_cases():
    gold = {item['id']: {entity['fqn'] for entity in item['impacted']}
            for item in map(json.loads, (katia.ROOT / 'dataset/processed/evaluation-only.jsonl').read_text().splitlines())}
    cases = []
    for row in range(20):
        task = katia.load_task(row)
        case = task['id']
        static = read(f'results/static-seed-diff/{case}.json')['candidates'][LATEST_ARM]
        base = read(f'results/static/{case}/candidates.json')['fingerprint']
        fingerprint = candidate_fingerprint(base, static)
        runs = {'static': [set(static)]}
        for variant in ('sp', 'ma'):
            runs[variant] = []
            for rep in range(REPETITIONS):
                old = read(f'results/runs/{LATEST_EXPERIMENT}/{variant}/{case}/{rep}/prediction.json')
                if (old['id'], old['model'], old['variant'], old['repeat'], old['static_fingerprint']) != (
                        case, MODEL, variant, rep, fingerprint):
                    raise ValueError(f'Old run metadata mismatch for {case} {variant} {rep}')
                runs[variant].append(set(old['predictions']))
        new = read(f'results/ma-evidence/{EXPERIMENT}/{case}/result.json')
        if (new['id'], new['model'], new['parent_commit'], new['candidate_arm'],
                new['planner_enabled'], new['phase_query_limits']) != (
                case, MODEL, task['parent_commit'], LATEST_ARM, True, PHASE_QUERY_LIMITS):
            raise ValueError(f'New run metadata mismatch for {case}')
        run_dir = katia.ROOT / 'results/ma-evidence' / EXPERIMENT / case
        analyze_context = json.loads(read(run_dir / 'analyze-0.json')['request']['messages'][1]['content'])
        if analyze_context['static_candidates'] != static:
            raise ValueError(f'New candidate inputs mismatch for {case}')
        usage = new['phase_usage']
        for phase, counts in usage.items():
            if not 0 <= counts['tool_rounds'] <= counts['queries'] <= PHASE_QUERY_LIMITS[phase]:
                raise ValueError(f'Tool cap exceeded for {case} {phase}')
            if not 1 <= counts['model_turns'] <= PHASE_QUERY_LIMITS[phase] + 3:
                raise ValueError(f'Model turn cap exceeded for {case} {phase}')
        totals = {key: sum(item[key] for item in usage.values()) for key in ('tool_rounds', 'queries', 'model_turns')}
        if totals['queries'] != new['evidence_count']:
            raise ValueError(f'Evidence count mismatch for {case}')
        totals['followup'] = 'analyze-followup' in usage
        totals['exhausted'] = ', '.join(phase for phase, counts in usage.items() if counts.get('exhausted'))
        runs['recall'] = [set(new['recall_candidates'])]
        runs['confirmed'] = [set(new['confirmed'])]
        cases.append((case, gold[case], runs, totals))
    return cases


def metrics(cases, variant, mode):
    return ' / '.join(
        f'{mean(median(katia.score(run, gold, mode)[key] for run in runs[variant]) for _, gold, runs, _ in cases):.1%}'
        for key in ('precision', 'recall', 'f1'))


def format_runs(runs, gold):
    return ', '.join(f'{len(run & gold)}/{len(run)}' for run in runs)


def report(cases):
    lines = [
        '# 000–019 新旧 MA 对照', '',
        f'两版使用同样的 20 个样本、`{MODEL}`、温度 0、关闭思考模式和相同静态候选。'
        '旧 SP、旧 MA 各运行三次，新 MA 每例运行一次。000–009 参与过静态规则开发，010–019 用于检验迁移。', '',
        '## 精确率、召回率与 F1', '',
        '旧版先对每个案例的三次指标取中位数，再与新版按案例做宏平均。FQN 区分包名和参数，CE 只保留类名和成员名。'
        '新 MA 给出确认＋待核查的召回候选集，并单列独立核查后确认的实体。', '',
        '| 样本 | 方法 | FQN P / R / F1 | CE P / R / F1 | FQN 命中 / 标签（实体累计） |',
        '| --- | --- | --- | --- | ---: |',
    ]
    for scope, subset in [('000–009', cases[:10]), ('010–019', cases[10:]), ('全部', cases)]:
        labels = sum(len(gold) for _, gold, _, _ in subset)
        for variant, label in LABELS.items():
            hits = sum(median(len(run & gold) for run in runs[variant]) for _, gold, runs, _ in subset)
            lines.append(f'| {scope} | {label} | {metrics(subset, variant, "FQN")} | '
                         f'{metrics(subset, variant, "CE")} | {hits}/{labels} |')
    lines += ['', '旧版实体累计按各案例三次命中数的中位数相加。', '',
              '## 逐例预测和工具用量', '',
              '预测列为 FQN 命中 / 输出数。一次工具轮最多分发三个查询，错误查询也占用预算。'
              'Planner 不调用工具，Analyze、Review、补查 Analyze、补查 Review 的查询上限依次为 8、5、3、2。'
              '每例至多一次补查，最多 18 次工具查询和 33 个模型对话轮次。临时 API 错误单次模型轮最多请求三次。', '',
              '| 案例 | 标签 | 静态 | 旧 MA 三次 | 新 MA 确认＋待核查 | 新 MA 仅确认 | 工具轮 / 查询 / 模型轮 | 补查 |',
              '| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |']
    for case, gold, runs, usage in cases:
        predictions = ' | '.join(format_runs(runs[variant], gold) for variant in ('static', 'ma', 'recall', 'confirmed'))
        counts = ' / '.join(str(usage[key]) for key in ('tool_rounds', 'queries', 'model_turns'))
        lines.append(f'| {case[-3:]} | {len(gold)} | {predictions} | {counts} | {"有" if usage["followup"] else "无"} |')
    exhausted = [f'{case[-3:]}（{usage["exhausted"]}）' for case, _, _, usage in cases if usage['exhausted']]
    if exhausted:
        lines += ['', '以下案例的审查阶段耗尽轮次，保留分析候选或前一轮已完成的审查结果。'
                  + '、'.join(exhausted) + '。']
    for key, label in [('tool_rounds', '工具轮'), ('queries', '工具查询'), ('model_turns', '模型轮')]:
        values = [usage[key] for _, _, _, usage in cases]
        lines += ['', f'{label}共 {sum(values)}，每例中位数 {median(values):g}，最高 {max(values)}。']

    lines += ['', '## 召回增量来源', '',
              '旧 MA 稳定命中指三次运行中至少两次匹配该 FQN。'
              '静态以外命中按该实体是否进入相同的静态输入集合判定。', '',
              '| 样本 | 保住静态命中 | 静态以外命中（确认数） | 补回旧 MA 漏检 | 丢失旧 MA 稳定命中 |',
              '| --- | ---: | ---: | ---: | ---: |']
    for scope, subset in [('000–009', cases[:10]), ('010–019', cases[10:]), ('全部', cases)]:
        kept = static_total = novel = novel_confirmed = recovered = lost = 0
        for _, gold, runs, _ in subset:
            static = gold & runs['static'][0]
            new = gold & runs['recall'][0]
            old = {entity for entity in gold if sum(entity in run for run in runs['ma']) >= 2}
            kept += len(new & static)
            static_total += len(static)
            novel += len(new - static)
            novel_confirmed += len((new - static) & runs['confirmed'][0])
            recovered += len(new - old)
            lost += len(old - new)
        lines.append(f'| {scope} | {kept}/{static_total} | {novel}（{novel_confirmed}） | {recovered} | {lost} |')

    lines += ['', '## 代表案例', '',
              '- **000** 旧 MA 三次均遗漏 `BrentOptimizer.doOptimize()`。新版 Review 读取调用处，确认 `best()` 的平局选择影响该方法的返回值。',
              '- **003** 静态候选已经覆盖 `VfsResource.normalize(String)`。新版 Review 以方法体可以原样复用为由将其排除，和数据集标签产生分歧。这一处漏检发生在审查阶段。',
              '- **016** 旧 MA 和静态候选均命中 2/12，新版候选命中 10/12。新增的 8 个命中都在静态候选以外，其中 Review 依据源码确认了 `rename`、`select` 和 `status`。该例占 9 个静态以外命中的 8 个。',
              '', '## 逐实体命中和漏检', '',
              '旧 MA 列为三次出现次数。额外输出指未匹配数据集标签的 FQN。', '']
    for case, gold, runs, _ in cases:
        lines += [f'### {case}', '',
                  '| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |',
                  '| --- | --- | ---: | --- |']
        for entity in sorted(gold):
            static = '是' if entity in runs['static'][0] else '否'
            old_hits = sum(entity in run for run in runs['ma'])
            state = ('确认' if entity in runs['confirmed'][0] else
                     '待核查' if entity in runs['recall'][0] else '漏检')
            lines.append(f'| `{entity}` | {static} | {old_hits}/3 | {state} |')
        extras = runs['recall'][0] - gold
        lines += ['', f'新版额外输出 {len(extras)} 个，其中确认 {len(extras & runs["confirmed"][0])} 个。', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    (katia.ROOT / 'docs/twenty-case-ma-comparison.md').write_text(report(load_cases()))
