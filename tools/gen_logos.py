#!/usr/bin/env python3
# Logo concepts for the KDSS redesign (pick one, then it replaces images/logo.svg + favicon.svg).
# KDSS 改版 Logo 候选（选定后替换 images/logo.svg 与 favicon.svg）。
import os
NAVY, NAVY2, BLUE, TEAL = "#0f2b5b", "#163a78", "#1d5fd1", "#0f8a7e"
os.makedirs("images/logo-options", exist_ok=True)

C = {}

# A — Shard hexagon: a hexagon (node / reliability) split into stacked shards, last one is parity.
# A — 分片六边形：六边形象征节点与稳固，内部是层叠分片，最后一层为校验。
C["a"] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs><clipPath id="h"><path d="M32 3 L57 17.5 V46.5 L32 61 L7 46.5 V17.5 Z"/></clipPath></defs>
  <g clip-path="url(#h)">
    <rect x="0" y="0" width="64" height="64" fill="{NAVY}"/>
    <rect x="0" y="19" width="64" height="2.6" fill="#fff" opacity=".9"/>
    <rect x="0" y="29" width="64" height="2.6" fill="#fff" opacity=".9"/>
    <rect x="0" y="39" width="64" height="2.6" fill="#fff" opacity=".9"/>
    <rect x="0" y="41.6" width="64" height="30" fill="{TEAL}"/>
  </g>
</svg>'''

# B — Monogram K built from shard blocks: vertical stem of data blocks, diagonals end in a parity block.
# B — 由分片方块组成的字母 K：竖笔为数据块，斜笔末端为校验块。
blocks = "".join(f'<rect x="10" y="{8+i*10}" width="11" height="8" rx="2" fill="{NAVY}"/>' for i in range(5))
C["b"] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  {blocks}
  <rect x="26" y="28" width="11" height="8" rx="2" fill="{NAVY2}"/>
  <rect x="36" y="18" width="11" height="8" rx="2" fill="{NAVY2}"/>
  <rect x="46" y="8" width="11" height="8" rx="2" fill="{BLUE}"/>
  <rect x="36" y="38" width="11" height="8" rx="2" fill="{NAVY2}"/>
  <rect x="46" y="48" width="11" height="8" rx="2" fill="{TEAL}"/>
</svg>'''

# C — Stacked platters: three isometric discs (drives / layers of protection), top edge accented teal.
# C — 层叠盘片：三层等距圆盘象征硬盘与多层保护，顶层青绿色描边。
def disc(cy, fill, stroke):
    return (f'<path d="M8 {cy} v6 c0 6 10.7 10 24 10 s24-4 24-10 v-6" fill="{fill}"/>'
            f'<ellipse cx="32" cy="{cy}" rx="24" ry="10" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
C["c"] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  {disc(44, NAVY, "#3b5a93")}
  {disc(31, NAVY2, "#4f73b3")}
  {disc(18, BLUE, TEAL)}
</svg>'''

# D — Interlocking squares: two offset rounded squares (redundancy), overlap filled teal (the parity that heals).
# D — 交叠方块：两个错位圆角方块象征冗余，交叠处青绿色代表可自愈的校验。
C["d"] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect x="6" y="6" width="34" height="34" rx="8" fill="{NAVY}"/>
  <rect x="24" y="24" width="34" height="34" rx="8" fill="{BLUE}"/>
  <path d="M24 32 a8 8 0 0 1 8 -8 h8 v8 a8 8 0 0 1 -8 8 h-8 z" fill="{TEAL}"/>
</svg>'''

for k, svg in C.items():
    open(f"images/logo-options/logo-{k}.svg", "w").write(svg + "\n")

names = {"a": "A · 分片六边形", "b": "B · 分片字母 K", "c": "C · 层叠盘片", "d": "D · 交叠方块"}
notes = {"a": "六边形象征节点与稳固，内部层叠分片，底部青绿为校验；最接近现有风格，小尺寸辨识度高。",
         "b": "由数据块拼出字母 K，斜笔末端青绿块是校验；品牌字母感最强，偏科技。",
         "c": "三层等距盘片象征硬盘与多层保护；存储行业语义最直白，较传统稳重。",
         "d": "两个错位方块代表冗余，交叠处青绿代表自愈；最简洁抽象，适合做图标。"}
cards = ""
for k in "abcd":
    cards += f'''
  <div class="card" style="padding:28px">
    <h3>{names[k]}</h3>
    <p class="small muted" style="margin:6px 0 20px">{notes[k]}</p>
    <div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap">
      <img src="images/logo-options/logo-{k}.svg" width="96" height="96" alt="">
      <img src="images/logo-options/logo-{k}.svg" width="32" height="32" alt="">
      <img src="images/logo-options/logo-{k}.svg" width="16" height="16" alt="">
      <div style="display:flex;align-items:center;gap:10px;font-weight:800;font-size:1.25rem;color:#0a1f44">
        <img src="images/logo-options/logo-{k}.svg" width="30" height="30" alt="">KDSS<small style="font-weight:500;font-size:.78rem;color:#6b7280;border-left:1px solid #d3d9e4;padding-left:10px">分布式存储</small></div>
    </div>
    <div style="margin-top:20px;background:#0a1f44;border-radius:10px;padding:18px 22px;display:flex;align-items:center;gap:10px;color:#fff;font-weight:800;font-size:1.2rem">
      <img src="images/logo-options/logo-{k}.svg" width="30" height="30" alt="" style="background:#fff;border-radius:8px;padding:3px">KDSS<span style="font-weight:500;font-size:.8rem;color:#93a5c7;margin-left:6px">页脚（深底）效果</span></div>
  </div>'''
page = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>KDSS Logo 候选</title><link rel="stylesheet" href="css/site.css"></head><body>
<section class="section"><div class="container">
<div class="section-head"><span class="eyebrow">Logo 候选（内部预览，不上线）</span><h2>KDSS Logo 方案</h2>
<p class="lead">每个方案依次展示：大图、32 px、16 px（浏览器标签图标大小）、页头组合、深色页脚组合。</p></div>
<div class="grid grid-2">{cards}
</div></div></section></body></html>
'''
open("logo-options.html", "w").write(page)
print("ok")
