# 独立计划 MA 五例对照

第二轮基线见 [seed-guided 五例报告](ma-guided-pilot.md)，对应远端提交 `203d22d`。本轮使用同样五例和模型 `deepseek-v4.1-flash-1017`，两轮均每例一次。评估标签只用于运行后的对照。

Planner 只读问题描述和种子 diff。程序用静态候选和符号索引消歧 Planner 点名的实体，只有完整签名相同或得到唯一解析才计为重合。每条有效计划执行一次初探，随后按初探证据排名，程序执行排名靠前的最多两条补查。Analyze 可使用剩余预算继续检索。

静态候选、计划候选和有 diff 证据的签名推断按 FQN 合并。Review 只证据复检，程序为最多六项准备独立源码或 diff 证据，优先重合项，并为有证据的非重合计划候选保留最多两项。未复检或证据不足的候选保持待核查。

## 阶段命中

各候选列为 FQN 命中数 / 输出数。第二轮“命中”一列的分母为标签数。计划命中已按 FQN 去重。

| 案例 | 标签 | Planner 点名 | 静态 | 重合 | 计划探索 | Review 后候选 | 仅确认 | 第二轮命中 | 查询 初探/排名后/Analyze追加/复检 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 003 | 1 | 1/5 | 1/13 | 1/3 | 0/3 | 1/14 | 0/1 | 1/1 | 4 / 2 / 0 / 6 |
| 016 | 12 | 0/1 | 2/2 | 0/0 | 9/10 | 9/10 | 6/6 | 2/12 | 4 / 2 / 0 / 6 |
| 013 | 1 | 0/4 | 0/8 | 0/1 | 0/3 | 0/9 | 0/1 | 0/1 | 3 / 2 / 0 / 6 |
| 014 | 1 | 0/4 | 0/14 | 0/0 | 1/2 | 1/16 | 0/0 | 0/1 | 3 / 2 / 0 / 6 |
| 019 | 1 | 0/4 | 0/23 | 0/1 | 0/3 | 0/24 | 0/2 | 1/1 | 4 / 2 / 0 / 6 |
| 合计 | 16 | 1/18 | 3/60 | 1/5 | 10/21 | 11/73 | 6/10 | 4/16 | 18 / 10 / 0 / 30 |

复检覆盖 30 个候选，其中 8 个为真实标签。Review 确认 10 个候选，其中 6 个为真实标签。本轮没有排除已经进入候选集的真实标签。

## 逐计划

| 案例 | 计划 | 命中 / 输出 | 静态外命中 | 查询 | 命中的完整签名 |
| --- | --- | ---: | ---: | ---: | --- |
| 003 | P1 | 0/1 | 0 | 2 | — |
| 003 | P2 | 0/0 | 0 | 1 | — |
| 003 | P3 | 0/1 | 0 | 1 | — |
| 003 | P4 | 0/1 | 0 | 2 | — |
| 016 | P1 | 2/2 | 0 | 2 | `org.apache.commons.net.imap.IMAPClient.list(java.lang.String,java.lang.String)`, `org.apache.commons.net.imap.IMAPClient.lsub(java.lang.String,java.lang.String)` |
| 016 | P2 | 7/7 | 7 | 2 | `org.apache.commons.net.imap.IMAPClient.create(java.lang.String)`, `org.apache.commons.net.imap.IMAPClient.delete(java.lang.String)`, `org.apache.commons.net.imap.IMAPClient.examine(java.lang.String)`, `org.apache.commons.net.imap.IMAPClient.rename(java.lang.String,java.lang.String)`, `org.apache.commons.net.imap.IMAPClient.select(java.lang.String)`, `org.apache.commons.net.imap.IMAPClient.subscribe(java.lang.String)`, `org.apache.commons.net.imap.IMAPClient.unsubscribe(java.lang.String)` |
| 016 | P3 | 0/0 | 0 | 1 | — |
| 016 | P4 | 0/1 | 0 | 1 | — |
| 013 | P1 | 0/1 | 0 | 2 | — |
| 013 | P2 | 0/0 | 0 | 1 | — |
| 013 | P3 | 0/2 | 0 | 2 | — |
| 014 | P1 | 0/1 | 0 | 2 | — |
| 014 | P2 | 1/1 | 1 | 1 | `org.apache.commons.configuration.CompositeConfiguration.appendListProperty(java.util.List,org.apache.commons.configuration.Configuration,java.lang.String)` |
| 014 | P3 | 0/0 | 0 | 2 | — |
| 019 | P1 | 0/2 | 0 | 2 | — |
| 019 | P2 | 0/0 | 0 | 2 | — |
| 019 | P3 | 0/0 | 0 | 1 | — |
| 019 | P4 | 0/1 | 0 | 1 | — |

## 案例观察

- **016** P2 初探后，排名阶段执行了 `doCommand (IMAPCommand` 源码搜索，恢复了 7 个静态外命中。结果共命中 9/12，`copy`、四参数 `append` 和 `status` 仍未命中。
- **014** 两处新增调用为 `appendListProperty` 提供 diff 证据。候选按 seed 所在类推断归属，参数签名保留为待核查。
- **013** 本轮搜索可跨包且调用未被权限拒绝，但计划主要跟踪报表文件构建，仍漏掉 `clean()`。
- **019** 仍找到设置目录变量的两个写入方法，本轮未沿消费路径找到 `classpathStarted`。
- **003** Planner 和静态候选重合的 `normalize` 进入复检队列，最终保留待核查。

## 预算与复跑

每例上限为 12 次探索查询和 6 次证据复检，合计 18 次。每个模型阶段最多 2、2、13、2 轮，合计 19 轮。初探、排名后查询和 Analyze 追加查询共用 12 次额度。错误查询和翻页计入预算。五例实际共 58 次，每例 11–12 次。Analyze 五例均在收到初探和排名后查询结果之后直接提交候选，未追加查询。

原始模型响应只保存在本地 `results/ma-evidence/independent-plans-ranked/`。

```bash
python src/ma_planned.py --rows 3,16,13,14,19 --env-file ../work/ripple/.env.ripple100
```
