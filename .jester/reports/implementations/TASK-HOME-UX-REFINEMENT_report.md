# Home — UX და ვიზუალური დახვეწა

Branch: `codex/home-editorial-reference`. სტატუსი: review; საბოლოო ვიზუალური დამტკიცება Founder-ს ეკუთვნის.

## კონკრეტული ცვლილებები

- `frontend/src/modules/home/HomePage.tsx`: ცარიელი connection-tag აღარ იკავებს ბარათის ადგილს; ინსაითის მეორეხარისხოვანი ფუნქციები ერთ disclosure-შია. რეალური accepted/incoming რაოდენობები გადაეცემა Hero-ს მხოლოდ connections-ის წარმატებული პასუხისას.
- `frontend/src/modules/home/HomeEditorial.tsx`: საკუთარი წრისა და შემოსული მოთხოვნების ბმულები, მოკლე აღწერა, საუბრის CTA „აირჩიე საუბარი“ და შესაბამისი ინსტრუქცია. ახალი API ველები არ დამატებულა.
- `frontend/src/modules/home/homeEditorial.css`: სახელისა და მეტამონაცემების ფიქსირებული ცარიელი სიმაღლეების მოცილება; კომპაქტური ფოტოები და ბარათები; უფრო მსხვილი მობილური ტექსტი; ინსაითის ერთი მკაფიო მთავარი მოქმედება; მხოლოდ Home-ზე გაუმჭვირვალე ქვედა ნავიგაცია და 48px სამიზნეები.
- `scripts/home-editorial-qa.cjs`: დამატებული დეტალების გახსნა/დახურვისა და კოპირების/წარმოშობის კონტროლების ხელმისაწვდომობის შემოწმება.
- `docs/HOME_EXPERIENCE.md`: განახლებული პერსონალური კონტექსტისა და disclosure-ის აღწერა.
- `.jester/tasks/review/TASK-HOME-UX-REFINEMENT.json`: ფარგლები და მიღების კრიტერიუმები.

## შედარება

საწყისი ეკრანებია `.jester/reports/verification/home-polish/`; ახალი ეკრანებია `.jester/reports/verification/home-refinement/`.

360px Discovery-ზე ადრე ერთი მაღალი რიგი დომინირებდა; ახლა მეორე რიგის მნიშვნელოვანი ნაწილიც ჩანს. სახელებსა და აღწერებს შორის დიდი სიცარიელე შემცირდა. ინსაითი აღარ აჩვენებს რამდენიმე კონკურენტ მოქმედებას ერთდროულად: ტექსტის სრულად გახსნა მთავარია, დამატებითი ფუნქციები რჩება დეტალებში. Desktop-ზე ინსაითის სიმაღლის შემცირებამ კავშირების სექციასთან ბალანსი გააუმჯობესა. ნავიგაციის უკან ტექსტი აღარ ჩანს.

შედარება ვიზუალურია: რეალური ყოველდღიური ტექსტი და პროფილების შემადგენლობა შეიძლება განსხვავდებოდეს, ამიტომ ეს pixel-perfect ან იდენტური მონაცემების ბენჩმარკი არ არის.

## შემოწმებები

- `node --experimental-strip-types --test scripts/home-model.test.mjs scripts/messaging-model.test.mjs` — exit 0, 15/15.
- `npm --prefix frontend run build` — exit 0; არსებული დიდი JS chunk-ის გაფრთხილება რჩება.
- `JESTER_QA_OUTPUT=.jester/reports/verification/home-refinement node scripts/home-editorial-qa.cjs` — exit 0, 7 შემაჯამებელი შემოწმება, რეალური Chrome/Auth/API.
- 1440, 1280, 768, 390, 360px: overflow არ არის; მობილურის ბოლო პროფილის მოქმედება ნავიგაციით არ იფარება; რეალური კავშირი/დაცული ფოტო/reload, ნავიგაცია და error/retry მუშაობს.
- ინსაითის disclosure ხსნის კოპირების და provenance-ის კონტროლებს და იკეცება კონტენტის დაკარგვის გარეშე.
- `git diff --check` — exit 0.

ლოგები: `home-refinement/tests.log`, `build.log`, `browser-evidence.json`. ეკრანები: `home-1440.png`, `home-390-viewport.png`, `discovery-360-viewport.png`, `footer-360-viewport.png` და სხვა ზომები იმავე საქაღალდეში.

მხოლოდ manifest-ით დადასტურებული დროებითი QA ანგარიშები და მათი მედია წაიშალა. არსებული მომხმარებლები არ გადატვირთულა. API, ავტორიზაცია, პირადი მედიის გზა, backend, routing და მონაცემთა სქემა უცვლელია. წინარე დაუკომიტებელი სამუშაო შენარჩუნებულია. Commit, push და deploy არ შესრულებულა.
