"""Compare bounded and planned MA on the same improved static candidates."""
import json
from statistics import mean, median

import katia
from compare_ten import MODEL, REPETITIONS
from ma_evidence import PHASE_QUERY_LIMITS
from report_full_fields import case_scores, load_cases, read
from run_full_fields import ARM, EXPERIMENT, MA, STATIC

OLD = 'bounded-ma-new20'
KEYS = ('precision', 'recall', 'f1')
VARIANTS = {
    'old': '旧有界 MA · 确认＋待核查', 'ma': '新版独立计划 MA · 确认＋待核查',
    'old_confirmed': '旧有界 MA · 仅确认', 'confirmed': '新版独立计划 MA · 仅确认',
}


def load_workflows():
    cases = load_cases()
    if read(MA / OLD / 'selection.json') != read(MA / EXPERIMENT / 'selection.json'):
        raise ValueError('The two workflows must use the same selection')
    for case in cases:
        case_id = case['id']
        reference = read(STATIC / f'{case_id}.json')['candidates'][ARM]
        case['runs'].update(old=[], old_confirmed=[])
        case['old_usage'] = []
        for rep in range(REPETITIONS):
            path = MA / OLD / f'repeat-{rep}' / case_id
            old = read(path / 'result.json')
            new = read(MA / EXPERIMENT / f'repeat-{rep}' / case_id / 'result.json')
            request = read(path / 'planner-0.json')['request']
            candidates = json.loads(request['messages'][1]['content'])['static_candidates']
            if (old['id'], old['model'], old['parent_commit'],
                old['candidate_arm'], old['planner_enabled'], candidates) != (
                    case_id, MODEL, new['parent_commit'], ARM, True, reference):
                raise ValueError(f'MA input mismatch for {case_id} repetition {rep + 1}')
            usage = old['phase_usage']
            if old['phase_query_limits'] != PHASE_QUERY_LIMITS:
                raise ValueError(f'Old workflow uses unexpected query limits: {path}')
            for phase, counts in usage.items():
                if not (0 <= counts['tool_rounds'] <= counts['queries'] <= PHASE_QUERY_LIMITS[phase]
                        and 1 <= counts['model_turns'] <= PHASE_QUERY_LIMITS[phase] + 3):
                    raise ValueError(f'Old workflow exceeded phase budget: {path} {phase}')
            queries = sum(u['queries'] for u in usage.values())
            turns = sum(u['model_turns'] for u in usage.values())
            if queries > 18 or turns > 33 or queries != old['evidence_count']:
                raise ValueError(f'Old workflow exceeded total or evidence budget: {path}')
            case['old_usage'].append(dict(queries=queries, model_turns=turns,
                                          review_exhausted=[p for p, u in usage.items() if u.get('exhausted')]))
            case['runs']['old'].append(set(old['recall_candidates']))
            case['runs']['old_confirmed'].append(set(old['confirmed']))
    return cases


def stable(runs):
    return {n for n in set().union(*runs) if sum(n in run for run in runs) >= 2}


def summarize(cases):
    summary = {}
    for variant in VARIANTS:
        metrics = {}
        for mode in ('FQN', 'CE'):
            scores = [case_scores(c['runs'][variant], c['gold'], mode) for c in cases]
            metrics[mode] = {key: mean(r[key] for r in scores) for key in KEYS}
        summary[variant] = dict(
            metrics=metrics,
            fqn_hits=sum(median(len(r & c['gold']) for r in c['runs'][variant]) for c in cases),
            outputs=sum(median(len(r) for r in c['runs'][variant]) for c in cases),
            static_hits_kept=sum(len(stable(c['runs'][variant]) & c['gold'] & c['runs']['static'][0]) for c in cases),
            outside_static_hits=sum(len((stable(c['runs'][variant]) & c['gold']) - c['runs']['static'][0])
                                    for c in cases))
    return summary


