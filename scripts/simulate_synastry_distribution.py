"""
Synastry V1 Distribution Simulation
Calculates compatibility across 50,000+ unique synthetic pairs using the frozen Synastry V1 engine.
Outputs statistical metrics, percentiles, bucket counts, and evaluates calibration candidates.
"""
import math
import random
import statistics
import uuid
from datetime import date, time

from backend.app.astrology.calculator import compute_natal_placements
from backend.app.astrology.models import BirthDataInput
from backend.app.compatibility.synastry import NatalInputPayload, SynastryEngine

CITIES = [
    {"lat": 41.7151, "lon": 44.8271, "tz": "Asia/Tbilisi", "name": "Tbilisi"},
    {"lat": 41.6416, "lon": 41.6359, "tz": "Asia/Tbilisi", "name": "Batumi"},
    {"lat": 42.2679, "lon": 42.6946, "tz": "Asia/Tbilisi", "name": "Kutaisi"},
    {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "name": "New York"},
    {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "name": "London"},
    {"lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin", "name": "Berlin"},
    {"lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris", "name": "Paris"},
    {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo", "name": "Tokyo"},
]

def generate_population(n: int = 350, seed: int = 42) -> list[NatalInputPayload]:
    random.seed(seed)
    people: list[NatalInputPayload] = []
    
    for i in range(n):
        year = random.randint(1975, 2004)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        city = random.choice(CITIES)
        
        is_unknown = random.random() < 0.10
        precision = "unknown" if is_unknown else "exact"
        b_time = None if is_unknown else time(hour, minute)
        lat = None if is_unknown else city["lat"]
        lon = None if is_unknown else city["lon"]
        
        bd = BirthDataInput(
            birth_date=date(year, month, day),
            birth_time=b_time,
            birth_time_precision=precision,
            birth_timezone=city["tz"],
            latitude=lat,
            longitude=lon,
            place_label=city["name"],
        )
        
        placements = compute_natal_placements(bd)
        
        # Convert to planet_longitudes dict format expected by NatalInputPayload
        planets_dict = {}
        for p in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]:
            planets_dict[p] = getattr(placements, f"{p}_longitude")
            
        people.append(NatalInputPayload(
            user_id=uuid.uuid4(),
            birth_data_version=1,
            birth_time_precision=precision,
            planet_longitudes=planets_dict,
            ascendant_longitude=placements.ascendant_longitude,
            retrogrades=placements.retrogrades,
        ))
        
    return people


def run_simulation(n_people: int = 350):
    print(f"Generating {n_people} synthetic charts via Swiss Ephemeris...")
    population = generate_population(n_people)
    engine = SynastryEngine()
    
    total_pairs = (n_people * (n_people - 1)) // 2
    print(f"Running Synastry V1 on {total_pairs:,} unique pairs...")
    
    raw_overall_list = []
    harmony_list = []
    attraction_list = []
    communication_list = []
    growth_list = []
    final_score_list = []
    
    for i in range(n_people):
        p_a = population[i]
        for j in range(i + 1, n_people):
            p_b = population[j]
            res = engine.calculate(p_a, p_b)
            
            s_h = res.dimensions["emotional_harmony"]
            s_a = res.dimensions["attraction"]
            s_c = res.dimensions["communication"]
            s_g = res.dimensions["growth_long_term"]
            
            raw = 0.30 * s_h + 0.30 * s_a + 0.20 * s_c + 0.20 * s_g
            
            raw_overall_list.append(raw)
            harmony_list.append(s_h)
            attraction_list.append(s_a)
            communication_list.append(s_c)
            growth_list.append(s_g)
            final_score_list.append(res.score)
            
    print(f"Simulation completed for {len(final_score_list):,} pairs.")
    return {
        "raw_overall": raw_overall_list,
        "harmony": harmony_list,
        "attraction": attraction_list,
        "communication": communication_list,
        "growth": growth_list,
        "final_score": final_score_list,
    }


def compute_percentile(sorted_data: list[float], p: float) -> float:
    if not sorted_data:
        return 0.0
    if p <= 0:
        return sorted_data[0]
    if p >= 100:
        return sorted_data[-1]
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[int(f)] * (c - k) + sorted_data[int(c)] * (k - f)


