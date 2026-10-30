(() => {
  const indicator = document.querySelector('[data-page-loading]');
  if (!indicator) return;
  const message = indicator.querySelector('[data-loading-message]');
  let reveal, timeout, dismiss;
  const stop = () => {
    clearTimeout(reveal); clearTimeout(timeout); clearTimeout(dismiss);
    indicator.hidden = true;
    message.textContent = '';
  };
  const start = (label = 'Cargando página…') => {
    stop();
    reveal = setTimeout(() => { indicator.hidden = false; message.textContent = label; }, 220);
    // A cancelled navigation or stalled resource must never leave a permanent loader.
    timeout = setTimeout(() => {
      message.textContent = 'Está tardando más de lo habitual…';
      dismiss = setTimeout(stop, 8000);
    }, 12000);
  };
  if (document.readyState !== 'complete') start();
  window.addEventListener('load', stop, { once: true });
  window.addEventListener('pageshow', stop);
  window.addEventListener('pagehide', stop);
  window.addEventListener('keydown', event => { if (event.key === 'Escape') stop(); });
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey ||
        link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || !['http:', 'https:'].includes(url.protocol) ||
        (url.pathname === location.pathname && url.search === location.search)) return;
    queueMicrotask(() => { if (!event.defaultPrevented) start(); });
  });
  document.addEventListener('submit', event => {
    const form = event.target;
    if (form.method === 'dialog' || (form.target && form.target !== '_self')) return;
    queueMicrotask(() => {
      if (!event.defaultPrevented) start(form.dataset.loadingMessage || 'Enviando información…');
    });
  });
})();
