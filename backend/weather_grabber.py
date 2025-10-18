#----------------------------------------------
# weather_grabber.py

# Script to grab current weather data for Princeton, NJ
# using OpenWeatherMap API and save it to a JSON file.
#----------------------------------------------
# Imports:
import requests
import json
import os

# Latitude and Longitude for Princeton, NJ
lat = 40.3431
lon = -74.6551

# Load API key from environment variable
API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

def grab_weather_data(lat, lon, api_key):
    
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'imperial'
    }
    response = requests.get(BASE_URL, params=params)


    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print(response.text)  # prints the error message returned by the API
        return None
    
    data = response.json()

    with open("weather_data.json", "w") as f:
        json.dump(data, f, indent=4)    

    print(f"Showing current weather data for {data['name']}, {data['sys']['country']}:")
    print(f"Temperature: {data['main']['temp']} °F")
    print(f"Weather: {data['weather'][0]['description']}")


if __name__ == "__main__":
    grab_weather_data(lat, lon, API_KEY)