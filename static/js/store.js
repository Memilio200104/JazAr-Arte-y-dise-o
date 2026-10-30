(() => {
  const source = document.getElementById('store-products');
  if (!source) return;
  const products = JSON.parse(source.textContent);
  const {normalizeCart, subtotalMinor} = window.JazarCart;
  const key = 'jazar.cart.v1';
  let items = [], memoryOnly = false, timer;
  const money = value => new Intl.NumberFormat('es-MX', {style:'currency',currency:'MXN'}).format(value / 100) + ' MXN';
  const announce = text => {
    const el = document.querySelector('[data-store-feedback]');
    if (!el) return;
    el.textContent = text;
    clearTimeout(timer);
    timer = setTimeout(() => { el.textContent = ''; }, 7000);
  };
  function read() {
    let raw = [];
    try { raw = JSON.parse(localStorage.getItem(key) || '[]'); }
    catch { memoryOnly = true; announce('No pudimos recuperar la selección. Puedes continuar en esta página.'); }
    const result = normalizeCart(raw, products);
    items = result.items;
    if (result.notices.length) announce(result.notices.join(' '));
  }
  function save() {
    if (!memoryOnly) {
      try { localStorage.setItem(key, JSON.stringify(items)); }
      catch { memoryOnly = true; announce('La selección se conservará solo mientras esta página esté abierta.'); }
    }
  }
  function node(tag, text, className) {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (className) el.className = className;
    return el;
  }
  function render() {
    document.querySelectorAll('[data-cart-count]').forEach(el => {
      el.textContent = items.reduce((sum, r) => sum + r.quantity, 0);
      el.hidden = !items.length;
    });
    document.querySelectorAll('[data-subtotal]').forEach(el => { el.textContent = money(subtotalMinor(items, products)); });
    document.querySelectorAll('[data-cart-empty]').forEach(el => { el.hidden = !!items.length; });
    document.querySelectorAll('[data-cart-continue]').forEach(el => { el.hidden = !items.length; el.href = '/pedido/solicitud/'; });
    document.querySelectorAll('[data-cart-items]').forEach(container => {
      container.replaceChildren();
      items.forEach(row => {
        const p = products.find(p => p.id === row.id);
        const article = node('article', '', 'cart-row');
        const img = node('img'); img.src = p.image_url; img.alt = ''; img.width = 100; img.height = 100;
        const content = node('div'), link = node('a', p.name); link.href = p.url;
        const label = node('label','Cantidad'), input = node('input');
        input.type = 'number'; input.min = 1; input.max = p.stock === null ? 99 : Math.min(99,p.stock);
        input.step = 1; input.value = row.quantity; input.inputMode = 'numeric';
        input.setAttribute('aria-label', 'Cantidad de ' + p.name);
        input.addEventListener('change', () => {
          const n = Number(input.value);
          if (!Number.isSafeInteger(n) || n < 1 || n > Number(input.max)) {
            input.value = row.quantity; announce('Elige una cantidad entera entre 1 y ' + input.max + '.'); return;
          }
          row.quantity = n; save();
          const index = items.findIndex(r => r.id === row.id);
          render(); container.querySelectorAll('input')[index]?.focus();
        });
        label.append(input); content.append(link,node('p',money(p.price_minor)),label);
        const remove = node('button', '', 'icon-button');
        remove.setAttribute('aria-label','Quitar ' + p.name); remove.title = 'Quitar pieza';
        const icon = node('i'); icon.dataset.lucide = 'trash-2'; icon.setAttribute('aria-hidden','true'); remove.append(icon);
        remove.addEventListener('click', () => {
          const index = items.findIndex(r => r.id === row.id);
          items = items.filter(r => r.id !== row.id); save(); render();
          const next = container.querySelectorAll('button');
          (next[Math.min(index,next.length-1)] || document.querySelector('[data-cart-empty] a'))?.focus();
          announce('Pieza retirada de tu selección.');
        });
        article.append(img,content,remove); container.append(article);
      });
    });
    window.lucide?.createIcons();
  }
  read();
  if (!document.querySelector('meta[name="jazar-order-page"]')) save();
  render();
  document.querySelectorAll('[data-add-product]').forEach(button => button.addEventListener('click', () => {
    const quantity = Number(document.getElementById('product-quantity').value);
    if (!Number.isSafeInteger(quantity) || quantity < 1 || quantity > 99) { announce('Elige una cantidad entre 1 y 99.'); return; }
    const result = normalizeCart([...items,{id:Number(button.dataset.addProduct),quantity}],products);
    items = result.items; save(); render();
    announce(result.notices.length ? result.notices.join(' ') : 'Pieza agregada. Puedes revisar tu selección en el carrito.');
  }));
  window.addEventListener('storage', event => { if (event.key === key || event.key === null) { read(); render(); } });
  document.querySelectorAll('[data-inactive-form]').forEach(form => {
    form.addEventListener('submit', event => { event.preventDefault(); });
    form.addEventListener('keydown', event => { if (event.key === 'Enter') event.preventDefault(); });
  });
  const dialog = document.querySelector('.photo-dialog'), opener = document.querySelector('[data-open-photo]');
  opener?.addEventListener('click', () => dialog.showModal());
  document.querySelector('[data-close-photo]')?.addEventListener('click', () => dialog.close());
  dialog?.addEventListener('close', () => opener.focus());
})();
