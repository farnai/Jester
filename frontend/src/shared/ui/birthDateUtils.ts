/**
 * JESTER — Birth Date & Age Utilities
 * Pure, deterministic, timezone-safe Gregorian calendar and Georgian localization logic.
 */

export interface GeorgianMonth {
  value: string; // "01", "02", ... "12"
  num: number; // 1 .. 12
  name: string; // "იანვარი", "თებერვალი", ...
}

export const GEORGIAN_MONTHS: GeorgianMonth[] = [
  { value: "01", num: 1, name: "იანვარი" },
  { value: "02", num: 2, name: "თებერვალი" },
  { value: "03", num: 3, name: "მარტი" },
  { value: "04", num: 4, name: "აპრილი" },
  { value: "05", num: 5, name: "მაისი" },
  { value: "06", num: 6, name: "ივნისი" },
  { value: "07", num: 7, name: "ივლისი" },
  { value: "08", num: 8, name: "აგვისტო" },
  { value: "09", num: 9, name: "სექტემბერი" },
  { value: "10", num: 10, name: "ოქტომბერი" },
  { value: "11", num: 11, name: "ნოემბერი" },
  { value: "12", num: 12, name: "დეკემბერი" },
];

export interface DateParts {
  day: string; // "01" - "31" or ""
  month: string; // "01" - "12" or ""
  year: string; // "1995" or ""
}

/**
 * Checks whether a given year is a leap year in the Gregorian calendar.
 */
export function isLeapYear(year: number): boolean {
  if (isNaN(year)) return false;
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}

/**
 * Returns the maximum number of days in the specified month and year.
 * If month is null/empty, defaults to 31.
 * If month is February and year is not specified, defaults to 29 to allow leap year selection.
 */
export function getDaysInMonth(year: number | null, month: number | null): number {
  if (!month) return 31;
  if (month === 4 || month === 6 || month === 9 || month === 11) {
    return 30;
  }
  if (month === 2) {
    if (year === null || isNaN(year)) return 29;
    return isLeapYear(year) ? 29 : 28;
  }
  return 31;
}

/**
 * Safely parses an ISO date string "YYYY-MM-DD" into DateParts.
 * Avoids any JavaScript Date object parsing to eliminate timezone offsets.
 */
export function parseIsoDate(isoString: string | null | undefined): DateParts {
  if (!isoString || typeof isoString !== "string") {
    return { day: "", month: "", year: "" };
  }
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoString.trim());
  if (!match) {
    return { day: "", month: "", year: "" };
  }
  const [, y, m, d] = match;
  return {
    year: y,
    month: m,
    day: d,
  };
}

/**
 * Serializes year, month, and day strings into an ISO "YYYY-MM-DD" string.
 * Returns "" if any part is missing or non-numeric.
 */
