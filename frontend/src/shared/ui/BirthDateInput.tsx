import React, { useState, useEffect, useRef, useId, useMemo } from "react";
import {
  GEORGIAN_MONTHS,
  parseIsoDate,
  formatIsoDate,
  getDaysInMonth,
  isLeapYear,
  formatMonthDative,
  validateBirthDateParts,
} from "./birthDateUtils";

export interface BirthDateInputProps {
  /**
   * Current value in ISO "YYYY-MM-DD" format, or empty string.
   */
  value: string;
  /**
   * Emits updated "YYYY-MM-DD" string when all three segments form a valid complete date.
   * Emits "" if the date is incomplete or invalid.
   */
  onChange: (isoDate: string) => void;
  /**
   * Main component label.
   */
  label?: string;
  /**
   * Subtitle / helper hint displayed below or above the selector.
   */
  helperText?: string;
  /**
   * External error string (e.g. from server submission).
   */
  error?: string | null;
  /**
   * Disables all interactive controls.
   */
  disabled?: boolean;
  /**
   * Whether the field is mandatory.
   */
  required?: boolean;
  /**
   * Reference date for age and future boundary calculations (defaults to today).
   */
  referenceDate?: Date;
  /**
   * Enforce Jester's 18+ policy (defaults to true).
   */
  enforceAdult?: boolean;
  /**
   * Optional custom HTML id.
   */
  id?: string;
}

interface GenerationOption {
  id: string;
  label: string;
  tooltip: string;
  startYear: number;
  endYear: number;
}

type FilterMode = "generations" | "decades";

