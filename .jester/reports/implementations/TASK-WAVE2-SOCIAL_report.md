# WAVE 2 — სოციალური პროფილები, ფოტოები და ინტერესები

## შედეგი და სტატუსი

რეალურ ლოკალურ Supabase/FastAPI გარემოში მომხმარებელი მართავს მაქსიმუმ ექვს
ფოტოსა და ინტერესებს; სხვა ავტორიზებული, არაბლოკირებული მომხმარებელი ხედავს
აღმოჩენად პროფილს. ტექნიკური კრიტერიუმები შემოწმებულია. ამოცანა გადადის `review`-ში.
ვიზუალური დიზაინი Founder-ის მიერ დამტკიცებული არ არის.

## 1. ხელახლა გამოყენებული ფუნქციონალი

- არსებული Supabase Auth/JWT, FastAPI პროფილები, კანონიკური ქალაქის რედაქტორი.
- `interest_categories`, `interests`, `user_interests` და არსებული არჩევის API.
- `is_discoverable`, ორმხრივი ბლოკირება, კავშირის მოთხოვნისა და გადასვლების API.
- უსაფრთხო ასტროლოგიური DTO, პერსონალური ინტერპრეტაციები, Compare Preview და კავშირის შემდეგ Why/ჩატი.
- React Query, AppShell, Noto Sans Georgian და არსებული JESTER ფერის ტოკენები.
- Home-ის დიზაინი შენარჩუნებულია; მის ავატარს მხოლოდ ავტორიზებული მედიის მხარდაჭერა დაემატა.

## 2. მონაცემთა ბაზა და API

- `028_social_profile_photos.sql`: ნორმალიზებული ფოტოები, ექვსი უნიკალური პოზიცია,
  კერძო bucket, მთავარი ფოტოდან `avatar_url`-ის სინქრონიზაცია, cleanup-რიგი,
  არსებული ავატარების ბმულების შენარჩუნება და ინტერესების SELECT RLS.
- `029_gallery_avatar_lifecycle.sql`: სერვერული lifecycle-ნიშანი; ბოლო ფოტოს
  წაშლის შემდეგ OAuth-ის ძველი ავატარის ავტომატური დაბრუნება აღარ ხდება.
- დაემატა ფოტოების სიის, ატვირთვის, სრული დალაგების, წაშლის და ავტორიზებული
  კონტენტის API; ზუსტი კონტრაქტებია `docs/SOCIAL_PROFILE_MEDIA.md`-ში.
- დაემატა `GET /v1/interests/people/{profile_id}` რეალურად საერთო ინტერესების UUID-ებით.
- ინტერესების ჩანაცვლება ახლა ატომურ DB-ტრანზაქციაში სრულდება.

## 3. განხორციელებული ცვლილებები

ME და Person Profile იწყება დიდი ფოტოთი, ინტერაქტიული გალერეით, სოციალური
იდენტობით, ბიოგრაფიითა და ინტერესებით. ასტროლოგიური კონტექსტი მეორეხარისხოვანია.
ME-ში მუშაობს ატვირთვა, მთავარი ფოტოს არჩევა, წინ/უკან დალაგება, წაშლა,
ინტერესების ძებნა/შეცვლა და არსებული პროფილის/ხილვადობის პარამეტრები.

ატვირთვა ამოწმებს MIME-ს, რეალურ ფორმატს, 5 MiB ზომასა და პიქსელების ზღვარს;
ასწორებს ორიენტაციას, აშორებს EXIF/GPS-ს და ქმნის მაქსიმუმ 1600×1600 WebP-ს.
ახალი onboarding-ატვირთვაც ამავე კერძო გალერეას იყენებს.

შეცდომები, ჩატვირთვა, ცარიელი გალერეა და შენახვის სტატუსი რეალურ API-ზეა
დაკავშირებული. Compare Preview-ის არყოფნისას გამოგონილი თანხვედრის ტექსტი მოიხსნა.

## 4. შეცვლილი ფაილები

Backend / დამოკიდებულებები:

- `backend/app/api/router.py`
- `backend/app/profiles/photos.py`
- `backend/app/profiles/router.py`
- `backend/app/interests/models.py`
- `backend/app/interests/router.py`
- `requirements.txt`

Frontend:

- `frontend/src/core/api/client.ts`
- `frontend/src/core/api/endpoints.ts`
- `frontend/src/core/api/types.ts`
- `frontend/src/shared/ui/ProfileImage.tsx`
- `frontend/src/shared/ui/Avatar.tsx`
- `frontend/src/modules/home/HomeElements.tsx`
- `frontend/src/modules/me/MePage.tsx`
- `frontend/src/modules/people/PersonProfilePage.tsx`
- `frontend/src/modules/people/SocialIdentity.tsx`
- `frontend/src/modules/people/social-profile.css`
- `frontend/src/modules/onboarding/BirthDataOnboardingPage.tsx`
- `frontend/src/modules/onboarding/steps/ProfilePhotoStep.tsx`

