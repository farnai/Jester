import test, { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  GEORGIAN_MONTHS,
  isLeapYear,
  getDaysInMonth,
  parseIsoDate,
  formatIsoDate,
  calculateExactAge,
  validateBirthDateParts,
} from "../birthDateUtils.ts";

describe("Birth Date Utils & Validation Suite", () => {
  // 1. Georgian Month Labels
  it("should have all 12 Georgian month names in correct chronological order", () => {
    assert.equal(GEORGIAN_MONTHS.length, 12);
    const expected = [
      "იანვარი",
      "თებერვალი",
      "მარტი",
      "აპრილი",
      "მაისი",
      "ივნისი",
      "ივლისი",
      "აგვისტო",
      "სექტემბერი",
      "ოქტომბერი",
      "ნოემბერი",
      "დეკემბერი",
    ];
    GEORGIAN_MONTHS.forEach((m, idx) => {
      assert.equal(m.num, idx + 1);
      assert.equal(m.value, String(idx + 1).padStart(2, "0"));
      assert.equal(m.name, expected[idx]);
    });
  });

  // 2. Leap Year Calculations
  it("should correctly identify Gregorian leap years", () => {
    assert.equal(isLeapYear(2024), true); // Divisible by 4
    assert.equal(isLeapYear(2020), true);
    assert.equal(isLeapYear(2000), true); // Divisible by 400
    assert.equal(isLeapYear(1900), false); // Century not divisible by 400
    assert.equal(isLeapYear(2023), false);
    assert.equal(isLeapYear(1995), false);
  });

  // 3. Days in Month Bounds
  it("should return the exact days for each month and respect leap years", () => {
    // 31-day months
    [1, 3, 5, 7, 8, 10, 12].forEach((m) => {
      assert.equal(getDaysInMonth(2024, m), 31);
      assert.equal(getDaysInMonth(2023, m), 31);
    });

    // 30-day months
    [4, 6, 9, 11].forEach((m) => {
      assert.equal(getDaysInMonth(2024, m), 30);
      assert.equal(getDaysInMonth(2023, m), 30);
    });

    // February
    assert.equal(getDaysInMonth(2024, 2), 29); // Leap year 2024
    assert.equal(getDaysInMonth(2023, 2), 28); // Common year 2023
    assert.equal(getDaysInMonth(2000, 2), 29); // Leap year 2000
    assert.equal(getDaysInMonth(1900, 2), 28); // Century non-leap year 1900
    assert.equal(getDaysInMonth(null, 2), 29); // Year not chosen yet -> allow up to 29
    assert.equal(getDaysInMonth(null, null), 31);
  });

  // 4. ISO Date Parsing (parseIsoDate)
  it("should safely parse YYYY-MM-DD into parts without timezone offsets", () => {
    const res = parseIsoDate("1995-08-24");
    assert.deepEqual(res, { year: "1995", month: "08", day: "24" });

    // Invalids & empties
    assert.deepEqual(parseIsoDate(""), { year: "", month: "", day: "" });
    assert.deepEqual(parseIsoDate(null), { year: "", month: "", day: "" });
    assert.deepEqual(parseIsoDate("invalid-date"), { year: "", month: "", day: "" });
  });

  // 5. ISO Date Serialization (formatIsoDate)
  it("should serialize valid parts to YYYY-MM-DD and return empty for partial inputs", () => {
    assert.equal(formatIsoDate("1995", "08", "24"), "1995-08-24");
    assert.equal(formatIsoDate("2000", "1", "5"), "2000-01-05");
    // Partial inputs
    assert.equal(formatIsoDate("1995", "08", ""), "");
    assert.equal(formatIsoDate("", "08", "24"), "");
    assert.equal(formatIsoDate("1995", "", "24"), "");
  });

  // 6. Age Calculation & Exact Birthday Boundary
  it("should calculate exact age using complete calendar date without timezone drift", () => {
    const fixedToday = new Date(2026, 10, 7); // Nov 7, 2026

    // Case A: Exact 18th birthday today
    // Born Nov 7, 2008 -> turns exactly 18 today
    assert.equal(calculateExactAge(2008, 11, 7, fixedToday), 18);

    // Case B: 18th birthday was yesterday (Nov 6, 2008) -> 18
    assert.equal(calculateExactAge(2008, 11, 6, fixedToday), 18);

    // Case C: 18th birthday is tomorrow (Nov 8, 2008) -> 17 (underage)
    assert.equal(calculateExactAge(2008, 11, 8, fixedToday), 17);

    // Case D: Next month (Dec 1, 2008) -> 17 (underage)
    assert.equal(calculateExactAge(2008, 12, 1, fixedToday), 17);

    // Case E: Adult (born 1990) -> 36
    assert.equal(calculateExactAge(1990, 4, 10, fixedToday), 36);
  });

  // 7. Validation: Valid Date Selection
  it("should accept valid dates for adults", () => {
    const fixedToday = new Date(2026, 10, 7); // Nov 7, 2026
    const res = validateBirthDateParts("1995", "08", "24", fixedToday, true);
    assert.equal(res.isValid, true);
    assert.equal(res.isComplete, true);
    assert.equal(res.error, null);
    assert.equal(res.age, 31);
  });

  // 8. Validation: Partial Selections
  it("should handle partial selections without throwing or falsely validating", () => {
    const fixedToday = new Date(2026, 10, 7);
    const partial1 = validateBirthDateParts("1995", "08", "", fixedToday, true);
    assert.equal(partial1.isValid, false);
    assert.equal(partial1.isComplete, false);
    assert.match(partial1.error || "", /ყველა ველი/);

    const empty = validateBirthDateParts("", "", "", fixedToday, true);
    assert.equal(empty.isValid, false);
    assert.equal(empty.isComplete, false);
    assert.equal(empty.error, null);
  });

  // 9. Validation: Leap-year February 29
  it("should accept Feb 29 in leap years and reject Feb 29 in non-leap years", () => {
    const fixedToday = new Date(2026, 10, 7);

    // Valid: Feb 29, 2000 (leap year)
    const leapValid = validateBirthDateParts("2000", "02", "29", fixedToday, true);
    assert.equal(leapValid.isValid, true);
    assert.equal(leapValid.error, null);

    // Invalid: Feb 29, 1999 (not a leap year)
    const leapInvalid = validateBirthDateParts("1999", "02", "29", fixedToday, true);
    assert.equal(leapInvalid.isValid, false);
    assert.match(leapInvalid.error || "", /არ არის ნაკიანი/);
  });

  // 10. Validation: Underage Rejection (< 18)
  it("should strictly reject users under 18 years of age", () => {
    const fixedToday = new Date(2026, 10, 7); // Nov 7, 2026

    // 17 years and 364 days old (born Nov 8, 2008)
    const underage = validateBirthDateParts("2008", "11", "08", fixedToday, true);
    assert.equal(underage.isValid, false);
    assert.match(underage.error || "", /18\+/);

    // Exactly 18 years old today (born Nov 7, 2008)
    const adultBoundary = validateBirthDateParts("2008", "11", "07", fixedToday, true);
    assert.equal(adultBoundary.isValid, true);
    assert.equal(adultBoundary.age, 18);
  });

  // 11. Validation: Future Dates
  it("should reject future birth dates", () => {
    const fixedToday = new Date(2026, 10, 7);
    const futureYear = validateBirthDateParts("2028", "01", "01", fixedToday, true);
    assert.equal(futureYear.isValid, false);
    assert.match(futureYear.error || "", /მომავალში/);

    const futureDay = validateBirthDateParts("2026", "11", "10", fixedToday, true);
    assert.equal(futureDay.isValid, false);
    assert.match(futureDay.error || "", /მომავალში/);
  });

  // 12. Validation: Pre-1900 Dates
  it("should reject birth years before 1900", () => {
    const fixedToday = new Date(2026, 10, 7);
    const tooOld = validateBirthDateParts("1880", "05", "15", fixedToday, true);
    assert.equal(tooOld.isValid, false);
    assert.match(tooOld.error || "", /1900/);
  });

  // 13. Validation: Non-existent month days (e.g. April 31)
  it("should reject invalid day numbers for 30-day months", () => {
    const fixedToday = new Date(2026, 10, 7);
    const apr31 = validateBirthDateParts("1995", "04", "31", fixedToday, true);
    assert.equal(apr31.isValid, false);
    assert.match(apr31.error || "", /აპრილს არ აქვს 31 დღე/);
  });
});

