/* Ahlam Alqamar — interactions and motion, carried over from the Homely site
   (header, mega menu, drawer, reveal, letter-split titles, hero zoom, tabs,
   gallery). The store scripts (cart, wishlist, quick view, forms) are gone. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const rtl = document.documentElement.dir === "rtl";
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const lock = (on) => { document.body.style.overflow = on ? "hidden" : ""; };

  /* ---------- Header: shadow on scroll, hide when scrolling down ---------- */
  const header = $(".site-header");
  let lastY = window.scrollY;
  const onScroll = () => {
    const y = window.scrollY;
    header?.classList.toggle("is-scrolled", y > 16);
    const menuOpen = $(".nav-item.is-open");
    if (header && !menuOpen) header.classList.toggle("is-hidden", y > 480 && y > lastY + 4);
    if (y < lastY - 4) header?.classList.remove("is-hidden");
    lastY = y;
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- Mega menu (hover on desktop, click everywhere) ---------- */
  const items = $$(".nav-item.has-drop");
  const closeAll = (except) => items.forEach((it) => {
    if (it === except) return;
    it.classList.remove("is-open");
    $("[aria-expanded]", it)?.setAttribute("aria-expanded", "false");
  });
  items.forEach((it) => {
    const btn = $(".nav-caret, .nav-drop-btn", it);
    let timer;
    const open = () => { clearTimeout(timer); closeAll(it); it.classList.add("is-open"); btn?.setAttribute("aria-expanded", "true"); };
    const close = () => { timer = setTimeout(() => { it.classList.remove("is-open"); btn?.setAttribute("aria-expanded", "false"); }, 160); };
    it.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") open(); });
    it.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") close(); });
    btn?.addEventListener("click", (e) => {
      e.stopPropagation();
      if (it.classList.contains("is-open")) { it.classList.remove("is-open"); btn.setAttribute("aria-expanded", "false"); }
      else open();
    });
    it.addEventListener("focusout", (e) => { if (!it.contains(e.relatedTarget)) { it.classList.remove("is-open"); btn?.setAttribute("aria-expanded", "false"); } });
  });
  document.addEventListener("click", (e) => { if (!e.target.closest(".nav-item")) closeAll(); });

  /* ---------- Drawer ---------- */
  const drawer = $(".drawer");
  const toggle = $(".menu-toggle");
  const setDrawer = (open) => {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    drawer.setAttribute("aria-hidden", String(!open));
    drawer.inert = !open;
    toggle?.setAttribute("aria-expanded", String(open));
    lock(open);
    if (open) setTimeout(() => $(".drawer-close", drawer)?.focus(), 80);
    else toggle?.focus();
  };
  if (drawer) drawer.inert = true;
  toggle?.addEventListener("click", () => setDrawer(true));
  drawer?.addEventListener("click", (e) => {
    if (e.target === drawer || e.target.closest(".drawer-close") || e.target.closest("a")) setDrawer(false);
  });
  /* ---------- Modals ---------- */
  let lastFocus;
  const setModal = (modal, open) => {
    if (open) lastFocus = document.activeElement;
    modal.classList.toggle("is-open", open);
    modal.setAttribute("aria-hidden", String(!open));
    lock(open);
    if (open) setTimeout(() => $(".modal-close", modal)?.focus(), 60);
    else lastFocus?.focus?.();
  };
  $$(".modal").forEach((modal) => modal.addEventListener("click", (e) => {
    if (e.target === modal || e.target.closest(".modal-close")) setModal(modal, false);
  }));

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    $$(".modal.is-open").forEach((mo) => setModal(mo, false));
    if (drawer?.classList.contains("is-open")) setDrawer(false);
    closeAll();
  });

  /* ---------- Quick view (product cards) ---------- */
  const data = window.AHLAM || { products: {}, strings: {} };
  const S = data.strings;
  const icon = (id) => `<svg class="icon" aria-hidden="true"><use href="#${id}"/></svg>`;
  const pic = (im, alt, sizes) => `<img src="${im.src}" srcset="${im.srcset}" sizes="${sizes}" width="${im.w}" height="${im.h}" alt="${esc(alt)}" class="${im.cutout ? "is-cutout" : "is-photo"}" decoding="async">`;
  const qvModal = $('[data-modal="quick-view"]');
  const quickView = (slug) => {
    const p = data.products[slug];
    const body = $("[data-qv-body]");
    if (!p || !body || !qvModal) return;
    const main = (i) => pic(p.images[i], p.name + (p.images[i].label ? " — " + p.images[i].label : ""), "(max-width: 1024px) 92vw, 450px");
    const thumbs = p.images.length > 1
      ? `<div class="qv-thumbs" role="group" aria-label="${esc(S.images_shown)}">${p.images.map((im, i) =>
          `<button type="button" class="qv-thumb${i ? "" : " is-active"}" data-qv-thumb="${i}" aria-pressed="${!i}" aria-label="${esc(im.label || `${i + 1} / ${p.images.length}`)}">${pic(im, "", "110px")}</button>`).join("")}</div>`
      : "";
    const fields = p.fields.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd><bdi>${esc(v)}</bdi></dd></div>`).join("");
    const ext = p.external ? ' target="_blank" rel="noopener"' : "";
    body.innerHTML = `<div class="qv">
      <div class="qv-media">
        <div class="qv-img img-zoom" data-qv-main>${main(0)}</div>
        ${thumbs}
        <p class="qv-label" data-qv-label>${esc(p.images[0].label)}</p>
      </div>
      <div class="qv-info">
        <p class="eyebrow">${esc(p.collection)}</p>
        <h2 class="qv-title">${esc(p.name)}</h2>
        <p class="muted">${esc(p.summary)}</p>
        <dl class="pd-specs">${fields}</dl>
        <div class="qv-actions">
          <a class="btn btn-dark" href="${p.enquire}"${ext}><span class="btn-dot"></span>${esc(S.enquire)}</a>
          <a class="arrow-link" href="${p.url}"><span>${esc(S.view_details)}</span><span class="arrow-dot">${icon("i-arrow-up")}</span></a>
        </div>
      </div>
    </div>`;
    $$("[data-qv-thumb]", body).forEach((b) => b.addEventListener("click", () => {
      const i = Number(b.dataset.qvThumb);
      $("[data-qv-main]", body).innerHTML = main(i);
      $("[data-qv-label]", body).textContent = p.images[i].label;
      $$("[data-qv-thumb]", body).forEach((o) => { o.classList.toggle("is-active", o === b); o.setAttribute("aria-pressed", String(o === b)); });
    }));
    setModal(qvModal, true);
  };
  document.addEventListener("click", (e) => {
    const qv = e.target.closest("[data-quick-view]");
    if (qv) { e.preventDefault(); quickView(qv.dataset.quickView); }
  });

  /* ---------- Giant titles: split into letters that rise one by one ---------- */
  $$(".h-giant").forEach((el) => {
    if (reduceMotion || document.documentElement.lang === "ar") return; // keep Arabic letters joined
    const text = el.textContent.trim();
    el.setAttribute("aria-label", text);
    el.innerHTML = [...text].map((ch, i) => ch === " " ? " " :
      `<span class="ch-wrap" aria-hidden="true"><span class="ch" style="--i:${i}">${esc(ch)}</span></span>`).join("");
  });

  /* ---------- Scroll reveal + stagger ---------- */
  $$("[data-reveal-group]").forEach((group) => {
    $$(":scope > [data-reveal]", group).forEach((el, i) => el.style.setProperty("--d", `${Math.min(i, 8) * 0.09}s`));
  });
  const reveal = (el) => el.classList.add("is-in");
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { reveal(entry.target); io.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    $$("[data-reveal], .h-giant").forEach((el) => io.observe(el));
  } else {
    $$("[data-reveal], .h-giant").forEach(reveal);
  }

  /* ---------- Hero image: gentle zoom as the page scrolls ---------- */
  const para = $("[data-parallax]");
  if (para && !reduceMotion) {
    const img = $("img", para);
    let ticking = false;
    const update = () => {
      const r = para.getBoundingClientRect();
      const p = Math.min(Math.max(-r.top / r.height, 0), 1);
      img.style.setProperty("--ps", (1 + p * 0.08).toFixed(4));
      ticking = false;
    };
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  }

  /* ---------- Tabs with a sliding pill ---------- */
  $$("[data-tabs]").forEach((tabs) => {
    const list = $(".tab-list", tabs);
    const btns = $$(".tab-btn", list);
    const pill = $(".tab-pill", list);
    const panels = btns.map((b) => document.getElementById(b.getAttribute("aria-controls")));
    const place = () => {
      const active = btns.find((b) => b.getAttribute("aria-selected") === "true") || btns[0];
      if (!pill || !active) return;
      const lr = list.getBoundingClientRect();
      const br = active.getBoundingClientRect();
      // the pill is anchored at inset-inline-start: 0, which is the right edge in RTL
      const x = rtl ? -(lr.right - br.right) : br.left - lr.left;
      pill.style.setProperty("--x", `${x}px`);
      pill.style.setProperty("--w", `${br.width}px`);
      pill.style.setProperty("--y", `${br.top - lr.top}px`);
      pill.style.setProperty("--h", `${br.height}px`);
    };
    const select = (i, focus) => {
      btns.forEach((b, j) => {
        const on = i === j;
        b.setAttribute("aria-selected", String(on));
        b.tabIndex = on ? 0 : -1;
        if (panels[j]) {
          panels[j].hidden = !on;
          panels[j].classList.toggle("is-active", on);
          if (on && !reduceMotion) {
            panels[j].classList.remove("is-entering"); void panels[j].offsetWidth; panels[j].classList.add("is-entering");
            $$("[data-reveal]", panels[j]).forEach(reveal);
          }
        }
      });
      if (focus) btns[i].focus();
      place();
    };
    btns.forEach((b, i) => {
      b.addEventListener("click", () => select(i));
      b.addEventListener("keydown", (e) => {
        const next = { ArrowRight: rtl ? -1 : 1, ArrowLeft: rtl ? 1 : -1, Home: -99, End: 99 }[e.key];
        if (next === undefined) return;
        e.preventDefault();
        const n = next === -99 ? 0 : next === 99 ? btns.length - 1 : (i + next + btns.length) % btns.length;
        select(n, true);
      });
    });
    // pill position needs fonts and layout; the list is always rendered, so observe its size
    if ("ResizeObserver" in window) new ResizeObserver(place).observe(list);
    document.fonts?.ready.then(place);
    place();
  });

  /* ---------- Product gallery ---------- */
  $$("[data-gallery]").forEach((g) => {
    const slides = $$("[data-slide]", g);
    const thumbs = $$("[data-thumb]", g);
    let cur = 0;
    const show = (i) => {
      cur = (i + slides.length) % slides.length;
      slides.forEach((s, j) => { s.hidden = j !== cur; s.classList.toggle("is-active", j === cur); });
      thumbs.forEach((t, j) => { t.classList.toggle("is-active", j === cur); t.setAttribute("aria-pressed", String(j === cur)); });
    };
    thumbs.forEach((t, i) => t.addEventListener("click", () => show(i)));
    $("[data-gallery-prev]", g)?.addEventListener("click", () => show(cur - 1));
    $("[data-gallery-next]", g)?.addEventListener("click", () => show(cur + 1));
    let x0 = null;
    const main = $(".pd-main", g);
    main?.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    main?.addEventListener("touchend", (e) => {
      if (x0 === null || slides.length < 2) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) show(cur + ((dx < 0) !== rtl ? 1 : -1));
      x0 = null;
    });
  });

  /* ---------- Misc ---------- */
  $$("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
