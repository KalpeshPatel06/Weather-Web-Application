"""
Vercel serverless function handler for FastAPI weather app.
"""
import os
import json
import requests
from urllib.parse import parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WeatherService:
    """Service class to interact with OpenWeatherMap API."""
    
    def __init__(self):
        """Initialize the weather service with API configuration."""
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
    
    def get_weather(self, city: str):
        """
        Fetch weather data for a given city.
        
        Args:
            city (str): Name of the city to fetch weather for
            
        Returns:
            dict: Weather data or error information
        """
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
            return {"error": "An unexpected error occurred. Please try again later."}


# Initialize weather service
try:
    weather_service = WeatherService()
except ValueError as e:
    weather_service = None
    print(f"Initialization error: {e}")


def handler(request):
    """
    Vercel serverless function handler.
    
    This function handles both GET and POST requests:
    - GET /api/health: Health check endpoint
    - POST /api/weather: Weather search endpoint
    """
    # Get request method and path
    method = request.method
    path = request.path
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle OPTIONS request (CORS preflight)
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Health check endpoint
    if path == '/api/health' or path == '/api':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'healthy',
                'service': 'weather-app'
            })
        }
    
    # Weather endpoint
    if path == '/api/weather' and method == 'POST':
        if not weather_service:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Weather service not initialized. Check API key configuration.'
                })
            }
        
        try:
            # Parse request body
            body = request.get_json() if hasattr(request, 'get_json') else {}
            
            # Get city from request
            city = body.get('city', '').strip()
            
            if not city:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'City parameter is required'
                    })
                }
            
            # Fetch weather data
            result = weather_service.get_weather(city)
            
            if 'error' in result:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps(result)
                }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': f'Server error: {str(e)}'
                })
            }
    
    # Default 404 response
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({
            'error': 'Not found'
        })
    }


# Vercel requires this specific function signature
def main(request):
    """Main entry point for Vercel."""
    return handler(request)
