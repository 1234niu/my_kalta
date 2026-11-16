# 000–019 新旧 MA 对照

两版使用同样的 20 个样本、`deepseek-v4.1-flash-1017`、温度 0、关闭思考模式和相同静态候选。旧 SP、旧 MA 各运行三次，新 MA 每例运行一次。000–009 参与过静态规则开发，010–019 用于检验迁移。

## 精确率、召回率与 F1

旧版先对每个案例的三次指标取中位数，再与新版按案例做宏平均。FQN 区分包名和参数，CE 只保留类名和成员名。新 MA 给出确认＋待核查的召回候选集，并单列独立核查后确认的实体。

| 样本 | 方法 | FQN P / R / F1 | CE P / R / F1 | FQN 命中 / 标签（实体累计） |
| --- | --- | --- | --- | ---: |
| 000–009 | 静态候选 | 16.6% / 88.8% / 25.5% | 16.6% / 90.2% / 25.2% | 21/26 |
| 000–009 | 旧 SP | 44.7% / 50.2% / 40.0% | 45.4% / 50.5% / 41.0% | 10/26 |
| 000–009 | 旧 MA | 32.7% / 42.7% / 33.0% | 35.2% / 44.5% / 35.0% | 13/26 |
| 000–009 | 新 MA · 确认＋待核查 | 20.7% / 78.8% / 27.4% | 20.6% / 80.2% / 27.0% | 20/26 |
| 000–009 | 新 MA · 仅确认 | 36.7% / 18.7% / 22.4% | 38.3% / 19.8% / 23.8% | 5/26 |
| 010–019 | 静态候选 | 14.5% / 26.5% / 9.9% | 14.5% / 26.5% / 9.9% | 10/39 |
| 010–019 | 旧 SP | 38.3% / 21.7% / 21.4% | 43.3% / 25.0% / 25.4% | 7/39 |
| 010–019 | 旧 MA | 50.0% / 32.0% / 34.9% | 53.3% / 32.0% / 36.2% | 10/39 |
| 010–019 | 新 MA · 确认＋待核查 | 14.1% / 36.5% / 16.8% | 15.1% / 37.3% / 17.8% | 19/39 |
| 010–019 | 新 MA · 仅确认 | 17.5% / 6.5% / 9.5% | 20.0% / 7.3% / 10.7% | 5/39 |
| 全部 | 静态候选 | 15.5% / 57.7% / 17.7% | 15.5% / 58.3% / 17.5% | 31/65 |
| 全部 | 旧 SP | 41.5% / 35.9% / 30.7% | 44.4% / 37.8% / 33.2% | 17/65 |
| 全部 | 旧 MA | 41.3% / 37.3% / 33.9% | 44.2% / 38.2% / 35.6% | 23/65 |
| 全部 | 新 MA · 确认＋待核查 | 17.4% / 57.7% / 22.1% | 17.9% / 58.8% / 22.4% | 39/65 |
| 全部 | 新 MA · 仅确认 | 27.1% / 12.6% / 15.9% | 29.2% / 13.6% / 17.3% | 10/65 |

旧版实体累计按各案例三次命中数的中位数相加。

## 逐例预测和工具用量

预测列为 FQN 命中 / 输出数。一次工具轮最多分发三个查询，错误查询也占用预算。Planner 不调用工具，Analyze、Review、补查 Analyze、补查 Review 的查询上限依次为 8、5、3、2。每例至多一次补查，最多 18 次工具查询和 33 个模型对话轮次。临时 API 错误单次模型轮最多请求三次。

