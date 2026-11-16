# 20 个案例的静态候选对照

000–009 是用于分析规则的原 10 例。010–019 是 Constantinople 按原顺序选取的下一批 10 例，沿用同一套静态规则。完整 FQN 命中包含对新增实体的签名推断。

## 汇总

| 范围 | 静态组 | FQN 命中 / 标签 | 召回率 | 候选总数 |
| --- | --- | ---: | ---: | ---: |
| 000–009 | 作者 JAR | 3 / 26 | 11.5% | 47 |
| 000–009 | 加字段 | 7 / 26 | 26.9% | 90 |
| 000–009 | 加多跳 | 9 / 26 | 34.6% | 154 |
| 000–009 | 加两跳调用 | 10 / 26 | 38.5% | 177 |
| 000–009 | 加 diff 与重写 | 21 / 26 | 80.8% | 194 |
| 010–019 | 作者 JAR | 5 / 39 | 12.8% | 71 |
| 010–019 | 加字段 | 6 / 39 | 15.4% | 101 |
| 010–019 | 加多跳 | 7 / 39 | 17.9% | 129 |
| 010–019 | 加两跳调用 | 7 / 39 | 17.9% | 156 |
| 010–019 | 加 diff 与重写 | 10 / 39 | 25.6% | 165 |
| 全部 20 例 | 作者 JAR | 8 / 65 | 12.3% | 118 |
| 全部 20 例 | 加字段 | 13 / 65 | 20.0% | 191 |
| 全部 20 例 | 加多跳 | 16 / 65 | 24.6% | 283 |
| 全部 20 例 | 加两跳调用 | 17 / 65 | 26.2% | 333 |
| 全部 20 例 | 加 diff 与重写 | 31 / 65 | 47.7% | 359 |

统计按实体累加得出。下表每格为命中数 / 候选数。

## 逐案例对照

| 案例 | 仓库 | 标签 | 作者 JAR | 加字段 | 加多跳 | 加两跳调用 | 加 diff 与重写 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [000](../results/static-seed-diff/constantinople-000.json) | apache/commons-math | 1 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 2 | 1 / 2 |
| [001](../results/static-seed-diff/constantinople-001.json) | apache/commons-io | 6 | 0 / 0 | 3 / 7 | 3 / 11 | 3 / 11 | 5 / 14 |
| [002](../results/static-seed-diff/constantinople-002.json) | apache/commons-net | 4 | 0 / 15 | 0 / 22 | 2 / 36 | 2 / 37 | 2 / 37 |
| [003](../results/static-seed-diff/constantinople-003.json) | apache/ant-ivy | 1 | 0 / 3 | 0 / 3 | 0 / 9 | 1 / 13 | 1 / 13 |
| [004](../results/static-seed-diff/constantinople-004.json) | apache/ant-ivy | 1 | 1 / 5 | 1 / 9 | 1 / 21 | 1 / 35 | 1 / 35 |
| [005](../results/static-seed-diff/constantinople-005.json) | apache/deltaspike | 2 | 0 / 1 | 0 / 7 | 0 / 8 | 0 / 8 | 2 / 10 |
| [006](../results/static-seed-diff/constantinople-006.json) | apache/commons-configuration | 1 | 0 / 2 | 0 / 7 | 0 / 8 | 0 / 9 | 1 / 13 |
| [007](../results/static-seed-diff/constantinople-007.json) | apache/commons-dbcp | 4 | 0 / 10 | 0 / 12 | 0 / 24 | 0 / 25 | 3 / 30 |
| [008](../results/static-seed-diff/constantinople-008.json) | apache/commons-jcs | 1 | 0 / 6 | 0 / 14 | 0 / 20 | 0 / 21 | 1 / 22 |
| [009](../results/static-seed-diff/constantinople-009.json) | apache/systemml | 5 | 1 / 3 | 2 / 7 | 2 / 15 | 2 / 16 | 4 / 18 |
| [010](../results/static-seed-diff/constantinople-010.json) | apache/ant-ivy | 5 | 1 / 16 | 1 / 16 | 2 / 30 | 2 / 37 | 2 / 39 |
| [011](../results/static-seed-diff/constantinople-011.json) | apache/commons-net | 2 | 0 / 1 | 0 / 8 | 0 / 8 | 0 / 8 | 1 / 9 |
| [012](../results/static-seed-diff/constantinople-012.json) | apache/ant-ivy | 3 | 1 / 8 | 1 / 13 | 1 / 13 | 1 / 14 | 1 / 14 |
| [013](../results/static-seed-diff/constantinople-013.json) | apache/ant-ivy | 1 | 0 / 4 | 0 / 6 | 0 / 7 | 0 / 7 | 0 / 8 |
| [014](../results/static-seed-diff/constantinople-014.json) | apache/commons-configuration | 1 | 0 / 3 | 0 / 8 | 0 / 11 | 0 / 12 | 0 / 14 |
| [015](../results/static-seed-diff/constantinople-015.json) | apache/parquet-mr | 1 | 0 / 4 | 1 / 6 | 1 / 11 | 1 / 14 | 1 / 14 |
| [016](../results/static-seed-diff/constantinople-016.json) | apache/commons-net | 12 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 |
| [017](../results/static-seed-diff/constantinople-017.json) | apache/commons-math | 1 | 0 / 5 | 0 / 8 | 0 / 12 | 0 / 20 | 0 / 21 |
| [018](../results/static-seed-diff/constantinople-018.json) | apache/opennlp | 12 | 1 / 17 | 1 / 18 | 1 / 18 | 1 / 19 | 3 / 21 |
| [019](../results/static-seed-diff/constantinople-019.json) | apache/ant-ivy | 1 | 0 / 11 | 0 / 16 | 0 / 17 | 0 / 23 | 0 / 23 |

