// Start python3 -m http.server 18769, then run: node test_frontend.cjs [URL]
// Requires the existing Playwright and installed Chrome; no app dependencies.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(process.argv[2] || 'http://127.0.0.1:18769/', { waitUntil: 'networkidle' });
    const tiers = [[200, 200, '100% Match'], [1000, 750, '75% Match'], [4000, 3000, '75% Match'], [10000, 6000, '60% Match']];
    const money = n => '$' + n.toLocaleString('en-US');
    async function check(index) {
      const [spend, credit, match] = tiers[index];
      assert.equal(await page.locator('#display-credit-val').innerText(), money(credit));
      assert.equal(await page.locator('#display-power-val').innerText(), money(spend + credit) + ' Ad Spend');
      assert.equal(await page.locator('#display-multiplier-val').innerText(), ((spend + credit) / spend).toFixed(2) + '×');
      assert.equal(await page.locator('#display-match-val').innerText(), match);
      assert.equal(await page.locator('#display-spend-val').innerText(), money(spend));
      assert.equal(await page.locator('#bar-credit-val').innerText(), money(credit));
      const share = await page.locator('#budget-credit-bar').evaluate(async el => {
        await Promise.all(el.getAnimations().map(animation => animation.finished));
        return el.getBoundingClientRect().width / el.parentElement.getBoundingClientRect().width;
      });
      assert.ok(Math.abs(share - credit / (spend + credit)) < .002, 'budget bar must match credit share');
      assert.equal(await page.locator('#tier-select-input').inputValue(), String(spend));
      assert.equal(await page.locator('.tier-option[aria-pressed="true"]').count(), 1);
      assert.equal(await page.locator('.tier-option').nth(index).getAttribute('aria-pressed'), 'true');
      assert.equal(await page.locator('#dash-sim-amount').innerText(), '+' + money(credit) + '.00 USD');
      for (const id of ['hero-main-cta', 'nav-cta-btn', 'calc-claim-button', 'dialog-submit-btn', 'dialog-summary-text']) {
        assert.ok((await page.locator('#' + id).textContent()).includes(money(credit)), id + ' must sync');
      }
    }
    await check(2);
    for (let i = 0; i < tiers.length; i++) { await page.locator('.tier-option').nth(i).click(); await check(i); }
    for (let i = 0; i < tiers.length; i++) { await page.locator('#tier-select-input').selectOption(String(tiers[i][0])); await check(i); }
    await page.locator('.tier-option').nth(0).focus();
    await page.keyboard.press('Space'); await check(0);
    await page.keyboard.press('Tab'); await page.keyboard.press('Enter'); await check(1);
    const faqUrls = ['https://getstartedtiktok.partnerlinks.io/apmgdhnv6eng', '#tiers', 'https://getstartedtiktok.partnerlinks.io/apmgdhnv6eng', 'https://ads.tiktok.com/i18n/account/payment_promotion'];
    for (const [i, url] of faqUrls.entries()) {
      await page.locator('.faq-btn').nth(i).click();
      assert.equal(await page.locator('#faq-cta').getAttribute('href'), url);
      assert.equal(await page.locator('.faq-btn[aria-pressed="true"]').count(), 1);
      assert.equal(await page.locator('#faq-cta').getAttribute('target'), url.startsWith('http') ? '_blank' : null);
    }
    const structure = await page.evaluate(() => {
      const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
      return {
        duplicates: ids.filter((id, i) => ids.indexOf(id) !== i),
        brokenAnchors: [...document.querySelectorAll('a[href^="#"]')].map(el => el.getAttribute('href')).filter(h => h !== '#' && !document.getElementById(h.slice(1))),
        unsafeLinks: [...document.querySelectorAll('a[target="_blank"]')].filter(el => !el.relList.contains('noopener')).length,
        h1: document.querySelectorAll('h1').length, main: document.querySelectorAll('main').length,
      };
    });
    assert.deepEqual(structure, { duplicates: [], brokenAnchors: [], unsafeLinks: 0, h1: 1, main: 1 });
    for (const width of [320, 375, 390, 640, 768, 900, 1024, 1200, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'overflow at ' + width);
      assert.deepEqual(await page.evaluate(() => [...document.querySelectorAll('main *')].filter(el => el.getBoundingClientRect().right > innerWidth + 1).map(el => el.className)), [], 'oversized element at ' + width);
    }
    await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'dark' });
    assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior), 'auto');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('.faq-btn').nth(0).click();
    assert.equal(await page.locator('.faq-btn').nth(0).getAttribute('aria-pressed'), 'true');
    assert.deepEqual(errors, []);
    console.log('PASS: proportional budget visualization, four tiers, two-way sync, keyboard, FAQs, links, nine widths, reduced motion, dark appearance, no JS errors.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
