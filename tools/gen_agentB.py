#!/usr/bin/env python3
# Diagrams for the Architecture page (write path, read path, stripe placement,
# raw-disk layout, deployment topology), zh + en, same style as gen_diagrams.py.
# 技术架构页插图（写入、读取、条带放置、裸盘布局、部署拓扑），中英各一份，风格同 gen_diagrams.py。
# Run from the repo root: python3 tools/gen_agentB.py
# 在仓库根目录运行：python3 tools/gen_agentB.py
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"
NAVY, NAVY2, BLUE, TEAL, INK, MUTED, LINE, SURF = "#0f2b5b", "#163a78", "#1d5fd1", "#0f8a7e", "#111827", "#6b7280", "#d3d9e4", "#f6f8fb"
AMBER = "#b7791f"
GREY = "#9fb1cf"
W = 880


def esc(t):
    # XML-escape label text. / 转义标签中的 XML 特殊字符。
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, title, sub="", fill="#fff", stroke=LINE, tcol=INK, scol=MUTED, r=10, ts=15, ss=12.5, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"{d}/>'
    cy = y + h / 2 + (0 if not sub else -8)
    s += f'<text x="{x+w/2}" y="{cy+5}" font-size="{ts}" font-weight="700" fill="{tcol}" text-anchor="middle">{esc(title)}</text>'
    if sub:
        s += f'<text x="{x+w/2}" y="{cy+25}" font-size="{ss}" fill="{scol}" text-anchor="middle">{esc(sub)}</text>'
    return s


