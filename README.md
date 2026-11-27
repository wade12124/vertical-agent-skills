# Vertical Agent Skills

一组**垂直场景**的 Agent Skills，遵循 [Agent Skills 开放标准](https://agentskills.io/specification)（目录 = `SKILL.md` + frontmatter，可附 `scripts/` 与 `references/`）。任何兼容该标准的 agent（Claude Code、Codex、Gemini CLI、Cursor、Qoder 等）都可以把整个目录放入其 skills 目录使用。

与通用 coding skill 合集不同，本仓库聚焦**行业工作流**：周期性数据跟踪、筛选章程诊断、投递前企业背调、中文类型小说创作、WebMCP 页面工具桥。

A collection of vertical-scenario Agent Skills following the Agent Skills open standard. Focus: industry workflows rather than generic coding. → [English guide](docs/README_EN.md)

## Skills

| Skill | 场景 | 附带 |
|---|---|---|
| [recurring-data-tracking-report](skills/recurring-data-tracking-report/SKILL.md) | 周期性数据跟踪研报的输出契约：题面自包含、阈值检查表、环比闭环、数据缺口清单 | — |
| [screening-funnel-diagnosis](skills/screening-funnel-diagnosis/SKILL.md) | 多闸门筛选章程的闸门效率诊断：留一法、Jaccard 冗余度、既要又要的代价方向 | `scripts/funnel_diagnose.py` |
| [company-background-check](skills/company-background-check/SKILL.md) | 投递前企业背调快筛：工商 + 司法文书 + 搜索交叉验证，结论先行 | — |
| [douban-genre-craft](skills/douban-genre-craft/SKILL.md) | 中文类型小说可迁移技法（12 条）＋版权边界＋机械文风闸门 | `scripts/gate.py`、`references/` |
| [webmcp-bridge](skills/webmcp-bridge/SKILL.md) | 发现并调用网页内注册的 WebMCP 工具（navigator.modelContextTesting） | — |

## 使用方法

1. 将 `skills/<name>/` 整个目录复制到你的 agent 的 skills 目录（各产品位置不同，见其文档）。
2. `SKILL.md` frontmatter 中的 `name` 需与目录名一致，`description` 是 agent 决定何时加载该技能的唯一依据。
3. 带脚本的技能（`scripts/`）需要本机 Python 3；调用方式写在各自 SKILL.md 的「执行」一节。

## 边界声明

- 各技能内不含任何私人路径、账号凭据或机器特定配置；脚本示例数据均为演示用途。
- `funnel_diagnose.py` 输出为筛选机制效率诊断，不构成投资建议。
- `douban-genre-craft` 只迁移写作方法层，明确禁止复制受保护表达。

## License

[MIT](LICENSE)
