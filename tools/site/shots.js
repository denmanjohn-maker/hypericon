// Renders the website's illustration screenshots from the live demo on the page.
// Usage: node tools/site/shots.js [review-dir]
const path = require('path');
const { chromium } = require('playwright');

const site = path.resolve(__dirname, '..', '..', 'site');
const themes = ['synthwave-84', 'scifi-hud', 'winter-holiday', 'nineties-desktop'];
const review = process.argv[2];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1180, height: 800 }, deviceScaleFactor: 2 });
  const problems = [];
  page.on('console', (m) => { if (m.type() === 'error') problems.push(m.text()); });
  page.on('pageerror', (e) => problems.push(String(e)));
  page.on('requestfailed', (r) => { if (!/screenshot-/.test(r.url())) problems.push('failed: ' + r.url()); });

  for (const id of themes) {
    await page.goto('file://' + path.join(site, 'index.html') + '?theme=' + id);
    await page.waitForLoadState('networkidle');
    await page.locator('.scene').screenshot({ path: path.join(site, 'assets', `screenshot-${id}.png`) });
  }
  if (review) {
    await page.goto('file://' + path.join(site, 'index.html') + '?theme=synthwave-84');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: path.join(review, 'site-desktop.png'), fullPage: true, scale: 'css' });
    const phone = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    await phone.goto('file://' + path.join(site, 'index.html') + '?theme=halloween');
    await phone.waitForLoadState('networkidle');
    const overflow = await phone.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (overflow > 0) problems.push('phone layout scrolls horizontally by ' + overflow + 'px');
    await phone.screenshot({ path: path.join(review, 'site-phone.png'), fullPage: true });
  }
  await browser.close();
  if (problems.length) { console.error(problems.join('\n')); process.exit(1); }
  console.log('screenshots written');
})();
