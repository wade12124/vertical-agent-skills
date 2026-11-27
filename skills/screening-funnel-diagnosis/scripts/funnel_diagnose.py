#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选章程 · 闸门效率诊断
用法:
    python funnel_diagnose.py <pool.csv> [--config gate_config.py]

输出四步：单闸通过率 / 漏斗回放 / 留一法 / Jaccard 冗余度 / 候选质量对比

gate_config.py 需定义:
    GATES        : [(label, fn), ...]      只放硬闸，不要放分段复核通道
    FINAL        : (label, fn)             终局口径闸（收益率带等）
    QUALITY_COLS : [(key, 显示名), ...]     候选质量对比用列
    FIELD_MAP    : {字段名: CSV 列索引}      0-based
"""
import sys, csv, argparse, importlib.util, statistics as st
from collections import OrderedDict


def load_config(path):
    if not path:
        return EXAMPLE
    spec = importlib.util.spec_from_file_location("gate_config", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def num(s):
    """清洗数据导出格式： ="1.234" / =1.234 / 1,234 / 空"""
    if s is None:
        return None
    s = str(s).replace('="', '').replace('"', '').replace('=', '').replace(',', '').strip()
    if s in ('', '-', '--', 'nan', 'None', 'N/A'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def ok(v, lo=None, hi=None):
    """区间判定；v 为 None 一律不通过"""
    if v is None:
        return False
    if lo is not None and v < lo:
        return False
    if hi is not None and v > hi:
        return False
    return True


# ---------------- 内置示例配置（演示用，非投资建议）----------------
class EXAMPLE:
    FIELD_MAP = {'name': 2, 'ind1': 3, 'pb': 7, 'mcap': 9, 'pledge': 11,
                 'pbq': 12, 'roe': 13, 'debt': 14, 'gw': 15, 'div': 17, 'fcf': 19}
    HAS_HEADER = True
    GATES = [
        ("G1 便宜 PB<=1.6 且三年分位<=50%",
         lambda r: ok(r['pb'], None, 1.6) and ok(r['pbq'], None, .50)),
        ("G2 盈利 ROE>=4%", lambda r: ok(r['roe'], .04)),
        ("G3 负债率<=45%", lambda r: ok(r['debt'], None, .45)),
        ("G4 商誉/净资产<=5%", lambda r: ok(r['gw'], None, .05)),
        ("G5a FCF>0", lambda r: ok(r['fcf'], 1e-9)),
        ("质押<=20%", lambda r: ok(r['pledge'], None, .20)),
    ]
    FINAL = ("股息带 4%~6%", lambda r: ok(r['div'], .04, .06))
    QUALITY_COLS = [('pb', 'PB中位'), ('pbq', 'PB分位中位'), ('roe', 'ROE中位'),
                    ('debt', '负债率中位'), ('div', '股息率中位')]


def read_pool(path, cfg):
    fm = cfg.FIELD_MAP
    maxidx = max(fm.values())
    rows = []
    with open(path, encoding='utf-8-sig') as f:
        for i, x in enumerate(csv.reader(f)):
            if getattr(cfg, 'HAS_HEADER', True) and i == 0:
                continue
            if len(x) <= maxidx or not x[fm.get('name', 2)]:
                continue
            rows.append({k: (x[j] if k == 'name' or k == 'ind1' else num(x[j]))
                         for k, j in fm.items()})
    return rows


def median(g, k):
    v = [r[k] for r in g if r.get(k) is not None]
    return st.median(v) if v else float('nan')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_path')
    ap.add_argument('--config', default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    rows = read_pool(args.csv_path, cfg)
    GATES = cfg.GATES
    FLBL, FFN = cfg.FINAL
    N = len(rows)
    if N == 0:
        print("池子为空，检查 FIELD_MAP 与列索引"); return

    W = 92
    print("=" * W)
    print(f"闸门效率诊断 · 基准池 {N} 只")
    print("=" * W)

    # ---- 1 单闸 ----
    print("\n【1】单闸独立通过率（各自单独作用于全池）")
    print(f"  {'闸门':<34}{'通过':>7}{'占比':>9}{'淘汰':>7}")
    for lb, fn in GATES:
        c = sum(1 for r in rows if fn(r))
        flag = "  ← 全通闸/空转嫌疑" if c == N else ""
        print(f"  {lb:<34}{c:>7}{c/N:>9.1%}{N-c:>7}{flag}")
    c = sum(1 for r in rows if FFN(r))
    print(f"  {FLBL+'（终局口径）':<34}{c:>7}{c/N:>9.1%}{N-c:>7}")

    # ---- 2 漏斗 ----
    print("\n【2】按顺序漏斗回放")
    print(f"  {'步骤':<38}{'存活':>7}{'本步淘汰':>10}{'累计留存':>10}")
    alive, prev = rows[:], N
    print(f"  {'基准池':<38}{prev:>7}{'':>10}{100.0:>9.1f}%")
    for lb, fn in GATES:
        new = [r for r in alive if fn(r)]
        print(f"  {lb:<38}{len(new):>7}{prev-len(new):>10}{len(new)/N:>9.1%}")
        alive, prev = new, len(new)
    hard_surv = alive
    fin = [r for r in hard_surv if FFN(r)]
    print(f"  {'→ ' + FLBL:<38}{len(fin):>7}   (终局候选)")

    # ---- 3 留一法 ----
    print("\n【3】留一法：单独放宽某闸，终局候选能多出多少")
    base = len(fin)
    print(f"  {'放宽该闸':<38}{'终局候选':>9}{'新增':>8}{'增幅':>9}")
    print(f"  {'（全闸基准）':<38}{base:>9}{'':>8}{'':>9}")
    loo = []
    # 3a 硬闸逐个放宽
    for i, (lb, fn) in enumerate(GATES):
        keep = [g for j, g in enumerate(GATES) if j != i]
        s2 = [r for r in rows if all(g[1](r) for g in keep)]
        b2 = sum(1 for r in s2 if FFN(r))
        loo.append((lb, b2, b2 - base, (b2 / base - 1) if base else 0))
        mark = "  ← 空转闸" if b2 == base else ""
        print(f"  {'− ' + lb:<38}{b2:>9}{b2-base:>+8}{(b2/base-1) if base else 0:>+8.0%}{mark}")
    # 3b 终局口径闸放宽 = 硬闸幸存者全部成为候选
    b2 = len(hard_surv)
    loo.append((FLBL, b2, b2 - base, (b2 / base - 1) if base else 0))
    print(f"  {'− ' + FLBL + '（终局闸）':<38}{b2:>9}{b2-base:>+8}{(b2/base-1) if base else 0:>+8.0%}")
    top = max(loo, key=lambda t: t[1]) if loo else None
    total_gain = sum(max(0, t[1] - base) for t in loo)
    if top and top[1] > base:
        share = (top[1] - base) / total_gain if total_gain else 0
        print(f"\n  → 边际约束力最强：{top[0]}（{top[2]:+d} 只，{top[3]:+.0%}）")
        print(f"    它贡献了全部增量候选的 {share:.0%}"
              + ("  ← 稀缺性高度集中于单一闸" if share >= 0.5 else "  ← 约束较分散"))

    # ---- 4 Jaccard ----
    print("\n【4】Jaccard 冗余度（1.00=集合完全相同；≈0=完全独立）")
    S = OrderedDict((lb, {r['name'] for r in rows if fn(r)}) for lb, fn in GATES)
    S[FLBL] = {r['name'] for r in rows if FFN(r)}
    keys = list(S)
    hdr = "  " + " " * 26 + "".join(f"{k.split()[0][:6]:>8}" for k in keys)
    print(hdr)
    for a in keys:
        line = f"  {a[:25]:<26}"
        for b in keys:
            u = len(S[a] | S[b])
            line += f"{len(S[a] & S[b]) / u if u else 0:>8.2f}"
        mark = "  ← 全通闸，本行数值退化为其它闸通过率" if len(S[a]) == N else ""
        print(line + mark)

    # ---- 5 候选质量对比 ----
    print("\n【5】候选质量对比：被挡住的 vs 通过的（中位数）")
    blocked = [r for r in hard_surv if not FFN(r)]
    groups = [("通过「" + FLBL + "」", fin), ("被挡在同一闸外", blocked), ("硬闸全体", hard_surv)]
    hdr = f"  {'组':<26}{'数量':>6}" + "".join(f"{t:>13}" for _, t in cfg.QUALITY_COLS)
    print(hdr)
    for nm, g in groups:
        line = f"  {nm:<26}{len(g):>6}"
        for k, _ in cfg.QUALITY_COLS:
            v = median(g, k)
            line += f"{v:>13.3f}" if abs(v) < 10 else f"{v:>13.1f}"
        print(line)
    print("\n  判读：若「被挡住的」组在其它维度上的中位数优于「通过的」组，")
    print("        说明该闸不是提高质量，而是用一个维度换另一个维度（既要又要的代价）。")
    print("        注意：执行前先核对原章程是否有「分段复核通道」——若有，")
    print("        这些被挡标的可能本来就能走复核通道被捞回，勿直接判定为漏损。")

    print("\n" + "=" * W)
    print("提醒：本脚本输出为筛选机制的效率诊断，不构成投资建议。")
    print("      任何阈值/参数的改动，须走该策略自身的修订流程。")
    print("=" * W)


if __name__ == '__main__':
    main()
