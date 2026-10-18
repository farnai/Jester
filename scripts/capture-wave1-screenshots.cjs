const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');

const outDir = path.join('.jester', 'reports', 'verification', 'modern-home-wave1');
fs.mkdirSync(outDir, { recursive: true });

const baseUrl = process.env.JESTER_URL || 'http://localhost:3001';

const mockProfile = {
  id: 'viewer-1',
  display_name: 'გიორგი მ.',
  bio: 'არქიტექტურა, ურბანული დიზაინი და საინტერესო საუბრები.',
  city: 'Tbilisi',
  occupation: 'არქიტექტორი',
  timezone: 'Asia/Tbilisi',
  avatar_url: null,
  onboarding_completed: true,
  is_discoverable: true,
};

const mockDailyEnergy = {
  date: '2026-10-18',
  detection_mode: 'real_transit',
  label: 'ემოციური პაუზა და შინაგანი სიცხადე',
  interpretation: {
    text: 'გარედან თითქოს საკუთარ თავთან მარტო დარჩენა ერთადერთი რამაა, რაც დღეს ნორმალურ მდგომარეობას შეგინარჩუნებს. შიგნით კი საკუთარი თავშესაფარი დღეს შენი ერთადერთი გადარჩენაა — გაცილებით მეტი სიმშვიდე მოდის, როცა გარემო ხმაურს დროებით გამოეთიშები.',
  },
  do: ['ყურადღებით მოსმენა', 'მშვიდი სივრცე', 'აუჩქარებელი ტემპი'],
  dont: ['განწყობის მოშლა', 'მორღვეული საზღვრები', 'სრული პასიურობა'],
};

const mockConnections = [
  {
    id: 'conn-1',
    user_a_id: 'viewer-1',
    user_b_id: 'person-1',
    initiated_by: 'viewer-1',
    status: 'accepted',
  },
  {
    id: 'conn-2',
    user_a_id: 'viewer-1',
    user_b_id: 'person-4',
    initiated_by: 'person-4',
    status: 'pending',
  },
];

const mockDiscoveryPeople = [
  {
    id: 'person-1',
    display_name: 'ვაჟა ჯ.',
    avatar_url: null,
    occupation: 'ფოტოგრაფი',
    city: 'Batumi, Adjara',
    bio: 'ვიზუალური ამბები, მთები და კაფეები.',
    presence_sign_source: 'sun',
    hook_observation: {
      text: 'შთამბეჭდავი სიმშვიდე და ურყევი მზერა, რომელსაც ოთახში არქაეტული ქაოსი ვერაფერს აკლებს. ნახეთ, როგორ ჩანს ეს მყარი მანერა უშუალო კონტაქტში.',
    },
  },
  {
    id: 'person-2',
    display_name: 'ანა ბ.',
    avatar_url: null,
    occupation: 'მკვლევარი',
    city: 'Tbilisi',
    bio: 'კულტურული ანთროპოლოგია, წიგნები და საინტერესო დისკუსიები.',
    presence_sign_source: 'sun',
    hook_observation: {
      text: 'ცნობისმოყვარე და ანალიტიკური მზერა, რომელიც ყოველთვის პოულობს შეუმჩნეველ დეტალებს საუბარში.',
    },
  },
  {
    id: 'person-3',
    display_name: 'სალომე კ.',
    avatar_url: null,
    occupation: 'დიზაინერი',
    city: 'Tbilisi',
    bio: 'ინტერიერის დიზაინი, კერამიკა და მოგზაურობა.',
    presence_sign_source: 'sun',
    hook_observation: {
      text: 'ფრთხილი დისტანცია და უსიტყვო დაკვირვება, თითქოს ოთახში ტემპერატურას ზომავდეს. ნახეთ, როგორ იცვლება ეს თავდაცვითი პოზა, როცა დიალოგი ახლოვდება.',
    },
  },
];

