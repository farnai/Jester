# JESTER — Color & Design System v1

**სტატუსი:** Founder-ის მიერ შერჩეული ვიზუალური მიმართულების საფუძველზე მომზადებული დიზაინ-სისტემის პირველი იმპლემენტაციური სპეციფიკაცია (2026-10-15).  
**მნიშვნელოვანი გამიჯვნა:** ეს HEX კოდები არის შერჩეული პირველი mockup-ის ინტერპრეტაცია და სტანდარტიზებული საწყისი მნიშვნელობები, არა პიქსელურად ამოღებული ფერები. დიზაინზე ზუსტი ფერების საბოლოო დადასტურება ხდება რეალურ UI-ზე.  
**Scope:** Jester აპლიკაცია; **არ ვრცელდება** JesterAICompany-ის დამოუკიდებელ ბრენდინგზე.  
**Source precedence:** Founder-ის მიმდინარე მითითება → დამტკიცებული Product Foundation → დამტკიცებული დიზაინის წესები → სტრატეგიული მარკეტინგი → Design Exploration → მიმდინარე UI. ისტორიული დოკუმენტები თავიდან უნდა გადამოწმდეს Jester რეპოზიტორიაში. 

## 1. ბრენდი და პრინციპი

JESTER = People Discovery & Relationship Intelligence; არა dating clone, არა horoscope ან AI dashboard.  
ძირითადი მოსაზრება: **They show the match. JESTER explains the connection.**  
გამოცდილების გზა: **ME → YOU → US → MORE PEOPLE**.  
ტონი: დაკვირვებული, მახვილგონივრული, თბილი, ოდნავ სარკასტული; არა დამცინავი.  
არჩეული ვიზუალი: თბილი, მსუბუქი light UI, ერთი მკაფიო **carrot orange** მთავარი აქტიური ფერად, ინტელექტუალური მუქი ტექსტი, თბილი ღია ზედაპირები და დოზირებული სალბისფერი (sage) დამხმარედ.

## 2. ძირითადი პალიტრა

| როლი | Token | HEX | განკუთვნილი გამოყენება |
|---|---|---|---|
| მთავარი აქტიური | brand.orange-500 | #FF7A2F | CTA, active navigation, active tabs, focus emphasis |
| მთავარი hover | brand.orange-600 | #E9681F | hover, interaction states |
| ძირითადი რბილი | brand.orange-100 | #FFE7D7 | შერჩეული pill, მსუბუქი ფონი |
| აპლიკაციის ფონი | surface.canvas | #FAF7F2 | მთავარი canvas |
| Card | surface.card | #FFFFFF | ბარათები/ფორმები |
| ალტერნატიული ზედაპირი | surface.alt | #F3EEE6 | სექციები, მიკრო-ბლოკები |
| მთავარი ტექსტი | text.primary | #222630 | სათაურები, body |
| მეორეული ტექსტი | text.secondary | #6A716F | აღწერები, დამხმარე ტექსტი |
| მშვიდი დამატებითი ფერი | support.sage-400 | #95A686 | იშვიათი იკონები, გრაფიკული აქცენტები |
| Sage რბილი ფონი | support.sage-100 | #E8EFE2 | მშვიდი insight და info ფონები |
| Sage შიგნით ტექსტი | support.sage-ink | #4B6242 | კონტრასტული ტექსტი sage ფონზე |
| თბილი ინსაითის ფონი | accent.peach-soft | #FBEEE7 | Jester insights, რბილი ბანერები |
| საზღვარი | border.soft | #E6E0D7 | დეკორატიული გამყოფები |
| ფორმის საზღვარი | border.interactive | #8F8A83 | კონტროლი, სადაც 3:1 კონტრასტია საჭირო |

## 3. გამოყენების წესები

- **Carrot orange** მხოლოდ მთავარ მოქმედებებზე, შერჩეულ მდგომარეობებზე, მთავარ მეტრიკებსა და რამდენიმე გამორჩეულ Jester insight-ზე. არ შევღებოთ ყველა card, icon და chart.
- **Sage** არა მეორე primary; არ გამოიყენოთ მთავარ CTA-ზე. კარგია მსუბუქი საინფორმაციო ბლოკებისა და მეორეული მონიშნვებისთვის.
- **Peach** მცირე დოზით, არა dating-რომანტიკული აღქმისთვის. რბილი insight cards.
- **შინაარსობრივი ფერები** (success/error/warning/info) დამოუკიდებელია ბრენდისგან. შეცდომა მხოლოდ ფერით არ გამოვხატოთ.
- **ტიპოგრაფია:** ქართულად Noto Sans Georgian ან პროექტში უკვე დამტკიცებული შრიფტი, ლათინური განსხვავებული საჭიროების მიხედვით. ტექსტი ქართულ UI-ში, რას შეიძლება რეალურად გაუშვას სისტემა ამის მიხედვით.
- **ელემენტის მდგომარეობები:** default, hover, focus-visible, active, disabled, loading, invalid, success; dark mode არ დავამატოთ ამ ეტაპზე მოთხოვნის გარეშე.

