"""
Vercel serverless function handler — supports current weather + 5-day forecast.
"""
import os
import json
import requests
from http.server import BaseHTTPRequestHandler

# Read API key directly from environment (works on Vercel)
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


class WeatherService:
    """Fetches current weather and 5-day forecast from OpenWeatherMap."""

    def __init__(self):
        self.api_key = API_KEY
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is not set")

    def get_weather(self, city: str) -> dict:
        """Current weather for a city. Returns metric (Celsius) values."""
        city = city.strip()
        if not city:
            return {"error": "City name cannot be empty"}

        try:
            resp = requests.get(
                WEATHER_URL,
                params={"q": city, "appid": self.api_key, "units": "metric"},
                timeout=10,
            )
            if resp.status_code == 404:
                return {"error": f"City '{city}' not found. Please check the spelling."}
            resp.raise_for_status()
            d = resp.json()

            return {
                "success": True,
                "city": d["name"],
                "country": d["sys"]["country"],
                # Always return raw Celsius. Unit conversion handled on frontend.
                "temperature": round(d["main"]["temp"], 1),
                "feels_like": round(d["main"]["feels_like"], 1),
                "humidity": d["main"]["humidity"],
                "condition": d["weather"][0]["description"].title(),
                "icon": d["weather"][0]["icon"],
                "wind_speed": d["wind"]["speed"],
            }

        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Check your internet connection."}
        except requests.exceptions.RequestException as e:
            return {"error": f"API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def get_forecast(self, city: str) -> dict:
        """
        5-day forecast. OpenWeatherMap returns readings every 3 hours (40 total).
        We pick the entry closest to noon for each date to show one card per day.
        Returns metric (Celsius) values. Unit conversion is done on the frontend.
        """
        city = city.strip()
        if not city:
            return {"error": "City name cannot be empty"}

        try:
            resp = requests.get(
                FORECAST_URL,
                params={"q": city, "appid": self.api_key, "units": "metric"},
                timeout=10,
            )
            if resp.status_code == 404:
                return {"error": f"City '{city}' not found. Please check the spelling."}
            resp.raise_for_status()
            d = resp.json()

            # Group entries by date, keep the one closest to 12:00
            days: dict = {}
            for entry in d["list"]:
                date_str = entry["dt_txt"].split(" ")[0]   # e.g. "2024-05-10"
                time_str = entry["dt_txt"].split(" ")[1]   # e.g. "12:00:00"
                if date_str not in days:
                    days[date_str] = entry
                elif time_str <= "12:00:00":
                    days[date_str] = entry

            # Build clean list capped at 5 days
            forecast_list = []
            for date_str, entry in sorted(days.items())[:5]:
                forecast_list.append({
                    "date": date_str,
                    "day": _short_day(entry["dt"]),
                    "temp_min": round(entry["main"]["temp_min"], 1),
                    "temp_max": round(entry["main"]["temp_max"], 1),
                    "condition": entry["weather"][0]["description"].title(),
                    "icon": entry["weather"][0]["icon"],
                    "humidity": entry["main"]["humidity"],
                })

            return {
                "success": True,
                "city": d["city"]["name"],
                "forecast": forecast_list,
            }

        except requests.exceptions.Timeout:
            return {"error": "Forecast request timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Check your internet connection."}
        except requests.exceptions.RequestException as e:
            return {"error": f"API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


def _short_day(unix_ts: int) -> str:
    """Convert a Unix timestamp to a short day name e.g. 'Mon'."""
    import datetime
    return datetime.datetime.utcfromtimestamp(unix_ts).strftime("%a")


# Initialise service once at cold-start
try:
    weather_service = WeatherService()
except Exception as exc:
    weather_service = None
    print(f"[WeatherService] init failed: {exc}")


class handler(BaseHTTPRequestHandler):
    """Single Vercel Python serverless entry-point for all /api/* routes."""

    def _send(self, status: int, body: dict):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8")) if raw else {}

    def _no_service(self):
        self._send(500, {
            "error": "Weather service unavailable. Check OPENWEATHER_API_KEY in Vercel."
        })

    def do_OPTIONS(self):
        self._send(200, {})

    def do_GET(self):
        if self.path in ("/api/health", "/api"):
            self._send(200, {
                "status": "healthy",
                "service": "weather-app",
                "api_key_set": API_KEY is not None,
            })
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        # /api/weather — current conditions
        if self.path == "/api/weather":
            if not weather_service:
                return self._no_service()
            try:
                body = self._read_json()
                city = body.get("city", "").strip()
                if not city:
                    return self._send(400, {"error": "City parameter is required"})
                result = weather_service.get_weather(city)
                self._send(400 if "error" in result else 200, result)
            except Exception as e:
                self._send(500, {"error": f"Server error: {str(e)}"})

        # /api/forecast — 5-day forecast
        elif self.path == "/api/forecast":
            if not weather_service:
                return self._no_service()
            try:
                body = self._read_json()
                city = body.get("city", "").strip()
                if not city:
                    return self._send(400, {"error": "City parameter is required"})
                result = weather_service.get_forecast(city)
                self._send(400 if "error" in result else 200, result)
            except Exception as e:
                self._send(500, {"error": f"Server error: {str(e)}"})

        else:
            self._send(404, {"error": "Not found"})