მიგრაციები / ტესტები / ინსტრუმენტები:

- `supabase/migrations/028_social_profile_photos.sql`
- `supabase/migrations/029_gallery_avatar_lifecycle.sql`
- `tests/backend/test_social_profiles.py`
- `scripts/cleanup_profile_photos.py`
- `scripts/prepare_social_profile_qa.py`
- `scripts/run_isolated_regression.py`
- `scripts/social-profile-qa.cjs`

დოკუმენტაცია / მტკიცებულებები:

- `docs/API.md`, `docs/DATABASE.md`, `docs/SECURITY.md`
- `docs/SOCIAL_PROFILE_MEDIA.md`
- `.jester/tasks/review/TASK-WAVE2-SOCIAL.json`
- ეს ანგარიში და `.jester/reports/verification/wave2-social/`-ის PNG/JSON არტეფაქტები.

## 5. რეალური ტესტების შედეგები

| შემოწმება | შედეგი |
| --- | --- |
| `python -m pytest tests/backend/test_social_profiles.py -q` | exit 0; 7 passed; რეალური ლოკალური DB/Storage |
| `python -m scripts.run_isolated_regression` | exit 0; 371 passed; არსებული სრული ნაკრები ახალ gallery suite-ის გარდა |
| `npm --prefix frontend run build` | exit 0; TypeScript/Vite წარმატებული |
| `node scripts/social-profile-qa.cjs` | exit 0; ნამდვილი HTTP სერვისები, ორი პაროლით ავტორიზებული ანგარიში |
| `git diff --check` | exit 0 |

არსებული რეგრესიული ნაკრების ზოგი fixture ცხრილებს მთლიანად ასუფთავებს.
იგი გაეშვა მხოლოდ დროებით DB-ასლზე; ძირითადი ლოკალური მონაცემები არ განულებულა.
თავდაპირველი იზოლირებული runner-ის restore/fixture routing პრობლემები გასწორდა;
ზემოთ მოცემულია საბოლოო წარმატებული გაშვების შედეგები.

ახალი ტესტები ფარავს ძველ ერთ ავატარს, უფოტო პროფილს, ექვსი ფოტოს ატვირთვას,
მეშვიდის 409-ს, პარალელურ ატვირთვებს, მთავარი ფოტოს შეცვლას, დალაგებას,
წაშლას, ხელახალ წაკითხვას, სხვა მომხმარებლის ცვლილების უარყოფას,
ანონიმურ/ბლოკირებულ/დამალულ წვდომას და ინტერესების RLS-ს.

შეფერხების ტესტებში Storage-ის წარუმატებლობა **განზრახ არის ინექცირებული**:
ატვირთული ობიექტის შემდეგ შეცდომა იწვევს კომპენსაციას; წაშლისას Storage-ის
შეცდომა ტოვებს cleanup-ჩანაწერს, მაშინ როცა ფოტო API-დან უკვე მიუწვდომელია.
შემდგომი retry რეალურად შლის Storage-ის ობიექტს. ეს შემთხვევები არ არის
წარმოდგენილი როგორც ბუნებრივად მომხდარი ინფრასტრუქტურული გათიშვები.

ბრაუზერში შემოწმდა reload და logout/login-ის შემდეგ ფოტოებისა და ინტერესების
შენარჩუნება, ორი ანგარიშის ორი რეალურად საერთო ინტერესი, სხვისი პროფილი,
ბლოკირებული მდგომარეობა და Home-ზე ნავიგაცია. Auth/onboarding-ის არსებული
რეგრესიული ტესტები სრული ნაკრების ფარგლებში წარმატებულია.

## 6. Desktop/mobile ეკრანები და კორექცია

ყველა ზომაზე შემოწმდა ME და Person Profile: 1440×900, 1280×800, 390×844, 320×700.
`browser-results.json`: ყველა შემთხვევაში `scrollWidth == width`, ფოტოები
ჩატვირთულია, გამოყენებულია Noto Sans Georgian, JavaScript page errors — 0.

პირველ გავლაზე ME-ის 320px ვერსიაში ქვედა ღილაკები 14px-ით გადადიოდა საზღვარს.
დაემატა flex-wrap და განმეორებით ყველა ზომამ გაიარა შემოწმება. ფინალური
ეკრანები ხელახლა გადაიღო ნამდვილმა ბრაუზერმა.