def analyze_and_print(results: dict[str, list[float]]):
    percentiles = [0, 5, 10, 25, 50, 75, 90, 95, 99, 100]
    
    print("\n" + "=" * 80)
    print("JESTER SYNASTRY V1 — 50,000+ PAIR DISTRIBUTION ANALYSIS REPORT")
    print("=" * 80)
    
    n_pairs = len(results["final_score"])
    print(f"Total Evaluated Unique Pairs: {n_pairs:,}")
    
    metrics = ["raw_overall", "final_score", "harmony", "attraction", "communication", "growth"]
    
    header = f"{'Metric':<18} | {'Min':>6} | {'P5':>6} | {'P10':>6} | {'P25':>6} | {'Median':>6} | {'P75':>6} | {'P90':>6} | {'P95':>6} | {'P99':>6} | {'Max':>6} | {'Mean':>6} | {'Std':>5}"
    print("\n" + header)
    print("-" * len(header))
    
    for m in metrics:
        data = sorted(results[m])
        p_vals = [compute_percentile(data, p) for p in percentiles]
        mean_val = statistics.mean(data)
        std_val = statistics.stdev(data)
        
        print(f"{m:<18} | {p_vals[0]:6.1f} | {p_vals[1]:6.1f} | {p_vals[2]:6.1f} | {p_vals[3]:6.1f} | {p_vals[4]:6.1f} | {p_vals[5]:6.1f} | {p_vals[6]:6.1f} | {p_vals[7]:6.1f} | {p_vals[8]:6.1f} | {p_vals[9]:6.1f} | {mean_val:6.1f} | {std_val:5.1f}")
        
    print("\n" + "=" * 80)
    print("SCORE BUCKET DISTRIBUTION (CURRENT FINAL SCORE)")
    print("=" * 80)
    
    buckets = [
        ("0–39", 0.0, 39.99),
        ("40–49", 40.0, 49.99),
        ("50–59", 50.0, 59.99),
        ("60–69", 60.0, 69.99),
        ("70–79", 70.0, 79.99),
        ("80–89", 80.0, 89.99),
        ("90–97", 90.0, 97.99),
        ("98+", 98.0, 100.0),
    ]
    
    final_scores = results["final_score"]
    raw_scores = results["raw_overall"]
    
    print(f"{'Bucket':<10} | {'Raw Count':>10} | {'Raw %':>8} | {'Final Count':>12} | {'Final %':>8}")
    print("-" * 56)
    
    for label, low, high in buckets:
        cnt_raw = sum(1 for s in raw_scores if low <= s <= high)
        pct_raw = (cnt_raw / n_pairs) * 100.0
        
        cnt_final = sum(1 for s in final_scores if low <= s <= high)
        pct_final = (cnt_final / n_pairs) * 100.0
        
        print(f"{label:<10} | {cnt_raw:10d} | {pct_raw:7.2f}% | {cnt_final:12d} | {pct_final:7.2f}%")
        
    print("\n" + "=" * 80)
    print("CALIBRATION CANDIDATE EVALUATION")
    print("=" * 80)
    
    # Candidate 1: Enhanced Sigmoid Stretch (Soft S-Curve)
    def calib_candidate_1(r: float) -> float:
        z = (r - 57.0) / 7.5
        sig = 1.0 / (1.0 + math.exp(-z))
        return round(15.0 + 80.0 * sig, 1)

    # Candidate 2: Piecewise Power-Law Stretch (Monotonic & Symmetric Around 50)
    def calib_candidate_2(r: float) -> float:
        c = (r - 50.0) / 50.0
        sgn = 1.0 if c >= 0 else -1.0
        stretched = 50.0 + 50.0 * sgn * (abs(c) ** 0.65)
        return round(max(10.0, min(96.0, stretched)), 1)

    # Candidate 3: Quantile-Aligned Piecewise Linear Anchor (Anchored at P10=40, P50=65, P90=85)
    def calib_candidate_3(r: float) -> float:
        if r <= 50.0:
            val = 15.0 + (r - 25.0) * (35.0 / 25.0)
        elif r <= 65.0:
            val = 50.0 + (r - 50.0) * (28.0 / 15.0)
        else:
            val = 78.0 + (r - 65.0) * (18.0 / 20.0)
        return round(max(10.0, min(97.0, val)), 1)

    test_raws = [45.0, 50.0, 53.8, 58.1, 60.2, 61.4, 61.6, 61.9, 62.4, 63.8, 70.0, 75.0, 80.0, 85.0]
    print(f"\n{'Raw Score':<10} | {'Current Final':<15} | {'Cand 1 (Logistic)':<18} | {'Cand 2 (Power-0.65)':<20} | {'Cand 3 (Piecewise Anchor)':<25}")
    print("-" * 95)
    for r in test_raws:
        c = (r - 50.0) / 50.0
        sgn = 1.0 if c >= 0 else -1.0
        cur_final = round(max(10.0, min(98.0, 50.0 + 50.0 * sgn * (abs(c) ** 0.85))), 1)
        c1 = calib_candidate_1(r)
        c2 = calib_candidate_2(r)
        c3 = calib_candidate_3(r)
        print(f"{r:<10.1f} | {cur_final:<15.1f} | {c1:<18.1f} | {c2:<20.1f} | {c3:<25.1f}")


if __name__ == "__main__":
    res = run_simulation(350)
    analyze_and_print(res)
