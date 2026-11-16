"""Generate the auditable pilot report only after all expected runs exist."""
import json
from katia import ROOT, dump, evaluate, load_task


def main():
    experiment='deepseek-pilot'
    reports={v:evaluate(experiment,v,[0,1,2],3) for v in ('static','sp','ma')}
    usage={}
    for variant in ('sp','ma'):
        records=[json.loads(p.read_text()) for p in (ROOT/'results/runs'/experiment/variant).glob('**/stage-*.json') if not p.name.endswith('.request.json')]
        usage[variant]=dict(calls=len(records),seconds_sum=sum(r['seconds'] for r in records),
            tokens=sum(r['response'].get('usage',{}).get('total_tokens',0) for r in records),
            reported_models=sorted({r['response'].get('model','unknown') for r in records}))
    dump(ROOT/'results/evaluation/pilot-usage.json',usage)
    text=['# 首轮复现联调记录','', '_2026-11-16；DeepSeek 替代模型，三个原始顺序样本，每种变体每样本三次。_', '', '---', '', '## 📊 验证结果','',
          '这是工程联调，不是论文 Gemini 的完整数据集复现。所有请求和原始响应保存在 `results/runs/deepseek-pilot/`。', '',
          '| 变体 | FQN Precision | FQN Recall | FQN F1 | CE F1 |','| --- | ---: | ---: | ---: | ---: |']
    for variant,report in reports.items():
        f=report['metrics']['FQN'];c=report['metrics']['CE']
        text.append(f"| {variant} | {f['precision']:.2%} | {f['recall']:.2%} | {f['f1']:.2%} | {c['f1']:.2%} |")
    text+=['','先计算每个提交每项指标在三次重复中的中位数，再对提交作宏平均；不从宏 Precision/Recall 重新计算 F1。静态分析只运行一次。','', '## 🔍 样本与预测','', '| 样本 | 仓库 | 静态候选数 | SP 一致 | MA 一致 |','| --- | --- | ---: | --- | --- |']
    for row in range(3):
        task=load_task(row);static=json.loads((ROOT/'results/static'/task['id']/'candidates.json').read_text())
        text.append(f"| {task['id']} | {task['repo']} | {len(static['candidates'])} | {reports['sp']['per_case'][row]['consistent']} | {reports['ma']['per_case'][row]['consistent']} |")
    text += ['', '## 📋 逐实体命中、漏报与误报', '',
             '以下按完整限定名（FQN）匹配。静态候选只生成一次；SP、MA 的 `n/3` 表示三次预测中命中该标签的次数，其余 `3−n` 次为漏报。构造函数和字段也纳入统计。', '']
    labels = {r['id']: r for r in map(json.loads, (ROOT/'dataset/processed/evaluation-only.jsonl').read_text().splitlines())}
    for row in range(3):
        task = load_task(row)
        case = task['id']
        gold = labels[case]['impacted']
        target = {e['fqn'] for e in gold}
        candidate = set(json.loads((ROOT/'results/static'/case/'candidates.json').read_text())['candidates'])
        predictions = {v: [set(json.loads((ROOT/'results/runs'/experiment/v/case/str(i)/'prediction.json').read_text())['predictions']) for i in range(3)] for v in ('sp', 'ma')}
        text += [f"### {case} · {task['repo']}", '',
                 '| 真实受影响实体（FQN） | 类型 | 静态命中 | SP 命中 | MA 命中 |',
                 '| --- | --- | --- | ---: | ---: |']
        for e in gold:
            fqn = e['fqn']
            sp, ma = (sum(fqn in pred for pred in predictions[v]) for v in ('sp', 'ma'))
            text.append(f"| `{fqn}` | {e['type']} | {'是' if fqn in candidate else '否'} | {sp}/3 | {ma}/3 |")
        text += ['', '| 不在真实影响集中的模型预测（FQN） | SP 出现 | MA 出现 |', '| --- | ---: | ---: |']
        extras = set().union(*(p for runs in predictions.values() for p in runs)) - target
        if not extras:
            text.append('| 无 | 0/3 | 0/3 |')
        for fqn in sorted(extras):
            sp, ma = (sum(fqn in pred for pred in predictions[v]) for v in ('sp', 'ma'))
            text.append(f'| `{fqn}` | {sp}/3 | {ma}/3 |')
        text.append('')
    text += ['这里的误报指不在数据集真实影响集中的预测。CE 会忽略包名和参数，例如样本 002 的无参构造函数在 FQN 下是误报，但在 CE 下与同类的带参构造函数合并匹配。', '']
    text+=['', '对样本 001 调用作者 JAR 的 `ExecutableParser.getSeedMethod()` 核验：`CharSequenceInputStream.reset()` 已在 parent 中解析，关系结果仍为 `{}`。这个样本的零候选并非种子解析失败。复查入口：`tests/KatiaSeedAudit.java`。', '', '## ⚙️ 调用记录','', '| 变体 | 请求次数 | 总 token | 调用耗时之和（秒） |','| --- | ---: | ---: | ---: |']
    for variant,u in usage.items():
        text.append(f"| {variant} | {u['calls']} | {u['tokens']} | {u['seconds_sum']:.2f} |")
    text+=['','耗时之和不是并行运行的墙钟时间，也不是论文的 generation time。费用未计量，不推测价格。','', '## 📋 尚未完成','',
           '- 论文三种模型及固定 OpenRouter provider 的完整 263 提交实验','- 作者未公开的编排和输入序列化细节对齐','- 全数据实体签名、initializer、匿名类及特殊 CE 匹配审计','- 静态空候选的原因分类与源码布局覆盖审计','',
           '这些缺口不影响当前小样本链路重放，但影响与论文表格作直接比较。详见 [复现入口](../README.md)。','']
    (ROOT/'docs/pilot-report.md').write_text('\n'.join(text))
    print(json.dumps(usage))

if __name__=='__main__':main()
