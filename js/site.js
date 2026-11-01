/* KDSS website — small progressive enhancements: mobile menu, reveal-on-scroll, docs nav highlight.
   The site is fully readable without JavaScript.
   KDSS 官网轻量脚本：移动端菜单、滚动渐显、文档目录高亮；不开 JS 页面同样完整可读。 */
(function () {
  document.documentElement.classList.remove('no-js');

  // Mobile menu: toggle, close on Esc / outside click / link click
  // 移动端菜单：切换；按 Esc、点击菜单外或点击链接后关闭
  var header = document.querySelector('.site-header');
  var btn = document.querySelector('.menu-btn');
  if (header && btn) {
    var setOpen = function (open) {
      header.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    btn.addEventListener('click', function () { setOpen(!header.classList.contains('open')); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('open')) { setOpen(false); btn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (header.classList.contains('open') && !header.contains(e.target)) setOpen(false);
    });
    header.querySelectorAll('.nav a').forEach(function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });
  }

  // Scrollable figures marked data-center start centred on narrow screens.
  // 标记 data-center 的可横向滚动图在窄屏上初始居中。
  document.querySelectorAll('.scroll[data-center]').forEach(function (el) {
    var center = function () { el.scrollLeft = Math.max(0, (el.scrollWidth - el.clientWidth) / 2); };
    var img = el.querySelector('img');
    if (img && !img.complete) img.addEventListener('load', center); else center();
  });

  // Reveal on scroll / 滚动渐显
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && items.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // Docs side-nav highlight: the active item is the last section whose top has passed the
  // header line; at the bottom of the page the last item wins; clicks highlight at once.
  // 文档目录高亮：取顶部已越过页头基线的最后一节；滚到页底时高亮最后一项；点击目录立即高亮。
  var links = Array.prototype.slice.call(document.querySelectorAll('.docs-nav a[href^="#"]'));
  if (links.length) {
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
    var lock = 0;
    var activate = function (i) {
      links.forEach(function (a, j) { a.classList.toggle('active', j === i); });
    };
    var update = function () {
      if (Date.now() < lock) return;
      var line = (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h'), 10) || 68) + 32;
      var idx = 0;
      targets.forEach(function (el, i) { if (el && el.getBoundingClientRect().top - line <= 0) idx = i; });
      var doc = document.documentElement;
      if (window.innerHeight + window.scrollY >= doc.scrollHeight - 4) idx = links.length - 1;
      activate(idx);
    };
    links.forEach(function (a, i) {
      a.addEventListener('click', function () { activate(i); lock = Date.now() + 900; });
    });
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { ticking = false; update(); });
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  }
})();
