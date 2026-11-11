/* Shared helpers for the web maps: panel collapse, loading and error states, number format. */
(() => {
  "use strict";
  const root = document.documentElement;
  root.classList.add("gis");
  /* ?thumb: the map alone, for the site's thumbnails */
  if (new URLSearchParams(location.search).has("thumb")) {
    root.classList.add("gis-thumb", "gis-collapsed");
    // let maps that sized themselves before the panel was hidden fill the whole frame
    addEventListener("load", () => [0, 300, 1200].forEach((t) => setTimeout(() => dispatchEvent(new Event("resize")), t)));
  }

  const NB = " ";
  const GIS = {
    /* 2 500, with a non-breaking space */
    fmt: (n, d = 0) => (n == null || isNaN(n) ? "–" : Number(n).toFixed(d).replace(/\B(?=(\d{3})+(?!\d))/g, NB)),

    /* loading → ready, or a readable error */
    state(el, msg, err) {
      if (!el) return;
      if (msg === null) { el.classList.add("gone"); return; }
      el.classList.remove("gone"); el.classList.toggle("err", !!err);
      el.innerHTML = `<span class="gis-spin"></span><span></span>`;
      el.lastChild.textContent = msg;
    },

    /* panel open or closed; maps redraw on the resize event */
    setPanel(open) {
      root.classList.toggle("gis-collapsed", !open);
      document.querySelectorAll("[data-gis-toggle]").forEach((b) => b.setAttribute("aria-expanded", String(open)));
      requestAnimationFrame(() => dispatchEvent(new Event("resize")));
    },

    /* scale bar from the map's real km per screen pixel: a round length no wider than max px */
    scale(el, kmPerPx, max = 110) {
      if (!el || !(kmPerPx > 0)) return;
      const raw = kmPerPx * max, p = Math.pow(10, Math.floor(Math.log10(raw)));
      const km = [5, 2, 1].map((f) => f * p).find((v) => v <= raw) || p;
      const label = km >= 1 ? `${GIS.fmt(km)} km` : `${GIS.fmt(km * 1000)} m`;
      el.innerHTML = `${label}<i style="width:${(km / kmPerPx).toFixed(1)}px"></i>`;
    },

    /* size of the map workspace */
    size(el) { const r = el.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; },
  };

  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-gis-toggle]");
    if (b) GIS.setPanel(root.classList.contains("gis-collapsed"));
  });

  window.GIS = GIS;
})();
