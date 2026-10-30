// Writes a static backup image next to every banner zip: the end frame (t=7.4s, everything on screen) at 1x,
// as <banner>.jpg. Renders from the zip itself, so it is exactly what was delivered.
// usage: node backup.js <root_dir> <tmp_dir>
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const { execFileSync } = require('child_process');
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap(e =>
  e.isDirectory() ? (e.name.startsWith('_') ? [] : walk(path.join(d, e.name))) : e.name.endsWith('.zip') ? [path.join(d, e.name)] : []);
(async () => {
  const [root, tmp] = process.argv.slice(2);
  const zips = walk(root); const br = await chromium.launch(); const pages = {};
  let n = 0;
  for (const z of zips) {
    const dir = path.join(tmp, path.basename(z, '.zip'));
    fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    execFileSync('unzip', ['-q', '-o', z, '-d', dir]);
    const [W, H] = fs.readFileSync(path.join(dir, 'index.html'), 'utf8').match(/width=(\d+),height=(\d+)/).slice(1).map(Number);
    const key = W + 'x' + H;
    if (!pages[key]) pages[key] = await (await br.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })).newPage();
    const page = pages[key];
    await page.goto('file://' + path.resolve(dir, 'index.html'), { waitUntil: 'load' });
    await page.evaluate(async () => {
      if (document.fonts) await document.fonts.ready;
      document.documentElement.className = '';
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = 7400; }
    });
    // keep backups light: step quality down if a big unit comes out heavy
    const out = z.replace(/\.zip$/, '.jpg');
    for (const q of [90, 85, 80, 72, 65]) {
      fs.writeFileSync(out, await page.screenshot({ type: 'jpeg', quality: q }));
      if (fs.statSync(out).size <= 150 * 1024) break;
    }
    fs.rmSync(dir, { recursive: true, force: true });
    if (++n % 100 === 0) console.log(n + '/' + zips.length);
  }
  console.log('done', n);
  await br.close();
})();
