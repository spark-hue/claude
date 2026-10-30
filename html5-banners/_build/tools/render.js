// usage: node render.js <banner_dir> <out_prefix> [gif]
// Writes <out_prefix>_final.png, prints a QA JSON line, and (with "gif") writes frames to <out_prefix>_frames/.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const LOOP = 8.0, FPS = 15;

(async () => {
  const [dir, prefix, mode] = process.argv.slice(2);
  const html = path.resolve(dir, 'index.html');
  const m = fs.readFileSync(html, 'utf8').match(/width=(\d+),height=(\d+)/);
  const W = +m[1], H = +m[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: +(process.env.DSF || 1) });
  await page.goto('file://' + html);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(100);
  const seek = (t) => page.evaluate((ms) => {
    document.documentElement.className = '';
    for (const a of document.getAnimations()) { a.pause(); a.currentTime = ms; }
  }, t * 1000);

  // ---- final frame + QA -------------------------------------------------
  await seek(7.4);  // end of the hold, before the loop's fade-out
  await page.screenshot({ path: prefix + '_final.png' });
  const qa = await page.evaluate(([W, H]) => {
    const r = (sel) => { const e = document.querySelector(sel); if (!e) return null; const b = e.getBoundingClientRect(); return { x: b.left, y: b.top, r: b.right, b: b.bottom }; };
    const issues = [];
    const els = ['.logo', '.photo', '.head', '.body', '.cta'];
    const rects = {};
    for (const s of els) { const b = r(s); if (!b) continue; rects[s] = b;
      if (b.x < -0.5 || b.y < -0.5 || b.r > W + 0.5 || b.b > H + 0.5) issues.push(`${s} outside frame ${JSON.stringify(b)}`); }
    // headline must fit its box (no clipped / overflowing line)
    const h = document.querySelector('.head');
    if (h.scrollWidth > h.clientWidth + 1) issues.push(`headline wider than its box (${h.scrollWidth} > ${h.clientWidth})`);
    // text blocks must not collide with each other
    const ov = (a, b) => a && b && a.x < b.r && b.x < a.r && a.y < b.b && b.y < a.b;
    // glyph ink box of every text line (canvas metrics), not the line box, so leading doesn't count as overlap
    const ctx = document.createElement('canvas').getContext('2d');
    const ink = (blk) => [...document.querySelectorAll(blk + ' span')].map(s => {
      const cs = getComputedStyle(s); ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
      const m = ctx.measureText(s.textContent), fm = ctx.measureText('Hg');
      const rr = s.getBoundingClientRect(), fs = parseFloat(cs.fontSize);
      const contentH = fm.fontBoundingBoxAscent + fm.fontBoundingBoxDescent;
      const base = rr.top + (rr.height - contentH) / 2 + fm.fontBoundingBoxAscent;
      const w = m.width, x = cs.textAlign === 'right' ? rr.right - w : cs.textAlign === 'center' ? rr.left + (rr.width - w) / 2 : rr.left;
      if (w > rr.width + 0.5) issues.push(`${blk} line wider than its box: "${s.textContent}"`);
      return { x, r: x + w, y: base - m.actualBoundingBoxAscent, b: base + m.actualBoundingBoxDescent, t: s.textContent };
    });
    const lines = ink('.head'), body = ink('.body');
    for (const blk of [lines, body]) for (let i = 1; i < blk.length; i++)
      if (ov(blk[i], blk[i - 1])) issues.push(`lines collide: "${blk[i - 1].t}" / "${blk[i].t}"`);
    const cta = rects['.cta'], logo = rects['.logo'];
    for (const l of lines) { if (body.some(b => ov(l, b))) issues.push('headline overlaps body'); if (ov(l, cta)) issues.push('headline overlaps CTA'); if (ov(l, logo)) issues.push('headline overlaps logo'); }
    for (const l of body) { if (ov(l, cta)) issues.push('body overlaps CTA'); if (ov(l, logo)) issues.push('body overlaps logo'); }
    const gap = (a, b) => b.y - a.b;  // smallest vertical clearance between consecutive lines, for the report
    const minGap = Math.min(...[lines, body].flatMap(blk => blk.slice(1).map((l, i) => gap(blk[i], l))), 99);
    return { W, H, issues, minLineGap: +minGap.toFixed(2) };
  }, [W, H]);

  // pixel test: do text pixels land on photo pixels?
  const shot = async (show) => {
    await page.evaluate((show) => {
      for (const e of document.querySelectorAll('#ad>*')) e.style.visibility = show.some(s => e.matches(s)) ? 'visible' : 'hidden';
      document.getElementById('ad').style.background = 'transparent'; document.body.style.background = 'transparent';
      document.documentElement.style.background = 'transparent';
    }, show);
    return page.screenshot({ omitBackground: true });
  };
  if (await page.$('.photo')) {
    const a = await shot(['.photo']); const b = await shot(['.head', '.body', '.cta', '.logo']);
    fs.writeFileSync(prefix + '_m_photo.png', a); fs.writeFileSync(prefix + '_m_text.png', b);
  }
  await page.evaluate(() => { for (const e of document.querySelectorAll('#ad>*')) e.style.visibility = ''; document.getElementById('ad').style.background = ''; document.body.style.background = ''; document.documentElement.style.background = ''; });
  console.log(JSON.stringify(qa));

  // ---- GIF frames ---------------------------------------------------------
  if (mode === 'gif') {
    const fdir = prefix + '_frames'; fs.mkdirSync(fdir, { recursive: true });
    const n = Math.round(LOOP * FPS);
    for (let i = 0; i < n; i++) {
      await seek(i / FPS);
      await page.screenshot({ path: path.join(fdir, String(i).padStart(4, '0') + '.png') });
    }
  }
  await browser.close();
})();
