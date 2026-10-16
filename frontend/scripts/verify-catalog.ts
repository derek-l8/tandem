import assert from 'node:assert/strict';
import {catalog, defaultProfile, makeBundles} from '../src/catalog.ts';

const sizes = ['S', 'M', 'L', 'XL'];
const products = new Map(catalog.map(product => [product.id, product]));
assert.equal(products.size, catalog.length, 'Catalog IDs must be unique');

let cases = 0;
let checkedBundles = 0;

for (const maxItems of [2, 3, 4]) {
 for (const maxDiscount of [0, 5, 15, 30]) {
  for (const topSize of sizes) {
   for (const bottomSize of sizes) {
    for (const budget of [100, 200, 300]) {
     const profile = {...defaultProfile, styles:['Casual', 'Athletic'], looks:['l1', 'l2', 'l3'], topSize, bottomSize, budget};
     const rules = {maxItems, maxDiscount};
     const context = JSON.stringify({rules, topSize, bottomSize, budget});
     const bundles = makeBundles(profile, rules);

     assert.equal(bundles.length, 5, `${context}: five offers required`);
     assert.equal(new Set(bundles.map(bundle => bundle.id)).size, 5, `${context}: unique bundle IDs required`);
     assert.equal(new Set(bundles.map(bundle => [...bundle.items].sort().join('|'))).size, 5, `${context}: five distinct product combinations required`);

     bundles.forEach((bundle, index) => {
      const label = `${context} / ${bundle.id}`;
      assert.ok(bundle.items.length >= 2 && bundle.items.length <= maxItems, `${label}: item count must obey seller rule`);
      assert.equal(new Set(bundle.items).size, bundle.items.length, `${label}: no repeated product within an offer`);

      let sum = 0;
      let mismatchShown = false;
      for (const id of bundle.items) {
       const product = products.get(id);
       assert.ok(product, `${label}: product ${id} must exist`);
       assert.ok(product.stock > 0, `${label}: ${id} must be in stock`);
       sum += product.price;

       const bottom = ['Pants', 'Shorts'].includes(product.category);
       const offeredSize = bottom && bundle.issue === 'size' ? bundle.sizeOverride : bottom ? bottomSize : topSize;
       if (product.category !== 'Accessories') {
        assert.ok(offeredSize && product.sizes.includes(offeredSize), `${label}: ${id} must stock offered size ${offeredSize}`);
       }
       if (bottom && bundle.issue === 'size') {
        mismatchShown = true;
        assert.notEqual(offeredSize, bottomSize, `${label}: fit compromise must differ from requested size`);
       }
      }

      assert.equal(bundle.base, sum, `${label}: base total must equal product prices`);
      assert.ok(Number.isInteger(bundle.total) && bundle.total > 0, `${label}: offered total must be positive integer dollars`);
      assert.ok(bundle.total <= bundle.base, `${label}: offered total cannot exceed base total`);
      assert.ok((bundle.base - bundle.total) * 100 <= bundle.base * maxDiscount + 1e-8, `${label}: actual discount must not exceed seller rule`);
      if (bundle.issue === 'size') assert.ok(mismatchShown, `${label}: size compromise requires an actual affected bottom`);

      for (const [name, value] of Object.entries(bundle.scores)) {
       assert.ok(Number.isFinite(value) && value >= 0 && value <= 100, `${label}: ${name} score must be within 0–100`);
      }
      if (index > 0) assert.ok(bundles[index - 1].scores.match >= bundle.scores.match, `${label}: offers must sort by descending holistic match`);

      assert.ok(bundle.reason.startsWith(`${bundle.items.length} pieces:`), `${label}: explanation must show actual item count`);
      for (const id of bundle.items) assert.ok(bundle.reason.includes(products.get(id)!.name.toLowerCase()), `${label}: explanation must name included product ${id}`);
      if (bundle.id === 'bundle-5') {
       assert.equal(bundle.tradeoff.includes('above your'), bundle.total > budget, `${label}: budget tradeoff must follow actual total`);
      }
      checkedBundles++;
     });
     cases++;
    }
   }
  }
 }
}

const defaults = makeBundles({...defaultProfile, styles:['Casual', 'Athletic'], looks:['l1', 'l2', 'l3']}, {maxItems:4, maxDiscount:15});
assert.ok(defaults[0].total >= 140 && defaults[0].total <= 160, 'Recommended default bundle must be around $150');
assert.equal(defaults[0].issue, 'none', 'Recommended default bundle must avoid sizing/style compromises');

console.log(`Catalog checks passed: ${cases} profiles/rule combinations, ${checkedBundles} offers.`);
console.log(`Default ranked bundle prices: ${defaults.map(bundle => `$${bundle.total}`).join(', ')}.`);
