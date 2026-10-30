// Rasterizes Figma clip-path masks over each photo group's frame-relative box -> masks/<id>_alpha.png (cropped to the frame, like Figma's export)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const G = { // id: [frameW, frameH, groupX, groupY, scale]
  '1-3333': [970, 250, -1, -3, 2], '1-3352': [300, 600, -3, 381, 2], '1-3367': [336, 280, -1, 95, 2], '1-3381': [300, 250, -1, 84, 2],
  '1-3399': [150, 600, -11.147481918334961, 434, 2.2], '1-3414': [1024, 768, -21, 159, 2], '1-3439': [768, 1024, -3, 390, 2] };
(async () => {
  const dir = process.argv[2]; const br = await chromium.launch();
  for (const [id, [W, H, gx, gy, s]] of Object.entries(G)) {
    const svg = fs.readFileSync(path.join(dir, id + '.svg'), 'utf8').replace('fill="black"', 'fill="#000"');
    const page = await br.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: s });
    await page.setContent(`<html style="background:transparent"><body style="margin:0;background:transparent"><div style="position:absolute;left:${gx}px;top:${gy}px">${svg}</div></body></html>`);
    const box = await page.evaluate(() => { const r = document.querySelector('svg').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; });
    const x0 = Math.max(0, box[0]), y0 = Math.max(0, box[1]), x1 = Math.min(W, box[2]), y1 = Math.min(H, box[3]);
    await page.screenshot({ path: path.join(dir, id + '_alpha.png'), omitBackground: true, clip: { x: x0, y: y0, width: x1 - x0, height: y1 - y0 } });
    await page.close();
  }
  await br.close();
})();