export const BirthDateInput: React.FC<BirthDateInputProps> = ({
  value,
  onChange,
  label = "დაბადების თარიღი (Birth Date)",
  helperText,
  error: externalError,
  disabled = false,
  required = false,
  referenceDate = new Date(),
  enforceAdult = true,
  id: customId,
}) => {
  const componentId = useId();
  const rootId = customId || `birth-date-${componentId}`;
  const dayId = `${rootId}-day`;
  const monthId = `${rootId}-month`;
  const yearId = `${rootId}-year`;
  const errorId = `${rootId}-error`;
  const helperId = `${rootId}-helper`;

  // Parse initial parts from value
  const initialParts = parseIsoDate(value);

  // Internal state for each of the three segments
  const [day, setDay] = useState<string>(initialParts.day);
  const [month, setMonth] = useState<string>(initialParts.month);
  const [year, setYear] = useState<string>(initialParts.year);

  // Year combobox / popover state
  const [isYearOpen, setIsYearOpen] = useState(false);
  const [yearQuery, setYearQuery] = useState(initialParts.year);
  const [filterMode, setFilterMode] = useState<FilterMode>("generations");
  const [selectedCohort, setSelectedCohort] = useState<string | null>(null);
  const [highlightedYearIndex, setHighlightedYearIndex] = useState<number>(-1);
  const [dayResetNotice, setDayResetNotice] = useState<string | null>(null);
  const [internalError, setInternalError] = useState<string | null>(null);

  const yearContainerRef = useRef<HTMLDivElement>(null);
  const yearInputRef = useRef<HTMLInputElement>(null);
  const yearListboxRef = useRef<HTMLDivElement>(null);
  const lastCommittedIso = useRef<string>(value);

  // Sync internal state with external value when it changes from outside
  useEffect(() => {
    if (value !== lastCommittedIso.current) {
      lastCommittedIso.current = value;
      const parts = parseIsoDate(value);
      setDay(parts.day);
      setMonth(parts.month);
      setYear(parts.year);
      setYearQuery(parts.year);
    }
  }, [value]);

  // Current year & maximum allowable year
  const currentYear = referenceDate.getFullYear();
  const minAllowedYear = 1900;
  // If enforceAdult is active, user must be at least 18 years old
  const maxSuggestedYear = enforceAdult ? currentYear - 18 : currentYear;

  // Generational cohort filter chips
  const generationOptions: GenerationOption[] = useMemo(() => {
    return [
      {
        id: "gen-z",
        label: "Gen Z",
        tooltip: "1997 – 2012 (თაობა Z, 14–29 წელი)",
        startYear: 1997,
        endYear: currentYear,
      },
      {
        id: "millennials",
        label: "მილენიალები",
        tooltip: "1981 – 1996 (Millennials / Gen Y, 30–45 წელი)",
        startYear: 1981,
        endYear: 1996,
      },
      {
        id: "gen-x",
        label: "Gen X",
        tooltip: "1965 – 1980 (თაობა X, 46–61 წელი)",
        startYear: 1965,
        endYear: 1980,
      },
      {
        id: "boomers",
        label: "ბუმერები",
        tooltip: "1946 – 1964 (Baby Boomers, 62–80 წელი)",
        startYear: 1946,
        endYear: 1964,
      },
      {
        id: "silent",
        label: "დუმილის თაობა",
        tooltip: "1928 – 1945 (Silent Generation, 81+ წელი)",
        startYear: 1900,
        endYear: 1945,
      },
    ];
  }, [currentYear]);

  // Decades cohort filter chips (matches screenshot)
  const decadeOptions: GenerationOption[] = useMemo(() => {
    return [
      {
        id: "dec-2000s",
        label: "2000-იანები",
        tooltip: "2000 წლიდან დღემდე",
        startYear: 2000,
        endYear: currentYear,
      },
      {
        id: "dec-1990s",
        label: "1990-იანები",
        tooltip: "1990 – 1999 წლები",
        startYear: 1990,
        endYear: 1999,
      },
      {
        id: "dec-1980s",
        label: "1980-იანები",
        tooltip: "1980 – 1989 წლები",
        startYear: 1980,
        endYear: 1989,
      },
      {
        id: "dec-1970s",
        label: "1970-იანები",
        tooltip: "1970 – 1979 წლები",
        startYear: 1970,
        endYear: 1979,
      },
      {
        id: "dec-1960s",
        label: "1960 და ადრე",
        tooltip: "1969 წელი და უფრო ადრე",
        startYear: 1900,
        endYear: 1969,
      },
    ];
  }, [currentYear]);

  // Compute full available years list (descending from currentYear down to 1900)
  const allYears = useMemo(() => {
    const years: number[] = [];
    for (let y = currentYear; y >= minAllowedYear; y--) {
      years.push(y);
    }
    return years;
  }, [currentYear, minAllowedYear]);

  // Filtered years for the year popover
  const filteredYears = useMemo(() => {
    let result = allYears;
    const activeOptions = filterMode === "generations" ? generationOptions : decadeOptions;

    if (selectedCohort) {
      const cohort = activeOptions.find((c) => c.id === selectedCohort);
      if (cohort) {
        result = result.filter((y) => y >= cohort.startYear && y <= cohort.endYear);
      }
    } else if (yearQuery.trim()) {
      const q = yearQuery.trim();
      result = result.filter((y) => String(y).startsWith(q) || String(y).includes(q));
    }

    return result;
  }, [allYears, selectedCohort, yearQuery, filterMode, generationOptions, decadeOptions]);

  // Dynamic max days in the currently chosen month & year
  const parsedYear = year ? parseInt(year, 10) : null;
  const parsedMonth = month ? parseInt(month, 10) : null;
  const maxDays = useMemo(() => {
    return getDaysInMonth(parsedYear, parsedMonth);
  }, [parsedYear, parsedMonth]);

  // Close year popover on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (
        yearContainerRef.current &&
        !yearContainerRef.current.contains(e.target as Node)
      ) {
        setIsYearOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  // Propagate valid ISO date when all 3 fields are complete
  const commitDate = (newDay: string, newMonth: string, newYear: string) => {
    setDayResetNotice(null);

    const validation = validateBirthDateParts(
      newYear,
      newMonth,
      newDay,
      referenceDate,
      enforceAdult
    );

    if (validation.isValid) {
      setInternalError(null);
      const iso = formatIsoDate(newYear, newMonth, newDay);
      lastCommittedIso.current = iso;
      onChange(iso);
    } else {
      setInternalError(validation.error);
      lastCommittedIso.current = "";
      onChange(""); // Don't emit partial or invalid dates to parent
    }
  };

  // Handler: Day Selection
  const handleDayChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setDay(val);
    commitDate(val, month, year);
  };

  // Handler: Month Selection
  const handleMonthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newMonth = e.target.value;
    setMonth(newMonth);

    // Guard: Prevent silent birthday date shift if the previously selected day exceeds max days of the new month
    let updatedDay = day;
    if (day && newMonth) {
      const mNum = parseInt(newMonth, 10);
      const yNum = year ? parseInt(year, 10) : null;
      const allowedDays = getDaysInMonth(yNum, mNum);
      const dNum = parseInt(day, 10);

      if (dNum > allowedDays) {
        updatedDay = ""; // Reset day to prevent silent shift
        setDay("");
        const monthTitle = formatMonthDative(mNum);
        setDayResetNotice(
          `${monthTitle} აქვს მაქსიმუმ ${allowedDays} დღე. გთხოვთ აირჩიოთ დღე თავიდან.`
        );
      }
    }

    commitDate(updatedDay, newMonth, year);
  };

  // Handler: Direct Year Selection from List or Decade
  const selectYearValue = (yNum: number) => {
    const yStr = String(yNum);
    setYear(yStr);
    setYearQuery(yStr);
    setIsYearOpen(false);

    // Guard: Leap year February edge-case check
    let updatedDay = day;
    if (month === "02" && day === "29" && !isLeapYear(yNum)) {
      updatedDay = "";
      setDay("");
      setDayResetNotice(
        `${yNum} წელი არ არის ნაკიანი (თებერვალს აქვს 28 დღე). აირჩიეთ დღე თავიდან.`
      );
    }

    commitDate(updatedDay, month, yStr);
    yearInputRef.current?.focus();
  };

  // Handler: Year Input Typing
  const handleYearInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawVal = e.target.value.replace(/\D/g, "").slice(0, 4);
    setYearQuery(rawVal);
    if (!isYearOpen) setIsYearOpen(true);
    setHighlightedYearIndex(0);

    // If 4 valid digits typed
    if (rawVal.length === 4) {
      const yNum = parseInt(rawVal, 10);
      if (yNum >= minAllowedYear && yNum <= currentYear) {
        setYear(rawVal);

        let updatedDay = day;
        if (month === "02" && day === "29" && !isLeapYear(yNum)) {
          updatedDay = "";
          setDay("");
          setDayResetNotice(
            `${yNum} წელი არ არის ნაკიანი (თებერვალს აქვს 28 დღე). აირჩიეთ დღე თავიდან.`
          );
        }

        commitDate(updatedDay, month, rawVal);
        setIsYearOpen(false);
      } else {
        setYear(rawVal);
        commitDate(day, month, rawVal);
      }
    } else {
      setYear("");
      commitDate(day, month, "");
    }
  };

  // Year Input Keyboard Navigation
  const handleYearKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!isYearOpen) {
        setIsYearOpen(true);
        setHighlightedYearIndex(0);
      } else {
        setHighlightedYearIndex((prev) =>
          prev < filteredYears.length - 1 ? prev + 1 : 0
        );
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (isYearOpen) {
        setHighlightedYearIndex((prev) =>
          prev > 0 ? prev - 1 : filteredYears.length - 1
        );
      }
    } else if (e.key === "Enter") {
      if (isYearOpen && highlightedYearIndex >= 0 && filteredYears[highlightedYearIndex]) {
        e.preventDefault();
        selectYearValue(filteredYears[highlightedYearIndex]);
      }
    } else if (e.key === "Escape") {
      if (isYearOpen) {
        e.preventDefault();
        setIsYearOpen(false);
      }
    }
  };

  const displayError = externalError || internalError || dayResetNotice;
  const isInputInvalid = Boolean(displayError);

  // Common styling tokens aligned with JESTER Design System
  const controlBaseStyle: React.CSSProperties = {
    height: "46px",
    borderRadius: "10px",
    border: `1.5px solid ${
      isInputInvalid ? "#AE3534" : "#8F8A83"
    }`,
    backgroundColor: disabled ? "#F3EEE6" : "#FFFFFF",
    color: "#222630",
    fontSize: "0.95rem",
    fontWeight: 500,
    outline: "none",
    transition: "border-color 0.15s ease, box-shadow 0.15s ease",
    boxSizing: "border-box",
    cursor: disabled ? "not-allowed" : "pointer",
  };

  return (
    <fieldset
      id={rootId}
      aria-labelledby={`${rootId}-legend`}
      aria-describedby={
        displayError ? errorId : helperText ? helperId : undefined
      }
      style={{
        border: "none",
        padding: 0,
        margin: "0 0 1rem 0",
        width: "100%",
        boxSizing: "border-box",
        position: "relative",
        zIndex: isYearOpen ? 50 : "auto",
      }}
    >
      {label && (
        <legend
          id={`${rootId}-legend`}
          style={{
            fontSize: "0.875rem",
            fontWeight: 700,
            color: "#0F172A",
            marginBottom: "0.45rem",
            display: "block",
            padding: 0,
          }}
        >
          {label} {required && <span style={{ color: "#E9681F" }}>*</span>}
        </legend>
      )}

      {/* 3 Unified Horizontal Segments (Day / Month / Year) */}
      <div
        style={{
          display: "flex",
          gap: "0.65rem",
          width: "100%",
          boxSizing: "border-box",
          flexWrap: "wrap",
        }}
      >
        {/* SEGMENT 1: DAY (დღე) */}
        <div
          style={{
            flex: "1 1 70px",
            minWidth: "65px",
            display: "flex",
            flexDirection: "column",
            gap: "0.25rem",
          }}
        >
          <label
            htmlFor={dayId}
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              color: "#64748B",
            }}
          >
            დღე
          </label>
          <div style={{ position: "relative", width: "100%" }}>
            <select
              id={dayId}
              name="birth_day"
              value={day}
              onChange={handleDayChange}
              disabled={disabled}
              required={required}
              aria-label="დაბადების დღე"
              aria-invalid={isInputInvalid}
              style={{
                ...controlBaseStyle,
                width: "100%",
                padding: "0 1.5rem 0 0.65rem",
                appearance: "none",
                WebkitAppearance: "none",
                MozAppearance: "none",
              }}
              onFocus={(e) => {
                if (!isInputInvalid) {
                  e.target.style.borderColor = "#9E4215";
                  e.target.style.boxShadow = "0 0 0 2px rgba(158, 66, 21, 0.15)";
                }
              }}
              onBlur={(e) => {
                if (!isInputInvalid) {
                  e.target.style.borderColor = "#8F8A83";
                  e.target.style.boxShadow = "none";
                }
              }}
            >
              <option value="" disabled>
                დღე
              </option>
              {Array.from({ length: maxDays }, (_, i) => {
                const dStr = String(i + 1).padStart(2, "0");
                return (
                  <option key={dStr} value={dStr}>
                    {dStr}
                  </option>
                );
              })}
            </select>
            {/* Custom chevron icon */}
            <span
              aria-hidden="true"
              style={{
                position: "absolute",
                right: "0.6rem",
                top: "50%",
                transform: "translateY(-50%)",
                pointerEvents: "none",
                color: "#64748B",
                fontSize: "0.75rem",
              }}
            >
              ▼
            </span>
          </div>
        </div>

        {/* SEGMENT 2: MONTH (თვე) */}
        <div
          style={{
            flex: "2 1 135px",
            minWidth: "125px",
            display: "flex",
            flexDirection: "column",
            gap: "0.25rem",
          }}
        >
          <label
            htmlFor={monthId}
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              color: "#64748B",
            }}
          >
            თვე
          </label>
          <div style={{ position: "relative", width: "100%" }}>
            <select
              id={monthId}
              name="birth_month"
              value={month}
              onChange={handleMonthChange}
              disabled={disabled}
              required={required}
              aria-label="დაბადების თვე"
              aria-invalid={isInputInvalid}
              style={{
                ...controlBaseStyle,
                width: "100%",
                padding: "0 1.5rem 0 0.65rem",
                appearance: "none",
                WebkitAppearance: "none",
                MozAppearance: "none",
              }}
              onFocus={(e) => {
                if (!isInputInvalid) {
                  e.target.style.borderColor = "#9E4215";
                  e.target.style.boxShadow = "0 0 0 2px rgba(158, 66, 21, 0.15)";
                }
              }}
              onBlur={(e) => {
                if (!isInputInvalid) {
                  e.target.style.borderColor = "#8F8A83";
                  e.target.style.boxShadow = "none";
                }
              }}
            >
              <option value="" disabled>
                თვე
              </option>
              {GEORGIAN_MONTHS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.value} — {m.name}
                </option>
              ))}
            </select>
            <span
              aria-hidden="true"
              style={{
                position: "absolute",
                right: "0.6rem",
                top: "50%",
                transform: "translateY(-50%)",
                pointerEvents: "none",
                color: "#64748B",
                fontSize: "0.75rem",
              }}
            >
              ▼
            </span>
          </div>
        </div>

        {/* SEGMENT 3: YEAR (წელი) — Rapid Searchable Combobox */}
        <div
          ref={yearContainerRef}
          style={{
            flex: "1.2 1 90px",
            minWidth: "85px",
            display: "flex",
            flexDirection: "column",
            gap: "0.25rem",
            position: "relative",
            zIndex: isYearOpen ? 100 : 1,
          }}
        >
          <label
            htmlFor={yearId}
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              color: "#64748B",
            }}
          >
            წელი
          </label>
          <div style={{ position: "relative", width: "100%" }}>
            <input
              ref={yearInputRef}
              id={yearId}
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={4}
              placeholder="წელი"
              value={yearQuery}
              onChange={handleYearInputChange}
              onFocus={() => {
                if (!disabled) setIsYearOpen(true);
              }}
              onKeyDown={handleYearKeyDown}
              disabled={disabled}
              required={required}
              role="combobox"
              aria-expanded={isYearOpen}
              aria-autocomplete="list"
              aria-haspopup="listbox"
              aria-controls={`${rootId}-year-listbox`}
              aria-label="დაბადების წელი"
              aria-invalid={isInputInvalid}
              style={{
                ...controlBaseStyle,
                width: "100%",
                padding: "0 1.6rem 0 0.65rem",
              }}
            />
            {/* Clear or Dropdown Chevron Button */}
            <button
              type="button"
              tabIndex={-1}
              aria-label={isYearOpen ? "წლების სიის დახურვა" : "წლების სიის გახსნა"}
              disabled={disabled}
              onClick={() => {
                if (!disabled) {
                  setIsYearOpen((prev) => !prev);
                  yearInputRef.current?.focus();
                }
              }}
              style={{
                position: "absolute",
                right: "0.45rem",
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                color: "#64748B",
                fontSize: "0.75rem",
                cursor: disabled ? "not-allowed" : "pointer",
                padding: "0.25rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isYearOpen ? "▲" : "▼"}
            </button>
          </div>

          {/* Accessible Rapid Year Selection Popover */}
          {isYearOpen && !disabled && (
            <div
              id={`${rootId}-year-listbox`}
              role="listbox"
              ref={yearListboxRef}
              style={{
                position: "absolute",
                top: "100%",
                right: 0,
                marginTop: "0.35rem",
                width: "275px",
                maxWidth: "92vw",
                backgroundColor: "#FFFFFF",
                borderRadius: "10px",
                border: "1.5px solid #CBD5E1",
                boxShadow:
                  "0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
                zIndex: 1000,
                padding: "0.65rem",
                boxSizing: "border-box",
              }}
            >
              {/* Mode Toggle & Cohort Filter Chips */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "0.45rem",
                  paddingBottom: "0.35rem",
                  borderBottom: "1px solid #F1F5F9",
                }}
              >
                <div style={{ display: "flex", gap: "0.25rem", background: "#F1F5F9", padding: "2px", borderRadius: "6px" }}>
                  <button
                    type="button"
                    onClick={() => {
                      setFilterMode("generations");
                      setSelectedCohort(null);
                    }}
                    style={{
                      fontSize: "0.68rem",
                      padding: "0.15rem 0.45rem",
                      borderRadius: "4px",
                      border: "none",
                      background: filterMode === "generations" ? "#FFFFFF" : "transparent",
                      color: filterMode === "generations" ? "#0F172A" : "#64748B",
                      fontWeight: filterMode === "generations" ? 700 : 500,
                      cursor: "pointer",
                      boxShadow: filterMode === "generations" ? "0 1px 2px rgba(0,0,0,0.08)" : "none",
                    }}
                  >
                    თაობები
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setFilterMode("decades");
                      setSelectedCohort(null);
                    }}
                    style={{
                      fontSize: "0.68rem",
                      padding: "0.15rem 0.45rem",
                      borderRadius: "4px",
                      border: "none",
                      background: filterMode === "decades" ? "#FFFFFF" : "transparent",
                      color: filterMode === "decades" ? "#0F172A" : "#64748B",
                      fontWeight: filterMode === "decades" ? 700 : 500,
                      cursor: "pointer",
                      boxShadow: filterMode === "decades" ? "0 1px 2px rgba(0,0,0,0.08)" : "none",
                    }}
                  >
                    ათწლეულები
                  </button>
                </div>
                <span style={{ fontSize: "0.68rem", color: "#94A3B8" }}>
                  {filterMode === "generations" ? "თაობა" : "ათწლეული"}
                </span>
              </div>

              {/* Generational or Decades Cohort Filter Chips */}
              <div
                style={{
                  display: "flex",
                  gap: "0.35rem",
                  flexWrap: "wrap",
                  marginBottom: "0.55rem",
                  paddingBottom: "0.55rem",
                  borderBottom: "1px solid #E2E8F0",
                }}
              >
                <button
                  type="button"
                  title="ყველა წელი"
                  onClick={() => setSelectedCohort(null)}
                  style={{
                    fontSize: "0.72rem",
                    padding: "0.25rem 0.55rem",
                    borderRadius: "8px",
                    border: selectedCohort === null ? "1.5px solid #FF7A2F" : "1px solid #E2E8F0",
                    backgroundColor: "#FFFFFF",
                    color: selectedCohort === null ? "#E9681F" : "#334155",
                    fontWeight: selectedCohort === null ? 700 : 500,
                    cursor: "pointer",
                    boxShadow: selectedCohort === null ? "0 1px 2px rgba(255, 122, 47, 0.15)" : "none",
                  }}
                >
                  ყველა
                </button>
                {(filterMode === "generations" ? generationOptions : decadeOptions).map((cohort) => {
                  const isSelected = selectedCohort === cohort.id;
                  return (
                    <button
                      key={cohort.id}
                      type="button"
                      title={cohort.tooltip}
                      onClick={() => setSelectedCohort(cohort.id)}
                      style={{
                        fontSize: "0.72rem",
                        padding: "0.25rem 0.55rem",
                        borderRadius: "8px",
                        border: isSelected ? "1.5px solid #FF7A2F" : "1px solid #E2E8F0",
                        backgroundColor: "#FFFFFF",
                        color: isSelected ? "#E9681F" : "#334155",
                        fontWeight: isSelected ? 700 : 500,
                        cursor: "pointer",
                        boxShadow: isSelected ? "0 1px 2px rgba(255, 122, 47, 0.15)" : "none",
                      }}
                    >
                      {cohort.label}
                    </button>
                  );
                })}
              </div>

              {/* Scrollable Years Grid (3 Columns) */}
              <div
                style={{
                  maxHeight: "185px",
                  overflowY: "auto",
                  display: "grid",
                  gridTemplateColumns: "repeat(3, 1fr)",
                  gap: "0.4rem",
                  padding: "0.15rem 0.1rem",
                }}
              >
                {filteredYears.length === 0 ? (
                  <div
                    style={{
                      gridColumn: "1 / -1",
                      textAlign: "center",
                      color: "#94A3B8",
                      fontSize: "0.8rem",
                      padding: "1rem 0",
                    }}
                  >
                    წელი არ მოიძებნა
                  </div>
                ) : (
                  filteredYears.map((y, idx) => {
                    const isSelected = String(y) === year;
                    const isHighlighted = idx === highlightedYearIndex;
                    const isRecommendedAge = y <= maxSuggestedYear;

                    return (
                      <button
                        key={y}
                        type="button"
                        role="option"
                        aria-selected={isSelected}
                        onClick={() => selectYearValue(y)}
                        onMouseEnter={() => setHighlightedYearIndex(idx)}
                        style={{
                          padding: "0.5rem 0.2rem",
                          textAlign: "center",
                          borderRadius: "8px",
                          fontSize: "0.95rem",
                          cursor: "pointer",
                          backgroundColor: isSelected
                            ? "#FF7A2F"
                            : isHighlighted
                            ? "#F1F5F9"
                            : "transparent",
                          color: isSelected
                            ? "#FFFFFF"
                            : isRecommendedAge
                            ? "#0F172A"
                            : "#94A3B8",
                          fontWeight: isSelected ? 800 : isRecommendedAge ? 600 : 400,
                          border: isSelected ? "1px solid #E9681F" : "1px solid transparent",
                          userSelect: "none",
                          transition: "background-color 0.15s ease, color 0.15s ease",
                        }}
                      >
                        {y}
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Helper text or Error Feedback */}
      {displayError ? (
        <div
          id={errorId}
          role="alert"
          aria-live="polite"
          style={{
            marginTop: "0.45rem",
            color: "#AE3534",
            fontSize: "0.8rem",
            fontWeight: 500,
            display: "flex",
            alignItems: "center",
            gap: "0.35rem",
          }}
        >
          <span>⚠️</span>
          <span>{displayError}</span>
        </div>
      ) : helperText ? (
        <div
          id={helperId}
          style={{
            marginTop: "0.45rem",
            color: "#64748B",
            fontSize: "0.8rem",
          }}
        >
          {helperText}
        </div>
      ) : null}
    </fieldset>
  );
};
