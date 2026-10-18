# JESTER Wave 3 — შესრულების ანგარიში

- **Task:** TASK-WAVE3-DISCOVERY
- **თარიღი:** 2026-10-19
- **ტექნიკური სტატუსი:** მოთხოვნილი ლოკალური user loop შემოწმებულია; task გადადის `review`-ში.
- **ვიზუალური სტატუსი:** `FOUNDER_REVIEW_REQUIRED`.
- **Git:** `codex/wave3-swipe-discovery`, Wave 2-ის საწყისი commit `c451f0a`; მიწოდების commit შეიცავს ამ ანგარიშს. Remote შემოწმებულია: `git@github.com:farnai/Jester.git`. ჩვეულებრივი commit/push ავტორიზებულია Wave 3-ის დავალებით; production deployment არ შესრულებულა.

## აღდგენილი კონტექსტი და შენარჩუნებული სამუშაო

შეწყვეტის შემდეგ თავიდან შემოწმდა Git, თავდაპირველი Wave 3 მოთხოვნა და ცხრა ძირითადი ნაწილობრივი ფაილი: API router, interpretation router, photo API, ახალი discovery router, frontend endpoints/types, Home-ის identity deduplication, ProfileImage და migration 030. შემოწმდა task/package დამხმარე ფაილებიც. არც reset, არც არსებული ცვლილებების გადაყრა არ გამოყენებულა.

Wave 2-ის პირადი გალერეა, ექვსი ფოტოს ლიმიტი, მთავარი ფოტო, გადალაგება/წაშლა, ინტერესების შენახვა, ავტორიზაცია და cleanup საზღვარი შენარჩუნებულია. Person Profile-ის დიდი inline markup შეიცვალა ამავე ქცევის სოციალურ პრიორიტეტებზე მორგებული კომპოზიციით; სოციალური გალერეა კვლავ საერთო `SocialIdentity` კომპონენტია.

## განხორციელებული ცვლილებები

**Backend / API:** დაემატა `GET /v1/discovery/people` — 12 ჩანაწერი ნაგულისხმევად, მაქსიმუმ 24, UUID keyset cursor, სახელის literal ძებნა, canonical current-city და საერთო აქტიური ინტერესების ფილტრები. Self/hidden/ორმხრივი block იფილტრება გვერდის შერჩევამდე. სახელით ან bio-თი ადამიანები აღარ იკარგება.

არაცარიელი გვერდი იყენებს სამ batch SELECT-ს. Discover აღარ ითვლის Synastry-ს ან natal chart-ს თითოეული კანდიდატისთვის და აღარ იყენებს demo-viewer fallback-ს. ძველი discovery endpoint ინარჩუნებს list ფორმატს, მაგრამ იყენებს იმავე bounded სერვისს. `compatibility_score=null`; არსებული fresh safe sign-ის გარეშე hook/sign არ გამოიგონება. შედარება რჩება პროფილის გახსნისას არსებულ preview API-ზე.

Photo proxy-ს დაემატა `size=card`: private ავტორიზაცია უცვლელია, WebP მაქსიმუმ 720×900, `private, no-store`. Deck იღებს მხოლოდ მიმდინარე და შემდეგი კანდიდატის ფოტოს. გადმოწერილი next-photo კომპონენტი გამოიყენება მის მიმდინარე ბარათად ქცევისას.

**Frontend:** ახალი `DiscoverSwipeCard`, საერთო `ConnectionActions`, responsive discovery და Person Profile სტილები. მარცხენა swipe/ArrowLeft/Next მხოლოდ შემდეგ ადამიანზე გადადის. მარჯვენა swipe/ArrowRight/Connect ხსნის დადასტურებას; მხოლოდ გაგზავნის ღილაკი ქმნის რეალურ მოთხოვნას. Escape და „ჯერ არა“ არაფერს აგზავნის. ვერტიკალური touch scroll არ ცვლის ადამიანს; reduced-motion გამორთავს გადაადგილების ანიმაციას. ფოტო იცვლება tap-ით ან ღილაკებით.

Desktop აერთიანებს მარცხენა ფილტრებს, ცენტრალურ ბარათსა და მარჯვენა სოციალურ კონტექსტს; ალტერნატიული სია მუშაობს იმავე რეალურ მონაცემებზე. URL ინახავს ფილტრებს, ხედს და აქტიურ ადამიანს, მათ შორის Profile → Discover და browser Back დაბრუნებისთვის.

Connection controls იყენებს არსებულ canonical lifecycle-ს: `pending_out`, `pending_in` მიღება/უარყოფა, `accepted` საუბარი და პროფილზე Why. Likes/Matches ან მუდმივი უარყოფის მოდელი არ დამატებულა.

