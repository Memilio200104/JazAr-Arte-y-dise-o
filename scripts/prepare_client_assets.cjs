// Exact crops from client-supplied catalog renders; no generated product imagery.
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const root = process.argv[2];
if (!root) throw new Error('Usage: node scripts/prepare_client_assets.cjs <client-folder>');
const out = 'static/images/client';
const crops = [
  ['taza-blanca', 3, 25, 120, 455, 300],
  ['tazas-pareja', 3, 20, 745, 465, 275],
  ['taza-magica', 6, 35, 120, 410, 450],
  ['termo-recto', 10, 75, 115, 210, 465],
  ['playera-blanca', 14, 25, 100, 430, 415],
  ['bolsa-lona', 20, 65, 20, 310, 570],
  ['cuadro-cristal', 24, 20, 160, 450, 400],
  ['libreta', 30, 80, 155, 648, 460],
  ['separador', 30, 135, 802, 516, 404],
];
const photos = [
  ['laser', '11.11.47 AM (1)'], ['corte', '11.11.47 AM (2)'],
  ['impresora-3d', '11.11.47 AM (5)'], ['tazas-taller', '11.11.48 AM (2)'],
  ['diseno', '11.11.48 AM (3)'], ['taller', '11.11.48 AM (4)'],
  ['materiales', '11.11.48 AM (5)'], ['jazmin', '11.11.49 AM (1)'],
];
// Coordinates measured on 315 x 560 review previews, mapped to original renders.
const remaining = [
  ['c03-02',3,179,160,126,120], ['c03-04',3,118,430,193,108],
  ['c04-01',4,17,38,140,124], ['c04-02',4,164,173,130,126],
  ['c04-03',4,5,285,150,144], ['c04-04',4,140,429,138,119],
  ['c05-01',5,36,65,167,214], ['c05-02',5,107,300,196,246],
  ['c06-02',6,107,224,200,125], ['c06-03',6,7,382,202,160],
  ['c08-01',8,20,40,121,145], ['c08-02',8,210,126,78,170],
  ['c08-03',8,21,255,165,169], ['c08-04',8,142,435,157,118],
  ['c10-02',10,214,164,72,212], ['c10-03',10,12,366,162,188],
  ['c11-01',11,140,235,164,166], ['c11-02',11,24,17,105,213],
  ['c11-03',11,55,420,114,132],
  ['c12-01',12,33,42,138,167], ['c12-02',12,173,198,110,221],
  ['c12-03',12,35,379,122,177],
  ['c14-03',14,158,220,142,160], ['c14-05',14,6,340,156,196],
  ['c15-01',15,14,16,139,202], ['c15-03',15,161,232,150,187],
  ['c15-05',15,12,375,144,183],
  ['c16-01',16,12,29,166,193], ['c16-02',16,157,224,158,184],
  ['c16-03',16,12,369,158,184],
  ['c17-01',17,20,51,135,178], ['c17-03',17,173,216,122,173],
  ['c17-05',17,17,380,147,164],
  ['c18-01',18,6,53,159,149], ['c18-02',18,155,213,154,171],
  ['c18-03',18,15,349,145,211],
  ['c19-01',19,52,30,121,202], ['c19-02',19,140,238,168,117],
  ['c19-03',19,14,382,185,143],
  ['c20-02',20,133,201,179,177], ['c20-03',20,14,352,164,196],
  ['c21-01',21,21,60,170,167], ['c21-02',21,137,239,171,132],
  ['c21-03',21,11,411,171,121],
  ['c22-01',22,4,70,188,138], ['c22-02',22,6,357,192,165],
  ['c22-03',22,146,201,156,155],
  ['c24-02',24,143,227,161,151], ['c24-03',24,20,400,172,124],
  ['c25-01',25,23,66,135,166], ['c25-02',25,119,262,180,143],
  ['c25-03',25,0,437,181,88],
  ['c26-01',26,28,52,202,203], ['c26-02',26,123,262,178,272],
  ['c27-01',27,1,45,159,235],
  ['c28-01',28,5,24,163,174], ['c28-03',28,130,175,183,133],
  ['c28-04',28,9,313,130,113], ['c28-05',28,129,441,181,107],
  ['c29-01',29,14,17,174,156], ['c29-02',29,14,289,165,156],
  ['c29-03',29,144,177,170,133], ['c29-04',29,180,414,105,140],
  ['c31-01',31,15,64,166,162], ['c31-02',31,175,236,131,159],
  ['c31-03',31,29,414,141,142],
];
// Embedded originals avoid clipping and neighboring page text on tight layouts.
const originals = {
  'c06-02':'p06-0', 'c06-03':'p06-1', 'taza-magica':'p06-2',
  'c11-01':'p11-0', 'c11-02':'p11-1', 'c11-03':'p11-2',
  'c19-01':'p19-0', 'c19-03':'p19-1', 'c19-02':'p19-2',
  'c20-02':'p20-0', 'bolsa-lona':'p20-1', 'c20-03':'p20-2',
  'c22-01':'p22-0', 'c22-03':'p22-1', 'c22-02':'p22-2',
  'c24-03':'p24-0', 'cuadro-cristal':'p24-1', 'c24-02':'p24-2',
  'c29-03':'p29-0', 'c29-01':'p29-1', 'c29-02':'p29-2', 'c29-04':'p29-3',
  'c31-01':'p31-0', 'c31-02':'p31-1', 'c31-03':'p31-2',
};
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const files = fs.readdirSync(root);
  for (const [name, suffix] of photos) {
    const file = files.find(f => f.endsWith(suffix + '.jpeg'));
    if (!file) throw new Error('Missing photo: ' + suffix);
    await sharp(path.join(root, file)).rotate().resize({width:1600,height:1600,fit:'inside',withoutEnlargement:true})
      .webp({quality:85}).toFile(`${out}/${name}.webp`);
  }
  for (const [name, page, left, top, width, height] of crops) {
    await sharp(`artifacts/catalog-page-${page}.png`).extract({left,top,width,height})
      .resize(800,800,{fit:'contain',background:'#ffffff'}).webp({quality:88}).toFile(`${out}/${name}.webp`);
  }
  for (const [name,page,x,y,w,h] of remaining) {
    const input = `artifacts/catalog-page-${page}.png`;
    const meta = await sharp(input).metadata();
    const left=Math.round(x/315*meta.width), top=Math.round(y/560*meta.height);
    const width=Math.min(Math.round(w/315*meta.width),meta.width-left);
    const height=Math.min(Math.round(h/560*meta.height),meta.height-top);
    await sharp(input).extract({left,top,width,height}).resize(800,800,{fit:'contain',background:'#ffffff'})
      .webp({quality:88}).toFile(`${out}/${name}.webp`);
  }
  for (const [name,source] of Object.entries(originals)) {
    await sharp(`artifacts/pdf-images/${source}.png`).resize(800,800,{fit:'contain',background:'#ffffff'})
      .flatten({background:'#ffffff'}).webp({quality:88}).toFile(`${out}/${name}.webp`);
  }
  console.log(`Prepared ${photos.length} photos and ${crops.length+remaining.length} catalog images.`);
})().catch(e => { console.error(e); process.exitCode=1; });
