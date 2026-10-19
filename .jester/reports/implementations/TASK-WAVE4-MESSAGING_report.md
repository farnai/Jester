# Wave 4 — Connections & Messaging MVP: შესრულების ანგარიში

**ტექნიკური სტატუსი: VERIFIED / REVIEW.** ორი რეალური, ლოკალურად ავტორიზებული QA მომხმარებელი გადის ციკლს: Discover → მოთხოვნა → მიღება → საუბარი → reload/reconnect → გაგრძელება → ბლოკირება. Founder-ის ვიზუალური თანხმობა ცალკე რჩება. საჯარო deployment არ შესრულებულა.

## აღდგენილი მდგომარეობა და ფარგლები

- საწყისი commit: `28e99fa`, Wave 3; Wave 2-ის ისტორია შენარჩუნებულია. თავდაპირველად სამუშაო ხე სუფთა იყო — შეწყვეტილ მცდელობას კოდი არ ჰქონდა შეცვლილი.
- ადრე უარყოფილი ბრენჩის შექმნა შემოწმდა და შემდგომი ნებადართული ოპერაციით შეიქმნა `codex/wave4-connections-messaging`. Approval-ის კონტროლი არ შემოვლილა.
- შესრულებისას დაგროვილი ნაწილობრივი ცვლილებები შენარჩუნდა. Git reset, მონაცემების reset ან ისტორიის გადაწერა არ მომხდარა.
- Discover და Person Profile არ გადაკეთებულა. შეიცვალა მხოლოდ desktop context-ის დუბლირება, კავშირის შესაბამისი ტექსტები, ერთჯერადი swipe მინიშნება და mobile header spacing. პროფილის მთავარი connection მოქმედება შენარჩუნებულია.

## უსაფრთხოების შესწორებები

1. **P0 — ბლოკის უკანონო მოხსნა:** დაბლოკილი მონაწილე ვეღარ იყენებს `remove`-ს ბლოკის გასასუფთავებლად ან `block`-ს `blocked_by`-ის მისათვისებლად. მის ყველა transition-ზე პასუხია privacy-safe `404`. ბლოკის ავტორის `remove` იძლევა `400`; მხოლოდ მისი explicit `unblock` გადადის `removed` მდგომარეობაში. განმეორებული საკუთარი `block` იდემპოტენტურია.
2. **დამატებითი პირდაპირი DB გზა:** კლიენტის connection INSERT პოლიტიკა მხოლოდ `pending` მოთხოვნას უშვებს; `accepted`-ის გაყალბებით ჩატი ვეღარ გაიხსნება. პირდაპირი UPDATE/DELETE კვლავ აკრძალულია.
3. **Send/block შეჯახება:** API და DB INSERT trigger კეტავს canonical connection row-ს. რეალური კონკურენტული ტესტი ადასტურებს, რომ ბლოკირების lock-ზე მომლოდინე პირდაპირი შეტყობინების INSERT ბლოკის commit-ის შემდეგ უარყოფილია და შეტყობინება არ ინახება.
4. **Unread privacy:** read pointer ცალკე, owner-only `conversation_reads` ცხრილშია. კლიენტს აქვს მხოლოდ შესაბამისი SELECT; backend წერს ავტორიზაციის შემდეგ. ცხრილი Realtime-ში არ ქვეყნდება. სხვა მონაწილეს არ გადაეცემა read receipt ან წაკითხვის დრო.
5. შეტყობინებების DTO არ შეიცავს birth data-ს, raw astrology-ს ან nonce-ს. დამალული პროფილის სახელი/ავატარი არის `null`; ფოტო კვლავ დაცული media API-დან იტვირთება.

მტკიცებულებები: [მიგრაცია/RLS](../verification/wave4-messaging/migration-security.json), [ინტეგრაციის შედეგი](../verification/wave4-messaging/integration-tests.log), `tests/backend/test_messaging_wave4.py`.

## განხორციელებული API კონტრაქტები

| მოქმედება | კონტრაქტი |
|---|---|
| Inbox | `GET /v1/conversations`: რეალური მონაწილე, nullable name/avatar, ბოლო შეტყობინება, `last_activity_at`, რეალური `unread_count`; მხოლოდ აქტიური კავშირები, აქტივობის კლებადი რიგით |
| საუბრის შექმნა/აღდგენა | `POST /v1/conversations {target_user_id}`; canonical row lock და ტრანზაქცია გამორიცხავს კონკურენტულ დუბლირებას |
| ისტორია | `GET /v1/conversations/{id}/messages/page?limit=30&before=<UUID>` → `{items,next_cursor}`; მაქსიმუმ 100, exclusive cursor, გვერდში ქრონოლოგიური რიგი |
| ძველი history endpoint | `/messages` ინარჩუნებს list ფორმას, მაგრამ ახლა bounded-ია: default 30, max 100 |
| გაგზავნა/retry | `POST .../messages {body,client_nonce?}`; იგივე nonce/text აბრუნებს პირვანდელ შეტყობინებას; განსხვავებული ტექსტი იმავე nonce-ით → `409`; ტექსტი 1–2000 სიმბოლო |
| წაკითხვა | `PATCH .../read {last_read_message_id}`; pointer მხოლოდ წინ მიდის; პასუხში რეალური დარჩენილი unread რაოდენობაა |
| გაუქმებული/დაბლოკილი კავშირი | დეტალები, ისტორია, გაგზავნა და read მოქმედება → `404`; Inbox-იდან საუბარი გამორიცხულია |
| Starters | არსებული accepted-only `GET /v1/people/{id}/why`; არჩევანი ავსებს რედაქტირებად draft-ს, ავტომატურად არ აგზავნის |

