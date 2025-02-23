import tkinter as tk
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap
from datetime import datetime
import json
import os

# Funkcija za preuzimanje trenutne lokacije putem IP adrese
def get_current_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        city = data['city']
        country = data['country']
        return city, country
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get location: {e}")
        return None, None

# Funkcija za upisivanje podataka u JSON datoteku
def save_json(data, filename='cuvar_vremena.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.append(data)

    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=4)

# Funkcija za preuzimanje informacija od OpenWeatherMap API
def get_weather_forecast(city):
    API_key = "1a7c892e18e55596962ed493770b1599"
    
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
    weather_res = requests.get(weather_url)

    if weather_res.status_code == 404:
        messagebox.showerror("Error", "City Not Found")
        return None

    weather = weather_res.json()

    icon_id = weather["weather"][0]["icon"]
    temperature = weather["main"]["temp"] - 273.15
    feels_like = weather["main"]["feels_like"] - 273.15
    description = weather["weather"][0]["description"]
    humidity = weather["main"]["humidity"]
    visibility = weather.get("visibility", 0) / 1000  # u kilometrima
    wind_speed = weather["wind"]["speed"]
    sunrise = datetime.utcfromtimestamp(weather["sys"]["sunrise"]).strftime('%H:%M:%S')
    sunset = datetime.utcfromtimestamp(weather["sys"]["sunset"]).strftime('%H:%M:%S')
    city = weather["name"]
    country = weather["sys"]["country"]

    # UV indeks (potreban je drugi API poziv jer OWM nudi UV podatke putem drugog API-ja)
    uv_url = f"https://api.openweathermap.org/data/2.5/uvi?lat={weather['coord']['lat']}&lon={weather['coord']['lon']}&appid={API_key}"
    uv_res = requests.get(uv_url)
    uv_index = uv_res.json().get("value", "N/A")

    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"

    forecast_data = []
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_key}"
    forecast_res = requests.get(forecast_url)
    if forecast_res.status_code == 200:
        forecast = forecast_res.json()
        for i in range(1, 4):
            daily_temps = [forecast['list'][j]['main']['temp'] for j in range(i*8, (i+1)*8)]
            temp_min = min(daily_temps) - 273.15
            temp_max = max(daily_temps) - 273.15
            
            date_str = forecast['list'][i * 8]['dt_txt'].split()[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            
            icon_id = forecast['list'][i * 8]["weather"][0]["icon"]
            forecast_data.append((formatted_date, icon_id, temp_min, temp_max))

    return (icon_url, temperature, feels_like, description, city, country, humidity, visibility, wind_speed, sunrise, sunset, uv_index, forecast_data)

def convert_time(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')

# Funkcija za pretragu vremena grada
def search(city=None):
    if city is None:
        city = city_entry.get()
    result = get_weather_forecast(city)
    if result is None:
        return

    # Povećavamo veličinu prozora na punu veličinu i prikazujemo sve komponente
    root.geometry("450x800")
    message_label.pack_forget()  # Sakrivamo inicijalni tekst

    entry_frame.pack(pady=10)  # Ponovo prikazujemo frame za unos i dugmiće

    (icon_url, temperature, feels_like, description, city, country,
     humidity, visibility, wind_speed, sunrise, sunset, uv_index, forecast_data) = result

    location_label.configure(text=f"{city}, {country}")
    location_label.pack(pady=20)
    
    try:
        response = requests.get(icon_url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw)
        image = image.resize((120, 120), Image.Resampling.LANCZOS)  
        icon_image = ImageTk.PhotoImage(image)
        weather_icon_label.configure(image=icon_image)
        weather_icon_label.image = icon_image
    except Exception as e:
        print(f"Error loading image: {e}")
        weather_icon_label.configure(text="Image not available")

    weather_icon_label.pack(pady=10)

    temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
    temperature_label.pack()

    feels_like_label.configure(text=f"Feels Like: {feels_like:.2f}°C")
    feels_like_label.pack()

    description_label.configure(text=f"Description: {description}")
    description_label.pack()

    humidity_label.configure(text=f"Humidity: {humidity}%")
    humidity_label.pack(pady=5)

    visibility_label.configure(text=f"Visibility: {visibility} km")
    visibility_label.pack(pady=5)

    wind_label.configure(text=f"Wind Speed: {wind_speed} m/s")
    wind_label.pack(pady=5)

    sunrise_label.configure(text=f"Sunrise: {sunrise}")
    sunrise_label.pack(pady=5)

    sunset_label.configure(text=f"Sunset: {sunset}")
    sunset_label.pack(pady=5)

    uv_index_label.configure(text=f"UV Index: {uv_index}")
    uv_index_label.pack(pady=5)

    forecast_frame.pack(pady=10)

    for i, (date, icon_id, temp_min, temp_max) in enumerate(forecast_data):
        day_labels[i].configure(text=date)
        day_labels[i].grid(row=0, column=i*3, padx=5, pady=5)
        
        forecast_icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
        try:
            image = Image.open(requests.get(forecast_icon_url, stream=True).raw)
            icon_image = ImageTk.PhotoImage(image)
            icon_labels[i].configure(image=icon_image)
            icon_labels[i].image = icon_image
        except Exception as e:
            print(f"Error loading image: {e}")
            icon_labels[i].configure(text="Image not available")
        icon_labels[i].grid(row=1, column=i*3, padx=5, pady=5)

        min_temp_labels[i].configure(text=f"Min Temp: {temp_min:.2f}°C")
        min_temp_labels[i].grid(row=2, column=i*3, padx=5, pady=5)

        max_temp_labels[i].configure(text=f"Max Temp: {temp_max:.2f}°C")
        max_temp_labels[i].grid(row=3, column=i*3, padx=5, pady=5)

    city_entry.delete(0, tk.END)

    weather_data = {
        'city': city,
        'country': country,
        'temperature': temperature,
        'feels_like': feels_like,
        'description': description,
        'humidity': humidity,
        'visibility': visibility,
        'wind_speed': wind_speed,
        'sunrise': sunrise,
        'sunset': sunset,
        'uv_index': uv_index,
        'icon_url': icon_url,
        'forecast': forecast_data
    }
    
    save_json(weather_data)

# Definisanje funkcije za automatsku lokaciju
def auto_location():
    city, country = get_current_location()
    if city is not None:
        city_entry.delete(0, tk.END)
        city_entry.insert(0, city)
        search()

# Kreiranje glavnog prozora aplikacije
root = ttkbootstrap.Window(themename='superhero')
root.title("Weather App")

# Podesavanje inicijalne velicine prozora na 400x200
root.geometry("400x200")

# Kreiranje labela za inicijalni tekst
message_label = tk.Label(root, text="Please type wanted location", font=("Helvetica", 16, "bold"))
message_label.pack(expand=True)  # Centriranje labela

# Kreiranje frame-a za unos i dugmiće
entry_frame = tk.Frame(root)
entry_frame.pack(pady=10)

# Unos imena grada
city_entry = ttkbootstrap.Entry(entry_frame, font="Helvetica, 18")
city_entry.grid(row=0, column=0, padx=5)

# Dugme za pretragu
search_button = ttkbootstrap.Button(entry_frame, text="Search", command=search, bootstyle="warning")
search_button.grid(row=0, column=1, padx=5)

# Dugme za automatsku lokaciju (samo slika)
location_img = Image.open("/Users/damirb/Desktop/Projekat Python/slicica.png")
location_img = location_img.resize((20, 20), Image.Resampling.LANCZOS) 
location_icon = ImageTk.PhotoImage(location_img)
location_button = ttkbootstrap.Button(entry_frame, image=location_icon, command=auto_location, bootstyle="success")
location_button.grid(row=0, column=2, padx=5)

# Bindovanje Reurn za city_entry
city_entry.bind("<Return>", lambda event: search())

# Ostali widgeti aplikacije (inicijalno skriveni)
location_label = tk.Label(root, font="Helvetica, 25")
weather_icon_label = tk.Label(root)
temperature_label = tk.Label(root, font="Helvetica, 20")
feels_like_label = tk.Label(root, font="Helvetica, 15")
description_label = tk.Label(root, font="Helvetica, 20")
humidity_label = tk.Label(root, font="Helvetica, 15")
visibility_label = tk.Label(root, font="Helvetica, 15")
wind_label = tk.Label(root, font="Helvetica, 15")
sunrise_label = tk.Label(root, font="Helvetica, 15")
sunset_label = tk.Label(root, font="Helvetica, 15")
uv_index_label = tk.Label(root, font="Helvetica, 15")

forecast_frame = tk.Frame(root)
day_labels = []
icon_labels = []
min_temp_labels = []
max_temp_labels = []

for i in range(3):
    day_label = tk.Label(forecast_frame, font="Helvetica, 12")
    icon_label = tk.Label(forecast_frame)
    min_temp_label = tk.Label(forecast_frame, font="Helvetica, 12")
    max_temp_label = tk.Label(forecast_frame, font="Helvetica, 12")
    day_labels.append(day_label)
    icon_labels.append(icon_label)
    min_temp_labels.append(min_temp_label)
    max_temp_labels.append(max_temp_label)

root.mainloop()