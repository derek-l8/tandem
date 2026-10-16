# TANDEM image credits

The clothing and outfit photographs are illustrative assets for this frontend demo, sourced from Unsplash and retailer image servers. The catalog names, fabric/fit tags, stock, prices, discounts, and bundle recommendations are fictional demo data; they do not represent the photographed retailers' current inventory or offers.

Source URLs are also recorded in `scripts/image-sources.json`. The table lists the original downloaded files in `public/images`, including unused alternatives. SKU aliases below contain the same image bytes as their corresponding originals.

| Local assets | Image source |
| --- | --- |
| `look-shorts.jpg`, `shorts.jpg` | [ICIW](https://iciw.centracdn.net/client/dynamic/images/13144_58158d5a91-13777-325-2-full.jpg) |
| `look-grey.jpg`, `jogger.jpg` | [Quince](https://images.quince.com/3TrsGVlv7iMhj2hB0oDo0J/284063171a5dc821e66e246c329cc04b/M-PNT-13-HMRGRY-06_EDITED.jpg?w=700&q=80) |
| `trouser.jpg` | [Unsplash](https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=700&q=85&fit=crop) |
| `white-tee.jpg` | [Unsplash](https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=700&q=85&fit=crop) |
| `street.jpg` | [Unsplash](https://images.unsplash.com/photo-1523398002811-999ca8dec234?w=700&q=85&fit=crop) |
| `jeans.jpg` | [Unsplash](https://images.unsplash.com/photo-1542272604-787c3835535d?w=700&q=85&fit=crop) |
| `overshirt.jpg` | [Unsplash](https://images.unsplash.com/photo-1543076447-215ad9ba6923?w=700&q=85&fit=crop) |
| `track.jpg` | [Unsplash](https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=700&q=85&fit=crop) |
| `hoodie.jpg` | [Unsplash](https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=700&q=85&fit=crop) |
| `socks.jpg` | [Unsplash](https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=700&q=85&fit=crop) |
| `running-short.jpg` | [Unsplash](https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=700&q=85&fit=crop) |
| `formal.jpg`, `blazer.jpg` | [Unsplash](https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=700&q=85&fit=crop) |
| `coastal.jpg`, `shirt.jpg` | [Unsplash](https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=700&q=85&fit=crop) |
| `casual.jpg` | [Unsplash](https://images.unsplash.com/photo-1617137968427-85924c800a22?w=700&q=85&fit=crop) |
| `business.jpg` | [Unsplash](https://images.unsplash.com/photo-1618354691229-88d47f285158?w=700&q=85&fit=crop) |
| `black-tee.jpg` | [Unsplash](https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=700&q=85&fit=crop) |
| `crewneck.jpg` | [Unsplash](https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=700&q=85&fit=crop) |
| `look-soft.jpg` | [Abercrombie & Fitch](https://img.abercrombie.com/is/image/anf/KIC_118-4921-0056-176_model1?policy=product-medium) |
| `zip-hoodie.jpg` | [Retailer image CDN](https://static.ticimax.cloud/5334/uploads/urunresimleri/buyuk/bej-fermuarli-comfort-fit-erkek-esofma--8fc6d.jpeg) |
| `athletic.jpg`, `slate-tee.jpg` | [Gap Factory](https://www.gapfactory.com/webcontent/0057/321/337/cn57321337.jpg) |


## SKU image aliases

Each apparel size has its own SKU filename; socks use `OS`. These aliases reuse the credited source photograph rather than depicting different sizes. Per-size stock counts are explicitly seeded demo data in `src/data/inventory.json`. Fit/style grouping is separate in `src/data/product-meta.json`.

| Product group | SKU filenames | Credited original |
| --- | --- | --- |
| `p01` | `HDY-01-GR-S.jpg`, `HDY-01-GR-M.jpg`, `HDY-01-GR-L.jpg`, `HDY-01-GR-XL.jpg` | `hoodie.jpg` |
| `p02` | `PNT-01-TP-S.jpg`, `PNT-01-TP-M.jpg`, `PNT-01-TP-L.jpg`, `PNT-01-TP-XL.jpg` | `jogger.jpg` |
| `p03` | `TEE-01-WH-S.jpg`, `TEE-01-WH-M.jpg`, `TEE-01-WH-L.jpg`, `TEE-01-WH-XL.jpg` | `white-tee.jpg` |
| `p04` | `SWE-01-WH-S.jpg`, `SWE-01-WH-M.jpg`, `SWE-01-WH-L.jpg`, `SWE-01-WH-XL.jpg` | `crewneck.jpg` |
| `p05` | `SRT-01-OT-S.jpg`, `SRT-01-OT-M.jpg`, `SRT-01-OT-L.jpg`, `SRT-01-OT-XL.jpg` | `shorts.jpg` |
| `p06` | `TEE-02-BK-S.jpg`, `TEE-02-BK-M.jpg`, `TEE-02-BK-L.jpg`, `TEE-02-BK-XL.jpg` | `black-tee.jpg` |
| `p07` | `PNT-02-OL-S.jpg`, `PNT-02-OL-M.jpg`, `PNT-02-OL-L.jpg`, `PNT-02-OL-XL.jpg` | `trouser.jpg` |
| `p08` | `HDY-02-TP-S.jpg`, `HDY-02-TP-M.jpg`, `HDY-02-TP-L.jpg`, `HDY-02-TP-XL.jpg` | `zip-hoodie.jpg` |
| `p09` | `SOC-01-CR-OS.jpg` | `socks.jpg` |
| `p10` | `TEE-03-GR-S.jpg`, `TEE-03-GR-M.jpg`, `TEE-03-GR-L.jpg`, `TEE-03-GR-XL.jpg` | `slate-tee.jpg` |
| `p11` | `PNT-03-GR-S.jpg`, `PNT-03-GR-M.jpg`, `PNT-03-GR-L.jpg`, `PNT-03-GR-XL.jpg` | `athletic.jpg` |
| `p12` | `SRT-02-OT-S.jpg`, `SRT-02-OT-M.jpg`, `SRT-02-OT-L.jpg`, `SRT-02-OT-XL.jpg` | `shorts.jpg` |
| `p13` | `JNS-01-IN-S.jpg`, `JNS-01-IN-M.jpg`, `JNS-01-IN-L.jpg`, `JNS-01-IN-XL.jpg` | `jeans.jpg` |
| `p14` | `SHT-01-WH-S.jpg`, `SHT-01-WH-M.jpg`, `SHT-01-WH-L.jpg`, `SHT-01-WH-XL.jpg` | `shirt.jpg` |
| `p15` | `JKT-01-NV-S.jpg`, `JKT-01-NV-M.jpg`, `JKT-01-NV-L.jpg`, `JKT-01-NV-XL.jpg` | `blazer.jpg` |
| `p16` | `JKT-02-IN-S.jpg`, `JKT-02-IN-M.jpg`, `JKT-02-IN-L.jpg`, `JKT-02-IN-XL.jpg` | `overshirt.jpg` |

