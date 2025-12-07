import tkinter as tk
from tkinter import messagebox
import urllib.request
import urllib.parse
import json
from datetime import datetime

# Main Window
root = tk.Tk()
root.title("Weather App")
root.geometry("550x1050")
root.resizable(False, False)

# Modern Color Palette
BG_MAIN = "#0d1b2a"
BG_CARD = "#1a2f45"
BG_INPUT = "#0a0e27"
ACCENT = "#00d4ff"
ACCENT_DARK = "#0099cc"
TEXT_MAIN = "#ffffff"
TEXT_SUB = "#a0b0c0"
TEXT_LIGHT = "#d0dce6"

root.configure(bg=BG_MAIN)

# Weather icons - More realistic with better colors
WEATHER_ICONS = {
    'Clear Sky': {'icon': '☀️', 'color': '#FFD700'},
    'Mainly Clear': {'icon': '🌤️', 'color': '#FFD700'},
    'Partly Cloudy': {'icon': '⛅', 'color': '#87CEEB'},
    'Overcast': {'icon': '☁️', 'color': '#B8B8B8'},
    'Foggy': {'icon': '🌫️', 'color': '#C0C0C0'},
    'Light Drizzle': {'icon': '🌦️', 'color': '#87CEEB'},
    'Moderate Drizzle': {'icon': '🌧️', 'color': '#4682B4'},
    'Heavy Drizzle': {'icon': '⛈️', 'color': '#1E90FF'},
    'Slight Rain': {'icon': '🌧️', 'color': '#4682B4'},
    'Moderate Rain': {'icon': '🌧️', 'color': '#1E90FF'},
    'Heavy Rain': {'icon': '⛈️', 'color': '#0047AB'},
    'Slight Snow': {'icon': '🌨️', 'color': '#F0FFFF'},
    'Moderate Snow': {'icon': '🌨️', 'color': '#E8E8E8'},
    'Heavy Snow': {'icon': '❄️', 'color': '#F5F5F5'},
    'Slight Rain Showers': {'icon': '🌧️', 'color': '#4682B4'},
    'Moderate Rain Showers': {'icon': '🌧️', 'color': '#1E90FF'},
    'Heavy Rain Showers': {'icon': '⛈️', 'color': '#0047AB'},
    'Slight Snow Showers': {'icon': '🌨️', 'color': '#F0FFFF'},
    'Heavy Snow Showers': {'icon': '❄️', 'color': '#F5F5F5'},
    'Thunderstorm': {'icon': '⛈️', 'color': '#FF6B35'},
    'Thunderstorm with Hail': {'icon': '⛈️', 'color': '#FF6B35'},
    'Unknown': {'icon': '🌤️', 'color': '#87CEEB'}
}

# AQI Color mapping
AQI_DATA = {
    'Good': {'range': (0, 50), 'color': '#00E400', 'bg': '#E8F5E9'},
    'Fair': {'range': (51, 100), 'color': '#FFFF00', 'bg': '#FFFDE7'},
    'Moderate': {'range': (101, 150), 'color': '#FF7E00', 'bg': '#FFF3E0'},
    'Poor': {'range': (151, 200), 'color': '#FF0000', 'bg': '#FFEBEE'},
    'Very Poor': {'range': (201, 300), 'color': '#8F3F97', 'bg': '#F3E5F5'},
    'Severe': {'range': (301, 500), 'color': '#7E0023', 'bg': '#FCE4EC'}
}

def get_aqi_category(aqi_value):
    for category, data in AQI_DATA.items():
        if data['range'][0] <= aqi_value <= data['range'][1]:
            return category, data
    return 'Unknown', {'color': '#CCCCCC', 'bg': '#F5F5F5'}

# ============ TOP BAR - SEARCH ============
top_frame = tk.Frame(root, bg=BG_MAIN)
top_frame.pack(pady=15)

