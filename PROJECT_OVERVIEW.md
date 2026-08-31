# 🚀 პროექტების დეტალური ტექნიკური მიმოხილვა (Project Overview)

ეს დოკუმენტი შეიცავს სრულ ინფორმაციას მიმდინარე პროექტების ტექნოლოგიური სტეკების, არქიტექტურისა და ამ დრომდე განხორციელებული ფუნქციონალის შესახებ.

---

## 1. 🃏 Jester — Social Astrology Engine Backend

### 📌 პროექტის აღწერა
**Jester** წარმოადგენს სოციალური ასტროლოგიური პლატფორმის მაღალპროდუქტიულ ბექენდ ძრავს. იგი პასუხისმგებელია მაღალი სიზუსტის ნატალური რუკების გამოთვლაზე, მომხმარებლებს შორის ასტროლოგიური თავსებადობის (Synastry) ანალიზზე, რეალური დროის სოციალურ ინტერაქციასა და AI-ზე დაფუძნებულ ინტერპრეტაციებზე.

### 🛠️ ტექნოლოგიური სტეკი (Tech Stack)
| კომპონენტი | ტექნოლოგია / ბიბლიოთეკა | ვერსია / დეტალები |
| :--- | :--- | :--- |
| **Language** | Python | `3.11+` |
| **Web Framework** | FastAPI | `>=0.115.0` (ASGI, OpenAPI, Pydantic v2) |
| **Astro Engine** | PySwissEph | `>=2.10.3.2` (C-backed Swiss Ephemeris) |
| **Database & Auth** | Supabase | PostgreSQL 15+, Auth JWT, Row Level Security (RLS) |
| **DB Driver** | psycopg (v3) | `>=3.2.0` (Direct PostgreSQL Connection) |
| **HTTP & Security** | PyJWT, Cryptography, HTTPX | JWT verification, async requests |
| **AI / LLM** | OpenAI API Integration | GPT-4o-mini (ასტროლოგიური ტექსტების გენერაცია) |
| **Testing** | Pytest & pytest-asyncio | `>=8.3.0` (42/42 ტესტი წარმატებით გადის) |

---

### 🏛️ არქიტექტურა და სტრუქტურა
```text
Jester/
├── backend/app/
│   ├── api/             # სისტემის Health Endpoint-ები და V1 მარშრუტიზაცია
│   ├── astrology/       # Swiss Ephemeris კალკულატორი, ნატალური რუკები, ტრანზიტები
│   ├── auth/            # Supabase JWT ავტორიზაციის მიდლვერი
│   ├── comparisons/     # ასტროლოგიური თავსებადობის (Synastry) გამოთვლები
│   ├── connections/     # მეგობრობის მოთხოვნები და სოციალური კავშირები
│   ├── conversations/   # რეალური დროის ჩატი და შეტყობინებები
│   ├── core/            # გლობალური Exception-ები და Logging
│   ├── interpretation/ # წესებზე და AI-ზე დაფუძნებული განმარტებები
│   ├── jobs/            # ფონური ამოცანები (Daily Transit Recalculation)
│   ├── notifications/   # Push და In-App შეტყობინებები
│   ├── profiles/        # პროფილისა და დაბადების მონაცემების მართვა
│   └── users/           # მომხმარებელთა ანგარიშები
├── supabase/migrations/ # 20 SQL მიგრაციის ფაილი (RLS, Triggers, Functions)
├── tests/               # Unit, API და ბაზის უსაფრთხოების ტესტები
└── README.md            # სრული დოკუმენტაცია GitHub-ისთვის
```

---

### ⚙️ განხორციელებული ფუნქციონალი (Implemented Features)
1. **ასტროლოგიური გამოთვლების ძრავი**:
   - პლანეტების ზუსტი კოორდინატები (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, Lilith, North/South Nodes).
   - სახლების სისტემები (Placidus, Whole Sign) და კუთხური ასპექტები (Conjunction, Opposition, Trine, Square, Sextile).
   - ტრანზიტებისა და ყოველდღიური ენერგიების გამოთვლა.

2. **თავსებადობის (Synastry) ანალიზი**:
   - ორი მომხმარებლის ნატალური რუკების შედარება, ელემენტების/სტიქიების ბალანსი და ურთიერთობის ჯამური ინდექსი.

3. **მონაცემთა უსაფრთხოება & RLS**:
   - დაბადების ზუსტი დროისა და ადგილის დაცვა `astro_private` სქემაში.
   - 20 SQL მიგრაცია Supabase-ში RLS (Row Level Security) პოლიტიკებითა და `astro_safe_profile` ხედებით.

