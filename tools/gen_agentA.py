#!/usr/bin/env python3
# Diagrams for the Product (features) page, zh + en. Owner: agentA.
# 产品能力页插图（中/英），负责人 agentA。
# Run from repo root: python3 tools/gen_agentA.py
# 在仓库根目录运行：python3 tools/gen_agentA.py
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"
NAVY, NAVY2, BLUE, TEAL, INK, MUTED, LINE, SURF = "#0f2b5b", "#163a78", "#1d5fd1", "#0f8a7e", "#111827", "#6b7280", "#d3d9e4", "#f6f8fb"
AMBER = "#b7791f"

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="' + FONT + '">'
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#9fb1cf"/></marker></defs>')


def box(x, y, w, h, title, sub="", fill="#fff", stroke=LINE, tcol=INK, scol=MUTED, r=10, ts=14, ss=11.5):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
    cy = y + h / 2 + (0 if not sub else -7)
    s += f'<text x="{x+w/2}" y="{cy+5}" font-size="{ts}" font-weight="700" fill="{tcol}" text-anchor="middle">{title}</text>'
    if sub:
        s += f'<text x="{x+w/2}" y="{cy+24}" font-size="{ss}" fill="{scol}" text-anchor="middle">{sub}</text>'
    return s


def arrow(x1, y1, x2, y2, col="#9fb1cf", dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.6" marker-end="url(#ah)"{d}/>'


def ec_efficiency(lang):
    # Storage efficiency (usable / raw) by EC profile vs. 3-way replication.
    # 各纠删码档位得盘率与三副本对比。数值取自 facts.md。
    z = lang == "zh"
    t2, t3 = ("容错 2", "容错 3") if z else ("tolerates 2", "tolerates 3")
    rows = [("三副本" if z else "3 replicas", 33.3, t2, "ref"), ("EC 5+2", 71.4, t2, "auto"),
            ("EC 9+2", 81.8, t2, "auto"), ("EC 18+3", 85.7, t3, "auto"), ("EC 22+3", 88.0, t3, "manual"),
            ("EC 29+3", 90.6, t3, "hl"), ("EC 31+3", 91.2, t3, "manual")]
    W, H = 560, 480
    L, R, top, step = 130, 476, 70, 46  # bar area x-range, first row y, row pitch / 条形区域与行距
    o = [HEAD.format(w=W, h=H), f'<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="#fff" stroke="{LINE}"/>']
    o.append(f'<text x="22" y="38" font-size="17" font-weight="700" fill="{INK}">{"得盘率（可用容量 / 裸容量）" if z else "Storage efficiency (usable / raw)"}</text>')
    bottom = top + 7 * step
    for p in (0, 25, 50, 75, 100):
        x = L + (R - L) * p / 100
        o.append(f'<line x1="{x}" y1="{top-8}" x2="{x}" y2="{bottom-14}" stroke="#eef2f7"/>')
        o.append(f'<text x="{x}" y="{bottom+6}" font-size="12" fill="{MUTED}" text-anchor="middle">{p}%</text>')
    for i, (name, v, tol, kind) in enumerate(rows):
        y = top + i * step
        col = {"ref": "#c3cbd8", "auto": NAVY2, "manual": "#7d93bd", "hl": BLUE}[kind]
        w = (R - L) * v / 100
        o.append(f'<text x="{L-12}" y="{y+13}" font-size="14.5" font-weight="700" fill="{INK}" text-anchor="end">{name}</text>')
        o.append(f'<text x="{L-12}" y="{y+30}" font-size="12" fill="{MUTED}" text-anchor="end">{tol}</text>')
        o.append(f'<rect x="{L}" y="{y}" width="{w:.1f}" height="26" rx="4" fill="{col}"/>')
        o.append(f'<text x="{L+w+8:.1f}" y="{y+18}" font-size="14" font-weight="700" fill="{INK}">{v:.1f}%</text>')
    ly = H - 26
    items = [(NAVY2, "自动选型" if z else "Auto-selected"), (BLUE, "推荐 29+3" if z else "Recommended"),
             ("#7d93bd", "手动高密度" if z else "Manual"), ("#c3cbd8", "对照" if z else "Reference")]
    x = 22
    for c, t in items:
        o.append(f'<rect x="{x}" y="{ly-11}" width="13" height="13" rx="3" fill="{c}"/>')
        o.append(f'<text x="{x+19}" y="{ly}" font-size="13" fill="{MUTED}">{t}</text>')
        x += 19 + len(t) * (13 if z else 7.2) + 22
    o.append('</svg>')
    return "\n".join(o)


def disk_health(lang):
    # Four detection layers -> isolate -> storage-side rebuild -> in-place repair.
    # 四层监测 → 自动隔离 → 存储侧重建 → 原位修复。
    z = lang == "zh"
    layers = [("SMART 周期采集", "SMART polling", "跟踪劣化趋势" if z else "wear trends"),
              ("内核日志扫描", "Kernel log scan", "去抖后确认" if z else "debounced"),
              ("读写卡死看门狗", "Stuck-I/O watchdog", "读 120 s / 写 300 s" if z else "read 120 s / write 300 s"),
              ("I/O 错误滑动窗口", "I/O error window", "超阈值即隔离" if z else "isolate on threshold")]
    W, H = 560, 450
    o = [HEAD.format(w=W, h=H), f'<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="{SURF}"/>']
    o.append(f'<text x="20" y="36" font-size="14" font-weight="700" fill="{MUTED}">{"① 发现" if z else "1 · DETECT"}</text>')
    for i, (zt, et, sub) in enumerate(layers):
        y = 52 + i * 84
        o.append(box(20, y, 200, 68, zt if z else et, sub, ts=16, ss=13.5))
        o.append(f'<path d="M220 {y+34} C238 {y+34} 238 194 250 194" stroke="#9fb1cf" stroke-width="1.5" fill="none"/>')
    o.append(f'<text x="272" y="36" font-size="14" font-weight="700" fill="{MUTED}">{"② 隔离与修复" if z else "2 · ISOLATE &amp; REPAIR"}</text>')
    o.append(arrow(250, 194, 270, 92))
    o.append(box(272, 52, 250, 72, "自动隔离" if z else "Automatic isolation",
                 "退出读写，不拖慢集群" if z else "Disk leaves the I/O path", fill=NAVY, stroke=NAVY, tcol="#fff", scol="#c9d8f5", ts=16, ss=13.5))
    o.append(arrow(397, 124, 397, 146))
    o.append(box(272, 148, 250, 72, "存储侧重建" if z else "Storage-side rebuild",
                 "最劣先修 · 本地解码落盘" if z else "Worst-first, decoded locally", ts=16, ss=13.5))
    o.append(arrow(397, 220, 397, 242))
    o.append(box(272, 244, 250, 72, "换盘后原位修复" if z else "In-place repair",
                 "数据写回新盘原位置" if z else "Written back to the new disk", ts=16, ss=13.5))
    o.append(arrow(397, 316, 397, 338))
    o.append(box(272, 340, 250, 56, "恢复完整冗余" if z else "Full redundancy restored", fill="#e3f4f2", stroke="#bfe3de", tcol=TEAL, ts=16))
    o.append(f'<path d="M522 88 C548 88 548 368 524 368" stroke="{TEAL}" stroke-width="1.6" fill="none" stroke-dasharray="4 4" marker-end="url(#ah)"/>')
    o.append(f'<text x="20" y="{H-20}" font-size="13.5" fill="{MUTED}">{"绿色虚线：临时性故障恢复后，磁盘自动回到读写" if z else "Green dashed: disks recovering from a transient fault rejoin automatically"}</text>')
    o.append('</svg>')
    return "\n".join(o)


def capacity_guard(lang):
    # Three-tier capacity protection, narrow layout so it stays legible on phones.
    # 三级容量保护；窄版布局，手机上也能看清。
    z = lang == "zh"
    W, H = 460, 470
    o = [HEAD.format(w=W, h=H), f'<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="#fff" stroke="{LINE}"/>']
    o.append(f'<text x="20" y="38" font-size="18" font-weight="700" fill="{INK}">{"三级容量保护" if z else "Three-tier capacity protection"}</text>')
    tiers = [
        ("集群级" if z else "Cluster", "整体水位 ≥ 99%（默认）" if z else "Cluster usage ≥ 99% (default)",
         "停止新写入，修复照常" if z else "New writes stop, repair continues", "#e8f0fd", NAVY2, 0.99),
        ("单盘级" if z else "Disk", "单盘 ≥ 99.5%（可配到 99.8%）" if z else "Disk ≥ 99.5% (configurable to 99.8%)",
         "退出写入环，只接修复" if z else "Leaves the write ring, repair only", "#fbf1df", AMBER, 0.995),
        ("保底" if z else "Floor", "单盘剩余 &lt; 4 GiB" if z else "Disk free space &lt; 4 GiB",
         "完全只读" if z else "Disk becomes read-only", "#fde8e8", "#b42318", 1.0),
    ]
    for i, (lvl, cond, act, bg, col, fill) in enumerate(tiers):
        y = 60 + i * 124
        o.append(f'<rect x="20" y="{y}" width="420" height="110" rx="10" fill="#fff" stroke="{LINE}"/>')
        o.append(f'<rect x="20" y="{y}" width="6" height="110" rx="3" fill="{col}"/>')
        pw = 68 if z else 76
        o.append(f'<rect x="42" y="{y+16}" width="{pw}" height="26" rx="13" fill="{bg}"/>')
        o.append(f'<text x="{42+pw/2}" y="{y+34}" font-size="13.5" font-weight="700" fill="{col}" text-anchor="middle">{lvl}</text>')
        gx, gw = 250, 170
        o.append(f'<rect x="{gx}" y="{y+24}" width="{gw}" height="10" rx="5" fill="#eef2f7"/>')
        o.append(f'<rect x="{gx}" y="{y+24}" width="{gw*fill:.1f}" height="10" rx="5" fill="{col}" opacity=".85"/>')
        o.append(f'<text x="42" y="{y+70}" font-size="16" font-weight="700" fill="{INK}">{cond}</text>')
        o.append(f'<text x="42" y="{y+95}" font-size="15" fill="{col}" font-weight="600">→ {act}</text>')
    o.append(f'<text x="20" y="{H-18}" font-size="13" fill="{MUTED}">{"控制台据此实时给出“当前最大可写 / 保守可写”" if z else "The console derives max / conservative writable from these limits"}</text>')
    o.append('</svg>')
    return "\n".join(o)


def hole_reuse(lang):
    # Exact-size hole reuse and crash-safe compaction on a raw disk.
    # 裸盘上的同尺寸空洞复用与崩溃安全整理。
    z = lang == "zh"
    W, H = 580, 420
    cell, x0 = 59, 22
    o = [HEAD.format(w=W, h=H), f'<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="{SURF}"/>']

    def lane(y, cells, title):
        o.append(f'<text x="{x0}" y="{y-14}" font-size="15.5" font-weight="700" fill="{INK}">{title}</text>')
        x = x0
        for kind in cells:
            fill, stroke = {"d": ("#fff", LINE), "h": ("#fff", "#9fb1cf"), "n": ("#e8f0fd", BLUE),
                            "m": ("#e3f4f2", TEAL), "f": ("#eef2f7", "#eef2f7")}[kind]
            dash = ' stroke-dasharray="4 3"' if kind == "h" else ""
            o.append(f'<rect x="{x}" y="{y}" width="{cell-5}" height="44" rx="5" fill="{fill}" stroke="{stroke}"{dash}/>')
            x += cell

    lane(70, "dhddhdddf", "① 删除：进回收站，冻结期后形成空洞" if z else "1 · Delete: recycle bin, then a hole")
    lane(176, "dnddhdddf", "② 复用：同尺寸的新分片直接写入空洞" if z else "2 · Reuse: same-size shard fills the hole")
    lane(296, "dnddmddff", "③ 整理：尾部数据搬入空洞，回读校验后截断" if z else "3 · Compact: move tail data in, verify, truncate")
    a, b = x0 + 7 * cell + 27, x0 + 4 * cell + 27
    o.append(f'<path d="M{a} 344 C{a} 372 {b} 372 {b} 346" stroke="{TEAL}" stroke-width="1.8" fill="none" marker-end="url(#ah)"/>')
    fx = x0 + 7 * cell - 3
    o.append(f'<line x1="{fx}" y1="290" x2="{fx}" y2="346" stroke="{AMBER}" stroke-width="2"/>')
    o.append(f'<text x="{fx+8}" y="323" font-size="12.5" font-weight="600" fill="{AMBER}">{"新写入前沿" if z else "new frontier"}</text>')
    ly = H - 22
    items = [("#fff", LINE, "数据" if z else "Data"), ("#fff", "#9fb1cf", "空洞" if z else "Hole"),
             ("#e8f0fd", BLUE, "复用写入" if z else "Reused"), ("#e3f4f2", TEAL, "搬入数据" if z else "Moved")]
    x = x0
    for f, s, t in items:
        o.append(f'<rect x="{x}" y="{ly-12}" width="14" height="14" rx="3" fill="{f}" stroke="{s}"/>')
        o.append(f'<text x="{x+20}" y="{ly}" font-size="13.5" fill="{MUTED}">{t}</text>')
        x += 20 + len(t) * (13 if z else 7.2) + 20
    o.append(f'<text x="{W-22}" y="{ly}" font-size="13" fill="{MUTED}" text-anchor="end">{"元数据零改动 · 崩溃安全" if z else "No metadata change · crash-safe"}</text>')
    o.append('</svg>')
    return "\n".join(o)


for lang in ("zh", "en"):
    for name, fn in (("ec-efficiency", ec_efficiency), ("disk-health", disk_health),
                     ("capacity-guard", capacity_guard), ("hole-reuse", hole_reuse)):
        open(f"images/{name}-{lang}.svg", "w", encoding="utf-8").write(fn(lang) + "\n")
print("ok")
