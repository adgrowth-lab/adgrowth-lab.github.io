const assert = require('node:assert/strict');
const { chromium } = require('playwright');

const BASE_URL = process.argv[2] || 'http://127.0.0.1:18769';

const TOOLS = [
  {
    path: '/tools/voucher-calculator/',
    expectedTitleKeyword: 'Voucher Calculator',
    verifyInteraction: async (page) => {
      assert.equal(await page.locator('#display-credit-val').innerText(), '$3,000');
      await page.locator('.tier-option').nth(0).click();
      assert.equal(await page.locator('#display-credit-val').innerText(), '$200');
      await page.locator('.tier-option').nth(3).click();
      assert.equal(await page.locator('#display-credit-val').innerText(), '$6,000');
    }
  },
  {
    path: '/tools/cold-start-evaluator/',
    expectedTitleKeyword: 'Cold-Start Pacing Evaluator',
    verifyInteraction: async (page) => {
      assert.equal(await page.locator('#cs-score-val').innerText(), '75/100');
      await page.locator('#cs-budget').fill('20');
      await page.locator('#cs-cpa').fill('20');
      await page.locator('#cs-budget').dispatchEvent('input');
      const score = parseInt(await page.locator('#cs-score-val').innerText(), 10);
      assert.ok(score < 50, 'Low budget should lower viability score');
    }
  },
  {
    path: '/tools/pangle-leak-auditor/',
    expectedTitleKeyword: 'Pangle Leak Auditor',
    verifyInteraction: async (page) => {
      assert.equal(await page.locator('#pangle-waste-val').innerText(), '$1,125.00');
      await page.locator('#pangle-mode').selectOption('manual');
      assert.equal(await page.locator('#pangle-waste-val').innerText(), '$0.00');
      assert.equal(await page.locator('#pangle-status-badge').innerText(), 'ZERO LEAKAGE (ISOLATED)');
    }
  },
  {
    path: '/tools/compliance-linter/',
    expectedTitleKeyword: 'Compliance Linter',
    verifyInteraction: async (page) => {
      assert.ok((await page.locator('#linter-count-badge').innerText()).includes('Warning'));
      await page.locator('button:has-text("Compliant Copy")').click();
      assert.ok((await page.locator('#linter-count-badge').innerText()).includes('100% Compliant'));
    }
  },
  {
    path: '/tools/vcc-bin-evaluator/',
    expectedTitleKeyword: 'BIN Database',
    verifyInteraction: async (page) => {
      assert.equal(await page.locator('#bin-issuer-name').innerText(), 'Mercury Bank');
      assert.equal(await page.locator('#bin-pass-rate').innerText(), '96.5%');
      await page.locator('#bin-select-preset').selectOption('486695');
      assert.equal(await page.locator('#bin-issuer-name').innerText(), 'PST.net');
      assert.equal(await page.locator('#bin-risk-badge').innerText(), 'HIGH RISK');
    }
  },
  {
    path: '/tools/suspension-appeal/',
    expectedTitleKeyword: 'Appeal Letter Generator',
    verifyInteraction: async (page) => {
      const initial = await page.locator('#appeal-output-text').inputValue();
      assert.ok(initial.includes('Unusual Activity'));
      await page.locator('#appeal-company-name').fill('Global Hyper Media Corp');
      await page.locator('#appeal-company-name').dispatchEvent('input');
      const updated = await page.locator('#appeal-output-text').inputValue();
      assert.ok(updated.includes('Global Hyper Media Corp'));
    }
  }
];

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    for (const tool of TOOLS) {
      const url = `${BASE_URL.replace(/\/$/, '')}${tool.path}`;
      console.log(`\nTesting Standalone Tool Page: ${tool.path}`);
      
      const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
      const errors = [];
      page.on('pageerror', err => errors.push(err.message));

      const resp = await page.goto(url, { waitUntil: 'networkidle' });
      assert.equal(resp.status(), 200, `Page ${url} must return HTTP 200`);

      // 1. Verify SEO Metadata
      const title = await page.title();
      console.log(`  ✓ Title: "${title}"`);
      assert.ok(title.includes(tool.expectedTitleKeyword), `Title must contain "${tool.expectedTitleKeyword}"`);

      const desc = await page.locator('meta[name="description"]').getAttribute('content');
      assert.ok(desc && desc.length > 40, 'Meta description must be present and descriptive');
      console.log(`  ✓ Meta Description (${desc.length} chars)`);

      const canonical = await page.locator('link[rel="canonical"]').getAttribute('href');
      assert.ok(canonical && canonical.includes(tool.path), `Canonical URL must match ${tool.path}`);
      console.log(`  ✓ Canonical URL: ${canonical}`);

      // 2. Verify Schema.org JSON-LD structured data
      const jsonLdContent = await page.locator('script[type="application/ld+json"]').textContent();
      assert.ok(jsonLdContent, 'Schema JSON-LD must be present');
      const parsedSchema = JSON.parse(jsonLdContent);
      const graph = parsedSchema['@graph'] || [parsedSchema];
      const types = graph.map(item => item['@type']);
      assert.ok(types.includes('WebApplication'), 'Must contain WebApplication schema');
      assert.ok(types.includes('BreadcrumbList'), 'Must contain BreadcrumbList schema');
      assert.ok(types.includes('FAQPage'), 'Must contain FAQPage schema');
      console.log(`  ✓ Structured Data Verified: ${types.join(', ')}`);

      // 3. Verify Breadcrumbs & H1
      const h1 = await page.locator('h1').innerText();
      assert.ok(h1.length > 5, 'H1 must be present and visible');
      console.log(`  ✓ H1 Headline: "${h1}"`);

      // 4. Verify Interactive Tool Functionality
      await tool.verifyInteraction(page);
      console.log('  ✓ Interactive Tool Logic Passed');

      // 5. Verify Mobile Viewport & No Horizontal Scroll
      await page.setViewportSize({ width: 375, height: 812 });
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const innerWidth = await page.evaluate(() => window.innerWidth);
      assert.ok(scrollWidth <= innerWidth + 1, `Mobile 375px should not have horizontal overflow (scrollWidth: ${scrollWidth}, innerWidth: ${innerWidth})`);
      console.log('  ✓ Mobile Viewport (375px) Verified');

      assert.deepEqual(errors, [], `No page errors allowed on ${tool.path}`);
      await page.close();
    }

    console.log('\n======================================================');
    console.log('ALL 6 STANDALONE SEO TOOL PAGES VERIFIED 100% SUCCESFULLY!');
    console.log('======================================================\n');
  } finally {
    await browser.close();
  }
})().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
