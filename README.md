# Vertical Agent Skills

一组**垂直场景**的 Agent Skills，遵循 [Agent Skills 开放标准](https://agentskills.io/specification)（目录 = `SKILL.md` + frontmatter，可附 `scripts/` 与 `references/`）。任何兼容该标准的 agent（Claude Code、Codex、Gemini CLI、Cursor、Qoder 等）都可以把整个目录放入其 skills 目录使用。

与通用 coding skill 合集不同，本仓库聚焦**行业工作流**：周期性数据跟踪、定时自动化运维、筛选章程诊断、投递前企业背调、中文类型小说创作、中文长篇漂移闸门、WebMCP 页面工具桥。

A collection of vertical-scenario Agent Skills following the Agent Skills open standard. Focus: industry workflows rather than generic coding. → [English guide](docs/README_EN.md)

## Skills

| Skill | 场景 | 附带 |
|---|---|---|
| [recurring-data-tracking-report](skills/recurring-data-tracking-report/SKILL.md) | 周期性数据跟踪研报的输出契约：题面自包含、阈值检查表、环比闭环、数据缺口清单 | 测试用例 |
| [qoder-scheduled-automation-setup](skills/qoder-scheduled-automation-setup/SKILL.md) | Qoder 定时自动化全周期：云端/本地边界、权限模式、创建后回读验证、迁移与查重 | 测试用例 |
| [screening-funnel-diagnosis](skills/screening-funnel-diagnosis/SKILL.md) | 多闸门筛选章程的闸门效率诊断：留一法、Jaccard 冗余度、既要又要的代价方向 | `scripts/funnel_diagnose.py`、测试用例 |
| [company-background-check](skills/company-background-check/SKILL.md) | 投递前企业背调快筛：工商 + 司法文书 + 搜索交叉验证，结论先行 | 测试用例 |
| [douban-genre-craft](skills/douban-genre-craft/SKILL.md) | 中文类型小说可迁移技法（12 条）＋版权边界＋机械文风闸门 | `scripts/gate.py`、`references/`、测试用例 |
| [chinese-longform-drift-gate](skills/chinese-longform-drift-gate/SKILL.md) | 中文长篇跨会话续写的双层漂移闸门：单一正源分模块 + 机械脚本 + 人工审计清单 | `scripts/gate.py`、测试用例 |
| [webmcp-bridge](skills/webmcp-bridge/SKILL.md) | 发现并调用网页内注册的 WebMCP 工具（navigator.modelContextTesting） | 测试用例 |

## 验证状态（已验证 / 未验证分列）

详见 [EVALUATION.md](EVALUATION.md)。已验证且可复现：

- **规范符合性 + 凭据触发词扫描**：`python tools/validate.py skills`；
- **测试集完整性**：7 技能 × ≥3 激活用例（含负样本）+ 效果 rubric，`python tools/run_eval.py --check`；
- **脚本端到端**：funnel_diagnose.py / gate.py 在 Windows GBK 控制台实测（e2e 测试发现并修复过一个真实崩溃，见 commit `5bd74e8`）。

**未验证且不声称**：跨宿主激活率、执行成功率、真实用户数、时间节省量化、企业部署——`tools/run_eval.py --skeleton` 提供了填写模板与协议，欢送带证据的 PR。

## 快速开始

```bash
# 任意兼容宿主
npx skills add wade12124/vertical-agent-skills --list   # 预览仓库内技能
npx skills add wade12124/vertical-agent-skills          # 安装全部

# 或直接拿单个技能：把 skills/<name>/ 拷进宿主的 skills 目录
# （很多宿主扫描 ~/.agents/skills/<skill-name>/）
```

脚本示例：

```bash
# 筛选章程闸门诊断（CSV 首行表头）
python skills/screening-funnel-diagnosis/scripts/funnel_diagnose.py pool.csv --config my_gates.py

# 中文长篇机械闸门（每回收工跑一次；退出码 0 为过）
python skills/chinese-longform-drift-gate/scripts/gate.py draft.md --names 书名1 --max-short 5.0

# 仓库自检
python tools/validate.py skills && python tools/run_eval.py --check
```

## 使用方法

1. 将 `skills/<name>/` 整个目录复制到你的 agent 的 skills 目录（各产品位置不同，见其文档）。
2. `SKILL.md` frontmatter 中的 `name` 需与目录名一致，`description` 是 agent 决定何时加载该技能的唯一依据；部分技能附 `description_en`。
3. 带脚本的技能（`scripts/`）需要本机 Python 3；调用方式写在各自 SKILL.md 的「执行」/「闸门」一节。

## 边界声明

- 各技能内不含任何私人路径、账号凭据或机器特定配置（`tools/validate.py` 触发词扫描）；脚本示例数据均为演示用途。
- `funnel_diagnose.py` 输出为筛选机制效率诊断，不构成投资建议。
- `douban-genre-craft` 只迁移写作方法层，明确禁止复制受保护表达；`chinese-longform-drift-gate` 为通用方法论，不含任何未发表作品内容。
- `qoder-scheduled-automation-setup` 绑定 Qoder 的 `qoder_cron` 工具，其余技能宿主无关。

## License

[MIT](LICENSE)
