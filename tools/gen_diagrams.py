#!/usr/bin/env python3
# Generate site diagrams (zh + en) in one consistent light style.
# 生成站点示意图（中/英），统一浅色风格。
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"
NAVY, NAVY2, BLUE, TEAL, INK, MUTED, LINE, SURF = "#0f2b5b", "#163a78", "#1d5fd1", "#0f8a7e", "#111827", "#6b7280", "#d3d9e4", "#f6f8fb"

def box(x, y, w, h, title, sub="", fill="#fff", stroke=LINE, tcol=INK, scol=MUTED, r=10, ts=14):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
    cy = y + h / 2 + (0 if not sub else -6)
    s += f'<text x="{x+w/2}" y="{cy+5}" font-size="{ts}" font-weight="700" fill="{tcol}" text-anchor="middle">{title}</text>'
    if sub:
        s += f'<text x="{x+w/2}" y="{cy+24}" font-size="12" fill="{scol}" text-anchor="middle">{sub}</text>'
    return s

def arrow(x1, y1, x2, y2, label="", col="#9fb1cf", dash=False, lx=None, ly=None):
    d = ' stroke-dasharray="5 4"' if dash else ""
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.6" marker-end="url(#ah)"{d}/>'
    if label:
        s += f'<text x="{lx if lx is not None else (x1+x2)/2+6}" y="{ly if ly is not None else (y1+y2)/2}" font-size="12" fill="{MUTED}">{label}</text>'
    return s

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="' + FONT + '">'
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#9fb1cf"/></marker></defs>')

def architecture(lang):
    z = lang == "zh"
    L = dict(
        apps=("应用 / 客户端", "Applications"), fuse=("ksfs（FUSE 挂载）", "ksfs (FUSE mount)"), fuse_s=("POSIX 文件接口", "POSIX file access"),
        s3=("S3 兼容网关", "S3-compatible gateway"), s3_s=("AWS CLI · boto3 · SDK", "AWS CLI · boto3 · SDKs"),
        web=("Web 控制台", "Web console"), web_s=("监控 · 告警 · 管理", "Monitoring · alerts · admin"),
        master=("Master 集群（典型 5 台）", "Master cluster (typically 5)"), master_s=("元数据 · 选主 · 调度 · 审计", "Metadata · leader election · scheduling · audit"),
        mongo=("MongoDB 副本集", "MongoDB replica set"), mongo_s=("多数派写入 · zstd 压缩", "Majority writes · zstd"),
        st=("存储节点", "Storage node"), st_s=("裸盘 × 36", "36 raw disks"),
        meta=("元数据 gRPC", "metadata gRPC"), data=("分片并行读写 gRPC", "parallel shard I/O (gRPC)"), more=("… 横向扩展到数十节点", "… scales out to dozens of nodes"),
        prom=("Prometheus 指标 / 内置告警（飞书 · 邮件）", "Prometheus metrics / built-in alerts (Lark · email)"))
    t = {k: v[0 if z else 1] for k, v in L.items()}
    W, H = 1100, 460
    o = [HEAD.format(w=W, h=H)]
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="{SURF}"/>')
    o.append(box(40, 30, 1020, 44, t["apps"], fill="#fff", ts=14))
    o.append(box(40, 104, 320, 64, t["fuse"], t["fuse_s"]))
    o.append(box(390, 104, 320, 64, t["s3"], t["s3_s"]))
    o.append(box(740, 104, 320, 64, t["web"], t["web_s"]))
    for x in (200, 550, 900):
        o.append(arrow(x, 74, x, 102))
    # Master narrowed so the data paths can run past it on both sides. / Master 收窄，数据线从两侧绕过。
    o.append(box(150, 222, 460, 70, t["master"], t["master_s"], fill=NAVY, stroke=NAVY, tcol="#fff", scol="#c9d8f5"))
    o.append(box(700, 222, 360, 70, t["mongo"], t["mongo_s"], fill="#fff"))
    o.append(arrow(610, 257, 698, 257))
    # metadata (grey, solid): access tier -> master
    o.append(arrow(240, 168, 240, 220, t["meta"], lx=248, ly=198))
    o.append(arrow(550, 168, 550, 220))
    o.append(f'<path d="M900 168 C900 200 640 196 600 220" stroke="#9fb1cf" stroke-width="1.6" fill="none" marker-end="url(#ah)"/>')
    # storage row
    for i in range(6):
        x = 40 + i * 172
        o.append(box(x, 352, 156, 64, t["st"] + f" {i+1}", t["st_s"]))
    o.append(f'<text x="{W-40}" y="440" font-size="12" fill="{MUTED}" text-anchor="end">{t["more"]}</text>')
    # data (blue, dashed): clients -> storage, bypassing the master / 数据直达存储节点
    o.append(f'<path d="M90 168 L90 350" stroke="{BLUE}" stroke-width="1.8" fill="none" marker-end="url(#ah)" stroke-dasharray="6 4"/>')
    o.append(f'<path d="M650 168 L650 350" stroke="{BLUE}" stroke-width="1.8" fill="none" marker-end="url(#ah)" stroke-dasharray="6 4"/>')
    o.append(f'<text x="98" y="318" font-size="12" fill="{BLUE}" font-weight="600">{t["data"]}</text>')
    # control (grey, dashed): master <-> storage heartbeat & scheduling
    o.append(f'<path d="M380 292 L380 350" stroke="#9fb1cf" stroke-width="1.6" fill="none" marker-end="url(#ah)" stroke-dasharray="3 4"/>')
    o.append(f'<text x="388" y="326" font-size="12" fill="{MUTED}">{"心跳 · 调度（修复/均衡/回收）" if z else "heartbeats · repair / balance / GC scheduling"}</text>')
    o.append(f'<text x="{W-40}" y="322" font-size="12" fill="{MUTED}" text-anchor="end">{t["prom"]}</text>')
    o.append('</svg>')
    return "\n".join(o)

def console_capacity(lang):
    z = lang == "zh"
    t = dict(
        title="容量概览" if z else "Capacity overview",
        total="总容量" if z else "Total", used="已使用" if z else "Used", recycle="回收站" if z else "Recycle bin",
        maxw="当前最大可写" if z else "Max writable now", cons="保守可写" if z else "Conservative writable", demo="示意" if z else "Illustrative", avail="可用空间" if z else "Available",
        nodes="可写节点" if z else "Writable nodes", need="需要 ≥ 32" if z else "need ≥ 32", ok="正常" if z else "Healthy",
        bar="集群水位" if z else "Cluster watermark", reject="拒写线 99%" if z else "Reject line 99%")
    W, H = 560, 380
    o = [HEAD.format(w=W, h=H)]
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="#fff" stroke="{LINE}"/>')
    o.append(f'<rect x="0" y="0" width="{W}" height="46" rx="12" fill="{SURF}"/><rect x="0" y="34" width="{W}" height="12" fill="{SURF}"/>')
    o.append(f'<circle cx="22" cy="23" r="5" fill="#e5e8ef"/><circle cx="38" cy="23" r="5" fill="#e5e8ef"/><circle cx="54" cy="23" r="5" fill="#e5e8ef"/>')
    o.append(f'<text x="80" y="28" font-size="13" font-weight="700" fill="{INK}">{t["title"]}</text>')
    o.append(f'<rect x="{W-110}" y="13" width="88" height="20" rx="10" fill="#e3f4f2"/><text x="{W-66}" y="27" font-size="12" fill="#0b6b62" text-anchor="middle" font-weight="700">● {t["ok"]}</text>')
    # "Illustrative" tag next to the title / 标题旁的"示意"标记
    dx = 150 if z else 210; dw = 44 if z else 84
    o.append(f'<rect x="{dx}" y="13" width="{dw}" height="20" rx="10" fill="#fbf1df"/><text x="{dx+dw/2}" y="27" font-size="12" fill="#8a5a12" text-anchor="middle" font-weight="700">{t["demo"]}</text>')
    # Illustrative round numbers only (not a real cluster's readings). / 仅为取整示意值，非真实集群读数。
    cards = [(t["total"], "10", "PB", INK), (t["used"], "9", "PB", INK), (t["recycle"], "0.2", "PB", INK),
             (t["maxw"], "500", "TB", BLUE), (t["cons"], "400", "TB", BLUE), (t["avail"], "800", "TB", INK)]
    for i, (lab, val, unit, col) in enumerate(cards):
        r, c = divmod(i, 3)
        x = 22 + c * 176; y = 64 + r * 92
        hl = col == BLUE
        o.append(f'<rect x="{x}" y="{y}" width="164" height="80" rx="9" fill="{"#f3f7fe" if hl else "#fff"}" stroke="{"#bcd2f7" if hl else LINE}"/>')
        o.append(f'<text x="{x+14}" y="{y+26}" font-size="12" fill="{MUTED}">{lab}</text>')
        o.append(f'<text x="{x+14}" y="{y+60}" font-size="26" font-weight="800" fill="{NAVY if not hl else BLUE}">{val}<tspan font-size="13" font-weight="700" dx="4">{unit}</tspan></text>')
    y = 266
    o.append(f'<text x="22" y="{y}" font-size="12" fill="{MUTED}">{t["bar"]}</text>')
    o.append(f'<rect x="22" y="{y+10}" width="516" height="12" rx="6" fill="#eef2f7"/>')
    o.append(f'<rect x="22" y="{y+10}" width="{516*0.90:.0f}" height="12" rx="6" fill="{NAVY2}"/>')
    o.append(f'<line x1="{22+516*0.99:.0f}" y1="{y+4}" x2="{22+516*0.99:.0f}" y2="{y+28}" stroke="#b7791f" stroke-width="2"/>')
    o.append(f'<text x="{22+516*0.99:.0f}" y="{y+44}" font-size="12" fill="#8a5a12" text-anchor="end">{t["reject"]}</text>')
    o.append(f'<text x="22" y="{y+76}" font-size="12" fill="{MUTED}">{t["nodes"]}</text>')
    o.append(f'<text x="22" y="{y+100}" font-size="20" font-weight="800" fill="{NAVY}">36 <tspan font-size="12" fill="{MUTED}" font-weight="500">/ 36 · {t["need"]}</tspan></text>')
    for i in range(36):
        o.append(f'<rect x="{230 + i*8.6:.1f}" y="{y+86}" width="6" height="16" rx="1.5" fill="{TEAL}"/>')
    o.append('</svg>')
    return "\n".join(o)

for lang in ("zh", "en"):
    open(f"images/architecture-{lang}.svg", "w", encoding="utf-8").write(architecture(lang) + "\n")
    open(f"images/console-capacity-{lang}.svg", "w", encoding="utf-8").write(console_capacity(lang) + "\n")
print("ok")
