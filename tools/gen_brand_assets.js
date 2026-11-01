// Generate raster brand assets from the SVG mark with Playwright: favicon.ico (16 + 32 PNG frames),
// apple-touch-icon.png (180), images/og-zh.png and images/og-en.png (1200x630 social cards).
// Run from the repo root: NODE_PATH=~/.k2-watch/webtools/node_modules node tools/gen_brand_assets.js
// 用 Playwright 从 SVG 标志生成位图资源：favicon.ico（16/32 两帧 PNG）、apple-touch-icon.png（180）、
// 社交分享卡片 images/og-zh.png 与 images/og-en.png（1200×630）。在仓库根目录运行（见上方命令）。
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
// Light-mode mark only (raster icons cannot follow the color scheme). / 位图只用浅色版标志。
const MARK = fs.readFileSync(path.join(ROOT, 'images/logo.svg'), 'utf8').replace(/<!--[\s\S]*?-->/g, '');
const MARK_LIGHT = fs.readFileSync(path.join(ROOT, 'images/logo-light.svg'), 'utf8').replace(/<!--[\s\S]*?-->/g, '');
const FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif";

const OG = {
  zh: { title: '可信赖的 PB 级<br>纠删码分布式存储', sub: 'Reed-Solomon 纠删码 · 裸盘直写引擎 · POSIX 与 S3 双接口 · 滚动升级不停服',
        m: [['90.6%', 'EC 29+3 得盘率'], ['3', '29+3 下可同时故障的盘或节点'], ['近 190 PB', '累计部署规模']], brand: '分布式存储' },
  en: { title: 'Petabyte-scale storage<br>you can trust', sub: 'Reed-Solomon erasure coding · raw-disk engine · POSIX and S3 access · rolling upgrades',
        m: [['90.6%', 'Usable capacity with EC 29+3'], ['3', 'Concurrent disk or node failures (29+3)'], ['~190 PB', 'Deployed footprint']], brand: 'Distributed Storage' },
};

function ogHtml(lang) {
  const t = OG[lang];
  const metrics = t.m.map(([v, l]) => `<div class="m"><b>${v}</b><span>${l}</span></div>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:1200px;height:630px;font-family:${FONT};background:#0a1f44;color:#fff;position:relative;overflow:hidden}
  .glow{position:absolute;inset:0;background:radial-gradient(700px 380px at 100% 0%,rgba(47,116,230,.45),transparent 60%)}
  .grid{position:absolute;inset:0;opacity:.18;background-image:linear-gradient(#2a3e66 1px,transparent 1px),linear-gradient(90deg,#2a3e66 1px,transparent 1px);background-size:48px 48px}
  .wrap{position:absolute;inset:0;padding:64px 72px;display:flex;flex-direction:column}
  .brand{display:flex;align-items:center;gap:16px;font-weight:800;font-size:34px;letter-spacing:.02em}
  .brand svg{width:52px;height:52px}
  .brand small{font-weight:500;font-size:20px;color:#93a5c7;border-left:1px solid #2a3e66;padding-left:16px;letter-spacing:0}
  h1{margin-top:56px;font-size:62px;line-height:1.18;font-weight:800;letter-spacing:-.01em}
  p{margin-top:22px;font-size:23px;color:#b9c7e2}
  .ms{margin-top:auto;display:flex;gap:0;border-top:1px solid #1d3360;padding-top:26px}
  .m{flex:1;padding-right:24px}
  .m b{display:block;font-size:40px;font-weight:800;color:#fff}
  .m span{display:block;margin-top:6px;font-size:18px;color:#93a5c7}
  .url{position:absolute;right:72px;top:74px;font-size:20px;color:#93a5c7}
  </style></head><body><div class="glow"></div><div class="grid"></div>
  <div class="wrap"><div class="brand">${MARK_LIGHT}KDSS<small>${t.brand}</small></div>
  <h1>${t.title}</h1><p>${t.sub}</p><div class="ms">${metrics}</div></div>
  <div class="url">www.kdss.io</div></body></html>`;
}

function iconHtml(size, pad, bg) {
  return `<!doctype html><html><head><style>*{margin:0}html,body{width:${size}px;height:${size}px;background:${bg}}
  div{width:${size}px;height:${size}px;padding:${pad}px;box-sizing:border-box}svg{width:100%;height:100%;display:block}</style></head>
  <body><div>${MARK}</div></body></html>`;
}

// Pack PNG frames into an ICO container (PNG-in-ICO). / 把 PNG 帧打包进 ICO 容器。
function ico(frames) {
  const head = Buffer.alloc(6); head.writeUInt16LE(0, 0); head.writeUInt16LE(1, 2); head.writeUInt16LE(frames.length, 4);
  const dir = Buffer.alloc(16 * frames.length);
  let off = 6 + dir.length;
  frames.forEach(([size, png], i) => {
    const o = i * 16;
    dir.writeUInt8(size >= 256 ? 0 : size, o); dir.writeUInt8(size >= 256 ? 0 : size, o + 1);
    dir.writeUInt8(0, o + 2); dir.writeUInt8(0, o + 3); dir.writeUInt16LE(1, o + 4); dir.writeUInt16LE(32, o + 6);
    dir.writeUInt32LE(png.length, o + 8); dir.writeUInt32LE(off, o + 12); off += png.length;
  });
  return Buffer.concat([head, dir, ...frames.map(f => f[1])]);
}

(async () => {
  const browser = await chromium.launch();
  const shot = async (html, w, h, omitBackground) => {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await page.setContent(html);
    const buf = await page.screenshot({ omitBackground: !!omitBackground, clip: { x: 0, y: 0, width: w, height: h } });
    await page.close();
    return buf;
  };
  const f16 = await shot(iconHtml(16, 0, 'transparent'), 16, 16, true);
  const f32 = await shot(iconHtml(32, 1, 'transparent'), 32, 32, true);
  fs.writeFileSync(path.join(ROOT, 'favicon.ico'), ico([[16, f16], [32, f32]]));
  fs.writeFileSync(path.join(ROOT, 'apple-touch-icon.png'), await shot(iconHtml(180, 22, '#ffffff'), 180, 180, false));
  for (const lang of ['zh', 'en']) {
    fs.writeFileSync(path.join(ROOT, `images/og-${lang}.png`), await shot(ogHtml(lang), 1200, 630, false));
  }
  await browser.close();
  console.log('ok');
})();
