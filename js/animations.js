/**
 * KDSS Animations
 * Scroll reveal + counter animation + hero background
 * 滚动渐入 + 计数器动画 + Hero 背景
 */
(function () {
  'use strict';

  /** Scroll reveal with IntersectionObserver / 滚动渐入动画 */
  function initScrollReveal() {
    const elements = document.querySelectorAll('.reveal');
    if (!elements.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    elements.forEach(el => observer.observe(el));
  }

  /** Counter animation / 数字计数器动画 */
  function initCounters() {
    const counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach(el => observer.observe(el));
  }

  /** Animate a single counter / 执行单个计数器动画 */
  function animateCounter(el) {
    const target = el.dataset.count;
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    const isFloat = target.includes('.');
    const targetNum = parseFloat(target);
    const duration = 1500;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic / 缓出三次方
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = eased * targetNum;

      if (isFloat) {
        el.textContent = prefix + current.toFixed(1) + suffix;
      } else {
        el.textContent = prefix + Math.floor(current) + suffix;
      }

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }

  /** Hero grid background animation / Hero 网格背景动画 */
  function initHeroBackground() {
    const canvas = document.querySelector('.hero-canvas');
    if (!canvas || !(canvas instanceof HTMLCanvasElement)) return;

    const ctx = canvas.getContext('2d');
    let width, height, dots;
    let mouseX = -1000, mouseY = -1000;
    let animId;

    function resize() {
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
      createDots();
    }

    function createDots() {
      dots = [];
      const spacing = 40;
      const cols = Math.ceil(width / spacing);
      const rows = Math.ceil(height / spacing);
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          dots.push({
            x: i * spacing + spacing / 2,
            y: j * spacing + spacing / 2,
            baseRadius: 1,
            radius: 1
          });
        }
      }
    }

    function draw() {
      ctx.clearRect(0, 0, width, height);
      dots.forEach(dot => {
        const dx = mouseX - dot.x;
        const dy = mouseY - dot.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = 150;

        if (dist < maxDist) {
          const factor = 1 - dist / maxDist;
          dot.radius = dot.baseRadius + factor * 3;
          ctx.fillStyle = `rgba(37, 99, 235, ${0.2 + factor * 0.5})`;
        } else {
          dot.radius = dot.baseRadius;
          ctx.fillStyle = 'rgba(37, 99, 235, 0.08)';
        }

        ctx.beginPath();
        ctx.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    }

    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    });

    canvas.addEventListener('mouseleave', () => {
      mouseX = -1000;
      mouseY = -1000;
    });

    window.addEventListener('resize', resize);
    resize();
    draw();

    // Cleanup on page hide / 页面隐藏时清理
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        cancelAnimationFrame(animId);
      } else {
        draw();
      }
    });
  }

  /** Stagger animation for card grids / 卡片网格交错动画 */
  function initStaggerReveal() {
    const groups = document.querySelectorAll('.stagger-group');
    if (!groups.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const children = entry.target.children;
            Array.from(children).forEach((child, i) => {
              child.style.transitionDelay = `${i * 80}ms`;
              child.classList.add('visible');
            });
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    groups.forEach(el => observer.observe(el));
  }

  /** Initialize all animations / 初始化所有动画 */
  function init() {
    initScrollReveal();
    initCounters();
    initHeroBackground();
    initStaggerReveal();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
