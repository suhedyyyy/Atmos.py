import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
import Atmos


class AtmosTests(unittest.TestCase):
    def setUp(self):
        self.location = {
            "name": "Istanbul",
            "latitude": 41.0082,
            "longitude": 28.9784,
        }

    def test_known_weather_code(self):
        self.assertEqual(Atmos.WEATHER_CONDITIONS[0], "Clear sky")
        self.assertEqual(Atmos.WEATHER_CONDITIONS[95], "Thunderstorm")

    def test_unknown_weather_code_uses_fallback(self):
        self.assertEqual(Atmos.WEATHER_CONDITIONS.get(999, "Unknown"), "Unknown")

    @patch.object(Atmos, "api_request")
    def test_get_weather_data_requests_current_conditions(self, api_request):
        api_request.return_value = {"current": {"temperature_2m": 20}}
        result = Atmos.get_weather_data(self.location)
        self.assertEqual(result["current"]["temperature_2m"], 20)
        args, kwargs = api_request.call_args
        self.assertEqual(args[0], Atmos.WEATHER_URL)
        self.assertEqual(args[1]["latitude"], self.location["latitude"])
        self.assertIn("temperature_2m", args[1]["current"])
        self.assertNotIn("daily", args[1])

    @patch.object(Atmos, "api_request")
    def test_get_weather_data_includes_three_day_forecast_parameters(self, api_request):
        api_request.return_value = {"daily": {"time": []}}
        Atmos.get_weather_data(self.location, forecast=True)
        params = api_request.call_args.args[1]
        self.assertEqual(params["forecast_days"], 3)
        self.assertIn("temperature_2m_max", params["daily"])
        self.assertIn("sunrise", params["daily"])

    @patch.object(Atmos, "api_request", return_value={})
    def test_search_city_returns_none_when_no_results(self, api_request):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = Atmos.search_city("NoSuchCityForTest")
        self.assertIsNone(result)
        self.assertIn("No location found", output.getvalue())

    def test_monitor_temperature_rejects_interval_below_one(self):
        output = io.StringIO()
        with patch.object(Atmos, "get_weather_data") as get_weather_data:
            with contextlib.redirect_stdout(output):
                Atmos.monitor_temperature(self.location, threshold=30, interval=0)
        self.assertIn("at least 1 minute", output.getvalue())
        get_weather_data.assert_not_called()

    def test_print_forecast_handles_missing_daily_data(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            Atmos.print_forecast(self.location, {})
        self.assertIn("Forecast data is unavailable", output.getvalue())


if __name__ == "__main__":
    unittest.main()
