import { mkdir, writeFile, copyFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const frontend = fileURLToPath(new URL('../', import.meta.url));
// Explicit per-size demo counts. These are seed values, not live retailer stock.
const apparelStock = { S: 3, M: 3, L: 3, XL: 3 };
const seeds = [
  ['p01','HDY-01-GR','Cloud cotton hoodie','hoodie','Heather grey','85% cotton, 15% polyester',68,'Relaxed',['Casual','Athletic','Loungewear'],'hoodie','top',apparelStock,'Hoodies'],
  ['p02','PNT-01-TP','Everyday lounge jogger','pants','Taupe','88% polyester, 12% elastane',58,'Relaxed',['Casual','Athletic','Loungewear'],'jogger','bottom',apparelStock,'Pants'],
  ['p03','TEE-01-WH','Essential cotton tee','tee','White','100% cotton',32,'Regular',['Casual','Loungewear'],'white-tee','top',apparelStock,'T-shirts'],
  ['p04','SWE-01-WH','Soft-touch crewneck','sweatshirt','White','80% cotton, 20% polyester',62,'Loose',['Casual','Loungewear'],'crewneck','top',apparelStock,'Sweatshirts'],
  ['p05','SRT-01-OT','Sunday lounge short','shorts','Oat','95% cotton, 5% elastane',44,'Loose',['Casual','Athletic','Loungewear'],'shorts','bottom',apparelStock,'Shorts'],
  ['p06','TEE-02-BK','Graphic cotton tee','tee','Black','100% cotton',38,'Loose',['Streetwear','Casual'],'black-tee','top',apparelStock,'T-shirts'],
  ['p07','PNT-02-OL','Relaxed cotton trouser','pants','Olive','100% cotton',56,'Relaxed',['Casual','Loungewear'],'trouser','bottom',apparelStock,'Pants'],
  ['p08','HDY-02-TP','Zip-through lounge jacket','hoodie','Taupe','65% cotton, 35% polyester',72,'Relaxed',['Casual','Athletic','Loungewear'],'zip-hoodie','top',apparelStock,'Hoodies'],
  ['p09','SOC-01-CR','Patterned crew socks','socks','Cream & red','80% cotton, 18% polyester, 2% elastane',16,'Regular',['Streetwear','Casual'],'socks','accessory',{ OS: 12 },'Accessories'],
  ['p10','TEE-03-GR','Cotton lounge tee','tee','Light grey','100% cotton',36,'Relaxed',['Casual','Athletic','Loungewear'],'slate-tee','top',apparelStock,'T-shirts'],
  ['p11','PNT-03-GR','Track pant','pants','Heather grey','90% polyester, 10% elastane',64,'Regular',['Athletic'],'athletic','bottom',apparelStock,'Pants'],
  ['p12','SRT-02-OT','Everyday lounge short','shorts','Oat','95% cotton, 5% elastane',42,'Regular',['Casual','Athletic','Loungewear'],'shorts','bottom',apparelStock,'Shorts'],
  ['p13','JNS-01-IN','Classic straight jean','jeans','Indigo','100% cotton',78,'Regular',['Streetwear','Casual'],'jeans','bottom',apparelStock,'Pants'],
  ['p14','SHT-01-WH','Classic dress shirt','shirt','White','100% cotton',74,'Regular',['Business casual','Formal'],'shirt','top',apparelStock,'Shirts'],
  ['p15','JKT-01-NV','Tailored check blazer','jacket','Navy check','55% wool, 45% polyester',148,'Regular',['Formal','Business casual'],'blazer','top',{ S: 1, M: 2, L: 2, XL: 1 },'Jackets'],
  ['p16','JKT-02-IN','Denim jacket','jacket','Indigo','100% cotton',88,'Loose',['Streetwear','Casual'],'overshirt','top',{ S: 2, M: 2, L: 2, XL: 2 },'Jackets'],
];

const inventory = [];
const metadata = {};
for (const [id, prefix, name, category, color, material, price, fit, styles, asset, group, sizeStock, displayCategory] of seeds) {
  const skus = [];
  for (const [size, stock] of Object.entries(sizeStock)) {
    const sku = `${prefix}-${size}`;
    const image = `${sku}.jpg`;
    inventory.push({ sku, name, category, color, material, size, price, stock, image });
    skus.push(sku);
    await copyFile(path.join(frontend,'public/images',`${asset}.jpg`), path.join(frontend,'public/images',image));
  }
  metadata[id] = { skus, fit, styles, gender: 'Menswear', group, displayCategory, sourceAsset: `${asset}.jpg` };
}
await mkdir(path.join(frontend,'src/data'), { recursive: true });
await writeFile(path.join(frontend,'src/data/inventory.json'), JSON.stringify(inventory,null,2)+'\n');
await writeFile(path.join(frontend,'src/data/product-meta.json'), JSON.stringify(metadata,null,2)+'\n');

console.log(`Generated ${inventory.length} SKU records across ${seeds.length} products.`);

