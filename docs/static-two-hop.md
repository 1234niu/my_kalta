# 两跳正向调用窄对照

沿 CALLS 从方法种子向前走两条边，允许跨类。所得仓库内实体与原多跳候选取并集，按完整签名去重。

| 样本 | 候选 原→新 | 命中 原→新 | SP 输入增量（字符） | MA 前两阶段合计增量（字符） |
| --- | ---: | ---: | ---: | ---: |
| 000 | 2→2 | 1→1 | +0 | +0 |
| 001 | 11→11 | 3→3 | +0 | +0 |
| 002 | 36→37 | 2→2 | +89 | +178 |
| 003 | 9→13 | 0→1 | +252 | +504 |
| 004 | 21→35 | 1→1 | +1638 | +3276 |
| 005 | 8→8 | 0→0 | +0 | +0 |
| 006 | 8→9 | 0→0 | +141 | +282 |
| 007 | 24→25 | 0→0 | +73 | +146 |
| 008 | 20→21 | 0→0 | +68 | +136 |
| 009 | 15→16 | 2→2 | +88 | +176 |
| 合计 | 154→177 | 9→10 | +2349 | +4698 |

003 是唯一新增命中。证据路径为 VfsRepository.list(String) → VfsResource.getChildren() → VfsResource.normalize(String)。004 增加候选最多，但命中数不变。

提示词长度以渲染文本字符计。MA 前两阶段使用相同的前序证据文本测量候选列表带来的增量。实际模型 token 和 MA 生成的中间证据长度未测。

复跑：`python src/static_compare.py --cross-class-calls --rows 0,1,2,3,4,5,6,7,8,9`。逐样本 JSON 在 `results/static-two-hop/`。

## 🔍 种子 diff 叠加

用 Tree-sitter 分析种子 diff 的前后片段，将新增方法调用记录为从种子出发的 `ADDED_CALL` 边。目标可以是待解析的调用记录。按接收者、方法名和参数个数比较前后调用形状。变更前索引能按接收者和参数个数找到可能签名时，记录为 `possible_parent_targets`。这些签名没有经过完整的 Java 类型解析。Hunk 位置以数据集提供的行号为依据。

005 共提取 8 个新增调用点，其中有 `nullSafeValue(select, entityName)` 和 `nullSafeValue(where)`。两个调用分别以 2 个和 1 个参数保存，声明类均待解析。其余 6 个属于字符串构建器的调用链。同一批 10 个样本共提取 65 个调用点，其中 2 个记录了可能的 parent 目标。

原始叠加版本只记录调用线索。下节介绍加入候选的新版。三个静态对照组和两跳组的候选与上一轮逐样本一致。调用记录独立写入 `seed_diff_overlay.added_calls`，尚未传入 SP 或 MA。

```bash
python -m pip install -r requirements.txt
python src/static_compare.py --seed-diff-overlay --cross-class-calls --rows 0,1,2,3,4,5,6,7,8,9
```

结果见 [005 的种子 diff 叠加](../results/static-seed-diff/constantinople-005.json)。

## 🧪 叠加候选与重写关系对照

新版把新增调用的可能签名、diff 提示的新增字段写入，以及同签名的父类实例方法加入独立候选组 `diff_and_override`。对新增方法，使用旧源码里的实参类型、接收者返回类型、继承链和已用过的静态工具类生成候选。签名仍是推断，原始调用与状态继续保存在 JSON 中。真实标签和完整修复提交只用于评估。

| 范围 | 两跳组 FQN 命中 | 加叠加候选和重写关系 |
| --- | ---: | ---: |
| 全部 10 例 | 10 / 26 | 21 / 26 |
| 005 DeltaSpike | 0 / 2 | 2 / 2 |
| 006 Commons Configuration | 0 / 1 | 1 / 1 |
| 007 Commons DBCP | 0 / 4 | 3 / 4 |
| 008 Commons JCS | 0 / 1 | 1 / 1 |
| 009 SystemML | 2 / 5 | 4 / 5 |

005 通过外层类已有的 `QueryUtils.isNotEmpty(...)` 调用提出工具类候选，通过种子所属类的字段类型提出两个 String 重载。007 仍遗漏池装配方 `createConnectionPool(...)`。009 仍遗漏只在新 helper 内部出现的 `_documentBuilder`。此表来自用于分析规则的同一批案例，尚无独立样本测量。