| 案例 | 标签 | 静态 | 旧 MA 三次 | 新 MA 确认＋待核查 | 新 MA 仅确认 | 工具轮 / 查询 / 模型轮 | 补查 |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 000 | 1 | 1/2 | 0/0, 0/0, 0/0 | 1/1 | 1/1 | 4 / 10 / 12 | 有 |
| 001 | 6 | 5/14 | 4/4, 2/2, 4/4 | 5/15 | 1/3 | 4 / 10 / 11 | 有 |
| 002 | 4 | 2/37 | 3/6, 3/4, 3/6 | 2/39 | 1/3 | 3 / 7 / 9 | 有 |
| 003 | 1 | 1/13 | 0/1, 0/1, 0/1 | 0/11 | 0/0 | 5 / 13 / 12 | 有 |
| 004 | 1 | 1/35 | 1/6, 1/6, 1/11 | 1/35 | 0/1 | 7 / 18 / 15 | 有 |
| 005 | 2 | 2/10 | 0/0, 2/2, 0/0 | 2/10 | 0/2 | 4 / 9 / 11 | 有 |
| 006 | 1 | 1/13 | 0/0, 1/3, 0/0 | 1/11 | 0/0 | 5 / 13 / 12 | 有 |
| 007 | 4 | 3/30 | 0/0, 1/1, 3/5 | 3/30 | 1/1 | 3 / 8 / 10 | 有 |
| 008 | 1 | 1/22 | 1/2, 1/5, 1/2 | 1/22 | 0/2 | 6 / 15 / 12 | 有 |
| 009 | 5 | 4/18 | 2/4, 4/8, 3/6 | 4/18 | 1/1 | 6 / 15 / 13 | 有 |
| 010 | 5 | 2/39 | 1/3, 2/4, 0/6 | 2/36 | 2/2 | 6 / 15 / 13 | 有 |
| 011 | 2 | 1/9 | 2/2, 2/2, 2/2 | 1/9 | 0/0 | 4 / 8 / 11 | 无 |
| 012 | 3 | 1/14 | 2/3, 2/3, 2/3 | 2/16 | 0/0 | 2 / 5 / 10 | 无 |
| 013 | 1 | 0/8 | 0/1, 0/1, 0/1 | 0/10 | 0/2 | 6 / 16 / 14 | 有 |
| 014 | 1 | 0/14 | 0/1, 0/1, 0/0 | 0/14 | 0/0 | 6 / 15 / 13 | 有 |
| 015 | 1 | 1/14 | 0/0, 0/0, 0/0 | 1/13 | 0/3 | 4 / 10 / 10 | 有 |
| 016 | 12 | 2/2 | 2/2, 2/2, 2/2 | 10/11 | 3/4 | 6 / 15 / 13 | 有 |
| 017 | 1 | 0/21 | 1/1, 1/1, 1/1 | 0/23 | 0/2 | 5 / 13 / 12 | 有 |
| 018 | 12 | 3/21 | 2/2, 2/2, 2/2 | 3/22 | 0/3 | 4 / 10 / 11 | 有 |
| 019 | 1 | 0/23 | 0/0, 0/2, 0/1 | 0/24 | 0/1 | 5 / 13 / 12 | 有 |

以下案例的审查阶段耗尽轮次，保留分析候选或前一轮已完成的审查结果。011（review）、012（review）。

工具轮共 95，每例中位数 5，最高 7。

工具查询共 238，每例中位数 13，最高 18。

模型轮共 236，每例中位数 12，最高 15。

## ==召回增量来源==

旧 MA 稳定命中指三次运行中至少两次匹配该 FQN。静态以外命中按该实体是否进入相同的静态输入集合判定。

| 样本 | 保住静态命中 | 静态以外命中（确认数） | 补回旧 MA 漏检 | 丢失旧 MA 稳定命中 |
| --- | ---: | ---: | ---: | ---: |
| 000–009 | 20/21 | 0（0） | 8 | 1 |
| 010–019 | 10/10 | 9（3） | 11 | 2 |
| 全部 | 30/31 | 9（3） | 19 | 3 |

## 代表案例

- **000** 旧 MA 三次均遗漏 `BrentOptimizer.doOptimize()`。新版 Review 读取调用处，确认 `best()` 的平局选择影响该方法的返回值。
- **003** 静态候选已经覆盖 `VfsResource.normalize(String)`。新版 Review 以方法体可以原样复用为由将其排除，和数据集标签产生分歧。这一处漏检发生在审查阶段。
- **016** 旧 MA 和静态候选均命中 2/12，新版候选命中 10/12。新增的 8 个命中都在静态候选以外，其中 Review 依据源码确认了 `rename`、`select` 和 `status`。该例占 9 个静态以外命中的 8 个。

## 逐实体命中和漏检

旧 MA 列为三次出现次数。额外输出指未匹配数据集标签的 FQN。

