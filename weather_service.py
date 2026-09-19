import requests
import logging
from datetime import datetime

rain_umbrella_threshold = 50
hot_temperature_threshold = 33

def format_time(iso_time_str):

    parsed_time = datetime.strptime(iso_time_str, "%Y-%m-%dT%H:%M")
    return parsed_time.strftime("%I:%M %p")

def geocode_location(location_name):
     
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location_name,
        "count": 10
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = data.get("results", [])

    if not results:
        return None, "No matched. Please check spelling."

    philippine_matches = [r for r in results if r.get("country_code") == "PH"]

    if not philippine_matches:
        return None, "No Philippine location found with that name."

    best_match = max(philippine_matches, key=lambda r: r.get("population", 0))

    latitude = best_match["latitude"]
    longitude = best_match["longitude"]

    return (latitude, longitude), None

def generate_weather_report(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation_probability",
        "timezone": "Asia/Manila"
    }

    response = requests.get(url, params=params)
    data = response.json()

    now = datetime.now()
    current_hour_str = now.strftime("%Y-%m-%dT%H:00")

    try:
        start_index = data['hourly']['time'].index(current_hour_str)

    except ValueError:
        logging.error(f"Could not find the matching time slot for '{current_hour_str}' in weather data.")
        return None, "Could not find current weather data. Please try again."

    temps_next_12h = data['hourly']['temperature_2m'][start_index : start_index + 12]
    rain_next_12h = data['hourly']['precipitation_probability'][start_index : start_index + 12]

    times_next_12h = data['hourly']['time'][start_index : start_index + 12]

    peak_rain = max(rain_next_12h)
    peak_rain_index = rain_next_12h.index(peak_rain)
    peak_rain_time = times_next_12h[peak_rain_index]

    highest_temp = max(temps_next_12h)
    highest_temp_index = temps_next_12h.index(highest_temp)
    highest_temp_time = times_next_12h[highest_temp_index]

    lowest_temp = min(temps_next_12h)
    lowest_temp_index = temps_next_12h.index(lowest_temp)
    lowest_temp_time = times_next_12h[lowest_temp_index]

    highest_temp_readable = format_time(highest_temp_time)
    lowest_temp_readable = format_time(lowest_temp_time)
    peak_rain_readable = format_time(peak_rain_time)

    report_text = (
        f"Weather report for the next 12 Hours\n\n"
        f"{'Lowest Temperature':<20}: {lowest_temp} at {lowest_temp_readable}\n"
        f"{'Highest Temperature':<20}: {highest_temp} at {highest_temp_readable}\n"
        f"{'Chances of Rain':<20}: {peak_rain}% chance around {peak_rain_readable}"
    )

    advice = ""

    if peak_rain >= 50:
        advice += f"Bring an umbrella, there is a high chance of rain at {peak_rain_readable}. \n"

    if highest_temp >= 33:
        advice += f"It's going to be hot around {highest_temp_readable}. Wear light clothing, stay hydrated, and avoid prolonged sun exposure. \n"

    if advice == "":
        advice = "The weather condition looks fine, it's a good day to be outside."

    return report_text, advice