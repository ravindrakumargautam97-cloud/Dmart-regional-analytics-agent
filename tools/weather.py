
import os
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.3850, 78.4867),
    "Bengaluru": (12.9716, 77.5946),
    "Ahmedabad": (23.0225, 72.5714),
}

FIXED_STUB = {
    ("Mumbai", "2026-05-15"): (26.0, 43.0, 10.0, 0.0),
    ("Pune", "2026-05-16"): (25.0, 88.0, 11.0, 6.5),
    ("Hyderabad", "2026-04-01"): (30.0, 58.0, 6.0, 0.0),
}


def get_weather(city, date, mode=None):
    """Return offline stub or historical Open-Meteo weather."""

    if city not in CITY_COORDINATES:
        raise ValueError("Unsupported city")

    parsed_date = datetime.strptime(date, "%Y-%m-%d")
    date = parsed_date.date().isoformat()

    if mode is None:
        mode = os.getenv("WEATHER_MODE", "stub").lower()

    if mode == "stub":
        if (city, date) in FIXED_STUB:
            values = FIXED_STUB[(city, date)]
        else:
            day = parsed_date.timetuple().tm_yday
            length = len(city)

            values = (
                float(20 + (length + day) % 15),
                float(40 + (3 * length + day) % 50),
                float(5 + day % 10),
                6.5 if day % 4 == 0 else 0.0,
            )

        return {
            "city": city,
            "date": date,
            "temperature_c": values[0],
            "humidity_pct": values[1],
            "wind_speed_kmh": values[2],
            "rainfall_mm": values[3],
            "mode": "stub",
            "source": "Deterministic offline weather stub",
        }

    if mode != "live":
        raise ValueError("WEATHER_MODE must be stub or live")

    latitude, longitude = CITY_COORDINATES[city]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,
        "timezone": "Asia/Kolkata",
        "daily": ",".join([
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "wind_speed_10m_max",
            "precipitation_sum",
        ]),
    }

    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        + urlencode(params)
    )

    try:
        import json

        with urlopen(url, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"Weather API returned HTTP {response.status}"
                )

            payload = json.load(response)

        daily = payload.get("daily", {})

        required = [
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "wind_speed_10m_max",
            "precipitation_sum",
        ]

        if any(
            not isinstance(daily.get(field), list)
            or not daily[field]
            or daily[field][0] is None
            for field in required
        ):
            raise RuntimeError(
                "Weather API returned incomplete daily data"
            )

        return {
            "city": city,
            "date": date,
            "temperature_c": float(
                daily["temperature_2m_mean"][0]
            ),
            "humidity_pct": float(
                daily["relative_humidity_2m_mean"][0]
            ),
            "wind_speed_kmh": float(
                daily["wind_speed_10m_max"][0]
            ),
            "rainfall_mm": float(
                daily["precipitation_sum"][0]
            ),
            "mode": "live",
            "source": "Open-Meteo Historical Weather API",
        }

    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"Weather API connection failed: {exc}"
        ) from exc
    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(
            f"Invalid weather API response: {exc}"
        ) from exc