export function formatIsoDate(year: string, month: string, day: string): string {
  if (!year || !month || !day) return "";
  const y = parseInt(year, 10);
  const m = parseInt(month, 10);
  const d = parseInt(day, 10);
  if (isNaN(y) || isNaN(m) || isNaN(d)) return "";
  return `${String(y).padStart(4, "0")}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
}

/**
 * Calculates exact age in full years using calendar date arithmetic.
 * Eliminates timezone drift by operating strictly on year, month, day integers.
 */
export function calculateExactAge(
  year: number,
  month: number,
  day: number,
  referenceDate: Date = new Date()
): number {
  const refYear = referenceDate.getFullYear();
  const refMonth = referenceDate.getMonth() + 1;
  const refDay = referenceDate.getDate();

  let age = refYear - year;
  if (refMonth < month || (refMonth === month && refDay < day)) {
    age--;
  }
  return age;
}

export interface DateValidationResult {
  isValid: boolean;
  isComplete: boolean;
  error: string | null;
  age: number | null;
}

/**
 * Formats Georgian month name into proper dative case (e.g. "აპრილს", "აგვისტოს").
 */
export function formatMonthDative(monthNum: number): string {
  const dativeMap: Record<number, string> = {
    1: "იანვარს",
    2: "თებერვალს",
    3: "მარტს",
    4: "აპრილს",
    5: "მაისს",
    6: "ივნისს",
    7: "ივლისს",
    8: "აგვისტოს",
    9: "სექტემბერს",
    10: "ოქტომბერს",
    11: "ნოემბერს",
    12: "დეკემბერს",
  };
  return dativeMap[monthNum] || `${monthNum}-ე თვეს`;
}

/**
 * Validates birth date parts against:
 * 1. Completeness (Day, Month, Year present)
 * 2. Range limits (Year >= 1900)
 * 3. Real Gregorian calendar rules (e.g. Feb 29 leap years, 30-day months)
 * 4. Future birth date rejection
 * 5. 18+ platform policy enforcement
 */
export function validateBirthDateParts(
  yearStr: string,
  monthStr: string,
  dayStr: string,
  referenceDate: Date = new Date(),
  enforceAdult: boolean = true
): DateValidationResult {
  const hasYear = !!yearStr.trim();
  const hasMonth = !!monthStr.trim();
  const hasDay = !!dayStr.trim();

  // If completely empty:
  if (!hasYear && !hasMonth && !hasDay) {
    return { isValid: false, isComplete: false, error: null, age: null };
  }

  // If partially filled:
  if (!hasYear || !hasMonth || !hasDay) {
    return {
      isValid: false,
      isComplete: false,
      error: "გთხოვთ შეავსოთ დაბადების თარიღის ყველა ველი (დღე, თვე, წელი).",
      age: null,
    };
  }

  const year = parseInt(yearStr, 10);
  const month = parseInt(monthStr, 10);
  const day = parseInt(dayStr, 10);

  if (isNaN(year) || isNaN(month) || isNaN(day)) {
    return {
      isValid: false,
      isComplete: false,
      error: "თარიღის ფორმატი არასწორია.",
      age: null,
    };
  }

  // 1. Earliest year bound
  if (year < 1900) {
    return {
      isValid: false,
      isComplete: true,
      error: "დაბადების თარიღი უნდა იყოს 1900 წლის შემდეგ.",
      age: null,
    };
  }

  // 2. Month bound
  if (month < 1 || month > 12) {
    return {
      isValid: false,
      isComplete: true,
      error: "თვე უნდა იყოს 1-დან 12-მდე.",
      age: null,
    };
  }

  // 3. Days in month bound (Leap year awareness)
  const maxDays = getDaysInMonth(year, month);
  if (day < 1 || day > maxDays) {
    if (month === 2 && day === 29 && !isLeapYear(year)) {
      return {
        isValid: false,
        isComplete: true,
        error: `${year} წელი არ არის ნაკიანი — თებერვალს აქვს მხოლოდ 28 დღე.`,
        age: null,
      };
    }
    const monthDative = formatMonthDative(month);
    return {
      isValid: false,
      isComplete: true,
      error: `${monthDative} არ აქვს ${day} დღე (მაქსიმუმ ${maxDays}).`,
      age: null,
    };
  }

  // 4. Future date check
  const refYear = referenceDate.getFullYear();
  const refMonth = referenceDate.getMonth() + 1;
  const refDay = referenceDate.getDate();

  const isFuture =
    year > refYear ||
    (year === refYear && month > refMonth) ||
    (year === refYear && month === refMonth && day > refDay);

  if (isFuture) {
    return {
      isValid: false,
      isComplete: true,
      error: "დაბადების თარიღი არ შეიძლება იყოს მომავალში.",
      age: null,
    };
  }

  // 5. 18+ policy enforcement
  const age = calculateExactAge(year, month, day, referenceDate);
  if (enforceAdult && age < 18) {
    return {
      isValid: false,
      isComplete: true,
      error: "JESTER განკუთვნილია 18 წლიდან ზემოთ მომხმარებლებისთვის (18+).",
      age,
    };
  }

  return {
    isValid: true,
    isComplete: true,
    error: null,
    age,
  };
}
