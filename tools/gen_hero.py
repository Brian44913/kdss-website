#!/usr/bin/env python3
# Generate the homepage hero illustration (zh + en): one 256 MB block -> EC 29+3 -> 32 of 36 nodes.
# 生成首页主视觉（中/英）：一个 256 MB 数据块 → EC 29+3 → 写入 36 个节点中的 32 个。
import random

T = {
    "zh": dict(chunk="256 MB 数据块", data="29 个数据分片", parity="3 个校验分片",
               l1="数据分片", l2="校验分片", l3="空闲节点", foot="同一条带的 32 个分片分布在 32 个不同节点，任意 3 个同时丢失仍可读、可重建",
               node="节点"),
    "en": dict(chunk="256 MB block", data="29 data shards", parity="3 parity shards",
               l1="Data shard", l2="Parity shard", l3="Free node", foot="32 shards on 32 distinct nodes — any 3 can be lost at once and the data stays readable",
               node="Node"),
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"

def build(lang):
    t = T[lang]; W, H = 560, 420
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',
         '<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#0f2b5b"/><stop offset="1" stop-color="#1d5fd1"/></linearGradient></defs>',
         f'<rect x="180" y="16" width="200" height="50" rx="9" fill="url(#g)"/>',
         f'<text x="280" y="38" fill="#fff" font-size="14" font-weight="700" text-anchor="middle">{t["chunk"]}</text>',
         f'<text x="280" y="56" fill="#c9d8f5" font-size="12" text-anchor="middle">Reed-Solomon EC 29+3</text>']
    # shards row
    sx, sy, sw, gap = 24, 112, 13, 3.0
    o.append('<g stroke="#c5d3ea" stroke-width="1.2" fill="none">')
    for x in (40, 160, 280, 400, 520):
        o.append(f'<path d="M280 66 C280 92 {x} 86 {x} 110"/>')
    o.append('</g>')
    for i in range(32):
        x = sx + i * (sw + gap) + (6 if i >= 29 else 0)
        c = "#0f8a7e" if i >= 29 else "#163a78"
        o.append(f'<rect x="{x:.1f}" y="{sy}" width="{sw}" height="30" rx="2.5" fill="{c}"/>')
    o.append(f'<text x="24" y="162" fill="#6b7280" font-size="12">{t["data"]}</text>')
    o.append(f'<text x="536" y="162" fill="#0f8a7e" font-size="12" text-anchor="end">{t["parity"]}</text>')
    # nodes 4 x 9, 32 used (29 data, 3 parity), 4 free
    random.seed(7)
    idx = list(range(36)); random.shuffle(idx)
    free = set(idx[:4]); parity = set(idx[4:7])
    nw, nh, gx, gy, ox, oy = 54, 40, 4.5, 8, 24, 182
    for k in range(36):
        r, c = divmod(k, 9)
        x = ox + c * (nw + gx); y = oy + r * (nh + gy)
        o.append(f'<rect x="{x:.1f}" y="{y}" width="{nw}" height="{nh}" rx="6" fill="#fff" stroke="#d3d9e4"/>')
        fill = 26 + (k * 7) % 18
        o.append(f'<rect x="{x+8:.1f}" y="{y+27}" width="{fill}" height="4" rx="2" fill="#e5e8ef"/>')
        if k in free:
            o.append(f'<text x="{x+nw/2:.1f}" y="{y+18}" font-size="12" fill="#6b7280" text-anchor="middle">—</text>')
        else:
            col = "#0f8a7e" if k in parity else "#163a78"
            o.append(f'<rect x="{x+8:.1f}" y="{y+11}" width="{nw-16}" height="6" rx="2" fill="{col}"/>')
    ly = 388
    o.append(f'<g font-size="12" fill="#374151">'
             f'<rect x="24" y="{ly-9}" width="12" height="10" rx="2" fill="#163a78"/><text x="42" y="{ly}">{t["l1"]}</text>'
             f'<rect x="{24+ (96 if lang=="zh" else 104)}" y="{ly-9}" width="12" height="10" rx="2" fill="#0f8a7e"/><text x="{42+(96 if lang=="zh" else 104)}" y="{ly}">{t["l2"]}</text>'
             f'<rect x="{24+(192 if lang=="zh" else 212)}" y="{ly-9}" width="12" height="10" rx="2" fill="#fff" stroke="#d3d9e4"/><text x="{42+(192 if lang=="zh" else 212)}" y="{ly}">{t["l3"]}</text></g>')
    o.append(f'<text x="24" y="{ly+22}" fill="#6b7280" font-size="12">{t["foot"]}</text>')
    o.append('</svg>')
    return "\n".join(o)

for lang in ("zh", "en"):
    open(f"images/hero-stripe-{lang}.svg", "w", encoding="utf-8").write(build(lang) + "\n")
print("ok")