### constantinople-000

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.math3.optimization.univariate.BrentOptimizer.doOptimize()` | 是 | 0/3 | 确认 |

新版额外输出 0 个，其中确认 0 个。

### constantinople-001

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.io.input.CharSequenceInputStream.CharSequenceInputStream(java.lang.CharSequence,java.nio.charset.Charset,int)` | 是 | 0/3 | 待核查 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark` | 是 | 3/3 | 待核查 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark(int)` | 是 | 3/3 | 确认 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_bbuf` | 是 | 2/3 | 待核查 |
| `org.apache.commons.io.input.CharSequenceInputStream.mark_cbuf` | 是 | 2/3 | 待核查 |
| `org.apache.commons.io.input.CharSequenceInputStream.skip(long)` | 否 | 0/3 | 漏检 |

新版额外输出 10 个，其中确认 2 个。

### constantinople-002

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.REGEX` | 是 | 3/3 | 待核查 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig)` | 是 | 3/3 | 确认 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.UnixFTPEntryParser(org.apache.commons.net.ftp.FTPClientConfig,boolean)` | 否 | 0/3 | 漏检 |
| `org.apache.commons.net.ftp.parser.UnixFTPEntryParser.trimLeadingSpaces` | 否 | 3/3 | 漏检 |

新版额外输出 37 个，其中确认 2 个。

### constantinople-003

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `fr.jayasoft.ivy.repository.vfs.VfsResource.normalize(java.lang.String)` | 是 | 0/3 | 漏检 |

新版额外输出 11 个，其中确认 0 个。

### constantinople-004

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.ivy.core.resolve.ResolveEngine.computeConflicts(org.apache.ivy.core.resolve.VisitNode,org.apache.ivy.core.resolve.VisitNode,java.lang.String,java.util.Collection,java.util.Collection)` | 是 | 3/3 | 待核查 |

新版额外输出 34 个，其中确认 1 个。

### constantinople-005

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.deltaspike.data.impl.util.QueryUtils.nullSafeValue(java.lang.String)` | 是 | 1/3 | 待核查 |
| `org.apache.deltaspike.data.impl.util.QueryUtils.nullSafeValue(java.lang.String,java.lang.String)` | 是 | 1/3 | 待核查 |

新版额外输出 8 个，其中确认 2 个。

### constantinople-006

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.configuration2.interpol.ConfigurationInterpolator.registerLocalLookups(org.apache.commons.configuration2.interpol.ConfigurationInterpolator)` | 是 | 1/3 | 待核查 |

新版额外输出 10 个，其中确认 0 个。

### constantinople-007

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.dbcp2.BasicDataSource.createConnectionPool(org.apache.commons.dbcp2.PoolableConnectionFactory)` | 否 | 0/3 | 漏检 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.getConnectionIndex()` | 是 | 1/3 | 待核查 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.getDataSourceJmxName()` | 是 | 1/3 | 待核查 |
| `org.apache.commons.dbcp2.PoolableConnectionFactory.makeObject()` | 是 | 2/3 | 确认 |

新版额外输出 27 个，其中确认 0 个。

### constantinople-008

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.jcs.auxiliary.disk.block.BlockDisk.calculateByteOffsetForBlockAsLong(int)` | 是 | 3/3 | 待核查 |

新版额外输出 21 个，其中确认 2 个。

### constantinople-009

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.sysml.conf.DMLConfig._document` | 是 | 3/3 | 待核查 |
| `org.apache.sysml.conf.DMLConfig._documentBuilder` | 否 | 0/3 | 漏检 |
| `org.apache.sysml.conf.DMLConfig.getDocumentBuilder()` | 是 | 3/3 | 待核查 |
| `org.apache.sysml.conf.DMLConfig.parseConfig()` | 是 | 2/3 | 待核查 |
| `org.apache.sysml.conf.DMLConfig.setTextValue(org.w3c.dom.Element,java.lang.String,java.lang.String)` | 是 | 1/3 | 确认 |

新版额外输出 14 个，其中确认 0 个。

### constantinople-010

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.MAX_CREDENTILAS_CACHE_SIZE` | 否 | 0/3 | 漏检 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.credentialsCache` | 否 | 0/3 | 漏检 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.parseURI(java.lang.String)` | 是 | 2/3 | 确认 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.requestCredentials(java.lang.String)` | 否 | 1/3 | 漏检 |
| `org.apache.ivy.plugins.repository.ssh.AbstractSshBasedRepository.user` | 是 | 0/3 | 确认 |

新版额外输出 34 个，其中确认 0 个。