## 4. ხელმისაწვდომობა და კონტრასტი — კრიტიკული შესწორება

მნიშვნელოვანი: `#FF7A2F` ფონზე **თეთრი ჩვეულებრივი ტექსტი WCAG AA-ის 4.5:1 მინიმუმს ვერ აღწევს**. ამიტომ წინა პასუხში ნაჩვენები თეთრი ტექსტის primary button მაგალითი გამოყენებისთვის არასწორი იყო.

| წყვილი | კონტრასტი | რეკომენდაცია |
|---|---:|---|
| ნარინჯისფერი / თეთრი ტექსტი | 2.60:1 | არ გამოიყენოთ მცირე ტექსტისთვის |
| ნარინჯისფერი / მუქი ტექსტი | 5.82:1 | ძირითადი CTA |
| Hover / მუქი ტექსტი | 4.66:1 | hover ტექსტი |
| მუქი ნარინჯისფერი / თეთრი | 6.47:1 | თეთრი ტექსტის ალტერნატივა |
| მეორეული ტექსტი / თეთრი | 4.99:1 | პარაგრაფები |
| სქელი border / თეთრი | 3.43:1 | ველი/კონტროლი |

**დიზაინ წესი:** ნათელ `#FF7A2F` ღილაკზე `#222630` მუქი ტექსტი გამოიყენეთ (≈5.82:1). თუ საჭიროა აუცილებლად თეთრი ტექსტი, იმ ვარიანტისთვის ფონად გამოიყენეთ `#9E4215` (≈6.47:1), რაც ცალკე ალტერნატიული ქმედებითი ფერია, არა მთავარი ბრენდის ფერის ჩანაცვლება. UI-ს რეალური screenshot-ებით გადამოწმდეს.

- ჩვეულებრივი ტექსტი: მინ. 4.5:1; დიდი ტექსტი: მინ. 3:1; საჭირო UI კომპონენტის კონტური/იკონები: მინ. 3:1 შესაბამის გარემოში.
- focus-visible მკაფიოდ ჩანდეს და არ იყოს მხოლოდ ფერის მცირე სხვაობა.
- სტატუსი არ დაინიშნოს მხოლოდ ფერით; Icon/ტექსტი/label თან ახლდეს.
- ოპტიკურად მონიშნული სურათები mockup-ია და არა ფუნქციური, გამართული UX-ის მტკიცებულება.

## 5. კომპონენტების წესები

| კომპონენტი | Foundation | Active / Emphasis | განმარტება |
|---|---|---|---|
| Primary Button | `orange-500` + **მუქი ტექსტი** | hover `orange-600`, focus `orange-800` | min height 44px, keyboard focus |
| Secondary Button | white/card + border | მუქი ტექსტი | არ ეჯიბრება primary-ს |
| Text Input | `surface.card` | border.interactive, focus orange-800 | label უცვლელად ხილული, error state |
| Chip | `surface.alt` | `orange-100` + `orange-900` | active/inactive მკაფიო |
| Tabs / Navigation | neutrals | orange underline/icon | მხოლოდ ერთი selected ელემენტი |
| Standard Card | white/card | neutral border | ბარათებს არა ზედმეტი shadow |
| Insight Card | peach-soft ან sage-100 | foreground text primary/sage-ink | არასდროს ექცეს dating card-ად |
| Compare Bar | orange primary + neutral track | რიცხვითი label | ფერის გარეშე მნიშვნელობა გასაგები |
| Chat Bubble | თბილი ღია neutral | user ≠ incoming განსხვავება ტექსტით/განლაგებით | არა აუცილებელი ლურჯი bubble |
| Toast / Alert | semantic background | შესაბამისი semantic text | icon + ვერბალური ტექსტი |

## 6. ეკრანების დანიშნულება და ვიზუალური იერარქია

