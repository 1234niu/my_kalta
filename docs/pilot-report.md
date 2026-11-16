# 首轮复现联调记录

_2026-11-16；DeepSeek 替代模型，三个原始顺序样本，每种变体每样本三次。_

---

## 📊 验证结果

这是工程联调，不是论文 Gemini 的完整数据集复现。所有请求和原始响应保存在 `results/runs/deepseek-pilot/`。

| 变体 | FQN Precision | FQN Recall | FQN F1 | CE F1 |
| --- | ---: | ---: | ---: | ---: |
| static | 16.67% | 33.33% | 22.22% | 22.22% |
| sp | 33.33% | 33.33% | 33.33% | 33.33% |
| ma | 33.33% | 13.89% | 19.44% | 26.19% |

先计算每个提交每项指标在三次重复中的中位数，再对提交作宏平均；不从宏 Precision/Recall 重新计算 F1。静态分析只运行一次。

## 🔍 样本与预测

| 样本 | 仓库 | 静态候选数 | SP 一致 | MA 一致 |
| --- | --- | ---: | --- | --- |
| constantinople-000 | apache/commons-math | 2 | True | True |
| constantinople-001 | apache/commons-io | 0 | True | False |
| constantinople-002 | apache/commons-net | 15 | False | False |

## 📋 逐实体命中、漏报与误报

以下按完整限定名（FQN）匹配。静态候选只生成一次；SP、MA 的 `n/3` 表示三次预测中命中该标签的次数，其余 `3−n` 次为漏报。构造函数和字段也纳入统计。

### constantinople-000 · apache/commons-math

| 真实受影响实体（FQN） | 类型 | 静态命中 | SP 命中 | MA 命中 |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.math3.optimization.univariate.BrentOptimizer.doOptimize()` | executable | 是 | 3/3 | 0/3 |

| 不在真实影响集中的模型预测（FQN） | SP 出现 | MA 出现 |
| --- | ---: | ---: |
| 无 | 0/3 | 0/3 |

### constantinople-001 · apache/commons-io

| 真实受影响实体（FQN） | 类型 | 静态命中 | SP 命中 | MA 命中 |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.io.input.CharSequenceInputStream.CharSequenceInputStream(java.lang.CharSequence,java.nio.charset.Charset,int)` | executable | 否 | 0/3 | 0/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark` | field | 否 | 0/3 | 0/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_cbuf` | field | 否 | 0/3 | 1/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_bbuf` | field | 否 | 0/3 | 1/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.skip(long)` | executable | 否 | 0/3 | 0/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark(int)` | executable | 否 | 0/3 | 2/3 |

| 不在真实影响集中的模型预测（FQN） | SP 出现 | MA 出现 |
| --- | ---: | ---: |
| `org.apache.commons.io.input.CharSequenceInputStream` | 0/3 | 2/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark()` | 0/3 | 1/3 |

### constantinople-002 · apache/commons-net

| 真实受影响实体（FQN） | 类型 | 静态命中 | SP 命中 | MA 命中 |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig)` | executable | 否 | 0/3 | 2/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig,boolean)` | executable | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.REGEX` | field | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.trimLeadingSpaces` | field | 否 | 0/3 | 1/3 |

| 不在真实影响集中的模型预测（FQN） | SP 出现 | MA 出现 |
| --- | ---: | ---: |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser` | 1/3 | 0/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser()` | 0/3 | 2/3 |

这里的误报指不在数据集真实影响集中的预测。CE 会忽略包名和参数，例如样本 002 的无参构造函数在 FQN 下是误报，但在 CE 下与同类的带参构造函数合并匹配。


对样本 001 调用作者 JAR 的 `ExecutableParser.getSeedMethod()` 核验：`CharSequenceInputStream.reset()` 已在 parent 中解析，关系结果仍为 `{}`。这个样本的零候选并非种子解析失败。复查入口：`tests/KatiaSeedAudit.java`。

## ⚙️ 调用记录

| 变体 | 请求次数 | 总 token | 调用耗时之和（秒） |
| --- | ---: | ---: | ---: |
| sp | 9 | 8079 | 10.28 |
| ma | 27 | 51388 | 134.19 |

耗时之和不是并行运行的墙钟时间，也不是论文的 generation time。费用未计量，不推测价格。

## 📋 尚未完成

- 论文三种模型及固定 OpenRouter provider 的完整 263 提交实验
- 作者未公开的编排和输入序列化细节对齐
- 全数据实体签名、initializer、匿名类及特殊 CE 匹配审计
- 静态空候选的原因分类与源码布局覆盖审计

这些缺口不影响当前小样本链路重放，但影响与论文表格作直接比较。详见 [复现入口](../README.md)。
