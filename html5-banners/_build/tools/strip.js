// usage: node strip.js <banner_dir> <out.png> t1 t2 ...   (also checks every animation is infinite)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [dir, out, ...ts] = process.argv.slice(2); const br = await chromium.launch();
  const page = await br.newPage({ viewport: { width: 300, height: 250 } });
  await page.goto('file://' + path.resolve(dir, 'index.html')); await page.evaluate(() => document.fonts.ready);
  console.log('iterations:', await page.evaluate(() => [...new Set(document.getAnimations().map(a => a.effect.getTiming().iterations))]));
  let i = 0;
  for (const t of ts) { await page.evaluate((ms) => { document.documentElement.className = ''; for (const a of document.getAnimations()) { a.pause(); a.currentTime = ms; } }, +t * 1000);
    await page.screenshot({ path: `${out}_${String(i++).padStart(2, '0')}.png` }); }
  await br.close();
})();
