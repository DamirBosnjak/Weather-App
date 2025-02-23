# Weather App

## Overview

This is a Python-based weather application built using **Tkinter** and **ttkbootstrap** for the GUI, along with **OpenWeatherMap API** for fetching real-time weather data. The app allows users to search for weather conditions in any city or automatically retrieve their current location's weather.

## Features

- Fetch current weather details including temperature, humidity, wind speed, and more.
- Get a 3-day weather forecast with min/max temperature and weather icons.
- Auto-detect location using IP address.
- User-friendly graphical interface with a uInstall dependencies:
  ```
  pip install requests pillow ttkbootstrap
  ```
- Run the application:
  ```
  python weather_app.py
  ```

## API Key Setup

To use this application, you need an **OpenWeatherMap API key**. Replace the placeholder API key in the code with your own:
```
API_key = "your_api_key_here"
```

