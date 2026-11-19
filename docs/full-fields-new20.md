# 新 20 例静态、SP 与新版 MA 对照

选取 20 个此前未运行的案例，覆盖 10 个仓库。这些仓库没有出现在静态规则开发用的原 000–019 中。按数据集原顺序在仓库间轮询，排除已有实验或尝试的案例及重复 parent 快照，选定后再运行。

静态分析每例运行一次。SP 和新版 MA 使用同一份改进静态候选，使用 `deepseek-v4.1-flash-1017`、温度 0、关闭思考模式，每例各跑 3 次。MA 主结果包含确认和待核查，保留未被明确排除的静态候选。

## 论文口径的宏平均

FQN 严格匹配完整名称和签名。CE 保留声明类和成员名并去重。先逐提交算集合精确率、召回率、F1，模型组每项指标取三次中位数，最后对提交取宏平均。零分母按实验实现记为零。候选和 FQN 命中数按案例相加，模型组先取各案例三次计数的中位数。计算口径见 [katIA §V-A](https://arxiv.org/html/2611.10958v1#S5.SS1)。

| 方法 | FQN 精确率 / 召回率 / F1 | CE 精确率 / 召回率 / F1 | FQN 命中 / 标签 | 候选数 |
| --- | --- | --- | ---: | ---: |
| 改进前静态 | 10.93% / 30.13% / 14.32% | 11.67% / 31.55% / 15.29% | 34/101 | 380 |
| 改进后静态 | 9.46% / 35.09% / 13.14% | 10.57% / 36.71% / 14.46% | 39/101 | 471 |
| SP | 48.86% / 29.69% / 31.96% | 63.94% / 42.33% / 45.89% | 26/101 | 55 |
| 新版 MA · 确认＋待核查 | 13.51% / 48.31% / 18.77% | 14.88% / 49.94% / 20.36% | 45/101 | 496 |
| 新版 MA · 仅确认 | 24.17% / 18.98% / 18.02% | 25.42% / 20.56% / 19.86% | 13/101 | 40 |

## 逐案例 FQN 命中

预测格为命中数 / 输出数。SP、MA 的三次结果按运行顺序排列。

| 案例 | 仓库 | 标签 | 改进前静态 | 改进后静态 | SP 三次 | MA 三次 | MA 仅确认三次 |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 040 | apache/commons-compress | 9 | 6/49 | 6/49 | 1/1, 1/1, 1/1 | 6/49, 7/54, 8/51 | 1/4, 0/0, 3/6 |
| 064 | apache/commons-lang | 7 | 1/4 | 1/4 | 1/3, 1/7, 1/7 | 1/6, 1/4, 1/4 | 0/0, 1/4, 1/3 |
| 068 | apache/commons-scxml | 1 | 0/0 | 0/2 | 0/4, 0/0, 0/0 | 1/3, 1/4, 1/4 | 1/2, 1/2, 1/1 |
| 086 | apache/gora | 2 | 0/1 | 0/1 | 0/2, 0/2, 0/2 | 2/5, 0/1, 2/5 | 2/3, 0/0, 2/4 |
| 095 | apache/giraph | 1 | 0/5 | 0/7 | 0/2, 0/2, 0/2 | 0/8, 0/8, 0/10 | 0/3, 0/1, 0/4 |
| 128 | apache/commons-validator | 10 | 0/16 | 2/20 | 4/5, 0/2, 4/5 | 2/20, 2/22, 2/22 | 0/0, 0/0, 0/0 |
| 142 | apache/commons-vfs | 2 | 2/7 | 2/9 | 2/5, 2/5, 2/5 | 2/9, 2/11, 2/10 | 2/6, 1/1, 1/3 |
| 148 | apache/commons-digester | 3 | 2/15 | 2/21 | 1/1, 1/1, 1/1 | 2/29, 2/22, 2/22 | 0/3, 0/1, 0/1 |
| 160 | apache/commons-beanutils | 4 | 1/4 | 1/4 | 1/1, 1/1, 1/1 | 1/4, 3/6, 1/4 | 0/0, 0/2, 0/1 |
| 218 | apache/commons-bcel | 3 | 0/61 | 0/85 | 2/7, 3/4, 3/3 | 1/88, 1/87, 2/88 | 0/2, 0/0, 1/4 |
| 058 | apache/commons-compress | 2 | 2/16 | 2/17 | 2/3, 2/2, 2/2 | 2/21, 2/17, 2/22 | 0/2, 0/0, 0/6 |
| 065 | apache/commons-lang | 8 | 6/16 | 6/32 | 1/3, 1/3, 1/3 | 6/32, 6/32, 6/32 | 1/1, 1/4, 1/1 |
| 079 | apache/commons-scxml | 6 | 0/35 | 0/39 | 0/2, 0/2, 0/2 | 0/40, 0/39, 0/40 | 0/0, 0/1, 0/1 |
| 112 | apache/gora | 6 | 0/21 | 0/22 | 1/4, 1/4, 1/4 | 0/22, 0/24, 0/24 | 0/1, 0/4, 0/4 |
| 101 | apache/giraph | 4 | 0/1 | 0/1 | 2/3, 2/3, 2/3 | 0/5, 1/2, 0/1 | 0/2, 1/1, 0/0 |
| 132 | apache/commons-validator | 2 | 0/13 | 0/14 | 0/1, 0/1, 0/1 | 0/14, 0/14, 0/14 | 0/0, 0/1, 0/2 |
| 156 | apache/commons-vfs | 3 | 1/42 | 3/46 | 1/1, 1/1, 1/1 | 3/46, 3/46, 3/46 | 1/2, 1/2, 1/2 |
| 262 | apache/commons-digester | 8 | 6/12 | 7/18 | 3/7, 3/7, 7/14 | 7/20, 7/18, 7/18 | 1/4, 2/3, 2/2 |
| 206 | apache/commons-beanutils | 5 | 0/4 | 0/4 | 0/1, 0/1, 0/1 | 0/4, 1/5, 1/5 | 0/0, 1/1, 1/3 |
| 090 | apache/commons-compress | 15 | 7/58 | 7/76 | 3/3, 3/3, 3/3 | 7/77, 7/76, 7/76 | 2/5, 2/2, 1/2 |

## 召回和用量

- 静态改进在本组补回 5 个严格匹配标签，分布在 3 个案例。
  - 128 · `org.apache.commons.validator.routines.DomainValidator.DOMAIN_VALIDATOR`
  - 128 · `org.apache.commons.validator.routines.DomainValidator.allowLocal`
  - 156 · `org.apache.commons.vfs.impl.StandardFileSystemManager.createInstance(java.lang.String)`
  - 156 · `org.apache.commons.vfs.impl.StandardFileSystemManager.findClass(java.lang.String)`
  - 262 · `org.apache.commons.digester3.binder.DigesterLoader.createRuleSet()`
- SP 以三次中至少两次命中为阈值，保留静态命中 14/39 个，另找到 12 个静态候选以外的标签。预测集合三次完全一致的案例为 12/20。
- 新版 MA · 确认＋待核查 以三次中至少两次命中为阈值，保留静态命中 39/39 个，另找到 6 个静态候选以外的标签。预测集合三次完全一致的案例为 3/20。
- MA 每次运行最多 18 次工具查询及 19 个模型轮次。实际查询中位数 12、最高 12。模型轮次中位数 4、最高 4。SP 每次运行一个模型轮。
- MA 查询总量按阶段拆分为初探 227 次、排名后补查 120 次、Analyze 自主追加 0 次、复检 324 次。

## 标签级命中与漏检

静态列显示旧版 → 新版是否命中。模型列为三次运行中出现的次数，0/3 表示三次都漏检。

| 案例 | 数据集标签 FQN | 静态前 → 后 | SP | MA | MA 仅确认 |
| --- | --- | --- | ---: | ---: | ---: |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.createHuffmanDecodingTables(int,int)` | 否 → 否 | 0/3 | 2/3 | 1/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.getAndMoveToFrontDecode()` | 是 → 是 | 3/3 | 3/3 | 2/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.hbCreateDecodeTables(int[],int[],int[],char[],int,int,int)` | 否 → 否 | 0/3 | 1/3 | 1/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.recvDecodingTables()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.setupBlock()` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.setupNoRandPartA()` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.setupNoRandPartB()` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.setupRandPartA()` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 040 | `org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream.setupRandPartB()` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 064 | `org.apache.commons.lang.IDKey` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 064 | `org.apache.commons.lang.IDKey.IDKey(java.lang.Object)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 064 | `org.apache.commons.lang.IDKey.equals(java.lang.Object)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 064 | `org.apache.commons.lang.IDKey.hashCode()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 064 | `org.apache.commons.lang.IDKey.id` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 064 | `org.apache.commons.lang.IDKey.value` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 064 | `org.apache.commons.lang.builder.HashCodeBuilder.toIdentityHashCodeInteger(java.lang.Object)` | 是 → 是 | 3/3 | 3/3 | 2/3 |
| 068 | `org.apache.commons.scxml2.semantics.SCXMLSemanticsImpl.filterTransitionsSet(org.apache.commons.scxml2.Step,org.apache.commons.scxml2.EventDispatcher,org.apache.commons.scxml2.ErrorReporter,org.apache.commons.scxml2.SCInstance)` | 否 → 否 | 0/3 | 3/3 | 3/3 |
| 086 | `org.apache.gora.accumulo.store.AccumuloStore.putArray(org.apache.accumulo.core.data.Mutation,int,java.lang.Object,org.apache.accumulo.core.util.Pair)` | 否 → 否 | 0/3 | 2/3 | 2/3 |
| 086 | `org.apache.gora.accumulo.store.AccumuloStore.putMap(org.apache.accumulo.core.data.Mutation,int,org.apache.avro.Schema,java.lang.Object,org.apache.accumulo.core.util.Pair)` | 否 → 否 | 0/3 | 2/3 | 2/3 |
| 095 | `org.apache.giraph.comm.netty.NettyClient.stop.<anonymous>@556.operationComplete(io.netty.channel.ChannelFuture)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.DomainValidator.DOMAIN_VALIDATOR` | 否 → 是 | 0/3 | 3/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.DomainValidator.DOMAIN_VALIDATOR_WITH_LOCAL` | 否 → 否 | 2/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.DomainValidator.DomainValidator()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.DomainValidator.LOCAL_TLDS` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.DomainValidator.LOCAL_TLD_LIST` | 否 → 否 | 2/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.DomainValidator.allowLocal` | 否 → 是 | 0/3 | 3/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.EmailValidator.EMAIL_VALIDATOR` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.EmailValidator.EMAIL_VALIDATOR_WITH_LOCAL` | 否 → 否 | 2/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.EmailValidator.EmailValidator()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 128 | `org.apache.commons.validator.routines.EmailValidator.allowLocal` | 否 → 否 | 2/3 | 0/3 | 0/3 |
| 142 | `org.apache.commons.vfs2.provider.http.HttpFileContentInfoFactory.create(org.apache.commons.vfs2.FileContent)` | 是 → 是 | 3/3 | 3/3 | 3/3 |
| 142 | `org.apache.commons.vfs2.provider.http.HttpFileObject.doGetType()` | 是 → 是 | 3/3 | 3/3 | 1/3 |
| 148 | `org.apache.commons.digester3.ObjectCreateRule.ObjectCreateRule(java.lang.Class)` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 148 | `org.apache.commons.digester3.ObjectCreateRule.ObjectCreateRule(java.lang.String,java.lang.Class)` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 148 | `org.apache.commons.digester3.ObjectCreateRule.clazz` | 否 → 否 | 3/3 | 0/3 | 0/3 |
| 160 | `org.apache.commons.beanutils.MethodUtils.invokeExactMethod(java.lang.Object,java.lang.String,java.lang.Object)` | 否 → 否 | 3/3 | 0/3 | 0/3 |
| 160 | `org.apache.commons.beanutils.MethodUtils.invokeExactStaticMethod(java.lang.Class,java.lang.String,java.lang.Object)` | 否 → 否 | 0/3 | 1/3 | 0/3 |
| 160 | `org.apache.commons.beanutils.MethodUtils.invokeStaticMethod(java.lang.Class,java.lang.String,java.lang.Object)` | 否 → 否 | 0/3 | 1/3 | 0/3 |
| 160 | `org.apache.commons.beanutils.MethodUtils.toArray(java.lang.Object)` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 218 | `org.apache.bcel.generic.ReferenceType.isCastableTo(org.apache.bcel.generic.Type)` | 否 → 否 | 3/3 | 1/3 | 1/3 |
| 218 | `org.apache.bcel.generic.Type.normalizeForStackOrLocal()` | 否 → 否 | 3/3 | 0/3 | 0/3 |
| 218 | `org.apache.bcel.verifier.structurals.Pass3bVerifier.invalidReturnTypeError(org.apache.bcel.generic.Type,org.apache.bcel.generic.MethodGen)` | 否 → 否 | 2/3 | 3/3 | 0/3 |
| 058 | `org.apache.commons.compress.archivers.cpio.CpioArchiveOutputStream.writeNewEntry(org.apache.commons.compress.archivers.cpio.CpioArchiveEntry)` | 是 → 是 | 3/3 | 3/3 | 0/3 |
| 058 | `org.apache.commons.compress.archivers.cpio.CpioArchiveOutputStream.writeOldBinaryEntry(org.apache.commons.compress.archivers.cpio.CpioArchiveEntry,boolean)` | 是 → 是 | 3/3 | 3/3 | 0/3 |
| 065 | `org.apache.commons.lang3.time.FastDateFormat.FastDateFormat(java.lang.String,java.util.TimeZone,java.util.Locale)` | 是 → 是 | 3/3 | 3/3 | 2/3 |
| 065 | `org.apache.commons.lang3.time.FastDateParser.century` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 065 | `org.apache.commons.lang3.time.FastDateParser.escapeRegex(java.lang.StringBuilder,java.lang.String,boolean)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 065 | `org.apache.commons.lang3.time.FastDateParser.init()` | 是 → 是 | 0/3 | 3/3 | 1/3 |
| 065 | `org.apache.commons.lang3.time.FastDateParser.readObject(java.io.ObjectInputStream)` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 065 | `org.apache.commons.lang3.time.FastDateParser.serialVersionUID` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 065 | `org.apache.commons.lang3.time.FastDateParser.startYear` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 065 | `org.apache.commons.lang3.time.FastDateParser.thisYear` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 079 | `org.apache.commons.scxml.io.SCXMLParser.initRules(org.apache.commons.scxml.model.SCXML,org.apache.commons.scxml.PathResolver,java.util.List)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 079 | `org.apache.commons.scxml.io.SCXMLSerializer.serializeNamespaceDeclarations(org.apache.commons.scxml.model.NamespacePrefixesHolder)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 079 | `org.apache.commons.scxml.model.SCXML` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 079 | `org.apache.commons.scxml.model.SCXML.getNamespaces()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 079 | `org.apache.commons.scxml.model.SCXML.namespaces` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 079 | `org.apache.commons.scxml.model.SCXML.setNamespaces(java.util.Map)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 112 | `org.apache.gora.persistency.StatefulHashMap.clear()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 112 | `org.apache.gora.persistency.StatefulHashMap.put(java.lang.Object,java.lang.Object)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 112 | `org.apache.gora.persistency.StatefulHashMap.remove(java.lang.Object)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 112 | `org.apache.gora.persistency.StatefulHashMap.reuse()` | 否 → 否 | 3/3 | 0/3 | 0/3 |
| 112 | `org.apache.gora.persistency.StatefulMap.reuse()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 112 | `org.apache.gora.persistency.impl.PersistentBase.clear()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 101 | `org.apache.giraph.edge.MutableEdgesWrapper.MutableEdgesWrapper(org.apache.giraph.edge.OutEdges,org.apache.giraph.edge.OutEdges)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 101 | `org.apache.giraph.edge.MutableEdgesWrapper.decrementEdges()` | 否 → 否 | 3/3 | 0/3 | 0/3 |
| 101 | `org.apache.giraph.edge.MutableEdgesWrapper.numEdges` | 否 → 否 | 3/3 | 0/3 | 0/3 |
| 101 | `org.apache.giraph.edge.MutableEdgesWrapper.size()` | 否 → 否 | 0/3 | 1/3 | 1/3 |
| 132 | `org.apache.commons.validator.routines.DomainValidator.DOMAIN_LABEL_REGEX` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 132 | `org.apache.commons.validator.routines.DomainValidator.TOP_LABEL_REGEX` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 156 | `org.apache.commons.vfs.impl.StandardFileSystemManager.createInstance(java.lang.String)` | 否 → 是 | 0/3 | 3/3 | 0/3 |
| 156 | `org.apache.commons.vfs.impl.StandardFileSystemManager.findClass(java.lang.String)` | 否 → 是 | 0/3 | 3/3 | 0/3 |
| 156 | `org.apache.commons.vfs.impl.StandardFileSystemManager.findClassLoader()` | 是 → 是 | 3/3 | 3/3 | 3/3 |
| 262 | `org.apache.commons.digester3.binder.AbstractRulesModule.addError(java.lang.String,java.lang.Object[])` | 是 → 是 | 1/3 | 3/3 | 0/3 |
| 262 | `org.apache.commons.digester3.binder.AbstractRulesModule.addError(java.lang.Throwable)` | 是 → 是 | 1/3 | 3/3 | 0/3 |
| 262 | `org.apache.commons.digester3.binder.AbstractRulesModule.configure(org.apache.commons.digester3.binder.RulesBinder)` | 是 → 是 | 3/3 | 3/3 | 3/3 |
| 262 | `org.apache.commons.digester3.binder.AbstractRulesModule.forPattern(java.lang.String)` | 是 → 是 | 1/3 | 3/3 | 0/3 |
| 262 | `org.apache.commons.digester3.binder.AbstractRulesModule.install(org.apache.commons.digester3.binder.RulesModule)` | 是 → 是 | 1/3 | 3/3 | 0/3 |
| 262 | `org.apache.commons.digester3.binder.AbstractRulesModule.rulesBinder` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 262 | `org.apache.commons.digester3.binder.AbstractRulesModule.rulesBinder()` | 是 → 是 | 3/3 | 3/3 | 0/3 |
| 262 | `org.apache.commons.digester3.binder.DigesterLoader.createRuleSet()` | 否 → 是 | 3/3 | 3/3 | 2/3 |
| 206 | `org.apache.commons.beanutils.JDBCDynaClass.getColumnName(java.lang.String)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 206 | `org.apache.commons.beanutils.JDBCDynaClass.getObject(java.sql.ResultSet,java.lang.String)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 206 | `org.apache.commons.beanutils.ResultSetDynaClass.getObjectFromResultSet(java.lang.String)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 206 | `org.apache.commons.beanutils.ResultSetIterator.get(java.lang.String)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 206 | `org.apache.commons.beanutils.RowSetDynaClass.copy(java.sql.ResultSet)` | 否 → 否 | 0/3 | 2/3 | 2/3 |
| 090 | `org.apache.commons.compress.MemoryLimit` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.MemoryLimit.MEMORY_LIMIT_IN_KB` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.MemoryLimit.NO_LIMIT` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.MemoryLimit.getMemoryLimitInKb()` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.MemoryLimit.setMemoryLimitInKb(int)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.compressors.CompressorStreamFactory.CompressorStreamFactory()` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 090 | `org.apache.commons.compress.compressors.CompressorStreamFactory.CompressorStreamFactory(boolean)` | 是 → 是 | 0/3 | 3/3 | 0/3 |
| 090 | `org.apache.commons.compress.compressors.CompressorStreamFactory.CompressorStreamFactory(boolean,int)` | 是 → 是 | 0/3 | 3/3 | 1/3 |
| 090 | `org.apache.commons.compress.compressors.CompressorStreamFactory.memoryLimitInKb` | 是 → 是 | 0/3 | 3/3 | 1/3 |
| 090 | `org.apache.commons.compress.compressors.lzma.LZMACompressorInputStream.LZMACompressorInputStream(java.io.InputStream)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.compressors.lzma.LZMACompressorInputStream.LZMACompressorInputStream(java.io.InputStream,int)` | 是 → 是 | 3/3 | 3/3 | 2/3 |
| 090 | `org.apache.commons.compress.compressors.xz.XZCompressorInputStream.XZCompressorInputStream(java.io.InputStream,boolean)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.compressors.xz.XZCompressorInputStream.XZCompressorInputStream(java.io.InputStream,boolean,int)` | 是 → 是 | 3/3 | 3/3 | 1/3 |
| 090 | `org.apache.commons.compress.compressors.z.ZCompressorInputStream.ZCompressorInputStream(java.io.InputStream)` | 否 → 否 | 0/3 | 0/3 | 0/3 |
| 090 | `org.apache.commons.compress.compressors.z.ZCompressorInputStream.ZCompressorInputStream(java.io.InputStream,int)` | 是 → 是 | 3/3 | 3/3 | 0/3 |
