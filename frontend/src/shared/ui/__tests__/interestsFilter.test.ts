import { describe, it } from "node:test";
import assert from "node:assert/strict";

interface InterestItemTest {
  id: string;
  name: string;
  slug: string;
  category_slug: string;
  name_ka?: string;
  name_en?: string;
  aliases?: string[];
}

const SAMPLE_CATALOG: InterestItemTest[] = [
  {
    id: "1",
    name: "მუსიკის მოსმენა",
    slug: "music",
    category_slug: "music-stage",
    name_ka: "მუსიკის მოსმენა",
    name_en: "Listening to Music",
    aliases: ["music", "listening", "სიმღერები", "მელომანი"],
  },
  {
    id: "2",
    name: "როკი და ინდი",
    slug: "rock-indie",
    category_slug: "music-stage",
    name_ka: "როკი და ინდი",
    name_en: "Rock & Indie",
    aliases: ["rock", "indie", "როკ მუსიკა", "ინდი"],
  },
  {
    id: "3",
    name: "კინო",
    slug: "cinema",
    category_slug: "cinema-books-stories",
    name_ka: "კინო",
    name_en: "Cinema & Movies",
    aliases: ["movies", "film", "cinema", "ფილმები"],
  },
  {
    id: "4",
    name: "ანიმე",
    slug: "anime",
    category_slug: "cinema-books-stories",
    name_ka: "ანიმე",
    name_en: "Anime",
    aliases: ["anime", "animation", "ანიმაცია", "მანგა"],
  },
  {
    id: "5",
    name: "იოგა და პილატესი",
    slug: "yoga-pilates",
    category_slug: "sports-movement",
    name_ka: "იოგა და პილატესი",
    name_en: "Yoga & Pilates",
    aliases: ["yoga", "pilates", "იოგა", "პილატესი"],
  },
];

function filterInterests(
  items: InterestItemTest[],
  category: string,
  query: string
): InterestItemTest[] {
  const q = query.toLowerCase().trim();
  return items.filter((item) => {
    if (category !== "all" && item.category_slug !== category) {
      return false;
    }
    if (!q) return true;
    const candidates = [
      item.name,
      item.name_ka || "",
      item.name_en || "",
      ...(item.aliases || []),
    ];
    return candidates.some((text) => text.toLowerCase().includes(q));
  });
}

function validateSelectionCount(count: number): { isValid: boolean; error?: string } {
  if (count === 0) return { isValid: true }; // Skip allowed
  if (count < 3) return { isValid: false, error: "მინიმუმ 3 ინტერესია საჭირო" };
  if (count > 7) return { isValid: false, error: "მაქსიმუმ 7 ინტერესია ნებადართული" };
  return { isValid: true };
}

describe("Interests System V2 Logic & Filtering Suite", () => {
  it("should match by Georgian name", () => {
    const results = filterInterests(SAMPLE_CATALOG, "all", "კინო");
    assert.equal(results.length, 1);
    assert.equal(results[0].slug, "cinema");
  });

  it("should match by English name", () => {
    const results = filterInterests(SAMPLE_CATALOG, "all", "Pilates");
    assert.equal(results.length, 1);
    assert.equal(results[0].slug, "yoga-pilates");
  });

  it("should match by alias", () => {
    const results = filterInterests(SAMPLE_CATALOG, "all", "მელომანი");
    assert.equal(results.length, 1);
    assert.equal(results[0].slug, "music");
  });

  it("should filter by category slug", () => {
    const results = filterInterests(SAMPLE_CATALOG, "music-stage", "");
    assert.equal(results.length, 2);
    assert(results.every((r) => r.category_slug === "music-stage"));
  });

  it("should enforce minimum 3 and maximum 7 selection rules", () => {
    assert.equal(validateSelectionCount(0).isValid, true);
    assert.equal(validateSelectionCount(1).isValid, false);
    assert.equal(validateSelectionCount(2).isValid, false);
    assert.equal(validateSelectionCount(3).isValid, true);
    assert.equal(validateSelectionCount(5).isValid, true);
    assert.equal(validateSelectionCount(7).isValid, true);
    assert.equal(validateSelectionCount(8).isValid, false);
  });
});