Person Profile-ის რიგია ფოტო/იდენტობა → bio → ინტერესები → კავშირი → მოკლე preview → დახურული ასტროლოგიური კონტექსტი. მობილურზე კავშირის მოქმედება ქვედა ნავიგაციის ზემოთ რჩება. ასტროლოგია ითხოვება disclosure-ის გახსნისას; identity აღარ ელოდება მის ჩატვირთვას. უცნობს accepted-only Why ბმული არ ეჩვენება.

ზუსტი კონტრაქტი: [DISCOVERY_WAVE3.md](../../../docs/DISCOVERY_WAVE3.md). განახლებულია API, Architecture v1.2 და media დოკუმენტაციის შესაბამისი ნაწილები.

## რეალური ვიზუალური შემოწმება და შესწორება

Chrome/Supabase/FastAPI გამოიყენებოდა route mock-ებისა და ყალბი session-ების გარეშე. საბოლოო სურათები აღებულია ლოკალური production build preview-დან. ფოტოები repository-ის უკვე არსებული, აშკარად მონიშნული QA assets-ია.

პირველ 320×700 შემოწმებაში Discover-ის მოქმედებების ბოლო იყო **722px**, ხოლო ქვედა ნავიგაცია იწყებოდა **647px**-ზე. ფოტო დავაპატარავეთ viewport-ის შესაბამისად და დავამატეთ ავტომატური assertion, რომ ყველა მთავარი მოქმედება ხილულია ნავიგაციის ზემოთ. საბოლოოდ Discover-ის ბოლოა **612px**, ნავიგაცია — **647px**; Person Profile-ის მუდმივი კონტროლები სრულდება **647px**-ზე. 390×844-ზე კონტროლები ასევე ნავიგაციის ზემოთაა. ჰორიზონტალური overflow არც ერთ შემოწმებულ ზომაზე არ არის.

| ზედაპირი | Desktop | Mobile |
| --- | --- | --- |
| Discover | [1440×900](../verification/wave3-discovery/discover-1440x900.png), [1280×800](../verification/wave3-discovery/discover-1280x800.png) | [390×844](../verification/wave3-discovery/discover-390x844.png), [320×700](../verification/wave3-discovery/discover-320x700.png) |
| Person Profile | [1440×900](../verification/wave3-discovery/person-1440x900.png), [1280×800](../verification/wave3-discovery/person-1280x800.png) | [390×844](../verification/wave3-discovery/person-390x844.png), [320×700](../verification/wave3-discovery/person-320x700.png) |
| დადასტურება / touch | — | [კავშირის დადასტურება](../verification/wave3-discovery/connection-confirmation-390x844.png), [reduced motion](../verification/wave3-discovery/touch-reduced-motion.png) |

**Person Profile, წინა/ახალი შედარება:**

| ზომა | Wave 2-ის შენახული baseline | ახალი build, განმეორებული Wave 2 QA სცენარი |
| --- | --- | --- |
| Desktop სრული | [წინა](../verification/wave2-social/person-1440-full.png) | [ახალი](../verification/wave3-discovery/wave2-regression/person-1440-full.png) |
| Mobile სრული | [წინა](../verification/wave2-social/person-320-full.png) | [ახალი](../verification/wave3-discovery/wave2-regression/person-320-full.png) |

ეს არის ერთი და იმავე QA სცენარის ხელახლა შექმნილი, მონიშნული ანგარიშები; UUID-ები განსხვავდება. ძველი არტეფაქტები არ გადაწერილა. [პირველი პრობლემური მობილური კადრი](../verification/wave3-discovery/correction-before-320x700.png) და [საწყისი გაზომვები](../verification/wave3-discovery/correction-before-measurements.json) შენარჩუნებულია correction pass-ის დასამტკიცებლად.

## ტესტების მტკიცებულება