## SP／MA 逐案例对照

两组均使用最新静态候选、`deepseek-v4.1-flash-1017`、温度 0，每例重复 3 次。SP 单次调用，MA 三个阶段。每格依次列三次运行的 FQN 命中数 / 输出数。

已完成的预测轮次为 SP 60/60、MA 60/60。短横线表示未完成的运行。

| 案例 | 标签数 | 最新静态命中 | SP 三次 | MA 三次 |
| --- | ---: | ---: | --- | --- |
| 000 | 1 | 1 | 1/1, 1/1, 1/1 | 0/0, 0/0, 0/0 |
| 001 | 6 | 5 | 3/4, 1/2, 1/2 | 4/4, 2/2, 4/4 |
| 002 | 4 | 2 | 1/2, 0/0, 0/0 | 3/6, 3/4, 3/6 |
| 003 | 1 | 1 | 1/2, 1/2, 1/2 | 0/1, 0/1, 0/1 |
| 004 | 1 | 1 | 1/6, 1/6, 1/6 | 1/6, 1/6, 1/11 |
| 005 | 2 | 2 | 2/2, 2/2, 2/2 | 0/0, 2/2, 0/0 |
| 006 | 1 | 1 | 0/2, 0/2, 0/2 | 0/0, 1/3, 0/0 |
| 007 | 4 | 3 | 1/1, 1/1, 1/1 | 0/0, 1/1, 3/5 |
| 008 | 1 | 1 | 0/1, 0/1, 0/1 | 1/2, 1/5, 1/2 |
| 009 | 5 | 4 | 3/10, 3/10, 3/10 | 2/4, 4/8, 3/6 |
| 010 | 5 | 2 | 0/4, 0/2, 0/5 | 1/3, 2/4, 0/6 |
| 011 | 2 | 1 | 1/1, 1/1, 1/1 | 2/2, 2/2, 2/2 |
| 012 | 3 | 1 | 1/2, 1/2, 1/2 | 2/3, 2/3, 2/3 |
| 013 | 1 | 0 | 0/4, 0/4, 0/4 | 0/1, 0/1, 0/1 |
| 014 | 1 | 0 | 0/1, 0/1, 0/1 | 0/1, 0/1, 0/0 |
| 015 | 1 | 1 | 0/0, 0/0, 0/0 | 0/0, 0/0, 0/0 |
| 016 | 12 | 2 | 2/2, 2/2, 2/2 | 2/2, 2/2, 2/2 |
| 017 | 1 | 0 | 1/3, 1/3, 1/3 | 1/1, 1/1, 1/1 |
| 018 | 12 | 3 | 2/2, 2/2, 2/2 | 2/2, 2/2, 2/2 |
| 019 | 1 | 0 | 0/1, 0/1, 0/1 | 0/0, 0/2, 0/1 |