def text(x, y, s, size=12.5, col=MUTED, anchor="start", weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'


def line(x1, y1, x2, y2, col=GREY, dash=None, head=True, sw=1.6):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#ah)"' if head else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{sw}"{m}{d}/>'


def path(d, col=GREY, dash=None, head=True, sw=1.6):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#ah)"' if head else ""
    return f'<path d="{d}" stroke="{col}" stroke-width="{sw}" fill="none"{m}{da}/>'


def badge(x, y, n, col=BLUE):
    # Numbered step marker. / 步骤编号圆点。
    return (f'<circle cx="{x}" cy="{y}" r="11" fill="{col}"/>'
            f'<text x="{x}" y="{y+4.5}" font-size="12.5" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')


def head(h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="%s">' % (W, h, FONT) +
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="#9fb1cf"/></marker>'
            '<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="7" height="7" fill="#fbf1df"/><line x1="0" y1="0" x2="0" y2="7" stroke="#e6c48a" stroke-width="3"/></pattern></defs>'
            f'<rect x="0" y="0" width="{W}" height="{h}" rx="14" fill="{SURF}"/>')


def shard_row(o, x0, y, h, n=32, k=29, failed=(), total_w=820):
    # One stripe drawn as n shard tiles (k data + parity). / 一条条带画成 n 个分片方块。
    step = total_w / n
    w = step - 4
    centers = []
    for i in range(n):
        x = x0 + i * step
        cx = x + w / 2
        centers.append(cx)
        if i in failed:
            o.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="4" fill="#fff" stroke="{GREY}" stroke-dasharray="3 3"/>')
            o.append(f'<path d="M{cx-6:.1f} {y+h/2-6} l12 12 M{cx+6:.1f} {y+h/2-6} l-12 12" stroke="{AMBER}" stroke-width="2"/>')
        else:
            col = BLUE if i < k else TEAL
            o.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="4" fill="{col}" opacity="{0.9 if i < k else 1}"/>')
    return centers, step


def brace(o, x1, x2, y, label, col=MUTED):
    o.append(path(f"M{x1} {y} v6 H{x2} v-6", col=LINE, head=False, sw=1.4))
    o.append(text((x1 + x2) / 2, y + 24, label, 12.5, col, "middle"))


# --------------------------------------------------------------------------
def write_flow(z):
    T = lambda a, b: a if z else b
    H = 430
    o = [head(H)]
    # client / 客户端
    o.append(f'<rect x="30" y="30" width="350" height="190" rx="12" fill="#fff" stroke="{LINE}"/>')
    o.append(text(50, 58, T("客户端（ksfs）", "Client (ksfs)"), 15, INK, weight="700"))
    o.append(box(50, 72, 310, 50, T("写缓冲攒满 256 MB", "Buffer writes up to 256 MB"), fill=SURF, stroke=SURF, ts=14))
    o.append(badge(50, 72, 1))
    o.append(box(50, 140, 310, 62, T("本地 EC 编码（29+3）", "Local EC encode (29+3)"),
                 T("29 个数据分片 + 3 个校验分片，每片约 8.8 MB", "29 data + 3 parity shards, ≈8.8 MB each"), fill=SURF, stroke=SURF, ts=14))
    o.append(badge(50, 140, 3))
    # master + mongo / Master 与 MongoDB
    o.append(box(550, 30, 180, 70, T("Master（Leader）", "Master (leader)"), T("分配条带与目标节点", "allocates stripe + nodes"),
                 fill=NAVY, stroke=NAVY, tcol="#fff", scol="#c9d8f5"))
    o.append(box(760, 30, 100, 70, "MongoDB", T("多数派写入", "majority write"), ts=14))
    o.append(line(730, 65, 758, 65))
    o.append(line(380, 50, 548, 50))
    o.append(badge(400, 50, 2))
    o.append(text(418, 42, T("申请条带", "request stripe"), 12.5))
    o.append(line(548, 82, 382, 82, dash="5 4"))
    o.append(text(392, 100, T("返回条带 ID 与 32 个节点", "returns stripe ID + 32 nodes"), 12))
    # commit / 提交元数据
    o.append(path("M380 190 H640 V102"))
    o.append(badge(470, 190, 5))
    o.append(text(488, 182, T("全部分片写完后提交元数据", "commit metadata after all shards land"), 12.5))
    # shards / 分片
    centers, step = shard_row(o, 30, 300, 46)
    for i in (0, 7, 15, 23, 31):
        o.append(line(205, 220, centers[i], 298, col=BLUE, dash="6 4"))
    o.append(badge(530, 236, 4))
    o.append(text(548, 241, T("并行写入 32 个不同节点", "parallel write to 32 different nodes"), 12.5, BLUE, weight="600"))
    o.append(text(30, 410, T("每个节点只存放这条条带的 1 个分片", "Each node holds exactly one shard of this stripe"), 12.5, INK, weight="600"))
    brace(o, 30, 30 + 29 * step - 4, 352, T("29 个数据分片", "29 data shards"))
    brace(o, 30 + 29 * step, 850, 352, T("3 个校验分片", "3 parity"))
    o.append(text(850, 410, T("示意：以 EC 29+3 为例", "Illustrative: EC 29+3"), 11.5, MUTED, "end"))
    o.append('</svg>')
    return "\n".join(o)


def read_flow(z):
    T = lambda a, b: a if z else b
    H = 430
    o = [head(H)]
    o.append(box(30, 30, 300, 64, T("客户端", "Client"), T("ksfs 挂载 / S3 网关", "ksfs mount / S3 gateway"), ts=15))
    o.append(box(550, 30, 300, 64, "Master", T("返回条带的 32 个分片位置", "returns locations of the 32 shards"),
                 fill=NAVY, stroke=NAVY, tcol="#fff", scol="#c9d8f5"))
    o.append(line(330, 52, 548, 52))
    o.append(badge(352, 52, 1))
    o.append(text(370, 44, T("查询条带位置", "look up stripe"), 12.5))
    o.append(line(548, 76, 332, 76, dash="5 4"))
    # shards / 分片
    failed = (5, 17, 29)
    o.append(badge(41, 150, 2))
    o.append(text(60, 155, T("并行读取分片：每片校验 CRC32，并核对条带 ID 与分片序号", "Read shards in parallel — CRC32 plus stripe-ID / shard-index check on every shard"), 13, INK, weight="600"))
    o.append(line(180, 94, 180, 132))
    centers, step = shard_row(o, 30, 172, 46, failed=failed)
    for i, cx in enumerate(centers):
        if i not in failed and i % 4 == 1:
            o.append(line(cx, 218, cx, 266, col=BLUE, dash="5 4"))
    # decoder / 解码
    o.append(f'<rect x="30" y="268" width="820" height="76" rx="12" fill="#fff" stroke="{LINE}"/>')
    o.append(badge(52, 290, 3))
    o.append(text(72, 296, T("缺片实时解码（Reed-Solomon，SIMD 加速）", "On-the-fly decode (Reed-Solomon, SIMD)"), 15, INK, weight="700"))
    o.append(text(72, 324, T("缺失或校验不符的分片 ≤ 3 个时，用其余任意 29 个分片还原原始数据", "With up to 3 shards missing or failing checks, any 29 survivors rebuild the original data"), 12.5))
    o.append(line(440, 344, 440, 376))
    o.append(box(340, 378, 200, 36, T("返回数据", "Data returned"), fill="#e3f4f2", stroke="#bfe3dd", tcol=TEAL, ts=14))
    o.append(badge(352, 396, 4, TEAL))
    # legend / 图例
    o.append(f'<path d="M640 389 l10 10 M650 389 l-10 10" stroke="{AMBER}" stroke-width="2"/>')
    o.append(text(658, 399, T("故障盘或校验不符（示意）", "failed disk or bad CRC (illustrative)"), 12))
    o.append('</svg>')
    return "\n".join(o)


def stripe_placement(z):
    T = lambda a, b: a if z else b
    H = 494
    o = [head(H)]
    o.append(text(30, 40, T("一个 256 MB 数据块 = 一条条带 → 32 个分片（EC 29+3，每片约 8.8 MB）",
                            "One 256 MB block = one stripe → 32 shards (EC 29+3, ≈8.8 MB each)"), 14, INK, weight="700"))
    centers, step = shard_row(o, 30, 56, 40)
    brace(o, 30, 30 + 29 * step - 4, 102, T("29 个数据分片", "29 data shards"))
    brace(o, 30 + 29 * step, 850, 102, T("3 个校验分片", "3 parity"))
    o.append(line(440, 136, 440, 162))
    o.append(text(452, 154, T("每个分片放到不同的节点", "each shard goes to a different node"), 12.5, BLUE, weight="600"))
    # node grid 12 x 3 / 节点网格
    cols, cw, ch, gx, gy, y0 = 12, 62, 64, 7.45, 10, 172
    # stripe uses 32 of 36 nodes; 4 nodes hold other stripes / 本条带用到 32 个节点
    unused = {4, 15, 22, 33}
    k = 0
    for n in range(36):
        r, c = divmod(n, cols)
        x = 30 + c * (cw + gx); y = y0 + r * (ch + gy)
        use = n not in unused
        dash = "" if use else ' stroke-dasharray="4 3"'
        o.append(f'<rect x="{x:.1f}" y="{y}" width="{cw}" height="{ch}" rx="8" fill="#fff" stroke="{LINE}"{dash}/>')
        o.append(text(x + cw / 2, y + 17, T("节点 ", "Node ") + str(n + 1), 11, MUTED if use else "#b6bfcd", "middle"))
        hit = (k * 7) % 6 if use else -1
        for d in range(6):
            dx = x + 7 + d * 8.3
            fill = "#e5e8ef"
            if d == hit:
                fill = BLUE if k < 29 else TEAL
            o.append(f'<rect x="{dx:.1f}" y="{y+26}" width="6" height="28" rx="1.5" fill="{fill}"/>')
        if use:
            k += 1
    # rule box / 约束
    y = y0 + 3 * (ch + gy) + 6
    o.append(f'<rect x="30" y="{y}" width="820" height="66" rx="12" fill="#fff" stroke="#bcd2f7"/>')
    o.append(text(50, y + 27, T("放置约束：同一条带的任意两个分片绝不落在同一节点", "Placement rule: no two shards of a stripe ever share a node"), 14.5, NAVY, weight="700"))
    o.append(text(50, y + 50, T("写入、修复、均衡三条路径强制校验；后台放置审计持续全量巡检",
                                "Enforced on write, repair and rebalance; a background placement audit sweeps continuously"), 12.5))
    o.append(text(850, H - 14, T("示意：36 节点集群，虚线节点存放其他条带", "Illustrative 36-node cluster; dashed nodes hold other stripes"), 11.5, MUTED, "end"))
    o.append('</svg>')
    return "\n".join(o)


def disk_layout(z):
    T = lambda a, b: a if z else b
    H = 450
    o = [head(H)]
    o.append(text(30, 38, T("一块裸盘（直接写块设备，不建本地文件系统）", "One raw disk (block device written directly — no local file system)"), 14, INK, weight="700"))
    y, h = 70, 56
    o.append(f'<rect x="30" y="{y}" width="820" height="{h}" rx="8" fill="#fff" stroke="{LINE}"/>')
    # superblocks / 超级块
    o.append(f'<rect x="30" y="{y}" width="34" height="{h}" rx="8" fill="{NAVY}"/><rect x="50" y="{y}" width="14" height="{h}" fill="{NAVY}"/>')
    o.append(f'<rect x="64" y="{y}" width="30" height="{h}" fill="{NAVY2}"/>')
    o.append(text(47, y + h / 2 + 4, T("主", "P"), 11.5, "#fff", "middle", "700"))
    o.append(text(79, y + h / 2 + 4, T("备", "B"), 11.5, "#fff", "middle", "700"))
    segs = [(94, 120, "rec"), (214, 80, "rec"), (294, 74, "hole"), (368, 140, "rec"), (508, 66, "rec"), (574, 60, "hole"), (634, 76, "rec")]
    for x, w, kind in segs:
        if kind == "rec":
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#dbe7fb" stroke="#fff" stroke-width="2"/>')
            o.append(f'<rect x="{x+1}" y="{y}" width="10" height="{h}" fill="#9dbdf2"/>')
        else:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#hatch)" stroke="#fff" stroke-width="2"/>')
    wh = 710
    o.append(line(wh, y - 12, wh, y + h + 6, col=BLUE, head=False, sw=2))
    o.append(text(wh + 8, y + h / 2 + 4, T("空闲区", "free space"), 12.5, MUTED))
    o.append(text(wh, y - 18, T("写入前沿", "write head"), 12, BLUE, "middle", "600"))
    o.append(line(wh + 4, y + h + 18, 846, y + h + 18, col=BLUE))
    o.append(text(wh + 8, y + h + 36, T("顺序追加", "append-only"), 12, BLUE, "start", "600"))
    o.append(text(30, y + h + 22, T("超级块 主 / 备（盘首 4 KB）", "Superblock primary / backup (first 4 KB)"), 12, NAVY, weight="600"))
    o.append(text(331, y - 10, T("空洞", "hole"), 12, AMBER, "middle", "600"))
    o.append(text(604, y - 10, T("空洞", "hole"), 12, AMBER, "middle", "600"))
    # zoom of one record / 单条记录放大
    zy = 200
    o.append(path(f"M368 {y+h} L200 {zy}", col=LINE, head=False, dash="4 3"))
    o.append(path(f"M508 {y+h} L700 {zy}", col=LINE, head=False, dash="4 3"))
    o.append(f'<rect x="200" y="{zy}" width="500" height="54" rx="8" fill="#fff" stroke="{LINE}"/>')
    o.append(f'<rect x="200" y="{zy}" width="96" height="54" rx="8" fill="#9dbdf2"/><rect x="280" y="{zy}" width="16" height="54" fill="#9dbdf2"/>')
    o.append(text(248, zy + 32, T("记录头", "Header"), 13, NAVY, "middle", "700"))
    o.append(f'<rect x="296" y="{zy}" width="330" height="54" fill="#dbe7fb"/>')
    o.append(text(461, zy + 32, T("分片数据（读取时 CRC32 校验）", "Shard data (CRC32-checked on read)"), 13, NAVY, "middle", "700"))
    o.append(f'<rect x="626" y="{zy}" width="74" height="54" rx="0" fill="#eef2f7"/>')
    o.append(text(663, zy + 32, T("对齐填充", "padding"), 12, MUTED, "middle"))
    o.append(path(f"M200 {zy+62} v6 H700 v-6", col=GREY, head=False, sw=1.4))
    o.append(text(450, zy + 86, T("每条记录起止都对齐到 4 KB 边界", "Every record starts and ends on a 4 KB boundary"), 12.5, MUTED, "middle"))
    # lifecycle cards / 空间复用与整理
    cy = 312
    cards = [
        (T("空间复用", "Space reuse"), [T("删除为软删除，先进回收站", "Deletes are soft — data goes to the recycle bin"),
                                        T("冻结期过后成为空洞", "After a freeze period it becomes a hole"),
                                        T("尺寸精确匹配的新写入直接复用", "New writes of exactly that size reuse it")]),
        (T("碎片整理", "Defragmentation"), [T("把尾部记录搬入空洞", "Moves tail records into holes"),
                                           T("搬移后逐片回读校验，崩溃安全", "Read-back verified per shard, crash-safe"),
                                           T("截断回收尾部空间，元数据零改动", "Truncates the tail; no metadata changes")]),
    ]
    for i, (title, items) in enumerate(cards):
        x = 30 + i * 420
        o.append(f'<rect x="{x}" y="{cy}" width="400" height="116" rx="12" fill="#fff" stroke="{LINE}"/>')
        o.append(text(x + 20, cy + 28, title, 14.5, INK, weight="700"))
        for j, it in enumerate(items):
            o.append(f'<circle cx="{x+26}" cy="{cy+52+j*22}" r="3" fill="{TEAL}"/>')
            o.append(text(x + 38, cy + 56 + j * 22, it, 12.5, "#374151"))
    o.append('</svg>')
    return "\n".join(o)


def deploy(z):
    T = lambda a, b: a if z else b
    H = 470
    o = [head(H)]
    acc = [(T("应用主机", "Application hosts"), T("ksfs 挂载（POSIX）", "ksfs mount (POSIX)")),
           (T("S3 网关", "S3 gateway"), ":9000"),
           (T("Web 控制台", "Web console"), ":8081"),
           (T("监控与告警", "Monitoring & alerts"), T("Prometheus · 飞书 · 邮件", "Prometheus · Lark · email"))]
    for i, (a, b) in enumerate(acc):
        x = 30 + i * 210
        o.append(box(x, 30, 190, 62, a, b, ts=14))
        o.append(line(x + 95, 92, x + 95, 128, head=False))
    o.append(box(30, 128, 820, 46, T("数据交换网络 · 每节点 2 × 10 GbE 绑定（20 Gbps）", "Data network · 2 × 10 GbE bonded per node (20 Gbps)"),
                 fill=NAVY2, stroke=NAVY2, tcol="#fff", ts=14))
    gy = 222
    # mixed nodes / 混合节点
    o.append(f'<rect x="30" y="{gy}" width="360" height="200" rx="12" fill="#fff" stroke="{LINE}"/>')
    o.append(text(48, gy + 26, T("混合节点（典型 5 台）", "Hybrid nodes (typically 5)"), 14, INK, weight="700"))
    for i in range(5):
        x = 46 + i * 66
        o.append(f'<rect x="{x}" y="{gy+42}" width="58" height="128" rx="8" fill="{SURF}" stroke="{LINE}"/>')
        o.append(f'<rect x="{x+6}" y="{gy+50}" width="46" height="26" rx="5" fill="{NAVY}"/>')
        o.append(text(x + 29, gy + 67, "Master", 10.5, "#fff", "middle", "700"))
        o.append(f'<rect x="{x+6}" y="{gy+82}" width="46" height="26" rx="5" fill="#dbe7fb"/>')
        o.append(text(x + 29, gy + 99, "Storage", 10.5, NAVY, "middle", "700"))
        for d in range(4):
            o.append(f'<rect x="{x+8+d*11}" y="{gy+116}" width="8" height="26" rx="1.5" fill="#c8d3e6"/>')
    o.append(text(210, gy + 190, T("Master 与 Storage 同机 · 系统盘 RAID1", "Master + Storage on one host · RAID1 system disk"), 11.5, MUTED, "middle"))
    o.append(line(210, 174, 210, gy, head=False))
    # mongo / 副本集
    o.append(f'<rect x="410" y="{gy}" width="130" height="200" rx="12" fill="#fff" stroke="{LINE}"/>')
    o.append(text(475, gy + 26, "MongoDB", 14, INK, "middle", "700"))
    o.append(text(475, gy + 46, T("副本集 · SSD", "replica set · SSD"), 11.5, MUTED, "middle"))
    for i in range(3):
        yy = gy + 62 + i * 36
        o.append(f'<ellipse cx="475" cy="{yy+4}" rx="34" ry="6" fill="#e3f4f2" stroke="{TEAL}"/>')
        o.append(f'<path d="M441 {yy+4} v16 a34 6 0 0 0 68 0 v-16" fill="#e3f4f2" stroke="{TEAL}"/>')
    o.append(text(475, gy + 186, T("多数派写入", "majority writes"), 11.5, TEAL, "middle", "600"))
    o.append(line(475, 174, 475, gy, head=False))
    # pure storage / 纯存储节点
    o.append(f'<rect x="560" y="{gy}" width="290" height="200" rx="12" fill="#fff" stroke="{LINE}"/>')
    o.append(text(578, gy + 26, T("纯存储节点 × N", "Storage-only nodes × N"), 14, INK, weight="700"))
    for i in range(4):
        x = 576 + i * 62
        o.append(f'<rect x="{x}" y="{gy+42}" width="54" height="128" rx="8" fill="{SURF}" stroke="{LINE}"/>')
        o.append(f'<rect x="{x+5}" y="{gy+50}" width="44" height="26" rx="5" fill="#dbe7fb"/>')
        o.append(text(x + 27, gy + 67, "Storage", 10, NAVY, "middle", "700"))
        for r in range(3):
            for d in range(4):
                o.append(f'<rect x="{x+6+d*11}" y="{gy+84+r*22}" width="8" height="18" rx="1.5" fill="#c8d3e6"/>')
    o.append(text(836, gy + 115, "…", 18, MUTED, "end", "700"))
    o.append(text(705, gy + 190, T("36 × HDD · JBOD 直通", "36 × HDD · JBOD pass-through"), 11.5, MUTED, "middle"))
    o.append(line(705, 174, 705, gy, head=False))
    o.append(text(850, H - 16, T("示意：节点数量与盘数按规模规划", "Illustrative: node and disk counts follow capacity planning"), 11.5, MUTED, "end"))
    o.append('</svg>')
    return "\n".join(o)


GEN = {"arch-write": write_flow, "arch-read": read_flow, "arch-stripe": stripe_placement,
       "arch-disk": disk_layout, "arch-deploy": deploy}
for name, fn in GEN.items():
    for lang in ("zh", "en"):
        with open(f"images/{name}-{lang}.svg", "w", encoding="utf-8") as f:
            f.write(fn(lang == "zh") + "\n")
print("ok")
