#!/usr/bin/env python3
# Generate whitepaper-only diagrams (zh + en): images/wp-*-{zh,en}.svg
# 生成白皮书专用插图（中/英）：images/wp-*-{zh,en}.svg
# Style follows tools/gen_diagrams.py (same palette, box/arrow look). Canvas is 900 wide and fonts are
# larger than the website diagrams so text stays >= ~7pt when printed full width on A4.
# 风格与 tools/gen_diagrams.py 一致（同一配色、同样的方框与箭头）。画布宽 900、字号比网站图大，
# 保证在 A4 全宽打印时文字不小于约 7pt。
import os

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"
NAVY, NAVY2, BLUE, TEAL, INK, MUTED, LINE, SURF = "#0f2b5b", "#163a78", "#1d5fd1", "#0f8a7e", "#111827", "#6b7280", "#d3d9e4", "#f6f8fb"
AMBER, GREY = "#b7791f", "#9ca3af"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
W = 900

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="' + FONT + '">'
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#9fb1cf"/></marker></defs>')


def esc(s):
    # XML-escape text. / 文本做 XML 转义。
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def T(x, y, s, size=14, col=INK, weight="400", anchor="start"):
    # Text helper. / 文本辅助函数。
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{col}" text-anchor="{anchor}">{esc(s)}</text>'


def box(x, y, w, h, title, sub="", fill="#fff", stroke=LINE, tcol=INK, scol=MUTED, r=10, ts=16, ss=13):
    # Rounded box with a title and optional multi-line subtitle ("\n").
    # 圆角方框：标题 + 可选多行副标题（用 \n 分行）。
    lines = sub.split("\n") if sub else []
    block = ts + len(lines) * (ss + 5)
    top = y + (h - block) / 2 + ts - 2
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
    s += T(x + w / 2, top, title, ts, tcol, "700", "middle")
    for i, line in enumerate(lines):
        s += T(x + w / 2, top + (i + 1) * (ss + 5) + 2, line, ss, scol, "400", "middle")
    return s


def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#9fb1cf" stroke-width="1.8" marker-end="url(#ah)"/>'


def canvas(h):
    return [HEAD.format(w=W, h=h), f'<rect width="{W}" height="{h}" rx="14" fill="{SURF}"/>']


# 1. Raw capacity per 1 PB usable: 3x replication vs EC tiers. / 每 1 PB 可用容量所需裸容量。
def cost(lang):
    z = lang == "zh"
    rows = [("三副本" if z else "3× replication", 1, 2, True), ("EC 5+2", 5, 2, False), ("EC 9+2", 9, 2, False),
            ("EC 18+3", 18, 3, False), ("EC 22+3", 22, 3, False), ("EC 29+3", 29, 3, False)]
    H = 400
    o = canvas(H)
    o.append(T(30, 42, "每 1 PB 可用容量需要的裸容量" if z else "Raw capacity required per 1 PB of usable capacity", 18, NAVY, "700"))
    o.append(T(30, 68, "数值 = (k+m)/k；容错 = 可同时丢失的分片（盘或节点）数" if z else
               "Value = (k+m)/k. Tolerance = shards (disks or nodes) that can be lost at once.", 13.5, MUTED))
    x0, bw_max, top, rh = 170, 370, 96, 46
    for i, (lab, k, m, rep) in enumerate(rows):
        y = top + i * rh
        v = (k + m) / k
        bw = bw_max * v / 3.0
        col = GREY if rep else (NAVY if k >= 18 else BLUE)
        o.append(T(x0 - 14, y + 23, lab, 15, INK, "600", "end"))
        o.append(f'<rect x="{x0}" y="{y+6}" width="{bw:.1f}" height="24" rx="5" fill="{col}"/>')
        o.append(T(x0 + bw + 10, y + 24, f"{v:.2f} PB", 15, INK, "700"))
        eff = 100 * k / (k + m)
        o.append(T(W - 30, y + 24, (f"得盘率 {eff:.1f}% · 容错 {m}" if z else f"{eff:.1f}% efficient · tolerates {m}"), 14, MUTED, "400", "end"))
    o.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{top + len(rows) * rh}" stroke="{LINE}"/>')
    o.append(T(30, H - 22, "示意：未计入系统预留与拒写线水位。" if z else "Illustrative: excludes system reserve and the write-reject watermark.", 13, MUTED))
    o.append("</svg>")
    return "\n".join(o)