模型指标只使用三次均完成的案例，先取每例中位数，再跨案例取宏平均。P、R、F1 分别为精确率、召回率和 F1。覆盖案例数不同的行仅作进度记录。

| 范围 | 阶段 | 完整案例 | FQN P / R / F1 | CE P / R / F1 |
| --- | --- | ---: | --- | --- |
| 000–009 | 最新静态候选 | 10/10 | 16.6% / 88.8% / 25.5% | 16.6% / 90.2% / 25.2% |
| 000–009 | SP | 10/10 | 44.7% / 50.2% / 40.0% | 45.4% / 50.5% / 41.0% |
| 000–009 | MA | 10/10 | 32.7% / 42.7% / 33.0% | 35.2% / 44.5% / 35.0% |
| 010–019 | 最新静态候选 | 10/10 | 14.5% / 26.5% / 9.9% | 14.5% / 26.5% / 9.9% |
| 010–019 | SP | 10/10 | 38.3% / 21.7% / 21.4% | 43.3% / 25.0% / 25.4% |
| 010–019 | MA | 10/10 | 50.0% / 32.0% / 34.9% | 53.3% / 32.0% / 36.2% |
| 全部 20 例 | 最新静态候选 | 20/20 | 15.5% / 57.7% / 17.7% | 15.5% / 58.3% / 17.5% |
| 全部 20 例 | SP | 20/20 | 41.5% / 35.9% / 30.7% | 44.4% / 37.8% / 33.2% |
| 全部 20 例 | MA | 20/20 | 41.3% / 37.3% / 33.9% | 44.2% / 38.2% / 35.6% |

## 模型逐实体命中、漏报和误报

每列用 n/m 记录该实体在 m 次已完成运行中的出现次数。短横线表示该方法没有已完成的运行。额外输出按严格 FQN 计。

### constantinople-000

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.math3.optimization.univariate.BrentOptimizer.doOptimize()` | 受影响 | 是 | 3/3 | 0/3 |

### constantinople-001

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.io.input.CharSequenceInputStream.CharSequenceInputStream(java.lang.CharSequence,java.nio.charset.Charset,int)` | 受影响 | 是 | 0/3 | 0/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark` | 受影响 | 是 | 0/3 | 3/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark(int)` | 受影响 | 是 | 3/3 | 3/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_bbuf` | 受影响 | 是 | 1/3 | 2/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_cbuf` | 受影响 | 是 | 1/3 | 2/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.skip(long)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.io.input.CharSequenceInputStream.fillBuffer()` | 额外输出 | 是 | 3/3 | 0/3 |

### constantinople-002

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.REGEX` | 受影响 | 是 | 0/3 | 3/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig)` | 受影响 | 是 | 1/3 | 3/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig,boolean)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.trimLeadingSpaces` | 受影响 | 否 | 0/3 | 3/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser()` | 额外输出 | 是 | 1/3 | 3/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig, boolean)` | 额外输出 | 否 | 0/3 | 2/3 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.setTrimLeadingSpaces(boolean)` | 额外输出 | 否 | 0/3 | 2/3 |

### constantinople-003

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `fr.jayasoft.ivy.repository.vfs.VfsResource.normalize(java.lang.String)` | 受影响 | 是 | 3/3 | 0/3 |
| `fr.jayasoft.ivy.repository.vfs.VfsRepository` | 额外输出 | 否 | 0/3 | 1/3 |
| `fr.jayasoft.ivy.repository.vfs.VfsRepository.getVFSManager()` | 额外输出 | 是 | 3/3 | 0/3 |
| `fr.jayasoft.ivy.repository.vfs.VfsResource.getChildren()` | 额外输出 | 是 | 0/3 | 2/3 |

### constantinople-004

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.ivy.core.resolve.ResolveEngine.computeConflicts(org.apache.ivy.core.resolve.VisitNode,org.apache.ivy.core.resolve.VisitNode,java.lang.String,java.util.Collection,java.util.Collection)` | 受影响 | 是 | 3/3 | 3/3 |
| `org.apache.ivy.core.resolve.IvyNode.addCaller(java.lang.String,org.apache.ivy.core.resolve.IvyNode,java.lang.String,java.lang.String,java.lang.String[],org.apache.ivy.core.module.descriptor.DependencyDescriptor)` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.ivy.core.resolve.IvyNode.addRootModuleConfigurations(org.apache.ivy.core.resolve.IvyNodeUsage,java.lang.String,java.lang.String[])` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.ivy.core.resolve.IvyNode.confsToFetch` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.ivy.core.resolve.IvyNode.getDependencies(java.lang.String,java.lang.String,java.lang.String)` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.ivy.core.resolve.IvyNode.loadData(java.lang.String,org.apache.ivy.core.resolve.IvyNode,java.lang.String,java.lang.String,boolean,org.apache.ivy.core.resolve.IvyNodeUsage)` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.ivy.core.resolve.IvyNode.moveToRealNode(java.lang.String,org.apache.ivy.core.resolve.IvyNode,java.lang.String,java.lang.String,boolean,org.apache.ivy.core.resolve.IvyNode)` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.ivy.core.resolve.IvyNode.resolveSpecialConfigurations(java.lang.String[])` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.ivy.core.resolve.IvyNode.updateConfsToFetch(java.util.Collection)` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.ivy.core.resolve.IvyNodeUsage.setRequiredConfs(org.apache.ivy.core.resolve.IvyNode,java.lang.String,java.util.Collection)` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.ivy.core.resolve.VisitNode` | 额外输出 | 否 | 0/3 | 1/3 |

### constantinople-005

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.deltaspike.data.impl.util.QueryUtils.nullSafeValue(java.lang.String)` | 受影响 | 是 | 3/3 | 1/3 |
| `org.apache.deltaspike.data.impl.util.QueryUtils.nullSafeValue(java.lang.String,java.lang.String)` | 受影响 | 是 | 3/3 | 1/3 |

