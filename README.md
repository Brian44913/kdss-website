# KDSS 官网（www.kdss.io）

KDSS 分布式存储的官方网站与技术白皮书。纯静态站点（HTML + CSS + 少量 JS），由 nginx 直接托管，不需要构建。

## 目录

| 路径 | 内容 |
|---|---|
| `index.html` 等 6 个页面 | 英文站：首页、产品能力、解决方案、技术架构、文档、关于我们 |
| `zh/` | 中文站，文件名与英文一一对应 |
| `css/site.css` | 全站设计规范（颜色、字号、间距、组件、响应式） |
| `css/pages/*.css` | 单页专属样式 |
| `js/site.js` | 移动端菜单、滚动渐显、文档目录高亮（不开 JS 也能完整阅读） |
| `images/*-zh.svg` / `*-en.svg` | 插图，由 `tools/gen_*.py` 生成 |
| `whitepaper/` | 白皮书源文件（HTML + 打印样式） |
| `downloads/` | 白皮书 PDF |
| `tasks/` | 改版方案、事实清单（`facts.md`，页面所有数字与能力的唯一来源） |
| `tools/check_site.py` | 站点检查：站内链接与锚点、外部资源、敏感词、中英成对 |

## 本地预览

```bash
python3 -m http.server 8765 --bind 127.0.0.1
# 打开 http://127.0.0.1:8765/zh/ 或 http://127.0.0.1:8765/
```

## 修改流程

1. 改内容前先核对 `tasks/facts.md`；新能力或新数字先补进事实清单。
2. 改插图：编辑对应的 `tools/gen_*.py` 后运行，中英两份一起生成。
3. 改白皮书：编辑 `whitepaper/*.html`，再用 Playwright 渲染 PDF 到 `downloads/`。
4. 发布前运行 `python3 tools/check_site.py`（退出码 0 才发布），并在 1440 / 820 / 390 三档宽度下检查页面。

## 发布

线上目录由 nginx 托管。发布时先备份线上旧版本，再整体替换静态文件。

## 联系

- 商务与合作：contact@kdss.io
- 技术支持：support@kdss.io
