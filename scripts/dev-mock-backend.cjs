const http = require('node:http');
const url = require('node:url');

function makeJwt(userId = 'viewer-1', email = 'giorgi@jester.ge') {
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
  date: new Date().toISOString().split('T')[0],
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

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
  res.setHeader('Access-Control-Allow-Headers', '*');
}

// 1. Mock Supabase Gateway on port 54321
const supabaseServer = http.createServer((req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname || '';

  // Auth: Token (Password / Refresh)
  if (pathname.startsWith('/auth/v1/token') || pathname.startsWith('/auth/v1/signup')) {
    const jwt = makeJwt();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      access_token: jwt,
      token_type: 'bearer',
      expires_in: 360000,
      expires_at: Math.floor(Date.now() / 1000) + 360000,
      refresh_token: 'mock-refresh-token',
      user: {
        id: 'viewer-1',
        aud: 'authenticated',
        role: 'authenticated',
        email: 'giorgi@jester.ge',
        app_metadata: { provider: 'email' },
        user_metadata: { display_name: 'გიორგი მ.' },
      },
    }));
    return;
  }

  // Auth: User info
  if (pathname.startsWith('/auth/v1/user')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      id: 'viewer-1',
      aud: 'authenticated',
      role: 'authenticated',
      email: 'giorgi@jester.ge',
      app_metadata: { provider: 'email' },
      user_metadata: { display_name: 'გიორგი მ.' },
      created_at: new Date().toISOString(),
    }));
    return;
  }

  // REST: birth_data
  if (pathname.startsWith('/rest/v1/birth_data')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify([{ user_id: 'viewer-1' }]));
    return;
  }

  // Default REST
  if (pathname.startsWith('/rest/v1/')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify([]));
    return;
  }

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'ok' }));
});

// 2. Mock Jester API on port 8000
const apiServer = http.createServer((req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname || '';

  if (pathname === '/healthz' || pathname === '/v1/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy', version: '1.0.0-mock' }));
    return;
  }

  if (pathname === '/v1/profiles/me') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(mockProfile));
    return;
  }

  if (pathname.startsWith('/v1/interpretations/daily-energy')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(mockDailyEnergy));
    return;
  }

  if (pathname === '/v1/connections') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(mockConnections));
    return;
  }

  if (pathname === '/v1/interpretations/discovery-people') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(mockDiscoveryPeople));
    return;
  }

  if (pathname.includes('/why')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(mockWhy));
    return;
  }

  if (pathname === '/v1/notifications') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify([{ id: 'notif-1', read_at: null }]));
    return;
  }

  // Fallback for other API endpoints
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ success: true, message: 'Mock endpoint' }));
});

supabaseServer.listen(54321, '127.0.0.1', () => {
  console.log('Mock Supabase Gateway listening on http://127.0.0.1:54321');
});

apiServer.listen(8000, '127.0.0.1', () => {
  console.log('Mock Jester API Backend listening on http://127.0.0.1:8000');
});