# 2. Write / read data flow (FUSE path). / 写入与读取数据流（FUSE 路径）。
def dataflow(lang):
    z = lang == "zh"
    H = 380
    o = canvas(H)
    o.append(T(20, 36, "写入路径" if z else "WRITE PATH", 15, BLUE, "700"))
    ws = ([("缓冲", "客户端攒满 256 MB"), ("申请条带", "向 Master 申请"), ("EC 编码", "客户端本地完成"),
           ("并行写分片", "32 片 → 32 个节点"), ("提交元数据", "条带级记录")] if z else
          [("Buffer", "client fills 256 MB"), ("Allocate", "stripe from Master"), ("Encode", "locally on client"),
           ("Write shards", "32 shards → 32 nodes"), ("Commit", "stripe metadata")])
    bw, gap = 160, 15
    for i, (a, b) in enumerate(ws):
        x = 20 + i * (bw + gap)
        hl = i == 3
        o.append(box(x, 50, bw, 80, a, b, fill=NAVY if hl else "#fff", stroke=NAVY if hl else LINE,
                     tcol="#fff" if hl else INK, scol="#c9d8f5" if hl else MUTED))
        if i < len(ws) - 1:
            o.append(arrow(x + bw + 1, 90, x + bw + gap - 1, 90))
    o.append(T(20, 184, "读取路径" if z else "READ PATH", 15, TEAL, "700"))
    rs = ([("取位置", "向 Master 查询条带"), ("并行读分片", "每片 CRC32 校验"), ("缺片实时解码", "任意 29 片即可还原"),
           ("返回数据", "流式读取同样校验")] if z else
          [("Locate", "stripe from Master"), ("Read shards", "CRC32 on every shard"), ("Decode on the fly", "any 29 shards suffice"),
           ("Return data", "streaming reads verified")])
    bw2, gap2 = 205, 13
    for i, (a, b) in enumerate(rs):
        x = 20 + i * (bw2 + gap2)
        o.append(box(x, 198, bw2, 80, a, b, stroke=TEAL if i == 2 else LINE))
        if i < len(rs) - 1:
            o.append(arrow(x + bw2 + 1, 238, x + bw2 + gap2 - 1, 238))
    o.append(T(20, 320, "以 29+3 为例：每个分片约 8.8 MiB。" if z else "Shown for EC 29+3: each shard is about 8.8 MiB.", 13.5, MUTED))
    o.append(T(20, 344, "数据在客户端与存储节点之间直接传输，Master 只处理元数据。" if z else
               "Data moves directly between clients and storage nodes; the Master handles metadata only.", 13.5, MUTED))
    o.append("</svg>")
    return "\n".join(o)


# 3. Raw-disk layout (illustrative). / 裸盘布局（示意）。
def disk(lang):
    z = lang == "zh"
    H = 330
    o = canvas(H)
    o.append(T(30, 40, "单块 HDD（块设备，无本地文件系统）" if z else "One HDD (raw block device, no local file system)", 17, NAVY, "700"))
    x, y, h = 30, 78, 64
    sh = "分片" if z else "shard"
    segs = [(74, NAVY, "超级块" if z else "SB"), (92, BLUE, sh), (92, BLUE, sh), (84, "#fff", "空洞" if z else "hole"),
            (92, BLUE, sh), (92, BLUE, sh), (92, BLUE, sh), (222, "#fff", "")]
    cx = x
    for w, f, lab in segs:
        dash = ' stroke-dasharray="5 4"' if f == "#fff" and lab else ""
        o.append(f'<rect x="{cx}" y="{y}" width="{w}" height="{h}" fill="{f}" stroke="{LINE if f == "#fff" else "#fff"}"{dash}/>')
        if lab:
            o.append(T(cx + w / 2, y + h / 2 + 5, lab, 14, "#fff" if f != "#fff" else MUTED, "600", "middle"))
        cx += w
    o.append(f'<rect x="{x}" y="{y}" width="{cx - x}" height="{h}" fill="none" stroke="{NAVY}" stroke-width="1.4" rx="4"/>')
    front = x + sum(s[0] for s in segs[:-1])
    o.append(f'<line x1="{front}" y1="{y - 10}" x2="{front}" y2="{y + h + 10}" stroke="{TEAL}" stroke-width="2.6"/>')
    o.append(T(front + 10, y + h + 28, "写入前沿 →" if z else "Write frontier →", 14, TEAL, "700"))
    o.append(T(front + 10, y + h + 48, "顺序追加，4 KB 对齐" if z else "sequential append, 4 KB aligned", 13, TEAL))
    o.append(T(x, y + h + 28, "主 / 备超级块（CRC 保护）" if z else "Primary + backup superblock (CRC)", 14, NAVY, "700"))
    o.append(T(x, y + h + 48, "节点 ID · 盘 ID · 盘 UUID" if z else "node ID · disk ID · disk UUID", 13, NAVY))
    hx = x + 74 + 184 + 42
    o.append(T(hx, y - 14, "空洞：冻结期后可被同尺寸写入复用" if z else "Hole: reused by same-size writes after the freeze period", 13, MUTED, "400", "middle"))
    items = ([("本地索引 BadgerDB", "每次读取都做 CRC32 校验"), ("崩溃恢复", "从写入前沿向前扫描补齐索引"), ("碎片整理", "尾部数据搬入空洞后截断回收")] if z else
             [("Local index (BadgerDB)", "CRC32 verified on every read"), ("Crash recovery", "scan forward from the frontier"),
              ("Compaction", "move tail data into holes, truncate")])
    for i, (a, b) in enumerate(items):
        o.append(box(30 + i * 284, 230, 272, 72, a, b, ts=15))
    o.append("</svg>")
    return "\n".join(o)