def report_text(cases, stats):
    labels = sum(len(c['gold']) for c in cases)
    lines = [
        '# 同一改进静态候选下的新旧 MA 对照', '',
        f'与[完整实验](full-fields-new20.md)使用相同 20 个提交及 `combined_field_paths` 静态候选。'
        f'旧版为有界 Planner–Analyze–Review，含可选的一轮补查。新版为独立计划、初探、排名补查、独立复检。'
        f'两组均使用 `{MODEL}`、温度 0、关闭思考模式，每例各三次。', '',
        '两组的每次工具查询上限相同，均为 18。旧版和新版的模型轮次上限分别为 33 和 19。'
        '下表按论文口径先逐提交计算，每项指标取三次中位数，再对 20 个提交取宏平均。'
        '实体命中按各案例三次命中数中位数相加。 [katIA §V-A](https://arxiv.org/html/2611.10958v1#S5.SS1)', '',
        '| MA 流程 | FQN 精确率 / 召回率 / F1 | CE 精确率 / 召回率 / F1 | FQN 命中 / 标签 | 输出数 |',
        '| --- | --- | --- | ---: | ---: |',
    ]
    for key, label in VARIANTS.items():
        row = stats[key]
        scores = [' / '.join(f'{row["metrics"][mode][k]:.2%}' for k in KEYS) for mode in ('FQN', 'CE')]
        lines.append(f'| {label} | ' + ' | '.join(scores)
                     + f' | {row["fqn_hits"]:g}/{labels} | {row["outputs"]:g} |')
    lines.extend(['', '## 召回来源和工具用量', ''])
    for key in ('old', 'ma'):
        row = stats[key]
        lines.append(f'- {VARIANTS[key]}在至少两次运行中保住 {row["static_hits_kept"]} 个静态命中，'
                     f'找到 {row["outside_static_hits"]} 个静态之外的标签。')
    per_case_delta = [case_scores(c['runs']['ma'], c['gold'], 'FQN')['recall']
                      - case_scores(c['runs']['old'], c['gold'], 'FQN')['recall'] for c in cases]
    lines.append(f'- 按逐提交 FQN 召回的三次中位数比较，新版上升 {sum(d > 0 for d in per_case_delta)} 例，'
                 f'持平 {sum(d == 0 for d in per_case_delta)} 例，下降 {sum(d < 0 for d in per_case_delta)} 例。')
    old_queries = [r['queries'] for c in cases for r in c['old_usage']]
    old_turns = [r['model_turns'] for c in cases for r in c['old_usage']]
    new_queries = [sum(r) for c in cases for r in c['tool_counts']]
    new_turns = [r for c in cases for r in c['model_turns']]
    lines.append(f'- 旧 → 新的工具查询中位数为 {median(old_queries):g} → {median(new_queries):g}，'
                 f'模型轮次中位数为 {median(old_turns):g} → {median(new_turns):g}。')
    limits = [(c['id'][-3:], rep + 1, p) for c in cases for rep, u in enumerate(c['old_usage'])
              for p in u['review_exhausted']]
    if limits:
        lines.append('- 旧版审查达到上限时保留已有候选或前一轮复检结论：'
                     + '、'.join(f'{c} 第 {n} 次 {p}' for c, n, p in limits) + '。')
    lines += ['', '## 逐提交 FQN 对照', '',
              '三次列为每次的命中数 / 输出数。稳定新增与丢失比较各自三次至少两次命中的标签。', '',
              '| 案例 | 标签 | 旧版三次 | 新版三次 | 旧版仅确认 | 新版仅确认 | 稳定新增 / 丢失 |',
              '| --- | ---: | --- | --- | --- | --- | ---: |']
    for c in cases:
        g, runs = c['gold'], c['runs']
        text = [', '.join(f'{len(run & g)}/{len(run)}' for run in runs[v]) for v in VARIANTS]
        old, new = (stable(runs[v]) & g for v in ('old', 'ma'))
        lines.append(f'| {c["id"][-3:]} | {len(g)} | ' + ' | '.join(text) + f' | {len(new-old)} / {len(old-new)} |')
    return '\n'.join(lines) + '\n'


def main():
    cases = load_workflows()
    stats = summarize(cases)
    root = katia.ROOT
    (root / 'docs/ma-workflows-new20.md').write_text(report_text(cases, stats))
    katia.dump(root / 'results/evaluation/ma-workflows-new20.json',
               dict(cases=len(cases), static_arm=ARM, repetitions=REPETITIONS, summary=stats,
                    per_case=[dict(id=c['id'], scores={
                        variant: {mode: case_scores(c['runs'][variant], c['gold'], mode)
                                  for mode in ('FQN', 'CE')} for variant in VARIANTS},
                        old_usage=c['old_usage'], new_tools=c['tool_counts'], new_turns=c['model_turns'])
                              for c in cases]))
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
