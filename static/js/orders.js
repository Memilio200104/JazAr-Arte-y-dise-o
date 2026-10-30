(() => {
  const key = 'jazar.cart.v1';
  const form = document.querySelector('[data-order-request]');
  const el = (tag, text) => { const node = document.createElement(tag); if (text) node.textContent = text; return node; };
  if (form) {
    const input = form.querySelector('[name=rows]'), button = form.querySelector('[data-order-preview]');
    try {
      const products = JSON.parse(document.getElementById('store-products').textContent);
      const rows = input.value ? JSON.parse(input.value) : JSON.parse(localStorage.getItem(key) || '[]').map(r => ({...r, details:''}));
      if (!Array.isArray(rows) || !rows.length || rows.length > 100) throw new Error('selection');
      const container = form.querySelector('[data-order-lines]');
      rows.forEach((row, index) => {
        const product = products.find(p => p.id === row.id);
        const section = el('div'); section.className = 'order-line';
        section.append(el('h3', product?.name || 'Pieza no disponible'), el('p', `Cantidad: ${row.quantity}`));
        const label = el('label', 'Talla, color y detalles (opcional)'), details = el('textarea');
        details.id = `order-details-${index}`; label.htmlFor = details.id;
        details.name = `details-${index}`; details.maxLength = 300; details.rows = 2; details.autocomplete = 'off'; details.value = row.details || '';
        details.addEventListener('input', () => { row.details = details.value; input.value = JSON.stringify(rows); });
        section.append(label, details); container.append(section);
      });
      input.value = JSON.stringify(rows); button.disabled = false;
    } catch {
      document.querySelector('[data-order-selection-status]').textContent = 'No pudimos recuperar tu selección. Vuelve al carrito para revisarla.';
    }
  }
  const submitted = document.getElementById('submitted-order-cart');
  if (submitted) {
    const message = document.querySelector('[data-order-cleanup]');
    try {
      const current = JSON.parse(localStorage.getItem(key) || '[]'), sent = JSON.parse(submitted.textContent);
      const canonical = rows => JSON.stringify(rows.map(r => [r.id, r.quantity]).sort((a,b) => a[0]-b[0]));
      if (Array.isArray(current) && canonical(current) === canonical(sent)) {
        localStorage.removeItem(key);
        window.dispatchEvent(new StorageEvent('storage', {key}));
        message.textContent = 'Solicitud guardada. Tu selección enviada se retiró del carrito.';
      } else message.textContent = 'Solicitud guardada. Conservamos los cambios de tu carrito.';
    } catch { message.textContent = 'Solicitud guardada. No pudimos actualizar el carrito de este navegador.'; }
  }
  document.querySelector('[data-order-error]')?.focus();
})();
