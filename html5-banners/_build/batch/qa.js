// Renders the end frame (t=7.4s, before the loop's fade) of every banner at 2x and checks each animation loops.
// usage: node qa.js <manifest.json> <out_dir> <qa_dir> [filter]
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [manPath, out, qa, filter = ''] = process.argv.slice(2);
  const man = JSON.parse(fs.readFileSync(manPath)).filter(b => (b.folder + '/' + b.name).includes(filter));
  fs.mkdirSync(qa, { recursive: true });
  const br = await chromium.launch(); const res = {};
  const ctxs = {};
  let n = 0;
  for (const b of man) {
    const dir = path.join(out, b.folder, b.name);
    if (!fs.existsSync(dir)) continue;
    const key = b.OW + 'x' + b.H;
    if (!ctxs[key]) ctxs[key] = await (await br.newContext({ viewport: { width: b.OW, height: b.H }, deviceScaleFactor: 2 })).newPage();
    const page = ctxs[key];
    await page.goto('file://' + path.resolve(dir, 'index.html'), { waitUntil: 'load' });
    const info = await page.evaluate(() => {
      document.documentElement.className = '';
      const an = document.getAnimations();
      for (const a of an) { a.pause(); a.currentTime = 7400; }
      const broken = [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src);
      return { iterations: [...new Set(an.map(a => a.effect.getTiming().iterations))], broken };
    });
    await page.screenshot({ path: path.join(qa, b.id.replace(/:/g, '-') + '.png') });
    res[b.id] = info;
    if (++n % 50 === 0) console.log(n);
  }
  fs.writeFileSync(path.join(qa, 'qa.json'), JSON.stringify(res));
  await br.close();
})();
