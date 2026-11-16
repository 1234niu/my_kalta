# 10 个案例的静态候选与 SP／MA 对照

使用 Constantinople 原始顺序的前 10 行。前三例参与了静态规则设计，后七例用于检验扩展效果。每个案例使用同一个变更前快照、相同种子和问题描述。

模型统一使用 `deepseek-v4.1-flash-1017`，温度 0，关闭 thinking。SP 和 MA 保持现有提示词与编排，每个候选组各重复 3 次。原始候选组复用已保存的前三例响应。字段扩展只参加静态对照，模型对照使用原始候选和多跳候选。

## 静态候选逐案例比较

每组写作“FQN 命中数 / 候选数”。parent 已索引标签使用同一个源码索引核对。未索引可能来自新增实体或解析、签名映射缺口。

| 样本 | 仓库 | 标签数 | parent 已索引 | JAR 一跳 | 加字段 | 加多跳 | 加两跳调用 | 加 diff 与重写 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| constantinople-000 | apache/commons-math | 1 | 1 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 2 |
| constantinople-001 | apache/commons-io | 6 | 4 | 0 / 0 | 3 / 7 | 3 / 11 | 3 / 11 | 5 / 14 |
| constantinople-002 | apache/commons-net | 4 | 2 | 0 / 15 | 0 / 22 | 2 / 36 | 2 / 37 | 2 / 37 |
| constantinople-003 | apache/ant-ivy | 1 | 1 | 0 / 3 | 0 / 3 | 0 / 9 | 1 / 13 | 1 / 13 |
| constantinople-004 | apache/ant-ivy | 1 | 1 | 1 / 5 | 1 / 9 | 1 / 21 | 1 / 35 | 1 / 35 |
| constantinople-005 | apache/deltaspike | 2 | 0 | 0 / 1 | 0 / 7 | 0 / 8 | 0 / 8 | 2 / 10 |
| constantinople-006 | apache/commons-configuration | 1 | 0 | 0 / 2 | 0 / 7 | 0 / 8 | 0 / 9 | 1 / 13 |
| constantinople-007 | apache/commons-dbcp | 4 | 2 | 0 / 10 | 0 / 12 | 0 / 24 | 0 / 25 | 3 / 30 |
| constantinople-008 | apache/commons-jcs | 1 | 0 | 0 / 6 | 0 / 14 | 0 / 20 | 0 / 21 | 1 / 22 |
| constantinople-009 | apache/systemml | 5 | 2 | 1 / 3 | 2 / 7 | 2 / 15 | 2 / 16 | 4 / 18 |

| 样本范围 | 组别 | 全部 FQN 命中 / 标签 | parent 已索引命中 / 已索引标签 | 候选总数 |
| --- | --- | ---: | ---: | ---: |
| 前三例 | JAR 一跳 | 1/11 | 1/7 | 17 |
| 前三例 | 加字段 | 4/11 | 4/7 | 31 |
| 前三例 | 加多跳 | 6/11 | 6/7 | 49 |
| 前三例 | 加两跳调用 | 6/11 | 6/7 | 50 |
| 前三例 | 加 diff 与重写 | 8/11 | 6/7 | 53 |
| 后七例 | JAR 一跳 | 2/15 | 2/6 | 30 |
| 后七例 | 加字段 | 3/15 | 3/6 | 59 |
| 后七例 | 加多跳 | 3/15 | 3/6 | 105 |
| 后七例 | 加两跳调用 | 4/15 | 4/6 | 127 |
| 后七例 | 加 diff 与重写 | 13/15 | 5/6 | 141 |
| 全部十例 | JAR 一跳 | 3/26 | 3/13 | 47 |
| 全部十例 | 加字段 | 7/26 | 7/13 | 90 |
| 全部十例 | 加多跳 | 9/26 | 9/13 | 154 |
| 全部十例 | 加两跳调用 | 10/26 | 10/13 | 177 |
| 全部十例 | 加 diff 与重写 | 21/26 | 11/13 | 194 |

