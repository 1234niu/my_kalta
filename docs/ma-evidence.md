# Planner–Analyze–Review

本实验使用同一份变更前仓库、问题描述、种子 diff 和静态候选。Spoon 的源码索引按仓库、parent SHA 和导出器指纹缓存。索引包括实体、声明位置、调用、字段读写、继承和可能的重写边。Java 文本搜索可以补充 Spoon 未索引的源码。

| 阶段 | 输入和工作 | 输出 |
| --- | --- | --- |
| Planner | 读问题、种子 diff 和候选，提出要验证的问题 | 检索计划 |
| Analyze | 按名称和 FQN 查图，按位置读源码，最多查询 8 次 | 带证据 ID 的候选 |
| Review | 独立查询，最多 5 次。逐项核对候选是否需要配套修改 | 确认、待核查、排除，或具体补查问题 |
| 补查 | Analyze 最多查 3 次，Review 最多查 2 次 | 一轮补证后的审查结果 |

每轮最多发起 3 个查询，错误查询也计入预算。每例最多 18 轮工具调用、18 次查询和 33 个模型对话轮次。遇到临时 API 错误，每个模型轮最多发起 3 次请求。每个阶段的实际用量记录在结果的 `phase_usage` 中。

模型请求的查询由程序执行。查询只接受符号查找、相邻边、Java 源码搜索与指定行段读取。源码访问限于该案例的 parent 快照。当前版本要求 Review 独立读取相应源码后，才能把已有候选确认为受影响或排除。尚未验证的新签名保留为待核查。未审查的候选保留在待核查集合。审查耗尽轮次时保留候选，补查审查耗尽轮次时沿用第一次审查结果。运行结果同时保存确认集和确认加待核查集，便于按召回目标评估。

```bash
python src/ma_evidence.py --rows 0,5 --index-only
python src/ma_evidence.py --rows 0 --env-file ../work/ripple/.env.ripple100 --experiment ma-independent-review-000
python src/ma_evidence.py --rows 0 --env-file ../work/ripple/.env.ripple100 --analyze-review-only --experiment analyze-review-000
```

输入来自 `inputs.jsonl`。已生成新版静态候选的样本使用 `diff_and_override`，其他样本回退到作者 JAR，并记录候选组名。两组比较应先为相同的案例生成静态候选。请求、响应、工具证据和最终判定保存在 `results/ma-evidence/<experiment>/<case>/`。缓存和本地运行记录默认由 Git 忽略。

图覆盖取决于当前 Spoon 导出器的源码根和 no-classpath 解析能力。可能的重写关系按父类链和已有实例方法签名生成。外部库、动态分派及新增定义仍可能缺少证据。000–019 的结果见 [20 例新旧 MA 对照](twenty-case-ma-comparison.md)。

逐例运行可复用同一个实验名和已缓存响应。以下命令最多同时跑四个案例，再重建报告。

```bash
seq 0 19 | xargs -P 4 -I ROW python src/ma_evidence.py --rows ROW --env-file ../work/ripple/.env.ripple100 --experiment bounded-20
python src/report_ma_twenty.py
```
