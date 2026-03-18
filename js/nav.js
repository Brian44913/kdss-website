/**
 * KDSS Navigation
 * Mobile menu, scroll effects, active link
 * 移动端菜单、滚动效果、活跃链接
 */
(function () {
  'use strict';

  /** Scroll effect — add/remove .scrolled class on navbar / 滚动效果 */
  function initScrollEffect() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /** Mobile menu toggle / 移动端菜单切换 */
  function initMobileMenu() {
    const btn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('.mobile-nav');
    if (!btn || !nav) return;

    btn.addEventListener('click', () => {
      btn.classList.toggle('open');
      nav.classList.toggle('open');
      document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
    });

    // Close on link click / 点击链接时关闭
    nav.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        btn.classList.remove('open');
        nav.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /** Highlight active nav link based on current page / 高亮当前页面导航链接 */
  function initActiveLink() {
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-link').forEach(link => {
      const href = link.getAttribute('href');
      if (href === currentPath || (currentPath === '' && href === 'index.html')) {
        link.classList.add('active');
      }
    });
  }

  /** Back to top button / 返回顶部按钮 */
  function initBackToTop() {
    const btn = document.querySelector('.back-to-top');
    if (!btn) return;

    window.addEventListener('scroll', () => {
      btn.classList.toggle('visible', window.scrollY > 500);
    }, { passive: true });

    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /** Copy code button / 代码复制按钮 */
  function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const codeBlock = btn.closest('.code-block');
        const code = codeBlock?.querySelector('code');
        if (!code) return;

        navigator.clipboard.writeText(code.textContent).then(() => {
          btn.classList.add('copied');
          const originalText = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(() => {
            btn.classList.remove('copied');
            btn.textContent = originalText;
          }, 2000);
        });
      });
    });
  }

  /** Docs sidebar active state / 文档侧边栏活跃状态 */
  function initDocsSidebar() {
    const sidebar = document.querySelector('.docs-sidebar');
    if (!sidebar) return;

    const sections = document.querySelectorAll('.docs-content [id]');
    const links = sidebar.querySelectorAll('a[href^="#"]');

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            links.forEach(link => link.classList.remove('active'));
            const activeLink = sidebar.querySelector(`a[href="#${entry.target.id}"]`);
            if (activeLink) activeLink.classList.add('active');
          }
        });
      },
      { rootMargin: '-20% 0px -80% 0px' }
    );

    sections.forEach(section => observer.observe(section));
  }

  /** Docs search filter / 文档搜索过滤 */
  function initDocsSearch() {
    const input = document.querySelector('.docs-search input');
    if (!input) return;

    input.addEventListener('input', () => {
      const query = input.value.toLowerCase().trim();
      const sections = document.querySelectorAll('.docs-content > section');

      sections.forEach(section => {
        if (!query) {
          section.style.display = '';
          return;
        }
        const text = section.textContent.toLowerCase();
        section.style.display = text.includes(query) ? '' : 'none';
      });
    });
  }

  /** Initialize / 初始化 */
  function init() {
    initScrollEffect();
    initMobileMenu();
    initActiveLink();
    initBackToTop();
    initCopyButtons();
    initDocsSidebar();
    initDocsSearch();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