const mockWhy = {
  target_id: 'person-1',
  score: 78,
  interpretation: {
    text: 'როგორც ჩანს, ტემპების სხვაობა გაგიგებთ: ერთი მეორეს მუხრუჭს უქებს, მეორე პირველს — თვითმკვლელ მძღოლს. თუმცა მოიცადე — სანამ ერთი ფიქრობს, მეორე უკვე შეცდომას უშვებს — სამაგიეროდ, ბალანსი დაცულია.',
  },
};

const viewports = [
  { name: 'desktop-1440', width: 1440, height: 900 },
  { name: 'desktop-1280', width: 1280, height: 800 },
  { name: 'tablet-768', width: 768, height: 1024 },
  { name: 'mobile-390', width: 390, height: 844 },
  { name: 'mobile-320', width: 320, height: 700 },
];

function makeDummyJwt(userId = 'viewer-1', email = 'giorgi@jester.ge') {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const now = Math.floor(Date.now() / 1000);
  const payload = Buffer.from(JSON.stringify({
    sub: userId,
    aud: 'authenticated',
    role: 'authenticated',
    email,
    exp: now + 360000,
    iat: now,
    user_metadata: { display_name: 'გიორგი მ.' },
    app_metadata: { provider: 'email' },
  })).toString('base64url');
  const signature = Buffer.from('dummy_signature_bytes_12345').toString('base64url');
  return `${header}.${payload}.${signature}`;
}

const validJwt = makeDummyJwt();

async function setupMocks(page, connectionsData = mockConnections) {
  // Mock Supabase Auth endpoints specifically
  await page.route('**/auth/v1/user*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'viewer-1',
        aud: 'authenticated',
        role: 'authenticated',
        email: 'giorgi@jester.ge',
        app_metadata: { provider: 'email' },
        user_metadata: { display_name: 'გიორგი მ.' },
        created_at: new Date().toISOString(),
      }),
    });
  });

  await page.route('**/auth/v1/token*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: validJwt,
        token_type: 'bearer',
        expires_in: 360000,
        refresh_token: 'valid-refresh-token',
        user: {
          id: 'viewer-1',
          aud: 'authenticated',
          role: 'authenticated',
          email: 'giorgi@jester.ge',
          app_metadata: { provider: 'email' },
          user_metadata: { display_name: 'გიორგი მ.' },
        },
      }),
    });
  });

  await page.route('**/auth/v1/**', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'viewer-1',
        aud: 'authenticated',
        role: 'authenticated',
        email: 'giorgi@jester.ge',
        user_metadata: { display_name: 'გიორგი მ.' },
      }),
    });
  });

  await page.route('**/rest/v1/birth_data*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ user_id: 'viewer-1' }]),
    });
  });

  await page.route('**/rest/v1/**', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });

  await page.route('**/v1/profiles/me', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockProfile),
    });
  });

  await page.route('**/v1/interpretations/daily-energy*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockDailyEnergy),
    });
  });

  await page.route('**/v1/connections', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(connectionsData),
    });
  });

  await page.route('**/v1/interpretations/discovery-people', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockDiscoveryPeople),
    });
  });

  await page.route('**/v1/people/person-1/why', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockWhy),
    });
  });

  await page.route('**/v1/notifications', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 'notif-1', read_at: null }]),
    });
  });
}