# 4. Three-level capacity protection. / 三级容量保护。
def capacity(lang):
    z = lang == "zh"
    H = 300
    o = canvas(H)
    lv = ([("集群拒写线", "默认 99%", "整体达到后停止新写入\n修复照常进行", BLUE),
           ("单盘写入上限", "默认 99.5%，可配到 99.8%", "该盘退出写入环\n只接收修复数据", NAVY),
           ("单盘只读", "剩余 < 4 GiB", "完全只读\n保护盘上已有数据", AMBER)] if z else
          [("Cluster reject line", "default 99%", "New writes stop;\nrepair continues", BLUE),
           ("Per-disk write cap", "default 99.5%, up to 99.8%", "Disk leaves the write ring;\naccepts repair data only", NAVY),
           ("Per-disk read-only", "< 4 GiB free", "Fully read-only to protect\nthe data already on it", AMBER)])
    for i, (a, b, c, col) in enumerate(lv):
        x = 30 + i * 284
        o.append(f'<rect x="{x}" y="26" width="272" height="170" rx="10" fill="#fff" stroke="{LINE}"/>')
        o.append(f'<rect x="{x}" y="26" width="272" height="6" rx="3" fill="{col}"/>')
        o.append(T(x + 20, 68, f"{i+1}", 26, col, "800"))
        o.append(T(x + 50, 66, a, 16, INK, "700"))
        o.append(T(x + 20, 104, b, 15, col, "700"))
        for j, line in enumerate(c.split("\n")):
            o.append(T(x + 20, 140 + j * 22, line, 14, MUTED))
    o.append(T(30, 232, "控制台实时显示「当前最大可写」与「当前保守可写」。" if z else
               "The console shows “max writable now” and “conservative writable” in real time.", 14.5, INK))
    o.append(T(30, 260, "阈值为默认值，可按集群配置。" if z else "Thresholds shown are defaults and can be configured per cluster.", 13, MUTED))
    o.append("</svg>")
    return "\n".join(o)


# 5. Self-healing flow. / 自愈流程。
def heal(lang):
    z = lang == "zh"
    H = 440 if not z else 410
    o = canvas(H)
    src = (["SMART 周期采集", "内核日志扫描", "读写卡死看门狗", "I/O 错误窗口", "后台 CRC 巡检", "放置审计"] if z else
           ["SMART polling", "Kernel log scan", "Hang watchdog", "I/O error window", "CRC scrub", "Placement audit"])
    o.append(T(20, 34, "发现问题" if z else "DETECT", 15, BLUE, "700"))
    for i, s in enumerate(src):
        x = 20 + i * 145
        o.append(f'<rect x="{x}" y="46" width="135" height="44" rx="8" fill="#fff" stroke="{LINE}"/>')
        o.append(T(x + 67.5, 73, s, 13.5, INK, "600", "middle"))
    o.append(f'<path d="M450 94 L450 124" stroke="#9fb1cf" stroke-width="1.8" marker-end="url(#ah)"/>')
    steps = ([("隔离", "故障盘自动退出\n恢复后自动回归"), ("建任务", "缺片最多的先修\n数十万条带分钟级入队"),
              ("分布式领取", "多个 Master\n并行领取任务"), ("本地重建", "拉取存活分片\n本地解码落盘")] if z else
             [("Isolate", "faulty disk taken out;\nrejoins when healthy"), ("Queue", "worst stripes first;\n100,000s queued in minutes"),
              ("Dispatch", "claimed in parallel\nby multiple Masters"), ("Rebuild", "pull surviving shards;\ndecode and write locally")])
    bw, gap = 200, 20
    for i, (a, b) in enumerate(steps):
        x = 20 + i * (bw + gap)
        hl = i == 3
        o.append(box(x, 128, bw, 100, a, b, fill=NAVY if hl else "#fff", stroke=NAVY if hl else LINE,
                     tcol="#fff" if hl else INK, scol="#c9d8f5" if hl else MUTED))
        if i < 3:
            o.append(arrow(x + bw + 1, 178, x + bw + gap - 1, 178))
    o.append(T(20, 266, "集群整体达到拒写线时，修复仍可进行。" if z else "Repair continues even after the cluster reaches its reject line.", 14, MUTED))
    o.append(f'<rect x="20" y="292" width="860" height="{118 if not z else 92}" rx="10" fill="#fff" stroke="{TEAL}"/>')
    o.append(T(44, 328, "换盘之后：原位修复" if z else "After a disk is replaced: in-place repair", 16, TEAL, "700"))
    o.append(T(44, 358, "把该盘原有的数据重建后写回新盘的原位置。" if z else
               "Data that lived on the failed disk is rebuilt and written back", 14.5, INK))
    if not z:
        o.append(T(44, 382, "to the same positions on the new disk.", 14.5, INK))
    o.append("</svg>")
    return "\n".join(o)


def main():
    for name, fn in (("cost", cost), ("dataflow", dataflow), ("disk", disk), ("capacity", capacity), ("heal", heal)):
        for lang in ("zh", "en"):
            p = os.path.join(OUT, f"wp-{name}-{lang}.svg")
            with open(p, "w", encoding="utf-8") as f:
                f.write(fn(lang))
            print("wrote", os.path.relpath(p))


if __name__ == "__main__":
    main()
