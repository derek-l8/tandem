export type Product = { id: string; name: string; category: string; color: string; price: number; fabric: string; fit: string; styles: string[]; sizes: string[]; stock: number; image: string; gender: string };
const item = (id:string,name:string,category:string,color:string,price:number,fabric:string,fit:string,styles:string[],image:string,stock=12):Product => ({id,name,category,color,price,fabric,fit,styles,sizes:['S','M','L','XL'],stock,image:`/images/${image}.jpg`,gender:'Menswear'});
export const catalog:Product[] = [
 item('p01','Cloud cotton hoodie','Hoodies','Heather grey',68,'85% cotton, 15% polyester','Relaxed',['Casual','Athletic','Loungewear'],'hoodie'),
 item('p02','Everyday lounge jogger','Pants','Taupe',58,'88% polyester, 12% elastane','Relaxed',['Casual','Athletic','Loungewear'],'jogger'),
 item('p03','Essential cotton tee','T-shirts','White',32,'100% cotton','Regular',['Casual','Loungewear'],'white-tee'),
 item('p04','Soft-touch crewneck','Sweatshirts','White',62,'80% cotton, 20% polyester','Loose',['Casual','Loungewear'],'crewneck'),
 item('p05','Sunday lounge short','Shorts','Oat',44,'95% cotton, 5% elastane','Loose',['Casual','Athletic','Loungewear'],'shorts'),
 item('p06','Graphic cotton tee','T-shirts','Black',38,'100% cotton','Loose',['Streetwear','Casual'],'black-tee'),
 item('p07','Relaxed cotton trouser','Pants','Olive',56,'100% cotton','Relaxed',['Casual','Loungewear'],'trouser'),
 item('p08','Zip-through lounge jacket','Hoodies','Taupe',72,'65% cotton, 35% polyester','Relaxed',['Casual','Athletic','Loungewear'],'zip-hoodie'),
 item('p09','Patterned crew socks','Accessories','Cream & red',16,'80% cotton, 18% polyester, 2% elastane','Regular',['Streetwear','Casual'],'socks'),
 item('p10','Cotton lounge tee','T-shirts','Light grey',36,'100% cotton','Relaxed',['Casual','Athletic','Loungewear'],'slate-tee'),
 item('p11','Track pant','Pants','Heather grey',64,'90% polyester, 10% elastane','Regular',['Athletic'],'athletic'),
 item('p12','Everyday lounge short','Shorts','Oat',42,'95% cotton, 5% elastane','Regular',['Casual','Athletic','Loungewear'],'shorts'),
 item('p13','Classic straight jean','Pants','Indigo',78,'100% cotton','Regular',['Streetwear','Casual'],'jeans'),
 item('p14','Classic dress shirt','Shirts','White',74,'100% cotton','Regular',['Business casual','Formal'],'shirt'),
 item('p15','Tailored check blazer','Jackets','Navy check',148,'55% wool, 45% polyester','Regular',['Formal','Business casual'],'blazer',6),
 item('p16','Denim jacket','Jackets','Indigo',88,'100% cotton','Loose',['Streetwear','Casual'],'overshirt',8),
];
export const styles = [
 {name:'Casual',desc:'Easy, everyday staples',image:'look-grey'},
 {name:'Athletic',desc:'Comfort that moves with you',image:'athletic'},
 {name:'Streetwear',desc:'Bolder shapes. A little edge.',image:'street'},
 {name:'Coastal',desc:'Light layers, slower days',image:'look-shorts'},
 {name:'Business casual',desc:'A little more put-together',image:'casual'},
 {name:'Formal',desc:'For the occasion',image:'formal'},
];
export const looks = [
 {id:'l1',name:'The soft set',desc:'Tonal layers · relaxed fit',image:'look-soft',tags:['Minimal','Relaxed','Cotton']},
 {id:'l2',name:'Off-duty essentials',desc:'Clean basics · easy movement',image:'look-grey',tags:['Minimal','Relaxed','Breathable']},
 {id:'l3',name:'A lighter day',desc:'Easy shorts · neutral palette',image:'look-shorts',tags:['Minimal','Loose','Lightweight']},
 {id:'l4',name:'Street rotation',desc:'Structured layers · darker tones',image:'street',tags:['Expressive','Loose','Layered']},
 {id:'l5',name:'Ready to move',desc:'Sporty basics · tapered fit',image:'athletic',tags:['Sporty','Regular','Tapered']},
 {id:'l6',name:'Everyday layers',desc:'Classic shapes · casual texture',image:'trouser',tags:['Classic','Regular','Layered']},
];
export type Profile = {styles:string[];looks:string[];location:string;occasions:string;budget:number;topSize:string;bottomSize:string;fit:string};
export const defaultProfile:Profile={styles:[],looks:[],location:'Los Angeles',occasions:'Working from home, coffee runs, and relaxed weekends',budget:200,topSize:'M',bottomSize:'M',fit:'Relaxed'};
export type Rules = {maxItems:number;maxDiscount:number};
export type Bundle = {id:string;name:string;subtitle:string;items:string[];total:number;base:number;scores:{price:number;fit:number;style:number;match:number};reason:string;tradeoff:string;issue:'none'|'value'|'size'|'style'|'budget';sizeOverride?:string};
const combinations=[
 {name:'The everyday reset',subtitle:'Best overall match',items:['p01','p02','p03'],issue:'none',reason:'Soft layers, a quiet palette, and your requested sizes. Three everyday pieces that balance comfort and price.',tradeoff:'The hoodie is a warmer layer. Wear the cotton tee on its own on hot afternoons.'},
 {name:'A lighter kind of lounge',subtitle:'The lower-price option',items:['p04','p05','p03'],issue:'value',reason:'A light crewneck, easy shorts, and a cotton tee at a lower total. An understated option with less coverage.',tradeoff:'Shorts replace full-length joggers. Comfortable for warmer days, less useful for cool evenings.'},
 {name:'Room to spare',subtitle:'A fit compromise',items:['p08','p07','p03'],issue:'size',reason:'The palette and styling fit your selected looks, but the trousers in this offer run a size larger than requested.',tradeoff:'Trousers are offered one size up. This is an oversized alternative, not an exact size match.'},
 {name:'The throwback track set',subtitle:'A different direction',items:['p04','p11','p10'],issue:'style',reason:'The pieces fit your requested sizes and stay within budget. The tapered technical track pant leans toward a retro athletic look.',tradeoff:'Sportier and more trend-specific than the quiet, relaxed loungewear in your selected looks.'},
 {name:'The full lounge rotation',subtitle:'More pieces, higher total',items:['p08','p04','p02','p03'],issue:'budget',reason:'Four versatile pieces in your preferred palette and sizes, including two different layers.',tradeoff:'The total exceeds the default $200 budget. The extra layer also adds warmth you may not need in Los Angeles.'},
];
export function makeBundles(profile:Profile,rules:Rules):Bundle[]{
 return combinations.map((c,i)=>{
  const items=c.items.slice(0,rules.maxItems);
  const base=items.reduce((sum,id)=>sum+catalog.find(p=>p.id===id)!.price,0);
  const desired=[149,129,159,146,219][i];
  const total=Math.max(Math.ceil(base*(1-rules.maxDiscount/100)),Math.min(base,desired));
  const price=total<=profile.budget?Math.min(99,Math.round(90+(profile.budget-total)/10)):Math.max(25,Math.round(60-(total-profile.budget)*.8));
  const fit=[97,96,58,91,96][i]-(profile.fit==='Relaxed'?0:5);
  const style=[98,88,94,60,96][i];
  const sizeOverride=i===2?({'S':'M','M':'L','L':'XL','XL':'L'}[profile.bottomSize]||'L'):undefined;
  const itemNames=items.map(id=>catalog.find(p=>p.id===id)!.name.toLowerCase());
  const summary=`${items.length} pieces: ${itemNames.join(', ')}.`;
  const reason=[
   `${summary} Soft layers and a quiet palette, in your requested sizes.`,
   `${summary} A lower-price option that favors lighter coverage.`,
   `${summary} Your style direction, with a compromise on trouser sizing.`,
   `${summary} Your requested sizes, with a more retro athletic direction.`,
   `${summary} A fuller rotation of neutral, easy-to-wear layers.`,
  ][i];
  const tradeoff=[
   'The hoodie is a warmer layer. Best for cool mornings or indoor lounging.',
   'Lounge shorts replace full-length joggers, so there is less coverage on cool evenings.',
   `Trousers are offered in ${sizeOverride}, rather than your requested ${profile.bottomSize}. Check the fit before choosing.`,
   'The tapered technical track pant is sportier and more trend-specific than your selected lounge looks.',
   `${total>profile.budget?`${moneyLabel(total-profile.budget)} above your ${moneyLabel(profile.budget)} budget. `:'Within your budget. '}An extra top layer adds warmth and overlaps with pieces you may already own.`,
  ][i];
  return {...c,reason,tradeoff,issue:c.issue as Bundle['issue'],sizeOverride,id:`bundle-${i+1}`,items,total,base,scores:{price,fit,style,match:Math.round(price*.3+fit*.35+style*.35)}};
 }).sort((a,b)=>b.scores.match-a.scores.match);
}
function moneyLabel(n:number){return `$${n}`;}
