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
