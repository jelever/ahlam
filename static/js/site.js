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
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (drawer?.classList.contains("is-open")) setDrawer(false);
    closeAll();
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
