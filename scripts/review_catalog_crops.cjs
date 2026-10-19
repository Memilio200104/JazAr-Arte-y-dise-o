const fs = require('fs');
const sharp = require('sharp');
(async () => {
  const files = fs.readdirSync('static/images/client').filter(name => /^c[0-9].*webp$/.test(name));
  for (let group = 0; group < Math.ceil(files.length / 20); group++) {
    const layers = [];
    for (let j = 0; j < 20 && group * 20 + j < files.length; j++) {
      const name = files[group * 20 + j];
      const left = j % 4 * 180, top = Math.floor(j / 4) * 205;
      layers.push({input:await sharp(`static/images/client/${name}`).resize(180,180).png().toBuffer(),left,top});
      layers.push({input:Buffer.from(`<svg width="180" height="25"><text x="5" y="18" font-size="15">${name}</text></svg>`),left,top:top+180});
    }
    await sharp({create:{width:720,height:1025,channels:3,background:'white'}}).composite(layers).png().toFile(`artifacts/crops-review-${group}.png`);
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