(async () => {
  console.log('Launching browser for Wave 1 screenshot capture...');
  const browser = await chromium.launch({ channel: 'msedge', headless: true });

  try {
    // 1. Standard Rich State (Accepted connection + Discover preview)
    for (const vp of viewports) {
      console.log(`Capturing ${vp.name} (${vp.width}x${vp.height})...`);
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        deviceScaleFactor: 1,
      });
      const page = await context.newPage();
      await setupMocks(page);

      await page.goto(baseUrl + '/auth/login', { waitUntil: 'load' });
      await page.evaluate((jwt) => {
        const mockAuth = {
          access_token: jwt,
          token_type: 'bearer',
          expires_in: 360000,
          expires_at: Math.floor(Date.now() / 1000) + 360000,
          refresh_token: 'valid-refresh-token',
          user: {
            id: 'viewer-1',
            aud: 'authenticated',
            role: 'authenticated',
            email: 'giorgi@jester.ge',
            app_metadata: { provider: 'email' },
            user_metadata: { display_name: 'გიორგი მ.' },
          },
        };
        localStorage.setItem('sb-127-auth-token', JSON.stringify(mockAuth));
      }, validJwt);

      await page.goto(baseUrl, { waitUntil: 'networkidle' });
      console.log('Navigated to:', page.url());
      await page.waitForSelector('.home-experience', { timeout: 10000 });

      // Initial viewport screenshot
      await page.screenshot({
        path: path.join(outDir, `${vp.name}-viewport.png`),
        fullPage: false,
      });

      // Full page screenshot
      await page.screenshot({
        path: path.join(outDir, `${vp.name}-full.png`),
        fullPage: true,
      });

      await context.close();
    }

    // 2. New User State (Zero Connections)
    console.log('Capturing zero-connections state at 1280x800...');
    const noConnContext = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      deviceScaleFactor: 1,
    });
    const noConnPage = await noConnContext.newPage();
    await setupMocks(noConnPage, []);
    await noConnPage.goto(baseUrl + '/auth/login', { waitUntil: 'load' });
    await noConnPage.evaluate((jwt) => {
      const mockAuth = {
        access_token: jwt,
        token_type: 'bearer',
        expires_in: 360000,
        expires_at: Math.floor(Date.now() / 1000) + 360000,
        refresh_token: 'valid-refresh-token',
        user: {
          id: 'viewer-1',
          aud: 'authenticated',
          role: 'authenticated',
          email: 'giorgi@jester.ge',
          app_metadata: { provider: 'email' },
          user_metadata: { display_name: 'გიორგი მ.' },
        },
      };
      localStorage.setItem('sb-127-auth-token', JSON.stringify(mockAuth));
    }, validJwt);
    await noConnPage.goto(baseUrl, { waitUntil: 'networkidle' });
    await noConnPage.waitForSelector('.home-experience', { timeout: 10000 });
    await noConnPage.waitForTimeout(500);

    await noConnPage.screenshot({
      path: path.join(outDir, 'desktop-no-connections-full.png'),
      fullPage: true,
    });
    await noConnContext.close();

    // 3. User Menu Open State (Desktop 1280x800)
    console.log('Capturing user account dropdown menu open at 1280x800...');
    const menuContext = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      deviceScaleFactor: 1,
    });
    const menuPage = await menuContext.newPage();
    await setupMocks(menuPage);
    await menuPage.goto(baseUrl + '/auth/login', { waitUntil: 'load' });
    await menuPage.evaluate((jwt) => {
      const mockAuth = {
        access_token: jwt,
        token_type: 'bearer',
        expires_in: 360000,
        expires_at: Math.floor(Date.now() / 1000) + 360000,
        refresh_token: 'valid-refresh-token',
        user: {
          id: 'viewer-1',
          aud: 'authenticated',
          role: 'authenticated',
          email: 'giorgi@jester.ge',
          app_metadata: { provider: 'email' },
          user_metadata: { display_name: 'გიორგი მ.' },
        },
      };
      localStorage.setItem('sb-127-auth-token', JSON.stringify(mockAuth));
    }, validJwt);
    await menuPage.goto(baseUrl, { waitUntil: 'networkidle' });
    await menuPage.waitForSelector('.home-account-trigger', { timeout: 10000 });
    await menuPage.click('.home-account-trigger');
    await menuPage.waitForSelector('.home-account-popover', { timeout: 5000 });
    await menuPage.waitForTimeout(300);

    await menuPage.screenshot({
      path: path.join(outDir, 'desktop-user-menu-open.png'),
      fullPage: false,
    });
    await menuContext.close();

    console.log('All screenshots captured successfully!');
  } catch (err) {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
