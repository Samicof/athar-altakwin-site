(() => {
  const story = document.querySelector('.story');
  const chapters = [...document.querySelectorAll('.chapter')];
  const links = [...document.querySelectorAll('[data-chapter]')];
  if (!story || !chapters.length) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let scheduled = false;

  function update() {
    scheduled = false;
    const viewport = window.innerHeight;
    const focusLine = Math.min(viewport * 0.42, 340);
    let active = chapters[0];
    let closest = Infinity;
    for (const chapter of chapters) {
      const bounds = chapter.getBoundingClientRect();
      const distance = Math.abs(bounds.top + Math.min(bounds.height / 2, 230) - focusLine);
      if (distance < closest) {
        closest = distance;
        active = chapter;
      }
      // Only the decorative background word moves. Text and layout remain static.
      const offset = reduced.matches ? 0 : Math.max(-14, Math.min(14, (bounds.top - viewport / 2) * 0.035));
      chapter.style.setProperty('--offset', `${offset.toFixed(1)}px`);
    }
    for (const link of links) {
      if (link.dataset.chapter === active.id) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    }
    const first = chapters[0].getBoundingClientRect();
    const last = chapters[chapters.length - 1].getBoundingClientRect();
    const progress = Math.max(0, Math.min(1, (focusLine - first.top) / Math.max(1, last.bottom - first.top - viewport * 0.3)));
    story.style.setProperty('--progress', progress.toFixed(4));
  }
  function schedule() {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(update);
    }
  }
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule);
  reduced.addEventListener('change', schedule);
  update();
})();