search_label = tk.Label(
    top_frame,
    text="🔍 Find Weather",
    font=("Segoe UI", 10),
    fg=TEXT_SUB,
    bg=BG_MAIN
)
search_label.pack(pady=(0, 8))

city_var = tk.StringVar()

city_entry = tk.Entry(
    top_frame,
    textvariable=city_var,
    font=("Segoe UI", 12),
    width=28,
    bd=0,
    relief=tk.FLAT,
    justify="center",
    fg=TEXT_MAIN,
    bg=BG_INPUT,
    insertbackground=ACCENT
)
city_entry.pack(ipady=9)

def get_weather():
    city = city_var.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    search_btn.config(state=tk.DISABLED, text="⏳ Loading...")
    root.update()

    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1&language=en&format=json"
        
        with urllib.request.urlopen(geo_url, timeout=10) as response:
            geo_data = json.loads(response.read().decode())

        if not geo_data.get('results'):
            messagebox.showerror("Error", "City not found. Please try another name.")
            search_btn.config(state=tk.NORMAL, text="🔍 Search")
            return

        location = geo_data['results'][0]
        latitude = location['latitude']
        longitude = location['longitude']
        timezone = location['timezone']
        name = location['name']
        country = location.get('country', '')

        place_label.config(text=f"{name}, {country}")

        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%a, %d %b %Y")

        time_label.config(text=time_str)
        date_label.config(text=date_str)

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m,pressure_msl&temperature_unit=celsius"

        with urllib.request.urlopen(weather_url, timeout=10) as response:
            weather_data = json.loads(response.read().decode())

        current = weather_data['current']

        weather_desc = get_weather_description(current['weather_code'])
        weather_icon_data = WEATHER_ICONS.get(weather_desc, WEATHER_ICONS['Unknown'])

        temp_label.config(text=f"{current['temperature_2m']:.1f}°C")
        desc_label.config(text=weather_desc)
        emoji_label.config(text=weather_icon_data['icon'], fg=weather_icon_data['color'])

        wind_value_label.config(text=f"{current['wind_speed_10m']:.1f} m/s")
        humidity_value_label.config(text=f"{current['relative_humidity_2m']}%")
        pressure_value_label.config(text=f"{current['pressure_msl']:.0f} hPa")

        # Get AQI data
        aqi_value = None
        pm25 = None
        
        try:
            aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&current=us_aqi,pm2_5&timezone=auto"
            with urllib.request.urlopen(aqi_url, timeout=8) as response:
                aqi_data = json.loads(response.read().decode())
            
            if 'current' in aqi_data:
                us_aqi = aqi_data['current'].get('us_aqi')
                pm25 = aqi_data['current'].get('pm2_5')
                if us_aqi is not None and 0 <= us_aqi <= 500:
                    aqi_value = int(us_aqi)
        except:
            pass
        
        if aqi_value is None:
            try:
                aqi_url = f"https://api.waqi.info/feed/geo:{latitude};{longitude}/?token=demo"
                with urllib.request.urlopen(aqi_url, timeout=8) as response:
                    waqi_data = json.loads(response.read().decode())
                
                if waqi_data.get('status') == 'ok' and 'data' in waqi_data:
                    aqi_val = waqi_data['data'].get('aqi')
                    if isinstance(aqi_val, (int, float)) and 0 <= aqi_val <= 500:
                        aqi_value = int(aqi_val)
            except:
                pass
        
        if aqi_value is not None:
            aqi_category, aqi_colors = get_aqi_category(aqi_value)
            aqi_value_label.config(text=f"{aqi_value}", fg=aqi_colors['color'])
            
            if pm25 is not None:
                aqi_status_label.config(text=f"{aqi_category} • PM2.5: {pm25:.1f}μg/m³", fg=aqi_colors['color'])
            else:
                aqi_status_label.config(text=f"{aqi_category}", fg=aqi_colors['color'])
            
            aqi_card.config(bg=BG_CARD)
        else:
            aqi_value_label.config(text="--", fg="#CCCCCC")
            aqi_status_label.config(text="Data unavailable", fg="#999999")
            aqi_card.config(bg=BG_CARD)

        show_weather_data()
        city_entry.delete(0, tk.END)
        search_btn.config(state=tk.NORMAL, text="🔍 Search")

    except Exception as e:
        messagebox.showerror("Error", f"Could not get weather data.\n{str(e)}")
        search_btn.config(state=tk.NORMAL, text="🔍 Search")

