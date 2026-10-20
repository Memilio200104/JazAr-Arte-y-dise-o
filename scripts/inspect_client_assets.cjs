const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
(async () => {
  const root = 'C:/Users/emili/Downloads/JaZar';
  const files = fs.readdirSync(root).filter(f => f.endsWith('.jpeg')).sort();
  const layers = [];
  for (let i = 0; i < files.length; i++) {
    const input = await sharp(path.join(root, files[i])).rotate().resize(220, 200, { fit: 'contain', background: 'white' }).png().toBuffer();
    layers.push({ input, left: i % 4 * 240, top: Math.floor(i / 4) * 235 });
    layers.push({ input: Buffer.from(`<svg width="230" height="25"><text x="8" y="18" font-size="16">Photo ${i}</text></svg>`), left: i % 4 * 240, top: Math.floor(i / 4) * 235 + 200 });
  }
  await sharp({ create: { width: 960, height: Math.ceil(files.length / 4) * 235, channels: 3, background: 'white' } }).composite(layers).png().toFile('artifacts/client-photos.png');
  console.log(files.map((f, i) => `${i}: ${f}`).join('\n'));
})().catch(e => { console.error(e); process.exitCode = 1; });
