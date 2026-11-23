// Renders SVG files to transparent PNGs with headless Chromium.
// Usage: node render.js jobs.json   where jobs = [{svg, png, size}]
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  for (const job of jobs) {
    await page.setViewportSize({ width: job.size, height: job.size });
    const svg = fs.readFileSync(job.svg, 'utf8');
    await page.setContent(
      `<html><body style="margin:0;background:transparent">${svg}</body></html>`
    );
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.png, omitBackground: true });
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