def get_weather_description(code):
    codes = {
        0: 'Clear Sky', 1: 'Mainly Clear', 2: 'Partly Cloudy', 3: 'Overcast',
        45: 'Foggy', 48: 'Foggy', 51: 'Light Drizzle', 53: 'Moderate Drizzle',
        55: 'Heavy Drizzle', 61: 'Slight Rain', 63: 'Moderate Rain', 65: 'Heavy Rain',
        71: 'Slight Snow', 73: 'Moderate Snow', 75: 'Heavy Snow',
        80: 'Slight Rain Showers', 81: 'Moderate Rain Showers', 82: 'Heavy Rain Showers',
        85: 'Slight Snow Showers', 86: 'Heavy Snow Showers',
        95: 'Thunderstorm', 96: 'Thunderstorm with Hail', 99: 'Thunderstorm with Hail',
    }
    return codes.get(code, 'Unknown')

search_btn = tk.Button(
    top_frame,
    text="🔍 Search",
    font=("Segoe UI Semibold", 11),
    bg=ACCENT,
    fg="#000000",
    activebackground=ACCENT_DARK,
    activeforeground="#000000",
    bd=0,
    relief=tk.FLAT,
    padx=18,
    command=get_weather,
    cursor="hand2"
)
search_btn.pack(pady=(10, 0), ipady=7)

# ============ TIME & LOCATION AREA ============
time_frame = tk.Frame(root, bg=BG_MAIN)
time_frame.pack(pady=10)

place_label = tk.Label(
    time_frame,
    text="City, Country",
    font=("Segoe UI Semibold", 16),
    fg=ACCENT,
    bg=BG_MAIN
)
place_label.pack()

time_label = tk.Label(
    time_frame,
    text="--:-- --",
    font=("Segoe UI", 28, "bold"),
    fg=TEXT_MAIN,
    bg=BG_MAIN
)
time_label.pack(pady=(2, 0))

date_label = tk.Label(
    time_frame,
    text="",
    font=("Segoe UI", 10),
    fg=TEXT_SUB,
    bg=BG_MAIN
)
date_label.pack(pady=(1, 0))

# ============ MAIN WEATHER CARD ============
card = tk.Frame(root, bg=BG_CARD, relief=tk.RAISED, bd=0)
card.pack(pady=10, padx=18, fill=tk.X)

card_inner = tk.Frame(card, bg=BG_CARD)
card_inner.pack(padx=15, pady=12, fill=tk.BOTH, expand=True)

# Emoji and temp
top_row = tk.Frame(card_inner, bg=BG_CARD)
top_row.pack(fill=tk.X, pady=(0, 8))

emoji_label = tk.Label(
    top_row,
    text="☀️",
    font=("Arial", 48),
    bg=BG_CARD,
    fg="#FFD700"
)
emoji_label.pack(side=tk.LEFT, padx=(0, 12))

temp_section = tk.Frame(top_row, bg=BG_CARD)
temp_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

temp_label = tk.Label(
    temp_section,
    text="--°C",
    font=("Segoe UI", 36, "bold"),
    fg=TEXT_MAIN,
    bg=BG_CARD
)
temp_label.pack(anchor="w")

# Description
desc_label = tk.Label(
    card_inner,
    text="Weather description",
    font=("Segoe UI", 13),
    fg=TEXT_LIGHT,
    bg=BG_CARD,
    wraplength=280,
    justify="left"
)
desc_label.pack(anchor="w", pady=(5, 0))

