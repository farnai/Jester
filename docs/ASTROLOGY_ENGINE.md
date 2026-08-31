# Jester — Astrology Engine Documentation

## 🔮 Overview

The astrology engine in Jester handles astronomical calculations using **PySwissEph** (Python C-bindings for the Swiss Ephemeris library). It provides high-precision planetary longitudes, house cusps, and retrograde speed checks.

---

## 🛠️ Implementation Details & Math

### 1. Julian Day Calculation (`compute_julian_day`)
- **Input**: Local `birth_date` (`datetime.date`), optional `birth_time` (`datetime.time`), and `birth_timezone` (IANA timezone string).
- **Timezone Conversion**: Uses Python's native `zoneinfo.ZoneInfo(birth_timezone)`.
- **Exact / Approximate Time**:
  ```python
  dt_local = datetime.combine(birth_date, birth_time, tzinfo=ZoneInfo(birth_timezone))
  dt_utc = dt_local.astimezone(timezone.utc)
  hour_utc = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0 + dt_utc.microsecond / 3600000000.0
  jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_utc)
  ```
- **Unknown Time**: When `birth_time` is `None` (`birth_time_precision = 'unknown'`), uses **12:00 UTC (mean noon)**:
  ```python
  jd = swe.julday(birth_date.year, birth_date.month, birth_date.day, 12.0)
  ```

### 2. Planetary Bodies Calculation (`compute_natal_placements`)
Calculates positions using `swe.calc_ut` with default flags `swe.FLG_SWIEPH | swe.FLG_SPEED`:
- **Calculated Longitude**: Normalized to $[0^\circ, 360^\circ)$ using `lon % 360.0` and rounded to 6 decimal places.
- **Retrograde Detection**: Evaluates ecliptic longitude speed (`speed_lon = res[3]`). If `speed_lon < 0.0`, `retrogrades[planet_name] = True`.

### 3. Houses & Ascendant Calculation
- **Method**: Calls `swe.houses(jd, latitude, longitude, b"P")` (Placidus system).
- **House Cusps**: Returns a 12-element list of float longitudes rounded to 6 decimal places.
- **Ascendant**: Extracted from `ascmc_tuple[0] % 360.0`.
- **Unknown Time Guard**: If `birth_time_precision == 'unknown'`, Ascendant and Houses are strictly set to `None`.
- **Polar Region Error Handling**: Placidus is mathematically undefined at latitudes $> 66.5^\circ$. In these cases, `swe.houses` throws `swe.Error` which is caught and raised as `placidus_polar_error` (HTTP 400).

### 4. Zodiac Sign & Element / Modality Mapping
- **`longitude_to_sign`**: Maps longitude in $[0^\circ, 360^\circ)$ to 12 tropical Zodiac signs ($30^\circ$ segments starting at Aries $= 0^\circ$).
- **Dominant Element & Modality Derivation (`derive_primary_element_and_modality`)**:
  Computes element and modality scores using weighted placement counts:
  - **Sun**: Weight = 3
  - **Moon**: Weight = 3
  - **Ascendant**: Weight = 3 (if present)
  - **Mercury**: Weight = 2
  - **Venus**: Weight = 2
  - **Mars**: Weight = 2

---

## 🚦 Feature Status Inventory

| Feature | Status | Details |
| :--- | :--- | :--- |
| **PySwissEph C Integration** | **IMPLEMENTED** | Uses `swisseph` library flags `FLG_SWIEPH \| FLG_SPEED`. |
| **Julian Day & UTC Conversion** | **IMPLEMENTED** | Accurate IANA timezone handling via `zoneinfo.ZoneInfo`. |
| **10 Main Planetary Bodies** | **IMPLEMENTED** | Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto. |
| **Retrograde Speed Detection** | **IMPLEMENTED** | `speed_lon < 0.0` evaluated for all 10 planets. |
| **Zodiac Sign Mapping** | **IMPLEMENTED** | $30^\circ$ tropical Zodiac sign boundaries. |
| **Placidus House Calculation** | **IMPLEMENTED** | 12 house cusps calculated via `swe.houses(..., b"P")`. |
| **Ascendant Calculation** | **IMPLEMENTED** | Ascendant longitude extracted and mapped to sign. |
| **Primary Element / Modality Weighting**| **IMPLEMENTED** | Weighted counter algorithm for Fire/Earth/Air/Water & Cardinal/Fixed/Mutable. |
| **MC / IC / DC Points** | **MISSING** | Midheaven (MC), IC, and Descendant longitudes are not saved in `astro_private`. |
| **Planetary Aspects & Orbs** | **MISSING** | Zero angular aspect calculations (Conjunction, Trine, Square, etc.) exist. |
| **North Node / South Node** | **MISSING** | Lunar Nodes (`swe.MEAN_NODE` / `swe.TRUE_NODE`) are not calculated. |
| **Chiron & Lilith** | **MISSING** | Chiron (`swe.CHIRON`) and Black Moon Lilith (`swe.MEAN_LILITH`) are not calculated. |
| **Asteroids & Part of Fortune** | **MISSING** | Ceres, Pallas, Juno, Vesta, and Part of Fortune are not calculated. |
| **Alternative House Systems** | **MISSING** | No fallback to Whole Sign (`b"W"`) or Equal House when Placidus fails. |
| **Daily Planetary Transits** | **STUB** | `backend/app/astrology/transits.py` is empty (47 bytes). |
| **Synastry Overlay Engine** | **STUB** | `backend/app/comparisons/router.py` returns hardcoded baseline score (`82.5`). |

---

## 🛑 Limitations & Current Technical Constraints

1. **`backend/app/astrology/calculator.py` Constraints**:
   - Computes **only** the 10 core planets (Sun to Pluto).
   - Lacks aspect math (no orbs, no angular distance matrices).
   - Hardcodes Placidus house system. Crashes/errors on polar coordinates ($> 66.5^\circ$) without fallback.

2. **`backend/app/astrology/transits.py` Constraints**:
   - Contains no implementation code.

3. **Synastry & Compatibility Constraints**:
   - `comparisons/router.py` does not compare natal longitudes between two users. It returns a static score `82.5`.
