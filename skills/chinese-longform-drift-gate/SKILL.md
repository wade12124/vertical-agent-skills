---
name: chinese-longform-drift-gate
description: 中文长篇创作（章回体小说、连载长篇、系列研究稿）的分模块输出与双层偏移审计契约。当用户要求续写/修补中文长篇、保持原文风格不走样、防止多次续写后文体漂移、要求每回收工跑闸门、或反馈“稿件越改越像电报体/论断开篇/简历式人物出场/前后穿帮”时使用。核心：单一正源按模块增量 + 机械闸门脚本 + 人工审计清单，三层缺一不可。
description_en: Two-layer drift-control contract for long-form Chinese writing (serialized fiction, chapter-based non-fiction). Split output into incremental modules against a single source file, then audit every round with a mechanical gate script (CJK count, Latin intrusions, self-correction tic, title self-reference, short-sentence ratio) plus a human checklist for what scripts cannot catch (telegraphic fragments, essayistic openings, résumé-style character entries, foreshadowing leakage, outside→inside POV). Use when continuing or repairing long Chinese manuscripts and keeping voice stable across many sessions.
---

# 中文长篇漂移闸门（Longform Drift Gate）

## 什么时候用

- 跨多轮会话续写/修补同一部中文长篇，担心文体逐轮退化。
- 用户反馈：句子越改越碎、开头变成论断、人物像投简历一样出场、前文提前泄露后文事件。
- 需要把“保持原文风格”从愿望变成可验收、可回归测试的流程。

## 为什么需要它（问题机制）

任何模型在长距离续写中都会向“总结态”漂移：短句化、评论者视角、省略场景只交代结论。单次检查看不出来，每轮 1% 的偏移几百轮后就是文体换代。对策不是“写得更仔细”，而是把审计机械化：能脚本化的进闸门，脚本兜不住的进人工清单，两者每轮必跑。

## 单一正源与分模块输出

1. 一部作品只维护一个正源文件；按回/章增量追加，用 Edit 局部修改，不另起新文件、不用多版本散件。
2. 每模块流程：立因果钩 → 写场景 → 跑闸门 → 实测字数回填进度表。
3. 字数以脚本实测 CJK 统一汉字数为准，标点不计；长篇目标先按每轮产能折算轮次预算，早声明缺口，不拿单轮快照冒充整体。
4. 就地改写前先构造完整新字符串再开写句柄（避免拼接抛异常时文件已被清空）；改写前备份 `.bak`，非 git 目录也要备。

## 文体契约（六条硬约束，按项目可增删）

1. 完整自然语言句子，禁电报体总结短句碎片（≤6 汉字的句子占比设上限）。
2. 视角外→内两段式：前半旁人看角色动作，后半沉进角色视角；禁叙述者直接断言内心。
3. 场景起笔，禁论断开篇（“某某是某某”式开头）。
4. 人物在场景中出场，禁简历式起笔（“X 的腿是小时候摔的”）。
5. 插入层（公文、书信、账目等）用该文体真实形制，不被叙述者解释。
6. 结尾落动作不落议论。

## 模块衔接与穿帮检查

- 每模块末设因果钩，下模块承接其果；转场由主角个人利害驱动，不由程序步骤驱动。
- 禁穿帮预知：角色不得提前知道后文才发生的事。用脚本核对“人物首次出场回”与“事件发生回”的先后关系。
- 修衔接不等于削肌理：详细场景描写是风格本体不是冗余；补衔接时保留并恢复被删场景。

## 双层闸门

**机械层**（低自由度，每回收工必跑）：

```bash
python scripts/gate.py <file.md> --names <书名1,书名2> --max-short 5.0
```

检查项：CJK 字数、拉丁字母侵入、“——不”自我更正幥、书名自指、短句（≤6 汉字）占比。退出码 0 为过。

**人工层**（脚本兜不住，须逐条对照）：电报体碎片、论断开篇、简历式起笔、穿帮预知、外→内视角是否落实、详细场景是否被削、因果钩是否咬合。

发现偏移即时修正并复跑，不要攒到下一模块。

## 反模式

1. 只靠“提示词里叮嘱保持风格”——没有回归机制的约定会在第十轮失效。
2. 把详细场景当拖沓删除以“紧凑衔接”。
3. 用标点计入的字符数充字数。
4. 每轮人工目测代替脚本，疲劳后漏检率上升。
5. 多正源并行（每轮一个新文件）——无法环比，漂移无从发现。
