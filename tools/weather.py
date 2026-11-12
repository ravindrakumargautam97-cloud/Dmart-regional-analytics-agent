
from datetime import datetime

CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.3850, 78.4867),
    "Bengaluru": (12.9716, 77.5946),
    "Ahmedabad": (23.0225, 72.5714),
}


def get_weather(city, date, mode="stub"):
    if city not in CITY_COORDINATES:
        raise ValueError("Unsupported city")

    selected_date = datetime.strptime(date, "%Y-%m-%d")

    if mode != "stub":
        raise ValueError("Live mode is not implemented yet")

    day_of_year = selected_date.timetuple().tm_yday
    city_length = len(city)

    temperature = 20 + (city_length + day_of_year) % 15
    humidity = 40 + (3 * city_length + day_of_year) % 50
    wind_speed = 5 + day_of_year % 10
    rainfall = 6.5 if day_of_year % 4 == 0 else 0.0

    return {
        "city": city,
        "date": date,
        "temperature_c": temperature,
        "humidity_pct": humidity,
        "wind_speed_kmh": wind_speed,
        "rainfall_mm": rainfall,
        "mode": "stub",
        "source": "Deterministic offline weather stub",
    }
