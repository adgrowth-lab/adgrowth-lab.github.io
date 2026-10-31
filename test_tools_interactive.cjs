const assert = require('node:assert/strict');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));

    await page.goto(process.argv[2] || 'http://127.0.0.1:18769/', { waitUntil: 'networkidle' });

    // 1. Check Tool 1: Cold-Start Evaluator
    console.log('Testing Tool 1: Cold-Start Evaluator...');
    assert.equal(await page.locator('#cs-score-val').innerText(), '75/100');
    assert.equal(await page.locator('#cs-daily-conv').innerText(), '5.0 / day');
    await page.locator('#cs-budget').fill('20');
    await page.locator('#cs-cpa').fill('20');
    await page.locator('#cs-budget').dispatchEvent('input');
    const scoreText = await page.locator('#cs-score-val').innerText();
    assert.ok(parseInt(scoreText) < 50, 'Low budget should lower viability score');

    // 2. Switch to Tool 2: Pangle Leak Auditor
    console.log('Testing Tool 2: Pangle Leak Auditor...');
    await page.locator('#tab-btn-pangle').click();
    assert.ok(await page.locator('#panel-diag-pangle').isVisible());
    assert.equal(await page.locator('#pangle-waste-val').innerText(), '$1,125.00');
    await page.locator('#pangle-mode').selectOption('manual');
    assert.equal(await page.locator('#pangle-waste-val').innerText(), '$0.00');
    assert.equal(await page.locator('#pangle-status-badge').innerText(), 'ZERO LEAKAGE (ISOLATED)');

    // 3. Switch to Tool 3: Creative Compliance Linter
    console.log('Testing Tool 3: Creative Compliance Linter...');
    await page.locator('#tab-btn-linter').click();
    assert.ok(await page.locator('#panel-diag-linter').isVisible());
    assert.ok((await page.locator('#linter-count-badge').innerText()).includes('Warning'));
    // Click Compliant preset
    await page.locator('button:has-text("Compliant Hook")').click();
    assert.ok((await page.locator('#linter-count-badge').innerText()).includes('100% Compliant'));

    // 4. Switch to Tool 4: VCC BIN Evaluator
    console.log('Testing Tool 4: VCC BIN Evaluator...');
    await page.locator('#tab-btn-bin').click();
    assert.ok(await page.locator('#panel-diag-bin').isVisible());
    assert.equal(await page.locator('#bin-issuer-name').innerText(), 'Mercury Bank');
    assert.equal(await page.locator('#bin-pass-rate').innerText(), '96.5%');
    await page.locator('#bin-select-preset').selectOption('486695');
    assert.equal(await page.locator('#bin-issuer-name').innerText(), 'PST.net');
    assert.equal(await page.locator('#bin-risk-badge').innerText(), 'HIGH RISK');

    // 5. Switch to Tool 5: Suspension Appeal Generator
    console.log('Testing Tool 5: Suspension Appeal Generator...');
    await page.locator('#tab-btn-appeal').click();
    assert.ok(await page.locator('#panel-diag-appeal').isVisible());
    const initialText = await page.locator('#appeal-output-text').inputValue();
    assert.ok(initialText.includes('Unusual Activity'));
    await page.locator('#appeal-company-name').fill('Test Super Brand LLC');
    await page.locator('#appeal-company-name').dispatchEvent('input');
    const updatedText = await page.locator('#appeal-output-text').inputValue();
    assert.ok(updatedText.includes('Test Super Brand LLC'));

    // 6. Test Prominence & Hero Quick-Launch Chips
    console.log('Testing Hero Quick-Launch Chips & DOM Placement...');
    const sectionOrder = await page.evaluate(() => {
      const sections = [...document.querySelectorAll('main > section, main > div')];
      const toolsIndex = sections.findIndex(s => s.id === 'tools');
      const tiersIndex = sections.findIndex(s => s.id === 'tiers');
      return { toolsIndex, tiersIndex };
    });
    assert.ok(sectionOrder.toolsIndex < sectionOrder.tiersIndex, '#tools must precede #tiers in DOM hierarchy');
    const chips = await page.locator('.quick-tool-chip').all();
    assert.equal(chips.length, 5, 'Must render 5 quick tool chips in hero');
    await page.locator('.quick-tool-chip:has-text("Pangle Leak")').click();
    assert.ok(await page.locator('#panel-diag-pangle').isVisible());

    // 7. Test Mobile Viewport Display (375px & 320px)
    console.log('Testing Mobile Viewports & Touch Adaptation...');
    await page.setViewportSize({ width: 375, height: 812 });
    const tabStyles = await page.evaluate(() => {
      const btn = document.querySelector('.diag-tab-btn');
      const input = document.querySelector('#cs-budget');
      return {
        tabMinHeight: window.getComputedStyle(btn).minHeight,
        inputFontSize: window.getComputedStyle(input).fontSize,
      };
    });
    assert.ok(parseFloat(tabStyles.tabMinHeight) >= 38, 'Mobile tab min-height >= 38px');
    assert.equal(tabStyles.inputFontSize, '16px', 'Input font-size must be 16px to prevent iOS auto-zoom');

    await page.setViewportSize({ width: 320, height: 600 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '320px width has no horizontal scroll');
    const oversized = await page.evaluate(() =>
      [...document.querySelectorAll('main *')].filter(el => el.getBoundingClientRect().right > innerWidth + 1).map(el => el.className)
    );
    assert.deepEqual(oversized, [], 'No oversized elements at 320px');

    assert.deepEqual(errors, []);
    console.log('ALL 5 INTERACTIVE TOOLS + MOBILE PROMINENCE PASSED 100%!');
  } finally {
    await browser.close();
  }
})().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
