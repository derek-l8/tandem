# Brojans JSON formats

Every message between the buyer agent, the middle man and the seller agent is JSON.
The agents never talk directly: every message passes through the middle man, which
parses it, validates it, stores it and forwards it to the next stage.

**Negotiation: single round, 5 bundles**

```
1. inventory          (seller's catalog)
2. context            buyer  -> seller
3. bundles (5)        seller -> buyer
4. check              middle man
5. ratings            buyer  -> seller
6. analysis           seller (what works / what doesn't)
7. final bundle       seller -> buyer
8. check              middle man
9. decision           buyer  -> seller
```

Stage pattern: `JSON in -> [prompt + JSON] -> Claude -> JSON out -> middle man parses + validates -> next stage`.
If validation fails, the middle man re-prompts the same agent once with the errors.

---

## 1. Inventory item (product)

One JSON per SKU. Each size is its own SKU. Products have no images, only an image *file name*.

```json
{
  "sku": "JKT-01-BR-M",
  "name": "Canvas Jacket",
  "category": "jacket",
  "color": "brown",
  "material": "cotton canvas",
  "size": "M",
  "price": 89,
  "stock": 8,
  "image": "JKT-01-BR-M.jpg"
}
```

| Field | Type | Notes |
|---|---|---|
| `sku` | string | Unique id. Format `CAT-NN-COLOR-SIZE` |
| `name` | string | Display name |
| `category` | string | Product type (jacket, tee, pants, jeans, boots, ...) |
| `color` | string | Main color |
| `material` | string | Main material |
| `size` | string | Single size for this SKU (`M`, `32`, `10`, `OS`) |
| `price` | number | Dollars |
| `stock` | int | Units available. `0` = out of stock, never offered |
| `image` | string | Image file name, always passed along with the item |

Example inventory used in the examples below:

```json
[
  { "sku": "JKT-01-BR-M",  "name": "Canvas Jacket",     "category": "jacket",   "color": "brown",     "material": "cotton canvas",  "size": "M",  "price": 89,  "stock": 8,  "image": "JKT-01-BR-M.jpg" },
  { "sku": "JKT-02-OL-M",  "name": "Chore Jacket",      "category": "jacket",   "color": "olive",     "material": "cotton twill",   "size": "M",  "price": 110, "stock": 5,  "image": "JKT-02-OL-M.jpg" },
  { "sku": "JKT-03-NV-M",  "name": "Nylon Bomber",      "category": "jacket",   "color": "navy",      "material": "nylon",          "size": "M",  "price": 95,  "stock": 6,  "image": "JKT-03-NV-M.jpg" },
  { "sku": "TEE-01-OL-M",  "name": "Heavyweight Tee",   "category": "tee",      "color": "olive",     "material": "cotton",         "size": "M",  "price": 35,  "stock": 20, "image": "TEE-01-OL-M.jpg" },
  { "sku": "TEE-02-WH-M",  "name": "Boxy Tee",          "category": "tee",      "color": "white",     "material": "cotton",         "size": "M",  "price": 30,  "stock": 15, "image": "TEE-02-WH-M.jpg" },
  { "sku": "SHT-01-BL-M",  "name": "Oxford Shirt",      "category": "shirt",    "color": "pale blue", "material": "cotton oxford",  "size": "M",  "price": 68,  "stock": 10, "image": "SHT-01-BL-M.jpg" },
  { "sku": "PNT-01-OL-32", "name": "Ripstop Cargo",     "category": "pants",    "color": "olive",     "material": "cotton ripstop", "size": "32", "price": 75,  "stock": 9,  "image": "PNT-01-OL-32.jpg" },
  { "sku": "JNS-01-IN-32", "name": "Straight Jean",     "category": "jeans",    "color": "indigo",    "material": "denim",          "size": "32", "price": 95,  "stock": 7,  "image": "JNS-01-IN-32.jpg" },
  { "sku": "TRS-01-GR-32", "name": "Pleated Trouser",   "category": "trousers", "color": "grey",      "material": "wool blend",     "size": "32", "price": 98,  "stock": 4,  "image": "TRS-01-GR-32.jpg" },
  { "sku": "BOT-01-BR-10", "name": "Leather Work Boot", "category": "boots",    "color": "brown",     "material": "leather",        "size": "10", "price": 160, "stock": 3,  "image": "BOT-01-BR-10.jpg" },
  { "sku": "SNK-01-WH-10", "name": "Leather Sneaker",   "category": "sneakers", "color": "white",     "material": "leather",        "size": "10", "price": 120, "stock": 6,  "image": "SNK-01-WH-10.jpg" },
  { "sku": "LOF-01-BK-10", "name": "Penny Loafer",      "category": "loafers",  "color": "black",     "material": "leather",        "size": "10", "price": 150, "stock": 2,  "image": "LOF-01-BK-10.jpg" }
]
```

---

## 2. Context (buyer -> seller)

