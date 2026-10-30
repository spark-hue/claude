// Renders each banner's final frame at 2x with only .head/.body visible -> <qa>/<size>_text.png, plus line boxes json
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [out, qa] = process.argv.slice(2); const br = await chromium.launch(); const info = {};
  for (const dir of fs.readdirSync(out)) {
    const size = dir.split('_').pop(); const [W, H] = size.split('x').map(Number);
    const page = await br.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
    await page.goto('file://' + path.resolve(out, dir, 'index.html')); await page.evaluate(() => document.fonts.ready);
    info[size] = await page.evaluate(() => { document.documentElement.className = ''; for (const a of document.getAnimations()) { a.pause(); a.currentTime = 7000; }
      for (const e of document.querySelectorAll('#ad>*')) e.style.visibility = e.matches('.head,.body') ? 'visible' : 'hidden';
      for (const e of [document.documentElement, document.body, document.getElementById('ad')]) e.style.background = 'transparent';
      const o = {}; for (const c of ['head', 'body']) { const el = document.querySelector('.' + c); if (!el) continue;
        o[c] = [...el.children].map(s => { const r = s.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }); } return o; });
    await page.screenshot({ path: `${qa}/${size}_text.png`, omitBackground: true }); await page.close();
  }
  fs.writeFileSync(`${qa}/lines.json`, JSON.stringify(info)); await br.close();
})();
