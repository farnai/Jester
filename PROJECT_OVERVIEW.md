# 🃏 Jester — Social Astrology Engine Backend

ეს დოკუმენტი შეიცავს სრულ ინფორმაციას **Jester**-ის პროექტის ტექნოლოგიური სტეკის, არქიტექტურისა და ამ დრომდე განხორციელებული ფუნქციონალის შესახებ.

---

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