### constantinople-006

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.configuration2.interpol.ConfigurationInterpolator.registerLocalLookups(org.apache.commons.configuration2.interpol.ConfigurationInterpolator)` | 受影响 | 是 | 0/3 | 1/3 |
| `org.apache.commons.configuration2.AbstractConfiguration.getInterpolator()` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.commons.configuration2.SubsetConfiguration.SubsetConfiguration(org.apache.commons.configuration2.Configuration,java.lang.String)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.commons.configuration2.SubsetConfiguration.SubsetConfiguration(org.apache.commons.configuration2.Configuration,java.lang.String,java.lang.String)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.commons.configuration2.SubsetConfiguration.getInterpolator()` | 额外输出 | 是 | 0/3 | 1/3 |

### constantinople-007

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.dbcp2.BasicDataSource.createConnectionPool(org.apache.commons.dbcp2.PoolableConnectionFactory)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.getConnectionIndex()` | 受影响 | 是 | 0/3 | 1/3 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.getDataSourceJmxName()` | 受影响 | 是 | 0/3 | 1/3 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.makeObject()` | 受影响 | 是 | 3/3 | 2/3 |
| `org.apache.commons.dbcp2.Constants.JMX_CONNECTION_BASE_EXT` | 额外输出 | 否 | 0/3 | 1/3 |
| `org.apache.commons.dbcp2.Constants.JMX_STATEMENT_POOL_PREFIX` | 额外输出 | 否 | 0/3 | 1/3 |

### constantinople-008

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.calculateByteOffsetForBlockAsLong(int)` | 受影响 | 是 | 0/3 | 3/3 |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.allocateBlocks(int)` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.calculateByteOffsetForBlock(int)` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.putBytes` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.read(int[])` | 额外输出 | 是 | 0/3 | 1/3 |

