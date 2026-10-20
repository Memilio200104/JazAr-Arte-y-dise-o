const assert = require('node:assert/strict');
const {normalizeCart, subtotalMinor} = require('../static/js/cart-state.js');
const products = [{id:1,price_minor:19990,stock:null},{id:2,price_minor:100,stock:0}];
assert.deepEqual(normalizeCart('bad', products).items, []);
assert.deepEqual(normalizeCart([{id:77,quantity:1}], products).items, []);
for (const quantity of [-1,0,1.5,Infinity,'2']) {
  assert.deepEqual(normalizeCart([{id:1,quantity}], products).items, []);
}
assert.deepEqual(normalizeCart([{id:1,quantity:1},{id:1,quantity:1}],products).items,[{id:1,quantity:2}]);
assert.equal(normalizeCart([{id:1,quantity:999}],products).items[0].quantity,99);
assert.equal(normalizeCart([{id:1,quantity:999}],[{...products[0],stock:3}]).items[0].quantity,3);
assert.deepEqual(normalizeCart([{id:2,quantity:1}],products).items,[]);
assert.equal(subtotalMinor([{id:1,quantity:2,price_minor:1}],products),39980);
for (const stock of [3, null]) {
  const limit = stock === null ? 99 : stock;
  const result = normalizeCart([{id:1,quantity:limit},{id:1,quantity:1}], [{...products[0],stock}]);
  assert.equal(result.items[0].quantity,limit);
  assert.ok(result.notices.length, 'Repeated add at limit must explain unchanged quantity');
}
console.log('Cart state: PASS');
