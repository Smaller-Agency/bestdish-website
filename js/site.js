// BestDish — light scroll reveal + magnetic CTA
(function () {
  // Promote to "JS ready" so CSS can hide reveal targets and play the animation.
  // Without this class, .bd-reveal stays visible (no-JS / search engines / screenshot tools).
  document.documentElement.classList.add('js-reveal-ready');

  // Rotating hero showcase — crossfade through the featured dishes.
  // Runs regardless of reduced-motion (it just won't auto-advance there).
  document.querySelectorAll('.bd-hero-show').forEach((show) => {
    const slides = [...show.querySelectorAll('.bd-hero-show__slide')];
    const dots = [...show.querySelectorAll('.bd-hero-show__dots span')];
    const credit = (show.closest('.bd-hero-wrap') || document).querySelector('.bd-hero-full__credit');
    if (slides.length < 2) return;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let i = 0, timer = null;
    const show_n = (n) => {
      slides[i].classList.remove('is-active'); if (dots[i]) dots[i].classList.remove('is-on');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('is-active'); if (dots[i]) dots[i].classList.add('is-on');
      if (credit && slides[i].dataset.credit) credit.textContent = slides[i].dataset.credit;
    };
    const start = () => { if (reduce) return; clearInterval(timer); timer = setInterval(() => show_n(i + 1), parseInt(show.dataset.interval, 10) || 3500); };
    dots.forEach((d, idx) => d.addEventListener('click', (e) => { e.preventDefault(); show_n(idx); start(); }));
    show.addEventListener('mouseenter', () => clearInterval(timer));
    show.addEventListener('mouseleave', start);
    start();
  });

  // Savings calculator ("The math") — runs regardless of reduced-motion.
  const calc = document.getElementById('bd-calc');
  if (calc) {
    const PRICE = 24, WEEKS = 52;
    let meals = 4, price = 36;
    const mealsEl = document.getElementById('bd-calc-meals');
    const priceEl = document.getElementById('bd-calc-price');
    const resultEl = document.getElementById('bd-calc-result');
    const fmt = (n) => '$' + Math.round(n).toLocaleString('en-CA');
    const update = () => {
      mealsEl.textContent = meals;
      priceEl.textContent = fmt(price);
      resultEl.textContent = fmt(Math.max(price - PRICE, 0) * meals * WEEKS);
    };
    calc.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-calc]');
      if (!btn) return;
      const k = btn.dataset.calc;
      if (k === 'meals-') meals = Math.max(1, meals - 1);
      else if (k === 'meals+') meals = Math.min(14, meals + 1);
      else if (k === 'price-') price = Math.max(24, price - 1);
      else if (k === 'price+') price = Math.min(60, price + 1);
      update();
    });
    update();
  }

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

  // Restaurant map (Leaflet) — renders only where the map container exists
  // and the library loaded. Logo pins, branded popups, scroll-zoom disabled.
  const mapEl = document.getElementById('bd-map');
  const mapData = document.getElementById('bd-map-data');
  if (mapEl && mapData && window.L) {
    try {
      const rests = JSON.parse(mapData.textContent);
      const map = L.map(mapEl, { scrollWheelZoom: false, zoomControl: true });
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd', maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
      }).addTo(map);
      const markers = rests.map((r) => {
        const icon = L.divIcon({
          className: 'bd-pin',
          html: '<span class="bd-pin__tile"><img src="' + r.logo + '" alt=""></span><span class="bd-pin__point"></span>',
          iconSize: [52, 64], iconAnchor: [26, 64], popupAnchor: [0, -60]
        });
        return L.marker([r.lat, r.lng], { icon, title: r.name })
          .bindPopup(
            '<strong>' + r.name + '</strong>' +
            '<span class="bd-popup__meta">' + r.hood + ' &middot; ' + r.dish + '</span>' +
            '<a class="bd-popup__link" href="' + r.url + '">View &rarr;</a>',
            { className: 'bd-popup', closeButton: false }
          );
      });
      const group = L.featureGroup(markers).addTo(map);
      map.fitBounds(group.getBounds().pad(0.15));
    } catch (err) { /* leave the container empty on any failure */ }
  }

  // Single-location map on a dish page (the restaurant's spot).
  const dishMapEl = document.getElementById('bd-dishmap');
  if (dishMapEl && window.L) {
    try {
      const lat = parseFloat(dishMapEl.dataset.lat), lng = parseFloat(dishMapEl.dataset.lng);
      const map = L.map(dishMapEl, { scrollWheelZoom: false, zoomControl: true });
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd', maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
      }).addTo(map);
      const icon = L.divIcon({
        className: 'bd-pin',
        html: '<span class="bd-pin__tile"><img src="' + dishMapEl.dataset.logo + '" alt=""></span><span class="bd-pin__point"></span>',
        iconSize: [52, 64], iconAnchor: [26, 64]
      });
      L.marker([lat, lng], { icon }).addTo(map);
      map.setView([lat, lng], 15);
    } catch (err) { /* leave empty on failure */ }
  }

  // Buildings map — every freezer location, live vs coming pins.
  const bldgMapEl = document.getElementById('bd-buildings-map');
  const bldgData = document.getElementById('bd-buildings-map-data');
  if (bldgMapEl && bldgData && window.L) {
    try {
      const bldgs = JSON.parse(bldgData.textContent);
      const map = L.map(bldgMapEl, { scrollWheelZoom: false, zoomControl: true });
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd', maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
      }).addTo(map);
      const markers = bldgs.map((b) => {
        const icon = L.divIcon({
          className: 'bd-pin',
          html: '<span class="bd-bldgpin' + (b.live ? ' bd-bldgpin--live' : '') + '"></span>',
          iconSize: [22, 22], iconAnchor: [11, 11], popupAnchor: [0, -14]
        });
        return L.marker([b.lat, b.lng], { icon, title: b.name })
          .bindPopup(
            '<strong>' + b.name + '</strong>' +
            '<span class="bd-popup__meta">' + b.address + ' &middot; ' + b.status + '</span>',
            { className: 'bd-popup', closeButton: false }
          );
      });
      const group = L.featureGroup(markers).addTo(map);
      map.fitBounds(group.getBounds().pad(0.18));
    } catch (err) { /* leave the container empty on any failure */ }
  }

  // Feedback form — no backend, so compose a pre-filled email to feedback@bestdish.ca
  const fbForm = document.querySelector('.bd-feedback-form');
  if (fbForm) {
    fbForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = (id) => { const el = fbForm.querySelector('#' + id); return el ? el.value.trim() : ''; };
      const name = val('fb-name'), email = val('fb-email'), msg = val('fb-msg');
      const subject = 'BestDish feedback' + (name ? ' from ' + name : '');
      const body = (msg || '') + '\n\n— ' + (name || 'A visitor') + (email ? ' (' + email + ')' : '');
      window.location.href = 'mailto:feedback@bestdish.ca?subject=' +
        encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    });
  }

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
