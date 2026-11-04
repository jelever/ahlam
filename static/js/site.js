/* Ahlam Alqamar: interactions and motion.
   From the reference design (references/home-collections/ahlam, js/main.js
   and js/search.js): header, drawer, reveal and stagger, hero parallax, the
   olive slider and the search overlay. Carried over from the previous site:
   quick view, the gallery preview (lightbox) and the product gallery. New:
   the collection filter on the products page. No cart or store code. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const rtl = document.documentElement.dir === "rtl";
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const data = window.AHLAM || { products: {}, strings: {} };
  const S = data.strings;

  // The page stays locked while the drawer, the search or any modal is open.
  // iOS Safari ignores overflow: hidden on the body, so the page is pinned in
  // place (position: fixed at its scroll offset) and put back on close.
  let lockedY = null;
  // a cut-out's background tone (from build.py), filling the frame around it
  const edge = (im) => (im.cutout && im.edge ? ` style="--edge:${im.edge}"` : "");

  const lock = () => {
    const open = Boolean($(".modal.is-open, .drawer.is-open, .search-overlay.is-open"));
    const b = document.body.style;
    if (open && lockedY === null) {
      lockedY = window.scrollY;
      Object.assign(b, { position: "fixed", top: `-${lockedY}px`, left: "0", right: "0", overflow: "hidden" });
    } else if (!open && lockedY !== null) {
      Object.assign(b, { position: "", top: "", left: "", right: "", overflow: "" });
      const html = document.documentElement.style;
      html.scrollBehavior = "auto";          // jump back, do not smooth-scroll
      window.scrollTo(0, lockedY);
      html.scrollBehavior = "";
      lockedY = null;
    }
  };

  /* ---------- Header: frosted once the page scrolls ---------- */
  const header = $(".site-header");
  const onScroll = () => { if (lockedY === null) header?.classList.toggle("is-scrolled", window.scrollY > 24); };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- Drawer ---------- */
  const drawer = $(".drawer");
  const toggle = $(".menu-toggle");
  const setDrawer = (open) => {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    drawer.setAttribute("aria-hidden", String(!open));
    drawer.inert = !open;
    toggle?.setAttribute("aria-expanded", String(open));
    lock();
    if (open) setTimeout(() => $(".drawer-close", drawer)?.focus(), 80);
    else toggle?.focus();
  };
  if (drawer) drawer.inert = true;
  toggle?.addEventListener("click", () => setDrawer(true));
  drawer?.addEventListener("click", (e) => {
    if (e.target === drawer || e.target.closest(".drawer-close") || e.target.closest("a")) setDrawer(false);
  });

  /* ---------- Modals ----------
     They stack (the gallery opens over quick view): each remembers the
     element that opened it. */
  const setModal = (modal, open) => {
    if (open) modal._returnFocus = document.activeElement;
    modal.classList.toggle("is-open", open);
    modal.setAttribute("aria-hidden", String(!open));
    lock();
    if (open) setTimeout(() => $(".modal-close", modal)?.focus(), 60);
    else modal._returnFocus?.focus?.();
  };
  $$(".modal").forEach((modal) => modal.addEventListener("click", (e) => {
    if (e.target === modal || e.target.matches("[data-lb-stage], .lb-panel") || e.target.closest(".modal-close")) setModal(modal, false);
  }));

  /* ---------- Search overlay (Arabic-aware matching) ---------- */
  const search = $(".search-overlay");
  const setSearch = (open) => {
    if (!search) return;
    if (open) search._returnFocus = document.activeElement;
    search.classList.toggle("is-open", open);
    search.setAttribute("aria-hidden", String(!open));
    search.inert = !open;
    lock();
    if (open) setTimeout(() => $("#search-input", search)?.focus(), 60);
    else search._returnFocus?.focus?.();
  };
  if (search) {
    search.inert = true;
    const input = $("#search-input", search);
    const results = $("[data-search-results]", search);
    // hamza forms, alef maqsura and taa marbuta match their plain letters;
    // diacritics and tatweel are ignored
    const norm = (s) => String(s || "").toLowerCase().normalize("NFKD")
      .replace(/[ً-ٰٟـ]/g, "")
      .replace(/[أإآٱ]/g, "ا").replace(/ى/g, "ي").replace(/ة/g, "ه").replace(/ؤ/g, "و").replace(/ئ/g, "ي");
    const index = Object.entries(data.products).map(([slug, p]) => ({
      slug, p, text: norm([p.name, p.collection, slug.replace(/-/g, " "), ...p.fields.map((f) => f[1])].join(" ")),
    }));
    const render = () => {
      const raw = input.value.trim();
      const q = norm(raw);
      if (!q) { results.innerHTML = ""; return; }
      const words = q.split(/\s+/);
      const hits = index.filter((it) => words.every((w) => it.text.includes(w))).slice(0, 12);
      if (!hits.length) { results.innerHTML = `<p class="search-empty">${esc(S.search_empty)} «${esc(raw)}»</p>`; return; }
      results.innerHTML = `<p class="search-label">${esc(S.search_results)} (${hits.length})</p><div class="search-grid">` +
        hits.map(({ p }) => `<a class="search-item" href="${p.url}">
          <span class="search-thumb"><img src="${p.thumb}" alt="" width="64" height="64" loading="lazy" class="${p.images[0].cutout ? "is-cutout" : "is-photo"}"${edge(p.images[0])}></span>
          <span><strong>${esc(p.name)}</strong><small>${esc(p.collection)}</small></span>
        </a>`).join("") + "</div>";
    };
    input.addEventListener("input", render);
    $$("[data-search-open]").forEach((b) => b.addEventListener("click", () => setSearch(true)));
    $("[data-search-close]", search).addEventListener("click", () => setSearch(false));
    search.addEventListener("click", (e) => { if (e.target === search) setSearch(false); });
    $$("[data-search-term]", search).forEach((b) => b.addEventListener("click", () => {
      input.value = b.dataset.searchTerm; render(); input.focus();
    }));
    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && !search.classList.contains("is-open") && !$(".modal.is-open") &&
          !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) {
        e.preventDefault(); setSearch(true);
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    // close only the top-most layer (the gallery before quick view)
    const top = $(".lightbox.is-open") || $(".modal.is-open");
    if (top) { setModal(top, false); return; }
    if (search?.classList.contains("is-open")) { setSearch(false); return; }
    if (drawer?.classList.contains("is-open")) setDrawer(false);
  });

  /* ---------- Gallery preview (full-size photos, product page + quick view) ---------- */
  const lb = $('[data-modal="lightbox"]');
  let lbItems = [];
  let lbCur = 0;
  const lbShow = (i) => {
    if (!lb || !lbItems.length) return;
    lbCur = (i + lbItems.length) % lbItems.length;
    const it = lbItems[lbCur];
    $("[data-lb-frame]", lb).innerHTML = `<img src="${it.src}" srcset="${it.srcset}" sizes="100vw" alt="${esc(it.alt)}" class="${it.cutout ? "is-cutout" : "is-photo"}"${edge(it)}>`;
    $("[data-lb-label]", lb).textContent = it.label || "";
    $("[data-lb-count]", lb).textContent = lbItems.length > 1 ? `${lbCur + 1} / ${lbItems.length}` : "";
    $$(".lb-nav", lb).forEach((b) => { b.hidden = lbItems.length < 2; });
  };
  const openGallery = (items, i) => {
    if (!lb || !items.length) return;
    lbItems = items;
    lbShow(i);
    setModal(lb, true);
  };
  if (lb) {
    $("[data-lb-prev]", lb).addEventListener("click", () => lbShow(lbCur - 1));
    $("[data-lb-next]", lb).addEventListener("click", () => lbShow(lbCur + 1));
    document.addEventListener("keydown", (e) => {
      if (!lb.classList.contains("is-open")) return;
      // the "next" photo is to the left in Arabic
      if (e.key === "ArrowRight") lbShow(lbCur + (rtl ? -1 : 1));
      if (e.key === "ArrowLeft") lbShow(lbCur + (rtl ? 1 : -1));
    });
    let lx = null;
    lb.addEventListener("touchstart", (e) => { lx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", (e) => {
      if (lx === null || lbItems.length < 2) return;
      const dx = e.changedTouches[0].clientX - lx;
      if (Math.abs(dx) > 40) lbShow(lbCur + ((dx < 0) !== rtl ? 1 : -1));
      lx = null;
    });
  }

  /* ---------- Product gallery (product page) ---------- */
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
    const main = $(".pdp-main", g);
    main?.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    main?.addEventListener("touchend", (e) => {
      if (x0 === null || slides.length < 2) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) show(cur + ((dx < 0) !== rtl ? 1 : -1));
      x0 = null;
    });
    const items = () => $$("[data-slide] img", g).map((img) => ({
      src: img.getAttribute("src"), srcset: img.getAttribute("srcset"), alt: img.alt,
      cutout: img.classList.contains("is-cutout"), edge: img.style.getPropertyValue("--edge"),
      label: img.closest("figure")?.querySelector("figcaption")?.textContent || "",
    }));
    $("[data-lb-open]", g)?.addEventListener("click", () => openGallery(items(), cur));
    $$("[data-slide] img", g).forEach((img) => img.addEventListener("click", () => openGallery(items(), cur)));
  });

  /* ---------- Quick view (product cards) ---------- */
  const icon = (id) => `<svg class="icon" aria-hidden="true"><use href="#${id}"/></svg>`;
  const pic = (im, alt, sizes) => `<img src="${im.src}" srcset="${im.srcset}" sizes="${sizes}" width="${im.w}" height="${im.h}" alt="${esc(alt)}" class="${im.cutout ? "is-cutout" : "is-photo"}"${edge(im)} decoding="async">`;
  const qvModal = $('[data-modal="quick-view"]');
  const quickView = (slug) => {
    const p = data.products[slug];
    const body = $("[data-qv-body]");
    if (!p || !body || !qvModal) return;
    const main = (i) => pic(p.images[i], p.name + (p.images[i].label ? ` (${p.images[i].label})` : ""), "(max-width: 900px) 92vw, 450px");
    const thumbs = p.images.length > 1
      ? `<div class="qv-thumbs" role="group" aria-label="${esc(S.images_shown)}">${p.images.map((im, i) =>
          `<button type="button" class="qv-thumb${i ? "" : " is-active"}" data-qv-thumb="${i}" aria-pressed="${!i}" aria-label="${esc(im.label || `${i + 1} / ${p.images.length}`)}">${pic(im, "", "90px")}</button>`).join("")}</div>`
      : "";
    const fields = p.fields.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd><bdi>${esc(v)}</bdi></dd></div>`).join("");
    const ext = p.external ? ' target="_blank" rel="noopener"' : "";
    body.innerHTML = `<div class="qv">
      <div class="qv-media">
        <div class="qv-img">
          <div class="qv-frame" data-qv-main>${main(0)}</div>
          <button type="button" class="icon-btn lb-open" data-qv-zoom aria-label="${esc(S.gallery_open)}">${icon("i-expand")}</button>
        </div>
        ${thumbs}
        <p class="qv-label" data-qv-label>${esc(p.images[0].label)}</p>
      </div>
      <div class="qv-info">
        <p class="eyebrow">${icon("i-dot")}${esc(p.collection)}</p>
        <h2 class="qv-title">${esc(p.name)}</h2>
        <p class="muted">${esc(p.summary)}</p>
        <dl class="pd-specs">${fields}</dl>
        <div class="qv-actions">
          <a class="btn btn-dark" href="${p.enquire}"${ext}>${esc(S.enquire)} ${icon("i-arrow")}</a>
          <a class="text-link" href="${p.url}">${esc(S.view_details)} ${icon("i-arrow")}</a>
        </div>
      </div>
    </div>`;
    let qvCur = 0;
    const zoom = () => openGallery(p.images.map((im) => ({
      src: im.src, srcset: im.srcset, cutout: im.cutout, edge: im.edge, label: im.label,
      alt: p.name + (im.label ? ` (${im.label})` : ""),
    })), qvCur);
    $("[data-qv-zoom]", body).addEventListener("click", zoom);
    $("[data-qv-main]", body).addEventListener("click", zoom);
    $$("[data-qv-thumb]", body).forEach((b) => b.addEventListener("click", () => {
      const i = Number(b.dataset.qvThumb);
      qvCur = i;
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

  /* ---------- Scroll reveal + stagger ---------- */
  $$("[data-reveal-group]").forEach((group) => {
    $$(":scope > [data-reveal]", group).forEach((el, i) => el.style.setProperty("--d", `${Math.min(i, 8) * 0.08}s`));
  });
  const reveal = (el) => el.classList.add("is-in");
  let io = null;
  if ("IntersectionObserver" in window && !reduceMotion) {
    io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { reveal(entry.target); io.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.08 });
    $$("[data-reveal]").forEach((el) => io.observe(el));
  } else {
    $$("[data-reveal]").forEach(reveal);
  }

  /* ---------- Hero parallax (after the entrance zoom), desktop only ----------
     The photo drifts down as the page scrolls, by at most the spare image
     the scale leaves above the frame, so the frame's empty top never shows.
     Off on phones and touch screens: there the photo stacks under the copy,
     and moving it during touch scrolling made it look stuck. */
  const para = $("[data-parallax]");
  const desktop = window.matchMedia("(min-width: 901px) and (hover: hover) and (pointer: fine)");
  if (para && !reduceMotion) {
    const img = $("img", para);
    const SCALE = 1.08;
    let ready = false, ticking = false;
    const update = () => {
      ticking = false;
      if (!ready || !img) return;
      if (!desktop.matches) { img.style.transform = ""; return; }
      const room = para.offsetHeight * (SCALE - 1) / 2;
      const y = Math.min(window.scrollY * 0.06, room);
      img.style.transform = `translateY(${y.toFixed(1)}px) scale(${SCALE})`;
    };
    // the entrance zoom keeps its last frame (fill: both), which would win
    // over the inline transform: drop it once it has played
    img?.addEventListener("animationend", () => { img.style.animation = "none"; ready = true; update(); }, { once: true });
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    desktop.addEventListener?.("change", update);
  }

  /* ---------- Olive slider (cross-fade) ---------- */
  $$('[data-slider="arrival"]').forEach((arrival) => {
    const slides = $$(".arrival-slide", arrival);
    const dotsWrap = $("[data-dots]", arrival);
    if (slides.length < 2 || !dotsWrap) return;
    let index = 0;
    let timer;
    const dots = slides.map((_, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", `${i + 1} / ${slides.length}`);
      b.addEventListener("click", () => { go(i); restart(); });
      dotsWrap.appendChild(b);
      return b;
    });
    const go = (i) => {
      index = (i + slides.length) % slides.length;
      slides.forEach((s, k) => {
        s.classList.toggle("is-active", k === index);
        s.setAttribute("aria-hidden", String(k !== index));
        s.inert = k !== index;
      });
      dots.forEach((d, k) => { d.classList.toggle("is-active", k === index); d.setAttribute("aria-current", String(k === index)); });
    };
    const restart = () => {
      clearInterval(timer);
      if (!reduceMotion) timer = setInterval(() => go(index + 1), 6000);
    };
    $("[data-prev]", arrival)?.addEventListener("click", () => { go(index - 1); restart(); });
    $("[data-next]", arrival)?.addEventListener("click", () => { go(index + 1); restart(); });
    arrival.addEventListener("mouseenter", () => clearInterval(timer));
    arrival.addEventListener("mouseleave", restart);
    arrival.addEventListener("focusin", () => clearInterval(timer));
    let x0 = null;
    arrival.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    arrival.addEventListener("touchend", (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) { go(index + ((dx < 0) !== rtl ? 1 : -1)); restart(); }
      x0 = null;
    });
    go(0);
    restart();
  });

  /* ---------- Products page: filter by collection, kept in ?c= ---------- */
  const grid = $("[data-filter-grid]");
  if (grid) {
    const chips = $$("[data-filter]");
    const cards = $$(".product-card", grid);
    const links = $("[data-coll-link]");
    const known = new Set(chips.map((c) => c.dataset.filter));
    const apply = (slug, animate) => {
      if (!known.has(slug)) slug = "";
      chips.forEach((c) => {
        const on = c.dataset.filter === slug;
        c.classList.toggle("is-active", on);
        if (on) c.setAttribute("aria-current", "true"); else c.removeAttribute("aria-current");
      });
      cards.forEach((card) => {
        card.hidden = Boolean(slug) && card.dataset.coll !== slug;
        if (!card.hidden) reveal(card);
      });
      if (links) {
        links.hidden = !slug;
        $$("[data-for]", links).forEach((p) => { p.hidden = p.dataset.for !== slug; });
      }
      if (animate && !reduceMotion) { grid.classList.remove("is-refreshing"); void grid.offsetWidth; grid.classList.add("is-refreshing"); }
    };
    const fromUrl = () => new URLSearchParams(location.search).get("c") || "";
    chips.forEach((chip) => chip.addEventListener("click", (e) => {
      e.preventDefault();
      const slug = chip.dataset.filter;
      const url = new URL(location.href);
      if (slug) url.searchParams.set("c", slug); else url.searchParams.delete("c");
      history.pushState({ c: slug }, "", url);
      apply(slug, true);
    }));
    window.addEventListener("popstate", () => apply(fromUrl(), true));
    apply(fromUrl(), false);
    // bring the chosen chip into view on phones
    if (fromUrl()) $(".chip.is-active", $(".shop-cats"))?.scrollIntoView({ block: "nearest", inline: "center" });
  }

  /* ---------- Misc ---------- */
  $$("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