# ============ WEATHER DETAILS (Wind, Humidity, Pressure) ============
details_frame = tk.Frame(root, bg=BG_MAIN)
details_frame.pack(pady=10, padx=18, fill=tk.X)

details_label = tk.Label(
    details_frame,
    text="📊 Weather Details",
    font=("Segoe UI Semibold", 11),
    fg=ACCENT,
    bg=BG_MAIN
)
details_label.pack(anchor="w", pady=(0, 8))

def make_detail_row(parent, label_text, emoji):
    row_frame = tk.Frame(parent, bg=BG_CARD, relief=tk.RAISED, bd=0)
    row_frame.pack(fill=tk.X, pady=5)
    
    inner_frame = tk.Frame(row_frame, bg=BG_CARD)
    inner_frame.pack(padx=14, pady=9, fill=tk.BOTH, expand=True)
    
    lbl = tk.Label(
        inner_frame,
        text=f"{emoji} {label_text}",
        font=("Segoe UI Semibold", 11),
        fg=TEXT_LIGHT,
        bg=BG_CARD,
        anchor="w"
    )
    val = tk.Label(
        inner_frame,
        text="--",
        font=("Segoe UI", 11, "bold"),
        fg=ACCENT,
        bg=BG_CARD,
        anchor="e"
    )
    lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
    val.pack(side=tk.RIGHT)
    return val

wind_value_label = make_detail_row(details_frame, "Wind Speed", "💨")
humidity_value_label = make_detail_row(details_frame, "Humidity", "💧")
pressure_value_label = make_detail_row(details_frame, "Pressure", "📊")

# ============ AQI SECTION (Prominent) ============
aqi_card = tk.Frame(root, bg=BG_CARD, relief=tk.RAISED, bd=0)
aqi_card.pack(pady=8, padx=18, fill=tk.X)

aqi_inner = tk.Frame(aqi_card, bg=BG_CARD)
aqi_inner.pack(padx=14, pady=10, fill=tk.BOTH, expand=True)

aqi_title_frame = tk.Frame(aqi_inner, bg=BG_CARD)
aqi_title_frame.pack(anchor="w", pady=(0, 6), fill=tk.X)

aqi_title = tk.Label(
    aqi_title_frame,
    text="💨 Air Quality Index (AQI)",
    font=("Segoe UI Semibold", 10),
    fg=ACCENT,
    bg=BG_CARD
)
aqi_title.pack(anchor="w")

aqi_content_frame = tk.Frame(aqi_inner, bg=BG_CARD)
aqi_content_frame.pack(fill=tk.X)

aqi_value_label = tk.Label(
    aqi_content_frame,
    text="--",
    font=("Segoe UI", 32, "bold"),
    fg="#00E400",
    bg=BG_CARD
)
aqi_value_label.pack(side=tk.LEFT, padx=(0, 10))

aqi_status_label = tk.Label(
    aqi_content_frame,
    text="Good",
    font=("Segoe UI Semibold", 11),
    fg="#00E400",
    bg=BG_CARD,
    wraplength=250,
    justify="left"
)
aqi_status_label.pack(side=tk.LEFT, anchor="w", expand=True)

# ============ INITIAL STATE ============
initial_frame = tk.Frame(root, bg=BG_MAIN)
initial_frame.pack(pady=60, expand=True)

initial_label = tk.Label(
    initial_frame,
    text="🌍\n\nEnter a city name to\ndiscover weather",
    font=("Segoe UI", 14),
    fg=TEXT_SUB,
    bg=BG_MAIN,
    justify="center"
)
initial_label.pack()

def show_weather_data():
    initial_label.pack_forget()
    initial_frame.pack_forget()

city_entry.focus()
city_entry.bind('<Return>', lambda event: get_weather())

root.mainloop()