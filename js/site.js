// BestDish — light scroll reveal + magnetic CTA
(function () {
  // Promote to "JS ready" so CSS can hide reveal targets and play the animation.
  // Without this class, .bd-reveal stays visible (no-JS / search engines / screenshot tools).
  document.documentElement.classList.add('js-reveal-ready');

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    // Reduced motion — reveal everything immediately.
    document.querySelectorAll('.bd-reveal').forEach((el) => el.classList.add('is-in'));
    return;
  }

  // Reveal-on-scroll
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '-10% 0px -10% 0px', threshold: 0.05 });

  document.querySelectorAll('.bd-reveal').forEach((el) => io.observe(el));

  // Subtle magnetic hover on .bd-btn--primary (within ~40px)
  document.querySelectorAll('.bd-btn--primary').forEach((btn) => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.18}px, ${y * 0.18}px)`;
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = '';
    });
  });

  // Splash parallax (light)
  const splashes = document.querySelectorAll('.bd-splash-fixed');
  if (splashes.length) {
    let raf = null;
    window.addEventListener('scroll', () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const y = window.scrollY;
        splashes.forEach((s, i) => {
          const speed = parseFloat(s.dataset.speed || (0.06 + i * 0.03));
          s.style.transform = `translateY(${y * speed}px) rotate(${y * speed * 0.6}deg)`;
        });
        raf = null;
      });
    }, { passive: true });
  }
})();
