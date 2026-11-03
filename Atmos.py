import json
import time
import argparse
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CONDITIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def api_request(url, params):
    request_url = f"{url}?{urlencode(params)}"
    with urlopen(request_url, timeout=20) as response:
        return json.load(response)


def search_city(city_name):
    data = api_request(
        GEOCODING_URL,
        {
            "name": city_name,
            "count": 10,
            "language": "en",
            "format": "json",
        },
    )

    results = data.get("results", [])

    if not results:
        print(f"\nError: No location found for '{city_name}'.")
        return None

    if len(results) > 1:
        print("\nMatching locations:")

        for i, place in enumerate(results, start=1):
            region = place.get("admin1", "")
            country = place.get("country", "Unknown")
            region_text = f", {region}" if region else ""

            print(
                f"{i}. {place['name']}{region_text} - {country}"
            )

        while True:
            choice = input(
                "\nChoose a location number (Enter for first result): "
            ).strip()

            if not choice:
                index = 0
                break

            try:
                index = int(choice) - 1
            except ValueError:
                print("Please enter a number from the list, or press Enter.")
                continue

            if 0 <= index < len(results):
                break

            print(f"Please choose a number between 1 and {len(results)}.")

        location = results[index]
    else:
        location = results[0]

    region = location.get("admin1", "")
    country = location.get("country", "Unknown")
    region_text = f", {region}" if region else ""

    print(
        f"\nLocation: {location['name']}"
        f"{region_text} - {country}"
    )

    return location


def get_weather_data(location, forecast=False):
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,is_day,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "timezone": "auto",
    }

    if forecast:
        params["daily"] = (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,sunrise,sunset"
        )
        params["forecast_days"] = 3

    return api_request(WEATHER_URL, params)


def print_current_weather(location, data):
    current = data["current"]
    code = current.get("weather_code")
    condition = WEATHER_CONDITIONS.get(code, "Unknown")

    print("\n" + "=" * 44)
    print("                 ATMOS.PY")
    print("=" * 44)
    print(f"City:          {location['name']}")
    print(f"Condition:     {condition}")
    print(f"Temperature:   {current.get('temperature_2m')} °C")
    print(f"Feels like:    {current.get('apparent_temperature')} °C")
    print(f"Humidity:      {current.get('relative_humidity_2m')}%")
    print(f"Wind speed:    {current.get('wind_speed_10m')} km/h")
    print(f"Precipitation: {current.get('precipitation')} mm")
    print(f"Local time:    {current.get('time')}")
    print("=" * 44)


def print_forecast(location, data):
    daily = data.get("daily")

    if not daily:
        print("Error: Forecast data is unavailable.")
        return

    print(f"\n--- ATMOS.PY: 3-DAY FORECAST: {location['name']} ---")

    for i, date in enumerate(daily["time"]):
        code = daily["weather_code"][i]
        condition = WEATHER_CONDITIONS.get(code, "Unknown")
        min_temp = daily["temperature_2m_min"][i]
        max_temp = daily["temperature_2m_max"][i]
        rain = daily["precipitation_probability_max"][i]

        print(f"\nDate:                  {date}")
        print(f"Condition:             {condition}")
        print(f"Temperature:           {min_temp} - {max_temp} °C")
        print(f"Precipitation chance:  {rain}%")
        print(f"Sunrise:               {daily['sunrise'][i]}")
        print(f"Sunset:                {daily['sunset'][i]}")


def monitor_temperature(location, threshold, interval):
    if interval < 1:
        print("Error: The interval must be at least 1 minute.")
        return

    if threshold < -100 or threshold > 100:
        print("Error: Please enter a realistic threshold between -100 and 100 °C.")
        return

    print(f"\nAtmos.py temperature monitoring: {location['name']}")
    print(f"Alert threshold: {threshold} °C")
    print(f"Check interval: {interval} minute(s)")
    print("Press Ctrl+C to stop monitoring.\n")

    try:
        while True:
            try:
                data = get_weather_data(location)
                current = data["current"]
                temperature = current["temperature_2m"]
                timestamp = current["time"]

                message = (
                    f"[{timestamp}] "
                    f"{location['name']}: {temperature} °C"
                )

                if temperature > threshold:
                    print(
                        f"[ALERT] Temperature exceeded "
                        f"{threshold} °C! {message}"
                    )
                else:
                    print(f"[NORMAL] {message}")

            except (
                URLError,
                KeyError,
                TypeError,
            ) as error:
                print(f"[WARNING] Unable to check weather: {error}")

            time.sleep(interval * 60)

    except KeyboardInterrupt:
        print("\nAtmos.py temperature monitoring stopped.")


