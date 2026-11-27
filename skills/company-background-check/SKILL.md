---
name: company-background-check
description: 投递前企业背调快筛。当用户给一个公司名要求背调/查底细/查涉诉/判断"去不去"时使用。串联工商登记与司法文书两类数据连接器，加 WebSearch 交叉验证，一轮并行跑完，输出"结论先行"的背调报告。
description_en: Pre-offer company due-diligence quick screen. Use when the user gives a company name and asks to check its background, litigation exposure, or whether to accept the job. Runs business-registry and court-document connectors plus cross-checking web search in one parallel burst, then outputs a conclusion-first due-diligence report with honest coverage caveats.
---

# 投递前企业背调（工商 + 司法连接器 + WebSearch）

> 依赖：需要「企查查（qcc）」类工商/司法数据连接器；若无，可将第 2 轮全部替换为 WebSearch 聚合快照，输出模板不变，但须在报告中显式降级标注。

## 效率铁律

1. **独立调用必须并行**：同一消息里发多个工具调用/WebSearch，禁止串行等待。
2. **两轮并行制**：第 1 轮只发 1 个调用（实体定位）；第 2 轮把其余全部并行发出。
3. **默认快筛 3 维度**：登记信息 + 变更记录 + 涉诉检索 + WebSearch×2。用户说"深查"才追加股东/年报/简介/高管。
4. 全程不留给用户任何"自己再查"的作业——官方站点（zxk.court.gov.cn / gsxt.gov.cn）有人机验证无法程序化访问，用 WebSearch 聚合快照替代，并在报告中标注"官方渠道可终验"。

## 流程

### 第 1 轮：实体定位（1 个调用）

工商连接器模糊查询 searchKey=公司名。

- 唯一匹配 → 拿全称+信用代码进第 2 轮。
- 多候选 → **必须展示候选清单让用户选**，禁止自动选第一个。

### 第 2 轮：并行轰炸（5-6 个调用同时发）

以下全部并行：

1. 工商登记信息（searchKey=信用代码）——法代/资本/实缴/参保人数/状态
2. 变更记录——变更频率、股权沿革（红旗：法人/股东高频变更）
3. 司法文书检索（**party=工商全称**）——涉诉文书；零命中≠没涉诉，如实标注
4. WebSearch：`"公司全称" 被执行 OR 失信 OR 限制消费`
5. WebSearch：`"公司全称" 劳动仲裁 OR 纠纷 OR 诉讼`
6. （快筛可选）WebSearch 公司名——顺带挖法代关联企业版图

### 涉诉命中时

用文书详情接口（caseNo）取全文，只对定性存疑的案件取，不要每条都取。

## 速判口径

- **红旗**：被执行人/失信/限消记录；劳动争议**批量**出现；法人/股东高频变更+注册资本虚高未实缴。
- **常态**：买卖/承揽/借贷类商事纠纷（小公司常见，不否决）；零星劳动仲裁。
- **正面信号**：实缴到位、参保人数稳定或增长、无公开涉诉、法代名下风险面板全零、法代有多年行业关联企业（老操盘手≠皮包公司）。
- 裁判文书公开率有限；WebSearch 命中的同名近似公司必须逐条甄别主体后才能引用。

## 输出模板（结论先行）

1. 一句话结论：去/不去/带什么问题去
2. 工商底细表（全称/法代/资本实缴/参保规模/状态/行业）
3. 关键发现（股权沿革时间线、变更频率、扩张或收缩）
4. 涉诉四路结果（文书库 + 被执行/失信搜索 + 仲裁搜索 + 法代风险面板）
5. 2-3 个面试时必须问的问题
6. 边界声明：文书库查不到≠没涉诉；第三方快照有滞后；官方 zxk/gsxt 可终验
