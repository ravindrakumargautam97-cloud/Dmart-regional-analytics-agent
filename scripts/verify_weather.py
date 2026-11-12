
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.weather import get_weather

data = json.loads(
    (ROOT / "eval/eval_results.json").read_text(
        encoding="utf-8"
    )
)

cases = [
    x for x in data["results"]
    if x["category"] == "weather"
]

passed = 0

print("WEATHER STUB VERIFICATION")
print("-" * 45)

for case in cases:
    answer = case["answer"]

    match = re.search(
        r"(Mumbai|Pune|Hyderabad|Bengaluru|Ahmedabad)"
        r" weather on (\d{4}-\d{2}-\d{2})",
        answer
    )

    ok = False

    if match:
        city, date = match.groups()

        weather = get_weather(city, date, mode="stub")
        repeat = get_weather(city, date, mode="stub")

        expected = [
            f"temperature {weather['temperature_c']} C",
            f"humidity {weather['humidity_pct']}%",
            f"wind speed {weather['wind_speed_kmh']} km/h",
            f"rainfall {weather['rainfall_mm']:.1f} mm",
            "simulated weather",
        ]

        ok = (
            weather == repeat
            and all(value in answer for value in expected)
        )

    if ok:
        passed += 1

    print(case["id"], "PASS" if ok else "FAIL")

print("-" * 45)
print("Verified:", passed, "/", len(cases))