def interactive_menu():
    print("\n" + "=" * 44)
    print("                 ATMOS.PY")
    print("=" * 44)
    print("Check current weather and forecasts worldwide.")

    while True:
        city = input(
            "\nEnter a city name (or 'q' to quit): "
        ).strip()

        if city.lower() in ("q", "quit", "exit"):
            print("Thank you for using Atmos.py. Goodbye!")
            break

        if not city:
            print("Please enter a valid city name.")
            continue

        try:
            location = search_city(city)

            if location is None:
                continue

            while True:
                print("\n" + "-" * 30)
                print(f"ATMOS.PY MENU - {location['name']}")
                print("-" * 30)
                print("1. Current weather")
                print("2. 3-day forecast")
                print("3. Temperature monitoring")
                print("4. Choose another city")
                print("5. Exit")

                choice = input("\nSelect an option (1-5): ").strip()

                if choice == "1":
                    data = get_weather_data(location)
                    print_current_weather(location, data)

                elif choice == "2":
                    data = get_weather_data(location, forecast=True)
                    print_forecast(location, data)

                elif choice == "3":
                    try:
                        text = input(
                            "Alert threshold in °C (default 35): "
                        ).strip()
                        threshold = float(text) if text else 35.0

                        text = input(
                            "Check interval in minutes (default 5): "
                        ).strip()
                        interval = int(text) if text else 5

                        monitor_temperature(
                            location, threshold, interval
                        )
                    except ValueError:
                        print("Please enter valid numeric values.")

                elif choice == "4":
                    break

                elif choice == "5":
                    print("Thank you for using Atmos.py. Goodbye!")
                    return

                else:
                    print("Invalid option. Please select 1-5.")

        except URLError as error:
            print(f"\nNetwork or API error: {error}")
            print("Check your internet connection, SSL certificates, and try again.")

        except (KeyError, TypeError, ValueError) as error:
            print(f"\nUnexpected data error: {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Atmos.py"
    )
    parser.add_argument("-c", "--city", type=str, default=None)
    parser.add_argument("-C", "--current", action="store_true")
    parser.add_argument("-f", "--forecast", action="store_true")
    parser.add_argument("-m", "--monitor", action="store_true")
    parser.add_argument("-t", "--threshold", type=float, default=35.0)
    parser.add_argument("-i", "--interval", type=int, default=5)

    args = parser.parse_args()

    selected_modes = sum((args.current, args.forecast, args.monitor))
    if args.city and selected_modes == 0:
        parser.error("use --current, --forecast, or --monitor together with --city")

    if args.interval < 1:
        parser.error("--interval must be at least 1 minute")

    if not -100 <= args.threshold <= 100:
        parser.error("--threshold must be between -100 and 100 °C")

    if selected_modes == 0:
        interactive_menu()
        return

    city = args.city or input("Enter a city name: ").strip()

    if not city:
        print("Error: City name cannot be empty.")
        return

    try:
        location = search_city(city)

        if location is None:
            return

        if args.current:
            print_current_weather(
                location, get_weather_data(location)
            )

        if args.forecast:
            print_forecast(
                location, get_weather_data(location, forecast=True)
            )

        if args.monitor:
            monitor_temperature(
                location, args.threshold, args.interval
            )

    except URLError as error:
        print(f"Network or API error: {error}")
        print("Check your internet connection, SSL certificates, and try again.")
    except (KeyError, TypeError, ValueError) as error:
        print(f"Unexpected data error: {error}")


if __name__ == "__main__":
    main()