### constantinople-009

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.sysml.conf.DMLConfig._document` | 受影响 | 是 | 3/3 | 3/3 |
| `org.apache.sysml.conf.DMLConfig._documentBuilder` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.sysml.conf.DMLConfig.getDocumentBuilder()` | 受影响 | 是 | 3/3 | 3/3 |
| `org.apache.sysml.conf.DMLConfig.parseConfig()` | 受影响 | 是 | 3/3 | 2/3 |
| `org.apache.sysml.conf.DMLConfig.setTextValue(org.w3c.dom.Element,java.lang.String,java.lang.String)` | 受影响 | 是 | 0/3 | 1/3 |
| `org.apache.sysml.api.mlcontext.MLContext.setConfigProperty(java.lang.String,java.lang.String)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.sysml.conf.DMLConfig.DMLConfig(java.lang.String)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.sysml.conf.DMLConfig.DMLConfig(java.lang.String,boolean)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.sysml.conf.DMLConfig.DMLConfig(org.w3c.dom.Element)` | 额外输出 | 是 | 3/3 | 2/3 |
| `org.apache.sysml.conf.DMLConfig.clone()` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.sysml.conf.DMLConfig.parseDMLConfig(java.lang.String)` | 额外输出 | 是 | 3/3 | 2/3 |
| `org.apache.sysml.conf.DMLConfig.readConfigurationFile(java.lang.String)` | 额外输出 | 是 | 3/3 | 2/3 |

### constantinople-010

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.MAX_CREDENTILAS_CACHE_SIZE` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.credentialsCache` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.parseURI(java.lang.String)` | 受影响 | 是 | 0/3 | 2/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.requestCredentials(java.lang.String)` | 受影响 | 否 | 0/3 | 1/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.user` | 受影响 | 是 | 0/3 | 0/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.getUser()` | 额外输出 | 是 | 2/3 | 0/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.getUserPassword()` | 额外输出 | 是 | 1/3 | 0/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.setUser(java.lang.String)` | 额外输出 | 是 | 1/3 | 0/3 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.setUserPassword(java.lang.String)` | 额外输出 | 是 | 1/3 | 0/3 |
| `org.apache.ivy.plugins.repository.ssh.SshCache.CfUserInfo.CfUserInfo(java.lang.String,java.lang.String,java.lang.String,java.io.File,java.lang.String,java.io.File)` | 额外输出 | 是 | 0/3 | 2/3 |
| `org.apache.ivy.plugins.repository.ssh.SshCache.Entry.getSession()` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.ivy.plugins.repository.ssh.SshCache.getSession(java.lang.String,int,java.lang.String,java.lang.String,java.io.File,java.lang.String,java.io.File)` | 额外输出 | 是 | 3/3 | 3/3 |
| `org.apache.ivy.plugins.repository.ssh.SshCache.requestCredentials(java.lang.String)` | 额外输出 | 是 | 3/3 | 2/3 |
| `org.apache.ivy.util.Credentials` | 额外输出 | 否 | 0/3 | 1/3 |
| `org.apache.ivy.util.Message.requestCredentials(java.lang.String)` | 额外输出 | 是 | 0/3 | 1/3 |

### constantinople-011

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.net.smtp.SimpleSMTPHeader.addHeaderField(java.lang.String,java.lang.String)` | 受影响 | 是 | 3/3 | 3/3 |
| `org.apache.commons.net.smtp.SimpleSMTPHeader.hasHeaderDate` | 受影响 | 否 | 0/3 | 3/3 |

### constantinople-012

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.ivy.util.XMLHelper.parse(java.net.URL,java.net.URL,org.xml.sax.helpers.DefaultHandler,org.xml.sax.ext.LexicalHandler)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.ivy.util.XMLHelper.parseToDom(java.io.InputStream,org.apache.ivy.plugins.repository.Resource,org.xml.sax.EntityResolver)` | 受影响 | 是 | 0/3 | 3/3 |
| `org.apache.ivy.util.XMLHelper.toSystemId(java.net.URL)` | 受影响 | 否 | 3/3 | 3/3 |
| `org.apache.ivy.util.XMLHelper.parseToDom(org.xml.sax.InputSource,org.xml.sax.EntityResolver)` | 额外输出 | 否 | 3/3 | 3/3 |

### constantinople-013

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.ivy.core.cache.DefaultResolutionCacheManager.clean()` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.ivy.core.cache.DefaultResolutionCacheManager.getConfigurationResolveReportInCache(java.lang.String,java.lang.String)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.ivy.core.cache.DefaultResolutionCacheManager.getConfigurationResolveReportsInCache(java.lang.String)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.ivy.core.cache.DefaultResolutionCacheManager.getResolvedIvyFileInCache(org.apache.ivy.core.module.id.ModuleRevisionId)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.ivy.core.cache.DefaultResolutionCacheManager.getResolvedIvyPropertiesInCache(org.apache.ivy.core.module.id.ModuleRevisionId)` | 额外输出 | 是 | 3/3 | 0/3 |
| `org.apache.ivy.plugins.report.XmlReportOutputter.output(org.apache.ivy.core.report.ConfigurationResolveReport, java.lang.String, java.lang.String[], org.apache.ivy.core.cache.ResolutionCacheManager)` | 额外输出 | 否 | 0/3 | 3/3 |

### constantinople-014

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.configuration.CompositeConfiguration.appendListProperty(java.util.List,org.apache.commons.configuration.Configuration,java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.configuration.ConfigurationUtils.appendListProperty(java.util.List,org.apache.commons.configuration.Configuration,java.lang.String)` | 额外输出 | 是 | 3/3 | 2/3 |