დეტალები: [API](../../../docs/API.md), [Messaging MVP](../../../docs/MESSAGING_WAVE4.md). ახალი `/starters` endpoint, read-only archive და 48-საათიანი cooldown არ გამოცხადებულა განხორციელებულად.

## ინტერფეისი და სინქრონიზაცია

- Inbox იყენებს conversations-list backend-ს; აქვს loading, empty, error/retry და რეალური unread badge.
- Connections მართავს შემოსულ, გაგზავნილ, მიღებულ და საკუთარი ბლოკის მდგომარეობებს. Decline/cancel/remove/unblock რეალურად ინახება.
- Supabase Realtime მოვლენები აახლებს ავტორიზებულ HTTP query-ებს; raw payload პირდაპირ არ ემატება ჩატის cache-ს. ID-ით გაერთიანება იცავს დუბლირებისგან.
- Re-subscription, online და visibility ცვლილებები აღადგენს მდგომარეობას. Foreground 5-წამიანი შემოწმება ფარავს დაკარგულ connection მოვლენებს, მათ შორის დაბლოკილი მომხმარებლისთვის RLS-ით დაფარულ row-ს. ისტორიის fallback განახლება 15 წამია.
- Realtime invalidation აღარ აუქმებს მიმდინარე older-page მოთხოვნას. რეალურ QA-ში აღმოჩენილი ეს შეჯახება გასწორდა.
- ქსელის დაკარგვისას draft და retry nonce ინარჩუნება; metadata refresh-ის შეცდომა უკვე ჩატვირთულ ჩატს აღარ ანაცვლებს ცარიელი ეკრანით. უსაფრთხოების `403/404` კვლავ დაუყოვნებლივ მალავს ჩატს.
- შემოწმებულია 1440, 1280, 390 და 320px ზომები; დამატებით 320×440 შემცირებული viewport. Composer არ ფარავს ქვედა ნავიგაციას; გაგზავნის ღილაკი მინიმუმ 44px-ია. რეალურ ტელეფონზე სისტემური keyboard შემოწმება ცალკე დარჩა.

## ტესტები და მტკიცებულება

| შემოწმება | შედეგი |
|---|---|
| საწყისი სრული იზოლირებული რეგრესია | **375 passed**, 23.41s, exit 0 |
| უსაფრთხოების race ტესტის დამატების შემდეგ სრული იზოლირებული რეგრესია | **376 passed**, 25.84s, exit 0 |
| ბოლო Wave 2/3/4 მიზნობრივი backend + Storage ინტეგრაცია | **15 passed**, 13.85s, exit 0; აქედან Wave 4 — 5 |
| Messaging frontend model tests | **6 passed** |
| Home frontend regression tests | **8 passed** |
| Production frontend build | **PASS**; დარჩა Vite-ის >500kB chunk გაფრთხილება |
| Wave 4 რეალური Chrome QA | **13 სცენარი**, 0 uncaught application error |
| Wave 3 რეალური Chrome რეგრესია | **12 სცენარი**, 0 uncaught application error; native touch + reduced motion ჩათვლით |
| `git diff --check` | **PASS** |

[შეჯამება და ზუსტი ბრძანებები](../verification/wave4-messaging/verification-summary.json), [375/376 შესრულების ჩანაწერი](../verification/wave4-messaging/regression-history.txt), [build log](../verification/wave4-messaging/build.log), [frontend tests](../verification/wave4-messaging/frontend-tests.log), [Home tests](../verification/wave4-messaging/home-tests.log), [Wave 4 browser evidence](../verification/wave4-messaging/evidence.json), [Wave 3 browser evidence](../verification/wave4-messaging/wave3-regression/browser-evidence.json).

QA შესრულდა რეალური Supabase Auth login-ით და backend-ით, mocked business პასუხებისა და გამოგონილი session-ების გარეშე. Offline რეჟიმი გამოიყენებოდა მხოლოდ ქსელის შეცდომის განზრახ შესაქმნელად. WebSocket მტკიცებულება ინახავს მიღებული Realtime მოვლენების ტიპებს, საიდუმლო token-ების გარეშე.

## მიგრაცია და ლოკალური მონაცემები