4. **ტესტირების დაფარვა (Test Coverage)**:
   - 42 ავტომატიზებული ტესტი (`tests/astrology`, `tests/backend`, `tests/database`), რომლებიც სრულად ჩაბარებულია.

5. **GitHub რეპოზიტორი**:
   - პროექტი ატვირთულია: `git@github.com:farnai/Jester.git` (`main` ბრენჩზე).

---

## 2. ⌚ SwissWatches Web (Luxury Watch E-Commerce & Editorial Portal)

### 📌 პროექტის აღწერა
**SwissWatches Web** წარმოადგენს ექსკლუზიურ ონლაინ პლატფორმასა და ლანდინგ გვერდების სისტემას შვეიცარიული საათების სეგმენტისთვის. პროექტი აგებულია თანამედროვე PHP/WordPress Bedrock არქიტექტურით და მოდულური SCSS დიზაინ-სისტემით.

### 🛠️ ტექნოლოგიური სტეკი (Tech Stack)
| კომპონენტი | ტექნოლოგია / ბიბლიოთეკა | დეტალები |
| :--- | :--- | :--- |
| **PHP Version** | PHP 8.2 | `^8.2` (Strict Types, Symfony Components) |
| **Framework Boilerplate** | WordPlate / Roots Bedrock | Თანამედროვე სტრუქტურა `public/` & `src/` გამიჯვნით |
| **CMS Core** | Roots WordPress | `^6.9.4` (Composer-managed WP core) |
| **Custom Fields** | ACF Pro (Advanced Custom Fields) | `^6.5` (მოდულური ბლოკები და ფილდები) |
| **Styling & Assets** | SCSS / Sass, Webpack Mix, Vite | Მოდულური სტილები, Fluid Typography |
| **Plugins** | Rank Math SEO, Complianz GDPR, WP Mail SMTP, Co-Authors Plus | Სეო, GDPR, ფოსტა და ავტორების მართვა |
| **Local Environment** | Laragon Stack | Local WAMP setup (PHP 8.2 + MySQL/MariaDB) |

---

### 🏛️ სტილებისა და ფრონტენდის სტრუქტურა
```text
swisswatches-web/
├── resources/styles/
│   ├── common/
│   │   └── _global.scss        # გლობალური სტილები, ბაზისური Reset, ტიპოგრაფია
│   └── landing/
│       └── lc/
│           ├── lc-landing.scss  # LC Landing-ის მთავარი SCSS (Fluid Heading Classes)
│           └── _block-lc-block-22.scss # კონკრეტული მოდულური ბლოკების სტილები
├── public/                     # WordPress Core და Compiled Assets
├── src/                        # Custom PHP Logic & Theme Controller
└── composer.json               # PHP დამოკიდებულებები
```

---

### ⚙️ განხორციელებული ფუნქციონალი (Implemented Features)
1. **Fluid Typography System**:
   - `lc-landing.scss`-ში დამატებულია CSS `clamp()` ფუნქციებზე დაფუძნებული დინამიური სათაურების ზომები (`.h1`-დან `.h6`-მდე), რომლებიც ავტომატურად ერგება ეკრანის ზომას:
     - `.h1`: `clamp(25px, 2.5vw + 15px, 46px)`
     - `.h2`: `clamp(23px, 1.3vw + 18px, 34px)`
     - `.h3`: `clamp(21px, 0.85vw + 17.8px, 28px)`
     - `.h4`: `clamp(19px, 0.6vw + 16.75px, 24px)`
     - `.h5`: `clamp(16px, 0.5vw + 14px, 20px)`
     - `.h6`: `clamp(14px, 0.36vw + 12.65px, 17px)`

2. **LC Landing & Custom Blocks**:
   - აწყობილია მოდულური კომპონენტები (მაგ. `_block-lc-block-22.scss`), ადაპტაციური განლაგება (Responsive Layouts) და უნიკალური დიზაინ-ელემენტები.

3. **WordPlate / Composer Architecture**:
   - WordPress-ის პლაგინები და თემა სრულად იმართება Composer-ით, რაც უზრუნველყოფს კოდის სისუფთავესა და ვერსიონირებას.

---

## 📊 შეჯამება (Summary Table)

| პროექტი | ტიპი | ძირითადი ენა / ფრეიმვორკი | მონაცემთა ბაზა / CMS | მიმდინარე სტატუსი |
| :--- | :--- | :--- | :--- | :--- |
| **Jester** | REST API Backend | Python / FastAPI | Supabase (PostgreSQL) | ✅ 42/42 ტესტი ჩაბარებულია, GitHub-ზე ატვირთულია |
| **SwissWatches** | Web Portal / Landing | PHP 8.2 / WordPlate (WP) | MySQL / Laragon | 🟡 SCSS Fluid Typography & Landing ბლოკების დამუშავება |