### constantinople-015

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.parquet.proto.ProtoWriteSupport.MessageWriter.MessageWriter(com.google.protobuf.Descriptors.Descriptor,org.apache.parquet.schema.GroupType)` | 受影响 | 是 | 0/3 | 0/3 |

### constantinople-016

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.net.imap.IMAPClient.append(java.lang.String,java.lang.String,java.lang.String,java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.copy(java.lang.String,java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.create(java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.delete(java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.examine(java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.list(java.lang.String,java.lang.String)` | 受影响 | 是 | 3/3 | 3/3 |
| `org.apache.commons.net.imap.IMAPClient.lsub(java.lang.String,java.lang.String)` | 受影响 | 是 | 3/3 | 3/3 |
| `org.apache.commons.net.imap.IMAPClient.rename(java.lang.String,java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.select(java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.status(java.lang.String,java.lang.String[])` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.subscribe(java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.commons.net.imap.IMAPClient.unsubscribe(java.lang.String)` | 受影响 | 否 | 0/3 | 0/3 |

### constantinople-017

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.commons.math3.optimization.linear.SimplexTableau.CUTOFF_THRESHOLD` | 受影响 | 否 | 3/3 | 3/3 |
| `org.apache.commons.math3.optimization.linear.SimplexTableau.getEntry(int,int)` | 额外输出 | 否 | 3/3 | 0/3 |
| `org.apache.commons.math3.optimization.linear.SimplexTableau.setEntry(int,int,double)` | 额外输出 | 否 | 3/3 | 0/3 |

### constantinople-018

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `opennlp.tools.util.featuregen.StringPattern.ALL_HIRAGANA` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.ALL_KATAKANA` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_COMMA` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_DIGIT` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_HYPHEN` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_LETTERS` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_PERIOD` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_SLASH` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_UPPERCASE` | 受影响 | 否 | 0/3 | 0/3 |
| `opennlp.tools.util.featuregen.StringPattern.isAllHiragana()` | 受影响 | 是 | 3/3 | 3/3 |
| `opennlp.tools.util.featuregen.StringPattern.isAllKatakana()` | 受影响 | 是 | 3/3 | 3/3 |
| `opennlp.tools.util.featuregen.StringPattern.recognize(java.lang.String)` | 受影响 | 是 | 0/3 | 0/3 |

### constantinople-019

| 实体 FQN | 数据集标签 | 在静态候选中 | SP | MA |
| --- | --- | --- | ---: | ---: |
| `org.apache.ivy.core.settings.XmlSettingsParser.classpathStarted(java.util.Map)` | 受影响 | 否 | 0/3 | 0/3 |
| `org.apache.ivy.core.settings.IvySettings.setSettingsVariables(java.io.File)` | 额外输出 | 是 | 0/3 | 1/3 |
| `org.apache.ivy.util.Checks.checkAbsolute(java.io.File, java.lang.String)` | 额外输出 | 否 | 3/3 | 1/3 |
| `org.apache.ivy.util.Checks.checkAbsolute(java.io.File,java.lang.String)` | 额外输出 | 否 | 0/3 | 1/3 |


## 新 10 例的命中和漏报

### constantinople-010 · When in ssh plugin we does not set username in scheme, Ivy always try to connect with guest username, even if we change one in panel.

| 类别 | 完整签名 |
| --- | --- |
| 两跳组已命中 | `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.parseURI(java.lang.String)` |
| 两跳组已命中 | `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.user` |
| 最新组仍漏报 | `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.MAX_CREDENTILAS_CACHE_SIZE` |
| 最新组仍漏报 | `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.credentialsCache` |
| 最新组仍漏报 | `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.requestCredentials(java.lang.String)` |

### constantinople-011 · SimpleSMTPHeader fails to supply the required Date: header

| 类别 | 完整签名 |
| --- | --- |
| diff 或重写补回 | `org.apache.commons.net.smtp.SimpleSMTPHeader.addHeaderField(java.lang.String,java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.smtp.SimpleSMTPHeader.hasHeaderDate` |

### constantinople-012 · Ivy default cache path with Umlauts lets it crash.

| 类别 | 完整签名 |
| --- | --- |
| 两跳组已命中 | `org.apache.ivy.util.XMLHelper.parseToDom(java.io.InputStream,org.apache.ivy.plugins.repository.Resource,org.xml.sax.EntityResolver)` |
| 最新组仍漏报 | `org.apache.ivy.util.XMLHelper.parse(java.net.URL,java.net.URL,org.xml.sax.helpers.DefaultHandler,org.xml.sax.ext.LexicalHandler)` |
| 最新组仍漏报 | `org.apache.ivy.util.XMLHelper.toSystemId(java.net.URL)` |

### constantinople-013 · NPE in XmlReportOutputter

| 类别 | 完整签名 |
| --- | --- |
| 最新组仍漏报 | `org.apache.ivy.core.cache.DefaultResolutionCacheManager.clean()` |

### constantinople-014 · ConfigurationConverter does not handle CompositeConfiguration correctly

| 类别 | 完整签名 |
| --- | --- |
| 最新组仍漏报 | `org.apache.commons.configuration.CompositeConfiguration.appendListProperty(java.util.List,org.apache.commons.configuration.Configuration,java.lang.String)` |

### constantinople-015 · Writing Protobuf messages with extensions results in an error or data corruption.

| 类别 | 完整签名 |
| --- | --- |
| 两跳组已命中 | `org.apache.parquet.proto.ProtoWriteSupport.MessageWriter.MessageWriter(com.google.protobuf.Descriptors.Descriptor,org.apache.parquet.schema.GroupType)` |

### constantinople-016 · IMAP fails to quote/encode mailbox names

| 类别 | 完整签名 |
| --- | --- |
| 两跳组已命中 | `org.apache.commons.net.imap.IMAPClient.list(java.lang.String,java.lang.String)` |
| 两跳组已命中 | `org.apache.commons.net.imap.IMAPClient.lsub(java.lang.String,java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.append(java.lang.String,java.lang.String,java.lang.String,java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.copy(java.lang.String,java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.create(java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.delete(java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.examine(java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.rename(java.lang.String,java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.select(java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.status(java.lang.String,java.lang.String[])` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.subscribe(java.lang.String)` |
| 最新组仍漏报 | `org.apache.commons.net.imap.IMAPClient.unsubscribe(java.lang.String)` |

### constantinople-017 · Not expected UnboundedSolutionException

| 类别 | 完整签名 |
| --- | --- |
| 最新组仍漏报 | `org.apache.commons.math3.optimization.linear.SimplexTableau.CUTOFF_THRESHOLD` |

### constantinople-018 · FeatureGeneratorUtil.tokenFeature() always returns "lc" for Japanese words

| 类别 | 完整签名 |
| --- | --- |
| 两跳组已命中 | `opennlp.tools.util.featuregen.StringPattern.recognize(java.lang.String)` |
| diff 或重写补回 | `opennlp.tools.util.featuregen.StringPattern.isAllHiragana()` |
| diff 或重写补回 | `opennlp.tools.util.featuregen.StringPattern.isAllKatakana()` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.ALL_HIRAGANA` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.ALL_KATAKANA` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.CONTAINS_COMMA` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.CONTAINS_DIGIT` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.CONTAINS_HYPHEN` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.CONTAINS_LETTERS` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.CONTAINS_PERIOD` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.CONTAINS_SLASH` |
| 最新组仍漏报 | `opennlp.tools.util.featuregen.StringPattern.CONTAINS_UPPERCASE` |

### constantinople-019 · ivy.settings.dir space escaping problem

| 类别 | 完整签名 |
| --- | --- |
| 最新组仍漏报 | `org.apache.ivy.core.settings.XmlSettingsParser.classpathStarted(java.util.Map)` |

## 复跑

```bash
python src/static_compare.py --seed-diff-overlay --cross-class-calls --rows 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
python src/compare_ten.py --latest --env-file ../work/ripple/.env.ripple100
python src/report_static_twenty.py --with-models
python src/report_ten.py
```

此前的原始候选与多跳候选模型对照见 [十案例报告](ten-case-comparison.md)。