The buyer agent extracts this from the user's images and chat. The seller never sees the
user's images, only this context.

```json
{
  "style": ["workwear", "minimal"],
  "colors_liked": ["brown", "olive"],
  "colors_avoid": ["neon"],
  "sizes": { "top": "M", "bottom": "32", "shoe": "10" },
  "budget": 400,
  "occasion": "weekend casual",
  "notes": ["no graphic prints", "no skinny fits", "must include a jacket"]
}
```

| Field | Type | Notes |
|---|---|---|
| `style` | string[] | Style keywords |
| `colors_liked` | string[] | Preferred colors |
| `colors_avoid` | string[] | **Hard rule**: never offered |
| `sizes` | object | Size per slot (`top`, `bottom`, `shoe`). Only matching SKUs are offered |
| `budget` | number | Dollars. **Hard rule**: bundle price must be at or under this |
| `occasion` | string | What it's for |
| `notes` | string[] | **Strictly followed.** The user's explicit rules, word for word. Any bundle that breaks a note is rejected |

---

## 3. Bundles (seller -> buyer)

Exactly 5 bundles, each 2-5 items, all different from each other so the ratings are informative.

```json
{
  "bundles": [
    { "id": "b1", "skus": ["JKT-01-BR-M", "TEE-01-OL-M", "PNT-01-OL-32"],                 "images": ["JKT-01-BR-M.jpg", "TEE-01-OL-M.jpg", "PNT-01-OL-32.jpg"],                     "items_total": 199, "price": 179 },
    { "id": "b2", "skus": ["JKT-03-NV-M", "TEE-02-WH-M", "JNS-01-IN-32", "SNK-01-WH-10"], "images": ["JKT-03-NV-M.jpg", "TEE-02-WH-M.jpg", "JNS-01-IN-32.jpg", "SNK-01-WH-10.jpg"], "items_total": 340, "price": 305 },
    { "id": "b3", "skus": ["JKT-02-OL-M", "SHT-01-BL-M", "TRS-01-GR-32", "LOF-01-BK-10"], "images": ["JKT-02-OL-M.jpg", "SHT-01-BL-M.jpg", "TRS-01-GR-32.jpg", "LOF-01-BK-10.jpg"], "items_total": 426, "price": 380 },
    { "id": "b4", "skus": ["JKT-02-OL-M", "TEE-01-OL-M", "PNT-01-OL-32", "SNK-01-WH-10"], "images": ["JKT-02-OL-M.jpg", "TEE-01-OL-M.jpg", "PNT-01-OL-32.jpg", "SNK-01-WH-10.jpg"], "items_total": 340, "price": 309 },
    { "id": "b5", "skus": ["JKT-01-BR-M", "JNS-01-IN-32", "BOT-01-BR-10"],                "images": ["JKT-01-BR-M.jpg", "JNS-01-IN-32.jpg", "BOT-01-BR-10.jpg"],                    "items_total": 344, "price": 315 }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | string | Bundle id |
| `skus` | string[] | Items in the bundle (no repeats) |
| `images` | string[] | Image file names, same order as `skus` |
| `items_total` | number | Sum of item prices. **Computed by code** |
| `price` | number | Bundle price in dollars. Must be 60-105% of `items_total` and at or under `budget` |

The buyer agent receives the full item JSONs for each SKU when rating.

---

## 4. Check (middle man)

Runs after every seller output (bundles and final).

```json
{ "stage": "bundles", "valid": true, "errors": [] }
```

On failure the seller is re-prompted once with the errors:

```json
{
  "stage": "bundles",
  "valid": false,
  "errors": [
    "b2: no jacket (breaks note 'must include a jacket')",
    "b4: SKU PNT-01-OL-30 wrong size (bottom is 32)"
  ]
}
```

Checks: valid JSON/schema, bundle count, SKUs exist, in stock, sizes match `sizes`, no
`colors_avoid`, every `notes` rule, no repeated SKU, price range, budget.

---

## 5. Ratings (buyer -> seller)

```json
{
  "ratings": [
    { "id": "b1", "probability": 0.78, "reason": "Brown jacket + olive tee and cargo: exact palette and workwear style" },
    { "id": "b2", "probability": 0.41, "reason": "Navy bomber and white sneakers feel sporty, not workwear" },
    { "id": "b3", "probability": 0.15, "reason": "Oxford, wool trousers and loafers are too formal for weekend casual" },
    { "id": "b4", "probability": 0.64, "reason": "All-olive works, but white sneakers break the workwear look" },
    { "id": "b5", "probability": 0.72, "reason": "Brown jacket + boots are strong; jeans fine" }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | string | Bundle id being rated |
| `probability` | number 0-1 | Chance the buyer buys this bundle at this price. 0.5 = coin flip. A broken note means 0.1 or lower |
| `reason` | string | Names the specific items that help or hurt |

---

## 6. Analysis (seller: what works / what doesn't)

The seller checks every rating. For each bundle rated **below 0.5**, it inspects each item
(per-item inference), then compares those inferences against the collective attribute
averages. Something is a `confirmed` issue only when both agree.

```json
{
  "avg": 0.54,
  "attribute_avgs": {
    "color":    { "brown": 0.75, "olive": 0.52, "white": 0.53, "navy": 0.41, "pale blue": 0.15, "grey": 0.15, "black": 0.15 },
    "category": { "boots": 0.72, "pants": 0.71, "sneakers": 0.53, "loafers": 0.15, "trousers": 0.15, "shirt": 0.15 }
  },
  "item_checks": [
    { "bundle": "b2", "sku": "JKT-03-NV-M",  "verdict": "hurts", "dimension": "style", "note": "Sporty bomber" },
    { "bundle": "b2", "sku": "SNK-01-WH-10", "verdict": "hurts", "dimension": "style", "note": "Sporty" },
    { "bundle": "b3", "sku": "SHT-01-BL-M",  "verdict": "hurts", "dimension": "style", "note": "Formal" },
    { "bundle": "b3", "sku": "TRS-01-GR-32", "verdict": "hurts", "dimension": "style", "note": "Formal" },
    { "bundle": "b3", "sku": "LOF-01-BK-10", "verdict": "hurts", "dimension": "style", "note": "Formal" }
  ],
  "works": [
    { "type": "color",    "value": "brown", "avg_prob": 0.75 },
    { "type": "category", "value": "boots", "avg_prob": 0.72 },
    { "type": "category", "value": "pants", "avg_prob": 0.71 }
  ],
  "fails": [
    { "type": "style", "value": "formal", "avg_prob": 0.15, "votes": 3, "confirmed": true },
    { "type": "style", "value": "sporty", "avg_prob": 0.41, "votes": 2, "confirmed": true }
  ],
  "keep_skus": ["JKT-01-BR-M", "TEE-01-OL-M", "PNT-01-OL-32", "BOT-01-BR-10"],
  "drop_skus": ["JKT-03-NV-M", "SNK-01-WH-10", "SHT-01-BL-M", "TRS-01-GR-32", "LOF-01-BK-10"],
  "main_issue": "style"
}
```

| Field | Type | Source | Notes |
|---|---|---|---|
| `avg` | number | code | Mean probability across the 5 bundles |
| `attribute_avgs` | object | code | Per attribute value: mean probability of bundles containing it |
| `item_checks[]` | array | Claude | One entry per item in each bundle rated < 0.5 |
| `item_checks[].verdict` | `hurts` \| `neutral` \| `helps` | Claude | |
| `item_checks[].dimension` | `category` \| `style` \| `color` \| `material` \| `size` \| `price` \| `none` | Claude | Why it hurts |
| `works[]` / `fails[]` | array | Claude + code | Attribute values pulling ratings up / down |
| `fails[].votes` | int | code | How many item checks blamed this value |
| `fails[].confirmed` | bool | code | True when the item checks and the averages agree |
| `keep_skus` / `drop_skus` | string[] | Claude | Used to build the final bundle. `drop_skus` are banned from the final |
| `main_issue` | string | Claude | The dimension most responsible for low ratings |

---

## 7. Final bundle (seller -> buyer)

Exactly 1 bundle, built from the analysis (best bundle improved with `keep_skus`, no `drop_skus`).

```json
{
  "final": {
    "id": "final",
    "skus": ["JKT-01-BR-M", "TEE-01-OL-M", "PNT-01-OL-32", "BOT-01-BR-10"],
    "images": ["JKT-01-BR-M.jpg", "TEE-01-OL-M.jpg", "PNT-01-OL-32.jpg", "BOT-01-BR-10.jpg"],
    "items_total": 359,
    "price": 319,
    "savings": 40,
    "why": "Best bundle (b1, 0.78) + boots from b5 (0.72); no formal or sporty pieces"
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `items_total` | number | **Computed by code** |
| `savings` | number | `items_total - price`. **Computed by code** |
| `why` | string | Seller's reasoning, referencing the ratings/analysis |

The middle man runs the same check (section 4) with `"stage": "final"`.

---

## 8. Decision (buyer -> seller)

```json
{ "decision": "accept", "probability": 0.88, "reason": "Follows all notes, matches style and colors, $81 under budget" }
```

| Field | Type | Notes |
|---|---|---|
| `decision` | `accept` \| `reject` | |
| `probability` | number 0-1 | Buy probability for the final bundle |
| `reason` | string | Why |

---

## Rules summary

- Prices are dollars everywhere.
- `notes`, `colors_avoid`, `sizes` and `budget` are hard rules, enforced by the middle man, not just the prompt.
- Only in-stock SKUs (`stock > 0`) are offered.
- Every item reference carries its `image` file name.
- Fields marked "computed by code" are never trusted from Claude's output; the middle man recalculates them.
