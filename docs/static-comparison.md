# 静态候选对照

_第一阶段验证，使用前三个已分析样本。_

---

## ⚙️ 对照设置

三组使用相同的 parent 快照和种子。基线直接运行作者 JAR。字段组在基线上加入从种子方法读写的字段和本类或父类中的字段写入方。多跳组还会从种子查一层本类或父类被调用方法，再沿字段写入方反查最多三层同一继承链中的调用方，并记录路径上读取的字段。

新索引用 Spoon 从源码提取直接调用和字段读写，边包含源码文件和行号。保留每个入口字段的一条最短证据路径。候选生成结束后才读真实标签。可运行 `python src/static_compare.py --rows 0,1,2` 重算。

## 📊 三个机制验证样本

每列为命中数 / 候选数。分母为候选集大小。变更前实体用索引中的完整签名核对。

| 样本 | 变更前可定位标签 | JAR 基线 | 加字段 | 加多跳 |
| --- | ---: | ---: | ---: | ---: |
| 000 Commons Math | 1 | 1 / 2 | 1 / 2 | 1 / 2 |
| 001 Commons IO | 4 | 0 / 0 | 3 / 7 | 3 / 11 |
| 002 Commons Net | 2 | 0 / 15 | 0 / 22 | 2 / 36 |

| 样本 | 新命中实体及路径 | 仍漏报 |
| --- | --- | --- |
| 001 | `reset()` 读 `mark`，反查写入方找到 `mark(int)` 和三参数构造函数 | `skip(long)` 无此路径。两个新增字段未进入 parent 索引 |
| 002 | `parseFTPEntry()` 调用 `matches()`，后者读 `pattern`。从写入方 `compileRegex()` 反查构造链到单参数构造函数，再在 `super(REGEX)` 的实参位置找到 `REGEX` | 双参数构造函数和布尔字段均为新增 |

详细结果见 [Commons Math](../results/static-compare/constantinople-000.json)、[Commons IO](../results/static-compare/constantinople-001.json) 和 [Commons Net](../results/static-compare/constantinople-002.json)。

## 🔍 实验边界

这三例参与了规则设计。它们用于核对路径和候选增量，泛化效果需要在独立样本上测量。新增候选有源码关系，是否需要随提交修改仍需进一步判断。当前继承链限制会排除链外写入方，Spoon 使用 no-classpath，签名未索引也可能是解析或签名映射的缺口。Commons Net 的 `pattern` 路径是由调用与读写边连接起来的，当前实现未做完整实参到形参的数据流分析。
