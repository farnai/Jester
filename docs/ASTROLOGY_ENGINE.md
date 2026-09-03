# Jester — Astrology Engine Documentation

## 🔮 Overview & Strategic Role

The astrology engine in Jester handles astronomical calculations using **PySwissEph** (Python C-bindings for the Swiss Ephemeris library) and provides a deterministic **Synastry V1** cross-chart compatibility scoring engine.

### Strategic Role:
In the JESTER product architecture, **astrology is the underlying deterministic intelligence layer, not the consumer brand or product identity**. Jester uses astrology strictly to power **People Discovery and Relationship Intelligence**.

```text
ASTROLOGICAL DATA
       ↓ (PySwissEph C Engine)
DETERMINISTIC SIGNALS & ASPECTS (aspects.py)
       ↓ (Rule-Based Aggregator)
CORE INTERPERSONAL DYNAMICS & MEANING
       ↓ (SynastryEngine / transits.py)
RELATIONSHIP / PERSONAL CONTEXT
       ↓ (Prompt Formatter with JESTER Voice Persona)
JESTER VOICE TRANSFORMATION
       ↓ (Structured Models)
USER-FACING INSIGHT (Short, witty, human-readable)
```

**Core Principle**: JESTER does not invent astrological meaning. The ephemeris and aspect engines produce exact mathematical signals; downstream interpretation layers convert those signals into human, witty JESTER observations.


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

### 5. Aspects Calculation & Orb Model (`backend/app/astrology/aspects.py`)
- Supported aspect angles: Conjunction ($0^\circ$), Sextile ($60^\circ$), Square ($90^\circ$), Trine ($120^\circ$), Opposition ($180^\circ$).
- Quadratic decay strength: $S_{\text{aspect}} = \left(1.0 - \frac{\delta}{\text{Orb}_{\text{max}}}\right)^2$.
- Luminary boost (+2.0°) and Ascendant constraint (capped at 6.0°).

### 6. Synastry V1 Engine (`backend/app/compatibility/`)
- Multi-dimensional scoring ($S_{\text{harmony}}$, $S_{\text{communication}}$, $S_{\text{attraction}}$, $S_{\text{growth}}$).
- Weighted planet-pair matrix, influence caps ($\pm 18.0$ per pair, outer aspect $+12.0$ combined cap), and non-linear stretch curve ($10.0 - 98.0$).
- Deterministic signal extraction, topic recommendations, conversation starters, and full audit evidence trace.

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
| **Planetary Aspects & Orbs** | **IMPLEMENTED** | Conjunction, Sextile, Square, Trine, Opposition with quadratic decay. |
| **Synastry Overlay Engine** | **IMPLEMENTED** | Deterministic Synastry V1 engine (`synastry-v1.0.0`). |
| **MC / IC / DC Points** | **MISSING** | Midheaven (MC), IC, and Descendant longitudes are not saved in `astro_private`. |
| **North Node / South Node** | **MISSING** | Lunar Nodes (`swe.MEAN_NODE` / `swe.TRUE_NODE`) are not calculated. |
| **Chiron & Lilith** | **MISSING** | Chiron (`swe.CHIRON`) and Black Moon Lilith (`swe.MEAN_LILITH`) are not calculated. |
| **Asteroids & Part of Fortune** | **MISSING** | Ceres, Pallas, Juno, Vesta, and Part of Fortune are not calculated. |
| **Alternative House Systems** | **MISSING** | No fallback to Whole Sign (`b"W"`) or Equal House when Placidus fails. |
| **Daily Planetary Transits** | **STUB** | `backend/app/astrology/transits.py` is empty (47 bytes). |

---

## 🛑 Limitations & Current Technical Constraints

1. **`backend/app/astrology/calculator.py` Constraints**:
   - Computes **only** the 10 core planets (Sun to Pluto).
   - Hardcodes Placidus house system. Crashes/errors on polar coordinates ($> 66.5^\circ$) without fallback.

2. **`backend/app/astrology/transits.py` Constraints**:
   - Contains no implementation code.