- [ME — desktop](../verification/wave2-social/me-1440x900.png)
- [ME — 1280](../verification/wave2-social/me-1280x800.png)
- [ME — 390](../verification/wave2-social/me-390x844.png)
- [ME — 320](../verification/wave2-social/me-320x700.png)
- [Person — desktop](../verification/wave2-social/person-1440x900.png)
- [Person — 1280](../verification/wave2-social/person-1280x800.png)
- [Person — 390](../verification/wave2-social/person-390x844.png)
- [Person — 320](../verification/wave2-social/person-320x700.png)
- [უფოტო პროფილი](../verification/wave2-social/empty-profile.png)
- [ბლოკირებული პროფილი](../verification/wave2-social/blocked-profile.png)

სურათებზე ჩანს მკაფიოდ მონიშნული QA პროფილები და repository-ის დემო assets.
ისინი რეალური მომხმარებლების ფოტოების მტკიცებულებად არ არის წარმოდგენილი.
შემოწმების შემდეგ წაიშალა მხოლოდ ამ ამოცანის ორი QA ანგარიში და მათი კერძო
ფოტოები. არსებული ანგარიშები და ავატარები შენარჩუნებულია.

## 7. Storage და კონფიდენციალურობა

ახალი bucket კერძოა. კლიენტს gallery/cleanup ცხრილებისა და private Storage-ის
პირდაპირი წვდომა არ აქვს. მედიის ყოველი ახალი მოთხოვნა გადის ავტორიზაციას,
აღმოჩენადობისა და ორმხრივი ბლოკირების შემოწმებას. პასუხია `private, no-store`;
საჯარო ან signed URL ახალი ფოტოსთვის არ გაიცემა.

მთავარი ფოტო განისაზღვრება მხოლოდ რიგით; `avatar_url` მისგან მიიღება.
უკან დაბრუნებული OAuth-ავატარისა და კონფლიქტური ძველი avatar-write-ის შემთხვევები
ტესტირებულია. დაბადების მონაცემები, ზუსტი ასტროლოგია და JWT-ის საწარმოო რეჟიმი არ შეცვლილა.

## 8. დარჩენილი შეზღუდვები

- ძველი საჯარო avatar URL-ები და ადრე ჩამოტვირთული ასლები RLS-ით ვერ გაუქმდება.
  ძველი reference-ის წაშლა მის საჯარო ობიექტს არ შლის; ისტორიული მედიის
  სრულად კერძო მოდელზე გადატანა ცალკე სამუშაოა.
- cleanup-რიგის retry-ბრძანება არსებობს; ავტომატური scheduler ამ ცვლილებას არ დაუყენებია.
- GIF ინახება პირველ კადრად; ფოტოს ხელით crop-editor და moderation workflow არ დამატებულა.
- პროდუქტის დოკუმენტში ინტერესების ზედა ზღვარი 7-ია, თუმცა მოქმედ API/UI-ში
  ეს ზღვარი არ იყო დანერგილი. შენარჩუნებულია მოქმედი წესი: 0 ან მინიმუმ 3.
  ზედა ზღვრის შეთანხმება/გასწორება ცალკე ნაბიჯია.
- build-ს რჩება დიდი bundle-ის გაფრთხილება; ეს ამ ამოცანაში არ შეცვლილა.
- 18+ სრული enforcement, გადახდები, recommendation algorithm და production deployment არ შესრულებულა.
- ვიზუალური დამტკიცება კვლავ Founder-ის გადაწყვეტილებაა.

## 9. Git

საწყისი სამუშაო ხე სუფთა იყო. შემოწმებულია `origin`: `farnai/Jester`.
მომხმარებლის დავალება ნებადართულად აცხადებს commit/push-ს წარმატებული
შემოწმების შემდეგ. მიწოდების branch: `codex/wave2-social-profiles`.
commit/push-ის საბოლოო შედეგი და commit ID მოცემულია თანმხლებ საბოლოო პასუხში.
Force-push და production deployment არ გამოიყენება.

## 10. შემდეგი MVP ნაბიჯი

Founder-ის ვიზუალური შეფასების შემდეგ — რეალური Discover-ის eligibility/privacy
ინტეგრაცია: დასრულებული onboarding, ფოტო და აღმოჩენადობა, ბლოკირების სრული
დაცვით; არსებული დამტკიცებული წესების ფარგლებში. საჯარო MVP-მდე ცალკე საჭიროა
18+ enforcement და მედიის moderation/cleanup-ის ოპერაციული უზრუნველყოფა.

## Acceptance

ექვსი ფოტო/მთავარი/რიგი/წაშლა — PASS; ავტორიზაცია/ბლოკირება — PASS;
ძველი ავატარების შენარჩუნება — PASS; ინტერესები/საერთო ინტერესები — PASS;
რეალური სერვისები/ოთხი viewport — PASS; ქართული ანგარიში — PASS.
ტექნიკური სტატუსი: `review`. ვიზუალური სტატუსი: Founder review pending.
