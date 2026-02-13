"""
Vercel serverless function handler for FastAPI weather app.
"""
import os
import json
import requests
from http.server import BaseHTTPRequestHandler

# Load environment variables
api_key = os.environ.get("OPENWEATHER_API_KEY")


class WeatherService:
    """Service class to interact with OpenWeatherMap API."""
    
    def __init__(self):
        """Initialize the weather service with API configuration."""
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
    
    def get_weather(self, city):
        """Fetch weather data for a given city."""
        if not city or not city.strip():
            return {"error": "City name cannot be empty"}
        
        params = {
            "q": city.strip(),
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 404:
                return {"error": f"City '{city}' not found"}
            
            response.raise_for_status()
            data = response.json()
            
            weather_data = {
                "success": True,
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["description"].title(),
                "icon": data["weather"][0]["icon"],
                "wind_speed": data["wind"]["speed"]
            }
            
            return weather_data
            
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Please check your internet connection."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch weather data: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


# Initialize weather service
try:
    weather_service = WeatherService()
except Exception as e:
    weather_service = None
    print(f"Failed to initialize weather service: {e}")


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""
    
    def _set_headers(self, status=200):
        """Set response headers."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self._set_headers(200)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/api/health' or self.path == '/api':
            self._set_headers(200)
            response = json.dumps({
                'status': 'healthy',
                'service': 'weather-app',
                'api_key_set': api_key is not None
            })
            self.wfile.write(response.encode())
        else:
            self._set_headers(404)
            response = json.dumps({'error': 'Not found'})
            self.wfile.write(response.encode())
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/weather':
            if not weather_service:
                self._set_headers(500)
                response = json.dumps({
                    'error': 'Weather service not initialized. Check API key configuration.'
                })
                self.wfile.write(response.encode())
                return
            
            try:
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8')) if body else {}
                
                # Get city from request
                city = data.get('city', '').strip()
                
                if not city:
                    self._set_headers(400)
                    response = json.dumps({'error': 'City parameter is required'})
                    self.wfile.write(response.encode())
                    return
                
                # Fetch weather data
                result = weather_service.get_weather(city)
                
                if 'error' in result:
                    self._set_headers(400)
                else:
                    self._set_headers(200)
                
                response = json.dumps(result)
                self.wfile.write(response.encode())
                
            except Exception as e:
                self._set_headers(500)
                response = json.dumps({'error': f'Server error: {str(e)}'})
                self.wfile.write(response.encode())
        else:
            self._set_headers(404)
            response = json.dumps({'error': 'Not found'})
            self.wfile.write(response.encode())