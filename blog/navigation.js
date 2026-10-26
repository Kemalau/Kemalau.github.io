(() => {
  "use strict";

  const sidebar = document.querySelector(".toc-sidebar");
  if (!sidebar) return;

  const titleLink = sidebar.querySelector(".toc-title");
  const entries = Array.from(sidebar.querySelectorAll("nav a[href^='#']"))
    .map((link) => {
      let heading;
      try {
        heading = document.getElementById(decodeURIComponent(link.hash.slice(1)));
      } catch {
        return null;
      }
      return heading ? { link, heading } : null;
    })
    .filter(Boolean);
  if (!entries.length) return;

  const links = [titleLink, ...entries.map(({ link }) => link)].filter(Boolean);
  const desktop = window.matchMedia("(min-width: 1200px)");
  let activeLink = null;
  let pending = false;
  let revealRequested = false;

  function revealInSidebar(link) {
    if (!desktop.matches || !link) return;
    const bounds = sidebar.getBoundingClientRect();
    const item = link.getBoundingClientRect();
    const inset = 12;

    // Only move the sidebar's scroll position, never the reading position.
    if (item.top < bounds.top + inset) {
      sidebar.scrollTop -= bounds.top + inset - item.top;
    } else if (item.bottom > bounds.bottom - inset) {
      sidebar.scrollTop += item.bottom - bounds.bottom + inset;
    }
  }

  function update(reveal) {
    const threshold = Math.min(120, Math.max(64, window.innerHeight * 0.15));
    let next = titleLink;

    for (const { link, heading } of entries) {
      if (heading.getBoundingClientRect().top > threshold) break;
      next = link;
    }

    const page = document.scrollingElement || document.documentElement;
    if (window.scrollY > 0 && window.scrollY + window.innerHeight >= page.scrollHeight - 2) {
      next = entries[entries.length - 1].link;
    }

    if (next !== activeLink) {
      links.forEach((link) => {
        if (link === next) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
      activeLink = next;
      reveal = true;
    }
    if (reveal) revealInSidebar(activeLink);
  }

  function schedule(reveal = false) {
    revealRequested = revealRequested || reveal;
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(() => {
      pending = false;
      const shouldReveal = revealRequested;
      revealRequested = false;
      update(shouldReveal);
    });
  }

  window.addEventListener("scroll", () => schedule(), { passive: true });
  window.addEventListener("resize", () => schedule(true));
  window.addEventListener("hashchange", () => schedule(true));
  window.addEventListener("load", () => schedule(true));
  window.addEventListener("pageshow", () => schedule(true));
  desktop.addEventListener("change", () => schedule(true));
  sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a[href^='#']")) schedule(true);
  });
  if (document.fonts) document.fonts.ready.then(() => schedule(true));
  schedule(true);
})();