两跳调用在 003 找回 `VfsResource.normalize(String)`。新增调用签名推断、字段写入和重写关系再补回 11 个标签。000–009 都曾用于分析或设计当前规则，独立对照见 [20 例静态结果](twenty-case-static.md)。

009 的 parent 归档含一个脚本测试目录的符号链接。提取时跳过了该链接，Java 源目录中的链接仍会触发显式检查。

## SP／MA 逐案例比较

每格依次列三次运行的“FQN 命中数 / 输出数”。模型表保留当时的原始候选与加多跳候选对照。最新静态组尚未接入这次模型对照。

| 样本 | 标签数 | SP 原始 | SP 多跳 | MA 原始 | MA 多跳 |
| --- | ---: | --- | --- | --- | --- |
| constantinople-000 | 1 | 1/1, 1/1, 1/1 | 1/1, 1/1, 1/1 | 0/0, 0/0, 0/0 | 0/1, 0/0, 0/0 |
| constantinople-001 | 6 | 0/0, 0/0, 0/0 | 3/4, 2/4, 2/4 | 1/2, 1/2, 2/3 | 4/4, 4/4, 4/4 |
| constantinople-002 | 4 | 0/1, 0/0, 0/0 | 2/3, 2/3, 2/3 | 2/3, 1/2, 0/0 | 3/5, 4/5, 3/4 |
| constantinople-003 | 1 | 1/1, 1/1, 1/1 | 1/1, 1/1, 1/1 | 1/1, 1/2, 1/1 | 1/1, 1/1, 1/1 |
| constantinople-004 | 1 | 1/2, 1/2, 1/2 | 1/2, 1/2, 1/2 | 1/4, 1/7, 1/2 | 1/1, 1/7, 1/2 |
| constantinople-005 | 2 | 0/1, 0/1, 0/1 | 0/1, 0/1, 0/1 | 0/1, 0/1, 0/0 | 0/1, 0/2, 0/2 |
| constantinople-006 | 1 | 0/1, 0/1, 0/1 | 0/3, 0/2, 0/2 | 0/0, 1/1, 1/1 | 1/1, 1/1, 0/1 |
| constantinople-007 | 4 | 1/1, 1/1, 1/1 | 1/1, 1/1, 1/1 | 3/5, 3/4, 1/1 | 3/5, 3/6, 3/3 |
| constantinople-008 | 1 | 1/1, 1/1, 1/1 | 1/1, 1/1, 1/1 | 1/3, 1/3, 1/3 | 1/4, 1/3, 1/3 |
| constantinople-009 | 5 | 1/2, 0/1, 0/1 | 2/2, 2/2, 2/2 | 1/1, 3/3, 2/3 | 4/9, 2/5, 4/10 |

每项指标先取单案例三次运行的中位数，再对案例作宏平均。

| 范围 | 模型阶段 | 候选组 | FQN P / R / F1 | CE P / R / F1 |
| --- | --- | --- | --- | --- |
| 前三例 | SP | baseline | 33.3% / 33.3% / 33.3% | 33.3% / 33.3% / 33.3% |
| 前三例 | SP | multihop | 72.2% / 61.1% / 65.7% | 83.3% / 68.9% / 74.8% |
| 前三例 | MA | baseline | 33.3% / 13.9% / 19.4% | 50.0% / 17.8% / 26.2% |
| 前三例 | MA | multihop | 58.3% / 47.2% / 51.7% | 66.7% / 53.3% / 58.3% |
| 后七例 | SP | baseline | 50.0% / 46.4% / 43.8% | 50.0% / 46.4% / 43.8% |
| 后七例 | SP | multihop | 64.3% / 52.1% / 52.0% | 64.3% / 52.1% / 52.0% |
| 后七例 | MA | baseline | 61.9% / 73.6% / 58.1% | 61.9% / 73.6% / 58.1% |
| 后七例 | MA | multihop | 54.8% / 79.3% / 62.4% | 56.2% / 79.3% / 63.6% |
| 全部十例 | SP | baseline | 45.0% / 42.5% / 40.7% | 45.0% / 42.5% / 40.7% |
| 全部十例 | SP | multihop | 66.7% / 54.8% / 56.1% | 70.0% / 57.2% / 58.8% |
| 全部十例 | MA | baseline | 53.3% / 55.7% / 46.5% | 58.3% / 56.8% / 48.5% |
| 全部十例 | MA | multihop | 55.8% / 69.7% / 59.2% | 59.3% / 71.5% / 62.0% |