031 პირველად გამოყენებამდე შემოწმდა ლოკალური გარემო, ბოლო მიგრაცია 030 და არსებული მონაცემები. 031 არის additive: ძველი შეტყობინებები არ გადაწერილა; `NOT VALID` body constraint ძველ ჩანაწერებს ინარჩუნებს და ახალ ჩაწერებს ამოწმებს. დასრულებისას ledger-ში 031-ის **ერთი ჩანაწერი** დადასტურდა; მიგრაცია ხელმეორედ არ გაშვებულა.

ყველა destructive legacy fixture შესრულდა disposable clone-ზე. QA ანგარიშები წაიშალა მხოლოდ manifest-ის ID/email გადამოწმების შემდეგ. საწყისი და საბოლოო რაოდენობები ემთხვევა: **25 profile, 1 conversation, 3 message, 5 connection**; private-media cleanup queue — **0**. ეს არის რაოდენობებისა და მიზნობრივი cleanup-ის შემოწმება, არა ყველა ძველი row-ს byte-for-byte hash შედარება. [მონაცემების შენარჩუნების მტკიცებულება](../verification/wave4-messaging/data-preservation.json).

## რეალური ეკრანის სურათები

| ზედაპირი | მტკიცებულება |
|---|---|
| Chat desktop | [1440px](../verification/wave4-messaging/chat-1440.png), [1280px](../verification/wave4-messaging/chat-1280.png) |
| Chat mobile | [390px](../verification/wave4-messaging/chat-390.png), [320px](../verification/wave4-messaging/chat-320.png), [შემცირებული viewport](../verification/wave4-messaging/chat-320-reduced-viewport.png) |
| Inbox | [desktop unread](../verification/wave4-messaging/inbox-unread-desktop.png), [390px](../verification/wave4-messaging/inbox-390.png), [320px](../verification/wave4-messaging/inbox-320.png) |
| Connections / Block | [desktop](../verification/wave4-messaging/connections-desktop.png), [390px](../verification/wave4-messaging/connections-390.png), [ბლოკი](../verification/wave4-messaging/blocked-390.png), [მიუწვდომელი ჩატი](../verification/wave4-messaging/chat-blocked-320.png) |
| Discover და Person Profile | [კავშირის შესაბამისი Discover](../verification/wave4-messaging/discover-connected-desktop.png), [Wave 3 regression არტეფაქტები](../verification/wave4-messaging/wave3-regression/) |

## შეცვლილი ფაილები

ყველა კოდის, დოკუმენტის, ტესტისა და screenshot-ის ზუსტი სია: [changed-files.txt](../verification/wave4-messaging/changed-files.txt).

- Backend: `backend/app/connections/{models,router}.py`, `backend/app/conversations/{models,router}.py`.
- Database: `supabase/migrations/031_messaging_mvp.sql`.
- Frontend contracts/sync: `frontend/src/core/api/{endpoints,types}.ts`, `frontend/src/core/realtime/SocialSync.tsx`, `frontend/src/shared/AppShell.tsx`.
- UI: `frontend/src/modules/chat/{ChatPage.tsx,messaging.css,messagingModel.ts}`, `frontend/src/modules/messages/MessagesPage.tsx`, `frontend/src/modules/connections/ConnectionsPage.tsx`, `frontend/src/modules/people/ConnectionActions.tsx`, `frontend/src/modules/discover/{DiscoverPage.tsx,DiscoverSwipeCard.tsx,discovery.css}`.
- Verification: `tests/backend/{test_conversations,test_messaging_wave4}.py`, `scripts/{prepare_social_profile_qa.py,discovery-wave3-qa.cjs,messaging-wave4-qa.cjs,messaging-model.test.mjs}`. Wave 3 script-ში შეიცვალა მხოლოდ output directory-ის override და ავტომატურ online-resync-თან შესაბამისი retry assertion.
- დოკუმენტაცია: `docs/{API,DATABASE,SECURITY,FRONTEND_CAPABILITY_SPECIFICATION,MESSAGING_WAVE4}.md`; შესაბამისი `.jester` task/report/evidence.

## დარჩენილი MVP შეზღუდვები და მიწოდება

- **საჯარო გაშვების პირობები:** რეალური 18+ enforcement, reporting/moderation და ოპერაციული abuse response ამ ტალღაში არ დასრულებულა.
- Founder visual approval და ფიზიკურ iOS/Android მოწყობილობებზე keyboard/background-resume acceptance ცალკეა.
- არ არის attachments, typing indicators, peer read receipts, persistent offline outbox, message push notifications ან read-only disconnect archive.
- Foreground polling და არსებული დიდი frontend bundle MVP-ის პრაქტიკული შეზღუდვებია; ამოცანა არ გაფართოებულა სხვა მოდულების ოპტიმიზაციაზე.
- Git მიწოდების სამიზნეა `farnai/Jester`, ბრენჩი `codex/wave4-connections-messaging`; commit hash მიეთითება საბოლოო მიწოდების პასუხში. Main-ზე merge ან საჯარო deploy არ შესრულებულა.

**Task status: review — ტექნიკური შემოწმება დასრულებულია; Founder-ის ვიზუალური დამტკიცება დამოუკიდებელია.**
