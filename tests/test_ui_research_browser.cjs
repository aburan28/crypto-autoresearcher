/* Optional visual/layout smoke test against an already-built static snapshot.
 * From ui/: npm install --no-save playwright; npx playwright install chromium
 * UI_TEST_URL=http://127.0.0.1:8787 node tests/test_ui_research_browser.cjs
 * Run the local server or serve a static export in the same network namespace.
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '../ui/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({headless:true});
  const base = process.env.UI_TEST_URL || 'http://127.0.0.1:8787';
  try {
    for (const width of [390, 1280]) {
      const page = await browser.newPage({viewport:{width,height:900}});
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(`${base}/#/curves`);
      await page.getByRole('heading',{name:'Curve catalog',exact:true}).waitFor();
      await page.getByRole('button',{name:'Inspect as first'}).first().click();
      await page.getByRole('button',{name:'Compare as second'}).last().click();
      assert.equal(await page.locator('.comparison-table').count(), 1);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth), false);
      await page.goto(`${base}/#/compare?a=primary-1&b=primary-2`);
      await page.locator('.comparison-table').waitFor();
      assert.ok(await page.locator('.comparison-table a[href*="/blob/"]').count() > 0);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth), false);
      await page.goto(`${base}/#/provenance`);
      await page.getByRole('heading',{name:'Research provenance',exact:true}).waitFor();
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth), false);
      assert.deepEqual(errors, []);
      await page.close();
    }
    console.log('Curves, Compare and Provenance passed at 390px and 1280px.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