## 逐实体命中和误报

按 FQN 核对。模型列中的数字为三次中命中的次数。各案例的静态 JSON 包含完整候选与扩展证据。

### constantinople-000 · apache/commons-math

[静态候选和源码路径](../results/static-seed-diff/constantinople-000.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.commons.math3.optimization.univariate.BrentOptimizer.doOptimize()` | ✓/✓/✓/✓/✓ | 3/3 | 0/0 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.commons.math3.optim.nonlinear.scalar.noderiv.BrentOptimizer` | 0/0 | 0/1 |

### constantinople-001 · apache/commons-io

[静态候选和源码路径](../results/static-seed-diff/constantinople-001.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.commons.io.input.CharSequenceInputStream.CharSequenceInputStream(java.lang.CharSequence,java.nio.charset.Charset,int)` | —/✓/✓/✓/✓ | 0/0 | 0/0 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark` | —/✓/✓/✓/✓ | 0/0 | 0/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark(int)` | —/✓/✓/✓/✓ | 0/1 | 2/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_bbuf` | —/—/—/—/✓ | 0/3 | 1/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_cbuf` | —/—/—/—/✓ | 0/3 | 1/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.skip(long)` | —/—/—/—/— | 0/0 | 0/0 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.commons.io.input.CharSequenceInputStream` | 0/0 | 2/0 |
| `org.apache.commons.io.input.CharSequenceInputStream.fillBuffer()` | 0/3 | 0/0 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark()` | 0/0 | 1/0 |
| `org.apache.commons.io.input.CharSequenceInputStream.read()` | 0/2 | 0/0 |

### constantinople-002 · apache/commons-net

[静态候选和源码路径](../results/static-seed-diff/constantinople-002.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.REGEX` | —/—/✓/✓/✓ | 0/3 | 0/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig)` | —/—/✓/✓/✓ | 0/3 | 2/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig,boolean)` | —/—/—/—/— | 0/0 | 0/1 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.trimLeadingSpaces` | —/—/—/—/— | 0/0 | 1/3 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser` | 1/0 | 0/0 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser()` | 0/3 | 2/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig, boolean)` | 0/0 | 0/1 |

### constantinople-003 · apache/ant-ivy

[静态候选和源码路径](../results/static-seed-diff/constantinople-003.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `fr.jayasoft.ivy.repository.vfs.VfsResource.normalize(java.lang.String)` | —/—/—/✓/✓ | 3/3 | 3/3 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `fr.jayasoft.ivy.repository.vfs.VfsRepository` | 0/0 | 1/0 |

### constantinople-004 · apache/ant-ivy

[静态候选和源码路径](../results/static-seed-diff/constantinople-004.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.ivy.core.resolve.ResolveEngine.computeConflicts(org.apache.ivy.core.resolve.VisitNode,org.apache.ivy.core.resolve.VisitNode,java.lang.String,java.util.Collection,java.util.Collection)` | ✓/✓/✓/✓/✓ | 3/3 | 3/3 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.ivy.core.resolve.IvyNode.IvyNode(org.apache.ivy.core.resolve.ResolveData,org.apache.ivy.core.resolve.IvyNode,org.apache.ivy.core.module.descriptor.DependencyDescriptor)` | 0/0 | 0/1 |
| `org.apache.ivy.core.resolve.IvyNode.addRootModuleConf(java.lang.String)` | 0/0 | 0/1 |
| `org.apache.ivy.core.resolve.IvyNode.addRootModuleConfig(java.lang.String)` | 0/0 | 1/0 |
| `org.apache.ivy.core.resolve.IvyNode.getAllConfigurations` | 0/0 | 1/0 |
| `org.apache.ivy.core.resolve.IvyNode.getDependencies(java.lang.String)` | 0/0 | 1/0 |
| `org.apache.ivy.core.resolve.IvyNode.getDependencies(java.lang.String,java.lang.String,java.lang.String)` | 3/3 | 3/1 |
| `org.apache.ivy.core.resolve.IvyNode.getRealConfs` | 0/0 | 1/0 |
| `org.apache.ivy.core.resolve.IvyNode.loadData(java.lang.String,org.apache.ivy.core.resolve.IvyNode,java.lang.String,java.lang.String,boolean,org.apache.ivy.core.resolve.IvyNodeUsage)` | 0/0 | 0/1 |
| `org.apache.ivy.core.resolve.IvyNode.moveToRealNode(java.lang.String,org.apache.ivy.core.resolve.IvyNode,java.lang.String,java.lang.String,boolean,org.apache.ivy.core.resolve.IvyNode)` | 0/0 | 0/1 |
| `org.apache.ivy.core.resolve.IvyNodeUsage` | 0/0 | 0/1 |
| `org.apache.ivy.core.resolve.ResolveEngine` | 0/0 | 1/0 |
| `org.apache.ivy.core.resolve.ResolveEngine.resolve(org.apache.ivy.core.resolve.ResolveOptions)` | 0/0 | 1/0 |
| `org.apache.ivy.core.resolve.VisitNode` | 0/0 | 1/1 |

### constantinople-005 · apache/deltaspike

[静态候选和源码路径](../results/static-seed-diff/constantinople-005.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.deltaspike.data.impl.util.QueryUtils.nullSafeValue(java.lang.String)` | —/—/—/—/✓ | 0/0 | 0/0 |
| `org.apache.deltaspike.data.impl.util.QueryUtils.nullSafeValue(java.lang.String,java.lang.String)` | —/—/—/—/✓ | 0/0 | 0/0 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.deltaspike.data.impl.builder.postprocessor.CountQueryPostProcessor.QueryExtraction.nullSafeValue` | 0/0 | 1/1 |
| `org.apache.deltaspike.data.impl.builder.postprocessor.CountQueryPostProcessor.QueryExtraction.nullSafeValue(...)` | 0/0 | 1/0 |
| `org.apache.deltaspike.data.impl.builder.postprocessor.CountQueryPostProcessor.QueryExtraction.nullSafeValue(String)` | 0/0 | 0/1 |
| `org.apache.deltaspike.data.impl.builder.postprocessor.CountQueryPostProcessor.QueryExtraction.nullSafeValue(String, String)` | 0/0 | 0/1 |
| `org.apache.deltaspike.data.impl.builder.postprocessor.CountQueryPostProcessor.QueryExtraction.nullSafeValue(java.lang.String)` | 2/3 | 0/1 |
| `org.apache.deltaspike.data.impl.builder.postprocessor.CountQueryPostProcessor.QueryExtraction.nullSafeValue(java.lang.String, java.lang.String)` | 0/0 | 0/1 |
| `org.apache.deltaspike.data.impl.builder.postprocessor.CountQueryPostProcessor.QueryExtraction.rewriteToCount()` | 1/0 | 0/0 |

### constantinople-006 · apache/commons-configuration

[静态候选和源码路径](../results/static-seed-diff/constantinople-006.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.commons.configuration2.interpol.ConfigurationInterpolator.registerLocalLookups(org.apache.commons.configuration2.interpol.ConfigurationInterpolator)` | —/—/—/—/✓ | 0/0 | 2/2 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `[]` | 0/0 | 0/1 |
| `org.apache.commons.configuration2.AbstractConfiguration.interpolate(java.lang.Object)` | 2/1 | 0/0 |
| `org.apache.commons.configuration2.SubsetConfiguration.SubsetConfiguration(org.apache.commons.configuration2.Configuration,java.lang.String)` | 1/3 | 0/0 |
| `org.apache.commons.configuration2.SubsetConfiguration.SubsetConfiguration(org.apache.commons.configuration2.Configuration,java.lang.String,java.lang.String)` | 0/3 | 0/0 |

### constantinople-007 · apache/commons-dbcp

[静态候选和源码路径](../results/static-seed-diff/constantinople-007.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.commons.dbcp2.BasicDataSource.createConnectionPool(org.apache.commons.dbcp2.PoolableConnectionFactory)` | —/—/—/—/— | 0/0 | 0/0 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.getConnectionIndex()` | —/—/—/—/✓ | 0/0 | 2/3 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.getDataSourceJmxName()` | —/—/—/—/✓ | 0/0 | 2/3 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.makeObject()` | —/—/—/—/✓ | 3/3 | 3/3 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.commons.dbcp2.Constants` | 0/0 | 1/0 |
| `org.apache.commons.dbcp2.Constants.JMX_CONNECTION_BASE_EXT` | 0/0 | 1/2 |
| `org.apache.commons.dbcp2.Constants.JMX_STATEMENT_POOL_PREFIX` | 0/0 | 1/2 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory._connectionIndex` | 0/0 | 0/1 |

### constantinople-008 · apache/commons-jcs

[静态候选和源码路径](../results/static-seed-diff/constantinople-008.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.calculateByteOffsetForBlockAsLong(int)` | —/—/—/—/✓ | 3/3 | 3/3 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.calculateByteOffsetForBlock(int)` | 0/0 | 3/3 |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.putBytes` | 0/0 | 0/1 |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.read(int[])` | 0/0 | 3/3 |

### constantinople-009 · apache/systemml

[静态候选和源码路径](../results/static-seed-diff/constantinople-009.json)

| 受影响实体 | 静态原始／字段／多跳／两跳／diff 与重写 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- | --- |
| `org.apache.sysml.conf.DMLConfig._document` | —/—/—/—/✓ | 0/3 | 2/3 |
| `org.apache.sysml.conf.DMLConfig._documentBuilder` | —/—/—/—/— | 0/0 | 0/0 |
| `org.apache.sysml.conf.DMLConfig.getDocumentBuilder()` | —/—/—/—/✓ | 0/3 | 3/3 |
| `org.apache.sysml.conf.DMLConfig.parseConfig()` | —/✓/✓/✓/✓ | 0/0 | 0/2 |
| `org.apache.sysml.conf.DMLConfig.setTextValue(org.w3c.dom.Element,java.lang.String,java.lang.String)` | ✓/✓/✓/✓/✓ | 1/0 | 1/2 |

| 模型额外输出 | SP 原始／多跳 | MA 原始／多跳 |
| --- | --- | --- |
| `org.apache.sysml.api.mlcontext.MLContext.setConfigProperty(java.lang.String,java.lang.String)` | 3/0 | 0/0 |
| `org.apache.sysml.conf.DMLConfig.DMLConfig()` | 0/0 | 1/0 |
| `org.apache.sysml.conf.DMLConfig.DMLConfig(java.lang.String)` | 0/0 | 0/2 |
| `org.apache.sysml.conf.DMLConfig.DMLConfig(java.lang.String,boolean)` | 0/0 | 0/2 |
| `org.apache.sysml.conf.DMLConfig.DMLConfig(org.w3c.dom.Element)` | 0/0 | 0/3 |
| `org.apache.sysml.conf.DMLConfig.clone()` | 0/0 | 0/3 |
| `org.apache.sysml.conf.DMLConfig.parseDMLConfig(java.lang.String)` | 0/0 | 0/3 |
| `org.apache.sysml.conf.DMLConfig.readConfigurationFile(java.lang.String)` | 0/0 | 0/1 |

## 复跑

```bash
python src/static_compare.py --seed-diff-overlay --cross-class-calls --rows 0,1,2,3,4,5,6,7,8,9
python src/compare_ten.py --env-file ../work/ripple/.env.ripple100
python src/report_ten.py
```