- **Home / Today’s Energy:** მთავარი ინსაითი; თბილი ნეიტრალური canvas, დაბალი კონტრასტის ინფორმაციული ბლოკები, მცირე orange signature.
- **Discover:** ფოტოზე ორიენტირებული კანდიდატების Swipe Deck და orange active filter; ინტერაქციის პრინციპი დამტკიცებულია, Wave 3-ის ვიზუალური შეფასება ჯერ მოლოდინშია. Home-ზე დასაშვებია ჰორიზონტალური, შეხებაზე მორგებული პროფილების კარუსელი სრული Discover ინტერაქციების გარეშე. მობილურზე ავარიდოთ თავი რამდენიმე კანდიდატის ბარათის ვერტიკალურ წყობას; ინდივიდუალური პროფილი შეიძლება ვერტიკალურად იხვეოდეს.
- **Person / Why:** ფოტოს ფონზე ტექსტის კონტრასტისა და safe overlay-ის შემოწმება; ღირებულება განმარტებაა, არა მარტო match პროცენტი.
- **Profile:** მშვიდი tags, მაღალი კითხვადობა, მკაფიო Connection action; ინფორმაცია არ გახდეს მხოლოდ რომანტიკული.
- **Compare / US:** ქულა + რეალური ნარატიული insight; მხოლოდ პროცენტის სტილის შეცვლა არ კმარა. Orange ნიშნები + neutral/sage მხარდაჭერა.
- **Conversation starters & Messages:** მოქმედებითი UI ნეიტრალებით; საუბრის დასაწყისი ბუნებრივი, ქართულად, ზედმეტი სიყვარულის სიმბოლოების გარეშე.
- **Registration/Onboarding:** არსებულ ავტორიზაციასა და ვალიდაციას არ ვეხებით; ფორმების spacing, typography, color states და responsivity ვმართოთ.

## 7. დიზაინის ტოკენების შრეები

1. **Primitive:** ფერის სკალები, ნედლი მნიშვნელობები (`brand.orange-500`).
2. **Semantic:** კომპონენტური მნიშვნელობა (`action.primary`, `text.on-primary`).
3. **Component:** Button/Input/Card/Chip/Tab/Alert mapping; კომპონენტი იდეალურად semantic tokens-ს იყენებს.
4. **Screen composition:** თანმიმდევრული გამოყენება და არა ახალი HEX-ების გამოგონება.

საბაზისო ფაილები: `jester.tokens.json`, `jester.reference-tokens.css`. ესენი **ჰენდოფის მაგალითებია**, არა უცვლელად დასაკოპირებელი target-path-ები. Gemini-მ ჯერ უნდა მოიძიოს არსებული სისტემა (მათ შორის Indigo tokens), გააკეთოს mapping და მხოლოდ ამის შემდეგ შეიტანოს უსაფრთხო ცვლილება.

## 8. დაცვა და Source of Truth

- იმუშაოს მხოლოდ Jester პროექტში. JesterAICompany-ს საერთო კოდში Jester-ის ფერები არ ჩავკეროთ.
- რეალური დოკუმენტების წაკითხვა: `docs/JESTER_PRODUCT_FOUNDATION.md`, `docs/JESTER_DESIGN_EXPLORATION.md`, `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md`, არსებული tokens/components, სანამ იმპლემენტაციას დაიწყებს.
- დამტკიცებული წესების კონფლიქტი მოხსენდეს Founder-ს; exploratory დიზაინი არ არის დამტკიცებული.
- მიმდინარე UI ფუნქციონალი არ შეიცვალოს (მათ შორის auth, onboarding, routing, privacy, API, connection state).
- განუხილველი Founder Proposals და dirty files არ გადაიწეროს.
- UX ფუნქციონალის შეცვლა რომ დასჭირდეს, შეჩერდეს და ავტორიზაცია მოითხოვოს.
- არ შეუცვალოს global body color ან tokens ბრმად: დადგინდეს გავლენის ზონა და გადაიტანოს ეტაპობრივად.

## 9. Definition of Done

- Source audit დასრულებულია და არქიტექტურის mapping წარმოდგენილია.
- ძირითადი token aliases არსებობს, hard-coded ფერები შემცირებულია სიის მიხედვით.
- primary CTA contrast დადასტურებულია dark label-ით ან მუქი ფონის white-label ვარიანტით.
- Buttons, Inputs, Cards, Chips, Tabs, Alerts და Navigation აღწერილი/მიგრირებულია სისტემასთან შესაბამისობაში.
- მინიმუმ Home, Discover, Person/Why, Compare, Registration მოწმდება representative ვიზუალებით desktop/mobile; თუ ავტომატური browser screenshot შეუძლებელია, ზუსტად აღინიშნოს.
- Build, არსებული relevant tests, targeted accessibility checks რეალურად გაივლის; დარღვევები ჩამოთვლილია.
- ყველა UI ტექსტი Georgian-first; არსებული როუტები და მონაცემთა კონტრაქტები უცვლელია.
- Founder იღებს before/after, diff, evidence; არ ხდება automatic commit/push/production deploy.

## 10. შენიშვნა ლოგოზე

ეს ფერთა სისტემა ეხება **აპლიკაციის UI-ს**. ადრე შემუშავებული სამქიმიანი ქუდის ლოგო არ უნდა გადაიხატოს ან შეიცვალოს ავტომატურად. მას შეიძლება ჰქონდეს ცალკე approved logo colorway; UI tokens-სთან შეთანხმება ცალკე Founder გადაწყვეტილებაა.
