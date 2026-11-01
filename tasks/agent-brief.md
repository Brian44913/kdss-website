# 子代理共用说明（KDSS 官网改版，2026-11-01）

仓库：`~/golang/kdss-website`，分支 `redesign-2026-11`（不要提交、不要切分支、不要 push，由主会话统一提交）。

## 必读
- `tasks/todo.md`：改版目标与信息架构。
- `tasks/facts.md`：**唯一事实来源**。页面里的每个能力、数字都必须能在这里找到；找不到就不写。不得出现集群名、IP、主机名、客户/矿工号、内部故障细节、安全弱点。生产规模只能用 facts.md 里的概数。
- `css/site.css`：设计规范（浅色企业风）。**不要修改 site.css**（多个代理并行）。优先用已有类：`.section / .section-alt / .section-head / .grid-2/3/4 / .split / .card / .card-flat / .feature-row / .figure / .table-wrap .table / .tag / ul.ticks / .steps .step / .case / .timeline / .cta / .contact-cards / .docs .docs-nav .prose / .callout / pre / .page-hero .breadcrumb / .metrics`。确有需要的页面专属样式，写到 `css/pages/<页面名>.css` 并只在本页引用。
- `zh/index.html`：已完成的中文首页 = 页头、页脚、首屏、卡片、表格写法的**模板**。所有页面的 `<head>`、页头、页脚结构照抄，只改 `<title>`、description、`aria-current` 所在链接。

## 路径约定
- 中文页面在 `zh/`，资源前缀 `../`；英文页面在根目录，资源无前缀。文件名不变（index/features/solutions/architecture/docs/about.html），互为对应。
- 语言切换：中文页 `<div class="lang"><span>中</span><a href="../<同名页>" hreflang="en">EN</a></div>`；英文页 `<div class="lang"><a href="zh/<同名页>" hreflang="zh-CN">中</a><span>EN</span></div>`（首页分别是 `../` 与 `zh/`）。
- `<link rel="alternate" hreflang>` 指向 `https://www.kdss.io/<页>` 与 `https://www.kdss.io/zh/<页>`。
- 白皮书下载链接：`downloads/kdss-whitepaper-zh.pdf` / `downloads/kdss-whitepaper-en.pdf`（中文页用 `../downloads/...`）。
- 联系：`contact@kdss.io`（商务与合作）、`support@kdss.io`（技术支持）。
- 页脚右下角版本 `26.11.1`（英文 `Version 26.11.1`）。

## 英文页头页脚文字
- 导航：Home / Product / Solutions / Architecture / Docs / About；按钮 Contact us；品牌副标题 `Distributed Storage`。
- 页脚列：Product（Features / Architecture / Solutions）· Resources（Docs / Whitepaper / S3 API）· Contact（两个邮箱 / About）。简介："Erasure-coded distributed storage for petabyte-scale data — low-cost, highly reliable infrastructure for long-term retention." 版权 `© 2026 KDSS. All rights reserved.`

## 插图
- 用 Python 脚本生成 SVG（参考 `tools/gen_diagrams.py` 的配色与 `box()/arrow()` 风格），每个代理用**自己的脚本文件** `tools/gen_<你的名字>.py`，输出 `images/<名>-zh.svg` 与 `images/<名>-en.svg`。不要改别人的脚本或图片。
- 配色：navy #0f2b5b / #163a78，blue #1d5fd1，teal #0f8a7e，ink #111827，muted #6b7280，line #d3d9e4，surface #f6f8fb。白底或 surface 底、细线、圆角 10。
- 图里的数字若来自真实集群，必须改为取整示意值并注明"示意"。

## 写作风格
- 中文：专业、克制、具体；短句；不堆形容词；先说结论再说原理。不用"极致""颠覆""业界领先"之类空话。
- 英文：与中文逐节对应，地道的企业技术文案（参考 NetApp / Pure Storage 的语气），不是逐字直译。
- 代码与命令只写真实存在的（S3 示例用 AWS CLI / boto3 等通用写法；KDSS CLI 只写 facts.md 提到的概念，不要编造参数）。

## 自查（必须做）
- 本地服务已在 `http://127.0.0.1:8765/` 运行（仓库根目录）。若不通，在仓库根目录执行 `python3 -m http.server 8765 --bind 127.0.0.1 &`。
- 截图：`cd ~/.k2-watch/webtools && node shot.js <输出目录> <url...>`（三档宽度，打印 overflow 与失败请求，要求 overflow=0、failed=[]；白皮书 PDF 链接未生成时允许 404）；分段细看：`node parts.js <输出目录> <url> <宽度>`，然后用 Read 工具查看 PNG。输出目录用 `/private/tmp/claude-501/-Users-dario/8d77aef9-b43e-4af4-9888-434ad136fa53/scratchpad/shots/<你的名字>/`。
- 至少检查 1440 与 390 两档宽度的每一段，修掉：文字溢出、单字成行、表格被截、图片过小、对齐问题。
- 页内锚点与站内链接都要能对上（首页卡片链接到 `features.html#reliability / #engine / #access / #operations`，文档 `docs.html#s3` 等）。
- 代码注释先英文后中文（双语）。

## 汇报
完成后用中文简短汇报：做了哪些文件、自查结果（overflow / 失败请求）、需要主会话决定或补充的事实。不要粘贴大段源码。