### constantinople-011

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.net.smtp.SimpleSMTPHeader.addHeaderField(java.lang.String,java.lang.String)` | 是 | 3/3 | 待核查 |
| `org.apache.commons.net.smtp.SimpleSMTPHeader.hasHeaderDate` | 否 | 3/3 | 漏检 |

新版额外输出 8 个，其中确认 0 个。

### constantinople-012

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.ivy.util.XMLHelper.parse(java.net.URL,java.net.URL,org.xml.sax.helpers.DefaultHandler,org.xml.sax.ext.LexicalHandler)` | 否 | 0/3 | 漏检 |
| `org.apache.ivy.util.XMLHelper.parseToDom(java.io.InputStream,org.apache.ivy.plugins.repository.Resource,org.xml.sax.EntityResolver)` | 是 | 3/3 | 待核查 |
| `org.apache.ivy.util.XMLHelper.toSystemId(java.net.URL)` | 否 | 3/3 | 待核查 |

新版额外输出 14 个，其中确认 0 个。

### constantinople-013

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.ivy.core.cache.DefaultResolutionCacheManager.clean()` | 否 | 0/3 | 漏检 |

新版额外输出 10 个，其中确认 2 个。

### constantinople-014

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.configuration.CompositeConfiguration.appendListProperty(java.util.List,org.apache.commons.configuration.Configuration,java.lang.String)` | 否 | 0/3 | 漏检 |

新版额外输出 14 个，其中确认 0 个。

### constantinople-015

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.parquet.proto.ProtoWriteSupport.MessageWriter.MessageWriter(com.google.protobuf.Descriptors.Descriptor,org.apache.parquet.schema.GroupType)` | 是 | 0/3 | 待核查 |

新版额外输出 12 个，其中确认 3 个。

### constantinople-016

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.net.imap.IMAPClient.append(java.lang.String,java.lang.String,java.lang.String,java.lang.String)` | 否 | 0/3 | 漏检 |
| `org.apache.commons.net.imap.IMAPClient.copy(java.lang.String,java.lang.String)` | 否 | 0/3 | 漏检 |
| `org.apache.commons.net.imap.IMAPClient.create(java.lang.String)` | 否 | 0/3 | 待核查 |
| `org.apache.commons.net.imap.IMAPClient.delete(java.lang.String)` | 否 | 0/3 | 待核查 |
| `org.apache.commons.net.imap.IMAPClient.examine(java.lang.String)` | 否 | 0/3 | 待核查 |
| `org.apache.commons.net.imap.IMAPClient.list(java.lang.String,java.lang.String)` | 是 | 3/3 | 待核查 |
| `org.apache.commons.net.imap.IMAPClient.lsub(java.lang.String,java.lang.String)` | 是 | 3/3 | 待核查 |
| `org.apache.commons.net.imap.IMAPClient.rename(java.lang.String,java.lang.String)` | 否 | 0/3 | 确认 |
| `org.apache.commons.net.imap.IMAPClient.select(java.lang.String)` | 否 | 0/3 | 确认 |
| `org.apache.commons.net.imap.IMAPClient.status(java.lang.String,java.lang.String[])` | 否 | 0/3 | 确认 |
| `org.apache.commons.net.imap.IMAPClient.subscribe(java.lang.String)` | 否 | 0/3 | 待核查 |
| `org.apache.commons.net.imap.IMAPClient.unsubscribe(java.lang.String)` | 否 | 0/3 | 待核查 |

新版额外输出 1 个，其中确认 1 个。

### constantinople-017

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.commons.math3.optimization.linear.SimplexTableau.CUTOFF_THRESHOLD` | 否 | 3/3 | 漏检 |

新版额外输出 23 个，其中确认 2 个。

### constantinople-018

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `opennlp.tools.util.featuregen.StringPattern.ALL_HIRAGANA` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.ALL_KATAKANA` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_COMMA` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_DIGIT` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_HYPHEN` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_LETTERS` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_PERIOD` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_SLASH` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.CONTAINS_UPPERCASE` | 否 | 0/3 | 漏检 |
| `opennlp.tools.util.featuregen.StringPattern.isAllHiragana()` | 是 | 3/3 | 待核查 |
| `opennlp.tools.util.featuregen.StringPattern.isAllKatakana()` | 是 | 3/3 | 待核查 |
| `opennlp.tools.util.featuregen.StringPattern.recognize(java.lang.String)` | 是 | 0/3 | 待核查 |

新版额外输出 19 个，其中确认 3 个。

### constantinople-019

| 数据集受影响实体 | 静态命中 | 旧 MA | 新 MA |
| --- | --- | ---: | --- |
| `org.apache.ivy.core.settings.XmlSettingsParser.classpathStarted(java.util.Map)` | 否 | 0/3 | 漏检 |

新版额外输出 24 个，其中确认 1 个。