| ბრძანება | შედეგი |
| --- | --- |
| `.venv/Scripts/python.exe -m scripts.run_isolated_regression` | Exit 0 — **371 passed**, ერთჯერად DB clone-ში; [ლოგი](../verification/wave3-discovery/backend-regression.txt) |
| `.venv/Scripts/python.exe -m pytest tests/backend/test_social_profiles.py tests/backend/test_discovery_deck.py -q --tb=short` | Exit 0 — **10 passed**, რეალურ private Storage/DB-ზე მხოლოდ UUID-scoped fixtures; [ლოგი](../verification/wave3-discovery/backend-integration.txt) |
| `npm --prefix frontend run build` | Exit 0 — TypeScript/Vite წარმატებულია; [ლოგი](../verification/wave3-discovery/frontend-build.txt) |
| `node --experimental-strip-types scripts/home-model.test.mjs` | Exit 0 — **8 passed**; [ლოგი](../verification/wave3-discovery/home-tests.txt) |
| `node scripts/discovery-wave3-qa.cjs` | Exit 0 — **12 შემოწმების ჯგუფი**, page errors = 0; [მოქმედებები, მედია და გაზომვები](../verification/wave3-discovery/browser-evidence.json) |
| `node scripts/social-profile-qa.cjs` ახალი `JESTER_QA_OUTPUT` დირექტორიით | Exit 0 — Wave 2-ის **14 flow**, ოთხი viewport, page errors = 0; [შედეგები](../verification/wave3-discovery/wave2-regression/browser-results.json) |
| `git diff --check` | Exit 0 |

Browser სცენარები მოიცავს რეალურ login-ს, ფოტო/tap/button/keyboard/touch მოქმედებებს, მოდალის გაუქმებას, ორ ანგარიშს შორის მოთხოვნა–მიღებას, რეალურ conversation-ის გახსნას, profile დაბრუნებას, ქალაქის/shared-interest ფილტრებს, list/deck, 12-კაციანი pagination boundary-ს, offline failure/retry-ს, empty state-ს და block-ის ორმხრივ 404-ს. Wave 2 განმეორებით ამოწმებს ექვს upload-ს, მეშვიდის შეზღუდვას, primary/reorder/delete-ს, ინტერესების ცვლილებას, logout/login persistence-სა და დაცულ გალერეას.

პირველ ფართო გაშვებაში ერთი არსებული resolver performance assertion ჩავარდა: 50,000 asset-ზე 1.766ms, ზღვარი 1.5ms, პარალელური browser/fixture დატვირთვისას. დატვირთვის გარეშე სრული განმეორებითი გაშვება 371/371-ით დასრულდა; არც threshold და არც resolver შეცვლილა. Build კვლავ აფრთხილებს >500kB bundle-ზე; ეს performance დავალიანება რჩება.

## მიგრაცია და მონაცემთა დაცვა

030-ის გაშვებამდე შემოწმდა: ბოლო გამოყენებული მიგრაცია 029, ახალი ინდექსები არ არსებობდა, 25 პროფილი, ხუთი legacy photo reference და ცარიელი cleanup queue. `npx supabase migration up --local`-მა გამოიყენა მხოლოდ ორი partial index-ის დამატება. მონაცემები/RLS/grants არ შეცვლილა.

დესტრუქციული ძველი ტესტები გაშვებულია მხოლოდ დროებით clone-ში. Browser-ის ექვსივე QA ანგარიში წაიშალა მხოლოდ manifest/email იდენტობის გადამოწმების შემდეგ. დასრულებისას დარჩა იგივე **25 პროფილი და ხუთი legacy reference**, cleanup = 0, QA private objects = 0. [მიგრაციისა და გაწმენდის მტკიცებულება](../verification/wave3-discovery/migration-and-cleanup.json).

## მიღების კრიტერიუმები

- **PASS:** bounded, deterministic pagination/filtering; feed-ში Synastry/recalculation არ იძახება; სამი SQL read დადასტურებულია instrumentation-ით.
- **PASS:** swipe/buttons/keyboard/native touch, reduced motion და დაბრუნებული პოზიცია.
- **PASS:** explicit confirmation, რეალური pending/incoming/accepted და conversation.
- **PASS:** private media, თვითგამორიცხვა, hidden/block privacy და Wave 2 regression.
- **PASS:** ოთხი viewport, რეალური screenshots, წინა/ახალი Person Profile შედარება და correction pass.
- **PASS:** ქართული ანგარიში და branch-ზე მიწოდება; საბოლოო commit იდენტიფიკატორი მოცემულია ჩატის შედეგში.

## დარჩენილი შეზღუდვები

საჯარო გაშვებამდე საჭიროა რეალური 18+ enforcement, report/flag/moderation, account deletion და Architecture v1.2-ის სხვა launch gates. Card ფოტო ყოველ request-ზე იკითხება/მცირდება სერვერზე; persistent thumbnails არ დამატებულა. Legacy public ფოტოები კვლავ ძველი საჯარო ბმულების საზღვრებში რჩება; cleanup worker-ის ავტომატური scheduling არ არსებობს. Cursor არ არის snapshot/ranking. რეალური მომხმარებლის მიერ უკვე ნანახი pixels უკუქცევით ვერ გაუქმდება. Founder-ის ვიზუალური თანხმობა ჯერ არ არის მიღებული.
