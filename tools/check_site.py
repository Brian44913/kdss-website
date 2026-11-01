#!/usr/bin/env python3
# Static site checker: internal links + anchors resolve, no external resource loads, no sensitive terms,
# zh/en page pairing, well-formed tag nesting. Exit 1 on any finding.
# 站点静态检查：站内链接与锚点可达、无外部资源加载、无敏感词、中英页面成对、标签嵌套正确；有问题退出码 1。
import os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = [p for p in ["index.html", "features.html", "solutions.html", "architecture.html", "docs.html", "about.html"]]
FILES = PAGES + ["zh/" + p for p in PAGES] + ["whitepaper/zh.html", "whitepaper/en.html"]
SENSITIVE = [r"10\.78\.", r"192\.168\.", r"172\.16\.", r"\bkdss-[123u]\b", r"kdss-36-", r"kdss-132-", r"\bf0\d{4,}", r"[Bb]itmain",
             r"seal98", r"post96", r"lianjing", r"47\.243\.", r"210\.245\.", r"2027-forClaude", r"2026-localSafe"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "path", "rect", "circle", "line", "polyline", "polygon", "ellipse", "stop"}

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = set(); self.links = []; self.res = []; self.stack = []; self.errors = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        for k in ("src",):
            if a.get(k): self.res.append(a[k])
        if tag == "link" and a.get("href"): self.res.append(a["href"])
        if tag not in VOID: self.stack.append((tag, self.getpos()))
    def handle_startendtag(self, tag, attrs): self.handle_starttag(tag, attrs);
    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.stack and self.stack[-1][0] == tag: self.stack.pop(); return
        if any(t == tag for t, _ in self.stack):
            while self.stack and self.stack[-1][0] != tag:
                t, pos = self.stack.pop()
                if t not in ("p", "li", "td", "th", "tr", "option"): self.errors.append(f"unclosed <{t}> at line {pos[0]}")
            self.stack.pop()
        else:
            self.errors.append(f"stray </{tag}> at line {self.getpos()[0]}")

parsed = {}
for f in FILES:
    path = os.path.join(ROOT, f)
    if not os.path.exists(path): print(f"MISSING {f}"); continue
    p = P(); txt = open(path, encoding="utf-8").read(); p.feed(txt); parsed[f] = (p, txt)

bad = 0
for f, (p, txt) in parsed.items():
    base = os.path.dirname(f)
    for e in p.errors[:5]: print(f"{f}: HTML {e}"); bad += 1
    for r in p.res:
        if re.match(r"^(https?:)?//", r) and not r.startswith("https://www.kdss.io"):
            print(f"{f}: EXTERNAL resource {r}"); bad += 1
    for h in p.links:
        if h.startswith(("mailto:", "http://", "https://")): continue
        target, _, frag = h.partition("#")
        if target == "":
            tf = f
        else:
            tf = os.path.normpath(os.path.join(base, target))
            if tf.endswith("/") or os.path.isdir(os.path.join(ROOT, tf)) or target.endswith("/"): tf = os.path.join(tf, "index.html")
            if tf == ".": tf = "index.html"
        tf = os.path.normpath(tf)
        if not os.path.exists(os.path.join(ROOT, tf)):
            print(f"{f}: BROKEN link {h} -> {tf}"); bad += 1; continue
        if frag and tf.endswith(".html"):
            if tf not in parsed:
                q = P(); q.feed(open(os.path.join(ROOT, tf), encoding="utf-8").read()); parsed[tf] = (q, "")
            if frag not in parsed[tf][0].ids:
                print(f"{f}: BROKEN anchor {h} (no id '{frag}' in {tf})"); bad += 1
    for r in p.res:
        if re.match(r"^(https?:)?//|^data:", r): continue
        rp = os.path.normpath(os.path.join(base, r.split("#")[0].split("?")[0]))
        if not os.path.exists(os.path.join(ROOT, rp)): print(f"{f}: MISSING resource {r}"); bad += 1
    for pat in SENSITIVE:
        for m in re.finditer(pat, txt):
            line = txt.count("\n", 0, m.start()) + 1
            print(f"{f}:{line}: SENSITIVE '{m.group(0)}'"); bad += 1
for pg in PAGES:
    if not (os.path.exists(os.path.join(ROOT, pg)) and os.path.exists(os.path.join(ROOT, "zh", pg))):
        print(f"PAIR missing for {pg}"); bad += 1
# images referenced by SVG-generating scripts may contain sensitive text too
for d in ("images",):
    for fn in os.listdir(os.path.join(ROOT, d)):
        if fn.endswith(".svg"):
            t = open(os.path.join(ROOT, d, fn), encoding="utf-8").read()
            for pat in SENSITIVE:
                if re.search(pat, t): print(f"images/{fn}: SENSITIVE {pat}"); bad += 1
print("findings:", bad)
sys.exit(1 if bad else 0)
