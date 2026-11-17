# 第二轮 MA 小样本对照

第一轮基线为 Git 提交 `b1d7ed1` 的 20 例实验。第二轮沿用 `deepseek-v4.1-flash-1017`、温度 0、关闭思考模式。两轮每例各跑一次。003、016 是指定样例。013、014、019 在旧 MA 的三次运行和第一轮新版里均无 FQN 命中。该组用于诊断流程回归。

| 案例 | 标签数 | 静态命中 | 第一轮命中 | 第二轮 Analyze 命中 | 第二轮 Score 后命中 | 其中确认 | 第二轮输出数 | 查询 / 模型轮 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 003 | 1 | 1 | 0 | 1 | 1 | 0 | 4 | 15 / 8 |
| 016 | 12 | 2 | 10 | 2 | 2 | 2 | 2 | 13 / 8 |
| 013 | 1 | 0 | 0 | 0 | 0 | 0 | 9 | 18 / 9 |
| 014 | 1 | 0 | 0 | 0 | 0 | 0 | 8 | 17 / 9 |
| 019 | 1 | 0 | 0 | 1 | 1 | 0 | 7 | 14 / 8 |
| 合计 | 16 | 3 | 10 | 4 | 4 | 2 | 30 | 77 / 42 |

Score 后的候选集包括确认和待核查。Analyze 列包含 Planner 选定且有图路径的起点，以及 Analyze 交付的沿途候选。

- **003** 保留了 `VfsResource.normalize(String)`。本轮证据来自源码搜索，Score 保留为待核查。第一轮曾把同一方法排除。
- **016** 只保住 `list` 和 `lsub`。四个 Planner 假设集中在现有 helper 的引号处理、编码及改名调用点。Analyze 搜了旧方法名和新方法名，没有查找直接传递 `mailboxName` 的同类命令。丢失的 8 个命中在 Score 之前已经发生。
- **013** 仍漏掉 `DefaultResolutionCacheManager.clean()`。Analyze 试图查找异常堆栈中的 `XmlReportOutputter.output(...)`，其包超出了本次已登记的搜索范围。
- **014** Analyze 推断出了与标签匹配的新增签名 `CompositeConfiguration.appendListProperty(java.util.List,org.apache.commons.configuration.Configuration,java.lang.String)`。该方法在 parent 中不存在，当前实现把它单列为未解决的 diff 推断，表中未将它计入候选命中。
- **019** `XmlSettingsParser.classpathStarted(java.util.Map)` 通过共享字段的两条读取边进入候选。Analyze 提出设置目录值的转义会影响该方法构建 classpath URL，Score 保留为待核查。共享读取边定位了相关方法，具体影响由源码解释。

## 检索与运行边界

Planner 使用 seed diff、问题描述、一跳调用和字段读写摘要。每个静态来源最多呈现 12 项，Planner 合计最多选 12 个起点及 4 个源码搜索假设。Analyze 可在 seed、已选起点和已返回节点上逐跳展开，每个起点外最多走 3 个图边。结果记录完整的 seed 路径。图谱和源码搜索每页最多 10 项，源码搜索限定为已登记文件或其直接所属包。Score 只可按已登记候选及证据路径节点回读源码，每次最多 60 行。

Planner、Analyze、Score 最多查询 0、12、6 次，模型对话轮次上限为 2、15、9。错误查询和翻页均占预算。每轮最多 3 项查询。每例无补查循环。原始响应、证据、候选路径及用量保存在被 Git 忽略的 `results/ma-evidence/guided-pilot-v2/`。

```bash
python src/ma_guided.py --rows 3,16,13,14,19 --env-file ../work/ripple/.env.ripple100
```
