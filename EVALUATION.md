# Evaluation Status — 评测现状与边界

本文件回应一个合理质疑：**收录这些技能不能证明它们有效**。下面把"已验证的"与"尚未验证的"分列清楚，不提供无法复现的数字。

## 已验证（可复现）

| 项 | 证据 | 复现方式 |
|---|---|---|
| 规范符合性：7 技能的 name/目录一致、description ≤1024、正文 ≤500 行、无悬空引用、无凭据/私人路径触发词 | `tools/validate.py` 全绿 | `python tools/validate.py skills` |
| 测试集合完整性：7 技能 × ≥3 激活用例（含负样本）+ 效果评分细则 | `tools/run_eval.py --check` 全绿 | 同上命令 |
| `funnel_diagnose.py` 端到端可运行（含 Windows GBK 控制台） | 本仓库 commit `5bd74e8`（e2e 测试发现 U+2212 崩溃并修复）| 见"复现方式"列的本地冒烟命令 |
| `gate.py` 正/负样例分别 PASS(exit 0)/FAIL(exit 1) | 本地实测记录 | `python skills/chinese-longform-drift-gate/scripts/gate.py <draft.md>` |
| CI 门禁（workflow 待补，见下） | 本地等价命令全部通过；`.github/workflows/validate.yml` 因当前 GitHub 连接器令牌缺 `workflow` 作用域暂缓提交，内容已备好 | `python tools/validate.py skills && python tools/run_eval.py --check` |

注：CI 的 workflow 文件内容就是上面四条命令的自动化版（规范校验 + 用例完整性 + 全脚本 AST + 两脚本冒烟），待令牌授权后补交，在那之前本表以本地执行为准。

## 未验证（不声称）

以下六项目前没有数据，**留空不填，欢迎带证据的 PR**：

1. **跨宿主激活一致性** —— 技能目录由多宿主共享（`~/.agents/skills/`），但 description 触发的准确率只在 Qoder 一个宿主上被长期使用间接检验过，未在 Claude Code / Codex / Cursor / Gemini CLI 上系统测过。
2. **系统化执行成功率** —— 评测协议与题库已就位（`tests/cases/` + `tools/run_eval.py --skeleton`），但**跑分需要在真实宿主会话里人工/代理执行并回填**，本仓库不预填任何分数。
3. **真实持续用户数** —— 仓库发布于 2026-11-27，为零用户首日。
4. **人工时间节省量化** —— 无前测/后测基线，不提供估算。
5. **企业环境部署** —— 无。
6. **与不用技能时的对照增益** —— 协议要求同题双跑（装技能/不装），尚未执行。

## 如何补齐（按官方评测指南的两维框架）

**描述评估**：对每个宿主开全新会话 → 只给技能目录（name+description 列表）+ 一条测试 prompt → 记录实际激活的技能 → 每 prompt 3 次。填 `tools/run_eval.py --skeleton <skill>` 生成的表格，存 `results/<host>/<skill>.md`。

**效果评估**：同一任务双跑（无技能 vs 有技能），按 case 内 rubric 逐项打勾，附产物。判定标准预先写在 rubric 里，避免事后解释。

安全说明：技能正文可能改变 agent 行为，安装前请按 awesome 列表的安全审查章节做人工复核；本仓库脚本仅做本地文件读写与打印，无网络与凭据访问（tripwires 扫描 + 人工审查）。
