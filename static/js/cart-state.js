(function (root) {
  function normalizeCart(raw, products) {
    const notices = [];
    if (!Array.isArray(raw)) return {items: [], notices: ['No pudimos recuperar la selección anterior.']};
    const items = new Map();
    for (const row of raw) {
      const p = products.find(p => p.id === row?.id);
      if (!p || !Number.isSafeInteger(row.quantity) || row.quantity < 1 || p.stock === 0) {
        notices.push('Ajustamos tu selección: una pieza o cantidad ya no está disponible.');
        continue;
      }
      const max = p.stock === null ? 99 : Math.min(99, p.stock);
      const requested = (items.get(p.id) || 0) + row.quantity;
      const quantity = Math.min(max, requested);
      if (quantity < requested) notices.push('Ajustamos la cantidad al límite disponible.');
      items.set(p.id, quantity);
    }
    return {items: [...items].map(([id, quantity]) => ({id, quantity})), notices: [...new Set(notices)]};
  }
  function subtotalMinor(items, products) {
    return normalizeCart(items, products).items.reduce((sum, row) =>
      sum + row.quantity * products.find(p => p.id === row.id).price_minor, 0);
  }
  const api = {normalizeCart, subtotalMinor};
  if (typeof module !== 'undefined') module.exports = api;
  else root.JazarCart = api;
})(typeof window === 'undefined' ? globalThis : window);
