import React, { useState, useEffect, useRef, useId } from "react";
import { API } from "../../core/api/endpoints";
import { CitySearchResult } from "../../core/api/types";

export interface SelectedCityValue {
  city_id: string;
  name: string;
  display_name: string;
  country_name: string;
  country_code: string;
  region: string | null;
}

export interface CitySelectorProps {
  value: string | null;
  initialDisplayLabel?: string;
  onChange: (city: SelectedCityValue) => void;
  onClear?: () => void;
  label?: string;
  helperText?: string;
  error?: string | null;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
}

export const CitySelector: React.FC<CitySelectorProps> = ({
  value,
  initialDisplayLabel,
  onChange,
  onClear,
  label = "ქალაქი (City)",
  helperText,
  error,
  placeholder = "მაგ. თბილისი, Batumi, London, Berlin...",
  disabled = false,
  required = false,
}) => {
  const componentId = useId();
  const inputId = `city-selector-${componentId}`;

  // Input & search state
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [popularCities, setPopularCities] = useState<CitySearchResult[]>([]);
  const [searchResults, setSearchResults] = useState<CitySearchResult[]>([]);
  const [activeIndex, setActiveIndex] = useState<number>(-1);
  const [selectedDisplay, setSelectedDisplay] = useState<string | null>(initialDisplayLabel || null);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const debounceTimerRef = useRef<number | null>(null);

  // 1. Initial resolution: fetch popular cities (top 10 Georgian hubs)
  useEffect(() => {
    let isMounted = true;
    API.geo
      .searchCities("", 10)
      .then((res) => {
        if (isMounted) {
          setPopularCities(res.items);
        }
      })
      .catch((err) => {
        console.warn("Could not preload popular cities:", err);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // 2. Resolve display label if value is set but display label is not yet known
  useEffect(() => {
    if (value && !selectedDisplay) {
      let isMounted = true;
      API.geo
        .getCity(value)
        .then((city) => {
          if (isMounted) {
            setSelectedDisplay(city.display_name);
          }
        })
        .catch(() => {
          // Graceful fallback
        });
      return () => {
        isMounted = false;
      };
    } else if (!value) {
      setSelectedDisplay(null);
    }
  }, [value, selectedDisplay]);

  // 3. Debounced Search Execution with AbortController
  useEffect(() => {
    const cleanQ = query.trim();

    // 0 characters -> show popular cities
    if (!cleanQ) {
      setSearchResults([]);
      setIsLoading(false);
      setFetchError(null);
      return;
    }

    // 1 character -> do not call backend
    if (cleanQ.length < 2) {
      setSearchResults([]);
      setIsLoading(false);
      setFetchError(null);
      return;
    }

    // Cancel prior pending debounce
    if (debounceTimerRef.current) {
      window.clearTimeout(debounceTimerRef.current);
    }

    setIsLoading(true);
    setFetchError(null);

    debounceTimerRef.current = window.setTimeout(() => {
      // Abort previous in-flight request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      API.geo
        .searchCities(cleanQ, 10, controller.signal)
        .then((res) => {
          setSearchResults(res.items);
          setActiveIndex(-1);
          setIsLoading(false);
        })
        .catch((err) => {
          if (err.name !== "AbortError") {
            console.error("City search failed:", err);
            setFetchError("ქალაქების მოძიება ვერ მოხერხდა.");
            setIsLoading(false);
          }
        });
    }, 250);

    return () => {
      if (debounceTimerRef.current) {
        window.clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query]);

  // 4. Click outside handler to dismiss dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Selection action
  const handleSelectCity = (city: CitySearchResult) => {
    const display = `${city.display_name}, ${city.country_name}`;
    setSelectedDisplay(display);
    setQuery("");
    setIsOpen(false);
    setActiveIndex(-1);
    setFetchError(null);

    onChange({
      city_id: city.city_id,
      name: city.name,
      display_name: city.display_name,
      country_name: city.country_name,
      country_code: city.country_code,
      region: city.region,
    });
  };

  // Clear / Change action
  const handleClear = () => {
    setSelectedDisplay(null);
    setQuery("");
    setIsOpen(true);
    setActiveIndex(-1);
    if (onClear) {
      onClear();
    }
    setTimeout(() => {
      inputRef.current?.focus();
    }, 50);
  };

  // Keyboard navigation
  const currentList = query.trim().length >= 2 ? searchResults : popularCities;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen) {
      if (e.key === "ArrowDown" || e.key === "Enter") {
        setIsOpen(true);
      }
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => (prev + 1 < currentList.length ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev - 1 >= 0 ? prev - 1 : currentList.length - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIndex >= 0 && activeIndex < currentList.length) {
        handleSelectCity(currentList[activeIndex]);
      }
    } else if (e.key === "Escape") {
      e.preventDefault();
      setIsOpen(false);
      setActiveIndex(-1);
    }
  };

  // Highlight matching portion of string
  const renderHighlighted = (text: string, highlight: string) => {
    if (!highlight.trim()) return text;
    const cleanHighlight = highlight.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const parts = text.split(new RegExp(`(${cleanHighlight})`, "gi"));
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === highlight.trim().toLowerCase() ? (
            <strong key={i} style={{ color: "#4f46e5", fontWeight: 700 }}>
              {part}
            </strong>
          ) : (
            part
          )
        )}
      </span>
    );
  };

  return (
    <div
      ref={containerRef}
      style={{
        position: "relative",
        width: "100%",
        marginBottom: "1rem",
        fontFamily: "inherit",
      }}
    >
      {/* Label */}
      {label && (
        <label
          htmlFor={inputId}
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: "0.85rem",
            fontWeight: 600,
            color: "#1e293b",
            marginBottom: "0.35rem",
          }}
        >
          <span>
            {label} {required && <span style={{ color: "#ef4444" }}>*</span>}
          </span>
          {value && (
            <span style={{ fontSize: "0.75rem", color: "#10b981", fontWeight: 700 }}>
              ✓ არჩეულია
            </span>
          )}
        </label>
      )}

      {/* STATE F: SELECTED STATE CARD */}
      {value && selectedDisplay ? (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0.85rem 1rem",
            backgroundColor: "#f8fafc",
            border: "1.5px solid #6366f1",
            borderRadius: "8px",
            boxShadow: "0 1px 3px rgba(99, 102, 241, 0.1)",
            transition: "all 0.15s ease",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span style={{ fontSize: "1.2rem" }}>📍</span>
            <div>
              <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#0f172a" }}>
                {selectedDisplay}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                კანონიკური ლოკაცია დადასტურებულია
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleClear}
            disabled={disabled}
            style={{
              padding: "0.4rem 0.75rem",
              fontSize: "0.8rem",
              fontWeight: 600,
              backgroundColor: "#ffffff",
              color: "#6366f1",
              border: "1px solid #c7d2fe",
              borderRadius: "6px",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            შეცვლა / Change
          </button>
        </div>
      ) : (
        /* STATE A - E: SEARCH INPUT & AUTOCOMPLETE */
        <>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              backgroundColor: disabled ? "#f8fafc" : "#ffffff",
              border: `1.5px solid ${error ? "#ef4444" : isOpen ? "#6366f1" : "#cbd5e1"}`,
              borderRadius: "8px",
              padding: "0 0.75rem",
              minHeight: "44px",
              transition: "border-color 0.15s ease",
              boxSizing: "border-box",
            }}
          >
            <span style={{ marginRight: "0.5rem", color: "#64748b", display: "flex" }}>
              🔍
            </span>

            <input
              ref={inputRef}
              id={inputId}
              type="text"
              autoComplete="off"
              disabled={disabled}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setIsOpen(true);
              }}
              onFocus={() => setIsOpen(true)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              style={{
                flex: 1,
                border: "none",
                outline: "none",
                background: "transparent",
                fontSize: "0.95rem",
                color: "#0f172a",
                padding: "0.6rem 0",
                minWidth: 0,
              }}
            />

            {isLoading && (
              <span
                style={{
                  fontSize: "0.9rem",
                  marginLeft: "0.5rem",
                  animation: "spin 1s linear infinite",
                  display: "inline-block",
                }}
              >
                ⌛
              </span>
            )}
          </div>

          {/* DROPDOWN POPUP */}
          {isOpen && !disabled && (
            <div
              style={{
                position: "absolute",
                top: "calc(100% + 4px)",
                left: 0,
                right: 0,
                backgroundColor: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05)",
                maxHeight: "280px",
                overflowY: "auto",
                zIndex: 50,
                padding: "0.4rem",
              }}
            >
              {fetchError ? (
                <div style={{ padding: "0.75rem", fontSize: "0.85rem", color: "#ef4444", textAlign: "center" }}>
                  ⚠️ {fetchError}
                </div>
              ) : query.trim().length === 1 ? (
                /* Hint for 1 character */
                <div style={{ padding: "0.6rem 0.8rem", fontSize: "0.825rem", color: "#64748b", textAlign: "center" }}>
                  შეიყვანეთ მინიმუმ 2 სიმბოლო ქალაქის მოსაძებნად...
                </div>
              ) : query.trim().length >= 2 ? (
                /* STATE D: Search Results */
                searchResults.length === 0 && !isLoading ? (
                  /* STATE E: No Results */
                  <div style={{ padding: "1rem", fontSize: "0.85rem", color: "#64748b", textAlign: "center" }}>
                    <div>ქალაქი ვერ მოიძებნა (No city found)</div>
                    <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "4px" }}>
                      სცადეთ ინგლისურად ან ქართული ტრანსლიტერაციით (მაგ. Tbilisi, Batumi, London...)
                    </div>
                  </div>
                ) : (
                  searchResults.map((city, idx) => {
                    const isHighlighted = idx === activeIndex;
                    const subtitle = city.region
                      ? `${city.region}, ${city.country_name}`
                      : city.country_name;

                    return (
                      <div
                        key={city.city_id}
                        onMouseEnter={() => setActiveIndex(idx)}
                        onClick={() => handleSelectCity(city)}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "0.6rem 0.8rem",
                          borderRadius: "6px",
                          backgroundColor: isHighlighted ? "#eef2ff" : "transparent",
                          cursor: "pointer",
                          transition: "background-color 0.1s ease",
                        }}
                      >
                        <div>
                          <div
                            style={{
                              fontSize: "0.9rem",
                              fontWeight: 600,
                              color: isHighlighted ? "#4338ca" : "#0f172a",
                            }}
                          >
                            📍 {renderHighlighted(city.display_name, query)}
                          </div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "2px" }}>
                            {subtitle}
                          </div>
                        </div>

                        <span style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: 600 }}>
                          {city.country_code}
                        </span>
                      </div>
                    );
                  })
                )
              ) : (
                /* STATE A: Empty Query -> Popular Georgian Cities */
                <div>
                  <div
                    style={{
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      color: "#64748b",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      padding: "0.3rem 0.6rem 0.4rem 0.6rem",
                    }}
                  >
                    პოპულარული ქალაქები (საქართველო):
                  </div>

                  {popularCities.map((city, idx) => {
                    const isHighlighted = idx === activeIndex;
                    const subtitle = city.region
                      ? `${city.region}, ${city.country_name}`
                      : city.country_name;

                    return (
                      <div
                        key={city.city_id}
                        onMouseEnter={() => setActiveIndex(idx)}
                        onClick={() => handleSelectCity(city)}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "0.55rem 0.8rem",
                          borderRadius: "6px",
                          backgroundColor: isHighlighted ? "#eef2ff" : "transparent",
                          cursor: "pointer",
                          transition: "background-color 0.1s ease",
                        }}
                      >
                        <div>
                          <div
                            style={{
                              fontSize: "0.875rem",
                              fontWeight: 600,
                              color: isHighlighted ? "#4338ca" : "#0f172a",
                            }}
                          >
                            📍 {city.display_name}
                          </div>
                          <div style={{ fontSize: "0.725rem", color: "#64748b", marginTop: "1px" }}>
                            {subtitle}
                          </div>
                        </div>

                        <span style={{ fontSize: "0.7rem", color: "#94a3b8", fontWeight: 600 }}>
                          {city.country_code}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Error and Helper Text */}
      {error ? (
        <span style={{ fontSize: "0.8rem", color: "#ef4444", marginTop: "0.3rem", display: "block" }}>
          ⚠️ {error}
        </span>
      ) : helperText ? (
        <span style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.3rem", display: "block" }}>
          {helperText}
        </span>
      ) : null}
    </div>
  );
};
