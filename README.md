# Atmos.py — Weather CLI Application

Atmos.py is a command-line weather application written in Python. It uses the Open-Meteo Geocoding API to find a city and the Open-Meteo Forecast API to retrieve current weather conditions and a three-day forecast.

## Features

- Search for a city by name and choose among matching locations.
- Display current temperature, feels-like temperature, humidity, wind speed, precipitation, weather condition, and local time.
- Display a three-day forecast with daily minimum and maximum temperatures, precipitation probability, sunrise, and sunset.
- Monitor a city's temperature at a configurable interval and print an alert when the selected threshold is exceeded.
- Switch to another city from the interactive menu.
- Run current weather, forecast, or temperature monitoring directly through command-line arguments.
- Handle common invalid input, missing locations, network/API errors, and unavailable response data.

## Requirements

- Python 3.9 or newer.
- An active internet connection.
- No third-party Python packages are required. The application uses Python standard-library modules only.

## Project Structure

```text
Atmos.py_Project/
├── Atmos.py
├── README.md
├── requirements.txt
├── .gitignore
├── contributions/
│   ├── SUHEDA_KARADAG_2409011037_suhedyyyy.md
│   ├── BERRA_VILDAN_ERSIN_2409011033_berraersinn.md
│   ├── EMRE_DEMIR_MUCAHITOGLU_2409011029_Demirmucahitoglu.md
│   ├── IREM_TOSUN_2409111009_tiremsn.md
│   └── OZGUR_OZTURK_2409111041_ozgurozt.md
└── test_atmos.py

### File Descriptions

- `Atmos.py`: Main application, including the interactive menu and command-line interface.
- `requirements.txt`: Notes that no third-party packages are required.
- `.gitignore`: Excludes Python cache files, virtual environments, and common local editor files.
- `contributions/`: Contains the individual contribution reports for all five team members.
- `tests/test_atmos.py`: Contains automated unit tests for selected application behavior.
- `README.md`: Project documentation and usage instructions.

## Run the Interactive Application

Open a terminal in the project directory and run:

```bash
python3 Atmos.py
```

Enter a city name. If multiple locations match, choose the desired result. Then select an option from the menu:

1. Current weather
2. Three-day forecast
3. Temperature monitoring
4. Choose another city
5. Exit

## Command-Line Usage

The application can also be run directly with command-line arguments, without using the interactive menu.

### Show current weather

```bash
python3 Atmos.py --city "Istanbul" --current
```

### Show a three-day forecast

```bash
python3 Atmos.py --city "Ankara" --forecast
```

### Monitor temperature

The following example checks Antalya every five minutes and prints an alert when the temperature exceeds 35 °C:

```bash
python3 Atmos.py --city "Antalya" --monitor --threshold 35 --interval 5
```

### Show available arguments

```bash
python3 Atmos.py --help
```

The `--city` argument can be omitted when using a direct mode. The application will then ask the user to enter a city name.

## Data Sources and Internet Access

The application uses these public Open-Meteo API endpoints:

- **Geocoding API:** `https://geocoding-api.open-meteo.com/v1/search`
- **Weather Forecast API:** `https://api.open-meteo.com/v1/forecast`

An active internet connection is required to search for locations and retrieve weather information. Weather data is provided by [Open-Meteo](https://open-meteo.com/).

## Testing

The project includes unit tests written with Python's built-in `unittest` framework. The tests mock API responses, so they do not require an internet connection.

Run the tests from the project root directory:

```bash
python3 -m unittest test_atmos -v
```

## Team Contributions

Individual contribution reports for all five team members are available in the `contributions/` directory. Each report describes the member's stated project responsibilities and contributions.

## Limitations

- Weather information cannot be retrieved without an internet connection.
- Temperature monitoring runs while the application remains open and stops when the user presses `Ctrl+C`.
- The application is a command-line educational project. It does not provide a graphical interface or store historical weather records.
