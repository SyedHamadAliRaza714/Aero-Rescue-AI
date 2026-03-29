import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import asyncio
import aiohttp
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

st.title("🌍 Aero-Rescue AI Global")
st.write("Loading data… please wait ⏳")

st.set_page_config(
    page_title="🌍 Aero-Rescue AI Global",
    layout="wide",
    page_icon="🫁",
    initial_sidebar_state="expanded"
)

WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]

if not WEATHER_API_KEY:
    st.sidebar.warning("⚠️ OpenWeatherMap API Key not set. Using historical data mode only.")

def init_session():
    defaults = {
        'analysis_done': False,
        'results': None,
        'current': "Rawalpindi, Pakistan",
        'destination': "Islamabad, Pakistan",
        'condition': "Asthma",
        'severity': 2,
        'emergency_contact': "+92-300-1234567",
        'sel_travel_mode': "Flight",
        'vehicle_type': "AC Vehicle" 
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

@st.cache_data(ttl=86400)
def load_cities():
    return {
        "Islamabad, Pakistan": {"lat": 33.6844, "lon": 73.0479, "country": "Pakistan", "pop": "2.0M", "detailed": True, "region": "South Asia"},
        "Rawalpindi, Pakistan": {"lat": 33.5651, "lon": 73.0169, "country": "Pakistan", "pop": "2.1M", "detailed": True, "region": "South Asia"},
        "Lahore, Pakistan": {"lat": 31.5204, "lon": 74.3587, "country": "Pakistan", "pop": "13.0M", "detailed": True, "region": "South Asia"},
        "Karachi, Pakistan": {"lat": 24.8607, "lon": 67.0011, "country": "Pakistan", "pop": "15.0M", "detailed": True, "region": "South Asia"},
        "Peshawar, Pakistan": {"lat": 34.0151, "lon": 71.5249, "country": "Pakistan", "pop": "1.9M", "detailed": True, "region": "South Asia"},
        "Quetta, Pakistan": {"lat": 30.1798, "lon": 66.9750, "country": "Pakistan", "pop": "1.0M", "detailed": True, "region": "South Asia"},
        "Multan, Pakistan": {"lat": 30.1575, "lon": 71.5249, "country": "Pakistan", "pop": "1.9M", "detailed": True, "region": "South Asia"},
        "Faisalabad, Pakistan": {"lat": 31.4504, "lon": 73.1350, "country": "Pakistan", "pop": "3.2M", "detailed": True, "region": "South Asia"},
        "Hyderabad, Pakistan": {"lat": 25.3960, "lon": 68.3578, "country": "Pakistan", "pop": "1.7M", "detailed": True, "region": "South Asia"},
        "Sukkur, Pakistan": {"lat": 27.7052, "lon": 68.8574, "country": "Pakistan", "pop": "0.5M", "detailed": True, "region": "South Asia"},
        "Gwadar, Pakistan": {"lat": 25.1216, "lon": 62.3254, "country": "Pakistan", "pop": "0.1M", "detailed": True, "region": "South Asia"},
        "Gilgit, Pakistan": {"lat": 35.9208, "lon": 74.3142, "country": "Pakistan", "pop": "0.2M", "detailed": True, "region": "South Asia"},

        "New Delhi, India": {"lat": 28.6139, "lon": 77.2090, "country": "India", "pop": "32.9M", "detailed": False, "region": "South Asia"},
        "Mumbai, India": {"lat": 19.0760, "lon": 72.8777, "country": "India", "pop": "20.4M", "detailed": False, "region": "South Asia"},
        "Bangalore, India": {"lat": 12.9716, "lon": 77.5946, "country": "India", "pop": "12.3M", "detailed": False, "region": "South Asia"},
        "Kolkata, India": {"lat": 22.5726, "lon": 88.3639, "country": "India", "pop": "14.8M", "detailed": False, "region": "South Asia"},
        "Chennai, India": {"lat": 13.0827, "lon": 80.2707, "country": "India", "pop": "10.9M", "detailed": False, "region": "South Asia"},
        "Hyderabad, India": {"lat": 17.3850, "lon": 78.4867, "country": "India", "pop": "10.0M", "detailed": False, "region": "South Asia"},
        "Ahmedabad, India": {"lat": 23.0225, "lon": 72.5714, "country": "India", "pop": "8.2M", "detailed": False, "region": "South Asia"},
        "Pune, India": {"lat": 18.5204, "lon": 73.8567, "country": "India", "pop": "6.8M", "detailed": False, "region": "South Asia"},
        "Jaipur, India": {"lat": 26.9124, "lon": 75.7873, "country": "India", "pop": "3.0M", "detailed": False, "region": "South Asia"},
        "Lucknow, India": {"lat": 26.8467, "lon": 80.9462, "country": "India", "pop": "3.5M", "detailed": False, "region": "South Asia"},
        "Kanpur, India": {"lat": 26.4499, "lon": 80.3319, "country": "India", "pop": "2.9M", "detailed": False, "region": "South Asia"},
        "Nagpur, India": {"lat": 21.1458, "lon": 79.0882, "country": "India", "pop": "2.5M", "detailed": False, "region": "South Asia"},
        "Patna, India": {"lat": 25.5941, "lon": 85.1376, "country": "India", "pop": "2.0M", "detailed": False, "region": "South Asia"},
        "Indore, India": {"lat": 22.7196, "lon": 75.8577, "country": "India", "pop": "2.1M", "detailed": False, "region": "South Asia"},
        "Chandigarh, India": {"lat": 30.7333, "lon": 76.7794, "country": "India", "pop": "1.1M", "detailed": False, "region": "South Asia"},

        "Dhaka, Bangladesh": {"lat": 23.8103, "lon": 90.4125, "country": "Bangladesh", "pop": "21.0M", "detailed": False, "region": "South Asia"},
        "Chittagong, Bangladesh": {"lat": 22.3569, "lon": 91.7832, "country": "Bangladesh", "pop": "2.5M", "detailed": False, "region": "South Asia"},
        "Khulna, Bangladesh": {"lat": 22.8456, "lon": 89.5403, "country": "Bangladesh", "pop": "1.0M", "detailed": False, "region": "South Asia"},

        "Kathmandu, Nepal": {"lat": 27.7172, "lon": 85.3240, "country": "Nepal", "pop": "1.0M", "detailed": False, "region": "South Asia"},
        "Colombo, Sri Lanka": {"lat": 6.9271, "lon": 79.8612, "country": "Sri Lanka", "pop": "0.6M", "detailed": False, "region": "South Asia"},

        "New York, USA": {"lat": 40.7128, "lon": -74.0060, "country": "USA", "pop": "8.8M", "detailed": False, "region": "North America"},
        "Los Angeles, USA": {"lat": 34.0522, "lon": -118.2437, "country": "USA", "pop": "3.9M", "detailed": False, "region": "North America"},
        "Chicago, USA": {"lat": 41.8781, "lon": -87.6298, "country": "USA", "pop": "2.7M", "detailed": False, "region": "North America"},
        "Houston, USA": {"lat": 29.7604, "lon": -95.3698, "country": "USA", "pop": "2.3M", "detailed": False, "region": "North America"},
        "Phoenix, USA": {"lat": 33.4484, "lon": -112.0740, "country": "USA", "pop": "1.7M", "detailed": False, "region": "North America"},
        "Philadelphia, USA": {"lat": 39.9526, "lon": -75.1652, "country": "USA", "pop": "1.6M", "detailed": False, "region": "North America"},
        "San Antonio, USA": {"lat": 29.4241, "lon": -98.4936, "country": "USA", "pop": "1.4M", "detailed": False, "region": "North America"},
        "San Diego, USA": {"lat": 32.7157, "lon": -117.1611, "country": "USA", "pop": "1.4M", "detailed": False, "region": "North America"},
        "Dallas, USA": {"lat": 32.7767, "lon": -96.7970, "country": "USA", "pop": "1.3M", "detailed": False, "region": "North America"},
        "San Jose, USA": {"lat": 37.3382, "lon": -121.8863, "country": "USA", "pop": "1.0M", "detailed": False, "region": "North America"},
        "Austin, USA": {"lat": 30.2672, "lon": -97.7431, "country": "USA", "pop": "0.9M", "detailed": False, "region": "North America"},
        "Jacksonville, USA": {"lat": 30.3322, "lon": -81.6557, "country": "USA", "pop": "0.9M", "detailed": False, "region": "North America"},
        "San Francisco, USA": {"lat": 37.7749, "lon": -122.4194, "country": "USA", "pop": "0.9M", "detailed": False, "region": "North America"},
        "Columbus, USA": {"lat": 39.9612, "lon": -82.9988, "country": "USA", "pop": "0.9M", "detailed": False, "region": "North America"},
        "Charlotte, USA": {"lat": 35.2271, "lon": -80.8431, "country": "USA", "pop": "0.9M", "detailed": False, "region": "North America"},
        "Indianapolis, USA": {"lat": 39.7684, "lon": -86.1581, "country": "USA", "pop": "0.9M", "detailed": False, "region": "North America"},
        "Seattle, USA": {"lat": 47.6062, "lon": -122.3321, "country": "USA", "pop": "0.7M", "detailed": False, "region": "North America"},
        "Denver, USA": {"lat": 39.7392, "lon": -104.9903, "country": "USA", "pop": "0.7M", "detailed": False, "region": "North America"},
        "Washington DC, USA": {"lat": 38.9072, "lon": -77.0369, "country": "USA", "pop": "0.7M", "detailed": False, "region": "North America"},
        "Boston, USA": {"lat": 42.3601, "lon": -71.0589, "country": "USA", "pop": "0.7M", "detailed": False, "region": "North America"},
        "Detroit, USA": {"lat": 42.3314, "lon": -83.0458, "country": "USA", "pop": "0.6M", "detailed": False, "region": "North America"},

        "Toronto, Canada": {"lat": 43.6532, "lon": -79.3832, "country": "Canada", "pop": "2.9M", "detailed": False, "region": "North America"},
        "Montreal, Canada": {"lat": 45.5017, "lon": -73.5673, "country": "Canada", "pop": "1.7M", "detailed": False, "region": "North America"},
        "Vancouver, Canada": {"lat": 49.2827, "lon": -123.1207, "country": "Canada", "pop": "2.6M", "detailed": False, "region": "North America"},
        "Calgary, Canada": {"lat": 51.0447, "lon": -114.0719, "country": "Canada", "pop": "1.2M", "detailed": False, "region": "North America"},
        "Ottawa, Canada": {"lat": 45.4215, "lon": -75.6972, "country": "Canada", "pop": "1.0M", "detailed": False, "region": "North America"},

        "London, UK": {"lat": 51.5074, "lon": -0.1278, "country": "UK", "pop": "9.0M", "detailed": False, "region": "Europe"},
        "Manchester, UK": {"lat": 53.4808, "lon": -2.2426, "country": "UK", "pop": "0.5M", "detailed": False, "region": "Europe"},
        "Birmingham, UK": {"lat": 52.4862, "lon": -1.8904, "country": "UK", "pop": "1.1M", "detailed": False, "region": "Europe"},
        "Glasgow, UK": {"lat": 55.8609, "lon": -4.2514, "country": "UK", "pop": "0.6M", "detailed": False, "region": "Europe"},
        "Liverpool, UK": {"lat": 53.4084, "lon": -2.9916, "country": "UK", "pop": "0.5M", "detailed": False, "region": "Europe"},
        "Edinburgh, UK": {"lat": 55.9533, "lon": -3.1883, "country": "UK", "pop": "0.5M", "detailed": False, "region": "Europe"},

        "Paris, France": {"lat": 48.8566, "lon": 2.3522, "country": "France", "pop": "2.2M", "detailed": False, "region": "Europe"},
        "Marseille, France": {"lat": 43.2965, "lon": 5.3698, "country": "France", "pop": "0.9M", "detailed": False, "region": "Europe"},
        "Lyon, France": {"lat": 45.7640, "lon": 4.8357, "country": "France", "pop": "0.5M", "detailed": False, "region": "Europe"},
        "Toulouse, France": {"lat": 43.6047, "lon": 1.4442, "country": "France", "pop": "0.5M", "detailed": False, "region": "Europe"},

        "Berlin, Germany": {"lat": 52.5200, "lon": 13.4050, "country": "Germany", "pop": "3.6M", "detailed": False, "region": "Europe"},
        "Hamburg, Germany": {"lat": 53.5511, "lon": 9.9937, "country": "Germany", "pop": "1.8M", "detailed": False, "region": "Europe"},
        "Munich, Germany": {"lat": 48.1351, "lon": 11.5820, "country": "Germany", "pop": "1.5M", "detailed": False, "region": "Europe"},
        "Cologne, Germany": {"lat": 50.9375, "lon": 6.9603, "country": "Germany", "pop": "1.1M", "detailed": False, "region": "Europe"},
        "Frankfurt, Germany": {"lat": 50.1109, "lon": 8.6821, "country": "Germany", "pop": "0.7M", "detailed": False, "region": "Europe"},

        "Rome, Italy": {"lat": 41.9028, "lon": 12.4964, "country": "Italy", "pop": "2.9M", "detailed": False, "region": "Europe"},
        "Milan, Italy": {"lat": 45.4642, "lon": 9.1900, "country": "Italy", "pop": "1.4M", "detailed": False, "region": "Europe"},
        "Naples, Italy": {"lat": 40.8518, "lon": 14.2681, "country": "Italy", "pop": "0.9M", "detailed": False, "region": "Europe"},
        "Turin, Italy": {"lat": 45.0703, "lon": 7.6869, "country": "Italy", "pop": "0.9M", "detailed": False, "region": "Europe"},

        "Madrid, Spain": {"lat": 40.4168, "lon": -3.7038, "country": "Spain", "pop": "3.2M", "detailed": False, "region": "Europe"},
        "Barcelona, Spain": {"lat": 41.3851, "lon": 2.1734, "country": "Spain", "pop": "1.6M", "detailed": False, "region": "Europe"},
        "Valencia, Spain": {"lat": 39.4699, "lon": -0.3763, "country": "Spain", "pop": "0.8M", "detailed": False, "region": "Europe"},
        "Seville, Spain": {"lat": 37.3891, "lon": -5.9845, "country": "Spain", "pop": "0.7M", "detailed": False, "region": "Europe"},

        "Amsterdam, Netherlands": {"lat": 52.3676, "lon": 4.9041, "country": "Netherlands", "pop": "0.9M", "detailed": False, "region": "Europe"},
        "Rotterdam, Netherlands": {"lat": 51.9244, "lon": 4.4777, "country": "Netherlands", "pop": "0.6M", "detailed": False, "region": "Europe"},
        "Brussels, Belgium": {"lat": 50.8503, "lon": 4.3517, "country": "Belgium", "pop": "0.2M", "detailed": False, "region": "Europe"},
        "Zurich, Switzerland": {"lat": 47.3769, "lon": 8.5417, "country": "Switzerland", "pop": "0.4M", "detailed": False, "region": "Europe"},
        "Geneva, Switzerland": {"lat": 46.2044, "lon": 6.1432, "country": "Switzerland", "pop": "0.2M", "detailed": False, "region": "Europe"},
        "Vienna, Austria": {"lat": 48.2082, "lon": 16.3738, "country": "Austria", "pop": "1.9M", "detailed": False, "region": "Europe"},
        "Stockholm, Sweden": {"lat": 59.3293, "lon": 18.0686, "country": "Sweden", "pop": "0.9M", "detailed": False, "region": "Europe"},
        "Copenhagen, Denmark": {"lat": 55.6761, "lon": 12.5683, "country": "Denmark", "pop": "0.6M", "detailed": False, "region": "Europe"},
        "Oslo, Norway": {"lat": 59.9139, "lon": 10.7522, "country": "Norway", "pop": "0.7M", "detailed": False, "region": "Europe"},
        "Helsinki, Finland": {"lat": 60.1699, "lon": 24.9384, "country": "Finland", "pop": "0.6M", "detailed": False, "region": "Europe"},
        "Warsaw, Poland": {"lat": 52.2297, "lon": 21.0122, "country": "Poland", "pop": "1.8M", "detailed": False, "region": "Europe"},
        "Prague, Czech Republic": {"lat": 50.0755, "lon": 14.4378, "country": "Czech Republic", "pop": "1.3M", "detailed": False, "region": "Europe"},
        "Budapest, Hungary": {"lat": 47.4979, "lon": 19.0402, "country": "Hungary", "pop": "1.7M", "detailed": False, "region": "Europe"},
        "Athens, Greece": {"lat": 37.9838, "lon": 23.7275, "country": "Greece", "pop": "0.7M", "detailed": False, "region": "Europe"},
        "Lisbon, Portugal": {"lat": 38.7223, "lon": -9.1393, "country": "Portugal", "pop": "0.5M", "detailed": False, "region": "Europe"},
        "Dublin, Ireland": {"lat": 53.3498, "lon": -6.2603, "country": "Ireland", "pop": "0.5M", "detailed": False, "region": "Europe"},

        "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708, "country": "UAE", "pop": "3.3M", "detailed": False, "region": "Middle East"},
        "Abu Dhabi, UAE": {"lat": 24.4539, "lon": 54.3773, "country": "UAE", "pop": "1.4M", "detailed": False, "region": "Middle East"},
        "Sharjah, UAE": {"lat": 25.3463, "lon": 55.4209, "country": "UAE", "pop": "1.3M", "detailed": False, "region": "Middle East"},
        "Riyadh, Saudi Arabia": {"lat": 24.7136, "lon": 46.6753, "country": "Saudi Arabia", "pop": "7.0M", "detailed": False, "region": "Middle East"},
        "Jeddah, Saudi Arabia": {"lat": 21.4858, "lon": 39.1925, "country": "Saudi Arabia", "pop": "4.7M", "detailed": False, "region": "Middle East"},
        "Mecca, Saudi Arabia": {"lat": 21.3891, "lon": 39.8579, "country": "Saudi Arabia", "pop": "2.0M", "detailed": False, "region": "Middle East"},
        "Medina, Saudi Arabia": {"lat": 24.5247, "lon": 39.5692, "country": "Saudi Arabia", "pop": "1.5M", "detailed": False, "region": "Middle East"},
        "Dammam, Saudi Arabia": {"lat": 26.3927, "lon": 50.0916, "country": "Saudi Arabia", "pop": "1.2M", "detailed": False, "region": "Middle East"},
        "Doha, Qatar": {"lat": 25.2854, "lon": 51.5310, "country": "Qatar", "pop": "2.4M", "detailed": False, "region": "Middle East"},
        "Kuwait City, Kuwait": {"lat": 29.3759, "lon": 47.9774, "country": "Kuwait", "pop": "4.1M", "detailed": False, "region": "Middle East"},
        "Manama, Bahrain": {"lat": 26.2285, "lon": 50.5860, "country": "Bahrain", "pop": "0.6M", "detailed": False, "region": "Middle East"},
        "Muscat, Oman": {"lat": 23.5880, "lon": 58.3829, "country": "Oman", "pop": "1.5M", "detailed": False, "region": "Middle East"},
        "Tehran, Iran": {"lat": 35.6892, "lon": 51.3890, "country": "Iran", "pop": "8.7M", "detailed": False, "region": "Middle East"},
        "Isfahan, Iran": {"lat": 32.6539, "lon": 51.6660, "country": "Iran", "pop": "2.0M", "detailed": False, "region": "Middle East"},
        "Baghdad, Iraq": {"lat": 33.3152, "lon": 44.3661, "country": "Iraq", "pop": "7.0M", "detailed": False, "region": "Middle East"},

        "Istanbul, Turkey": {"lat": 41.0082, "lon": 28.9784, "country": "Turkey", "pop": "15.5M", "detailed": False, "region": "Middle East"},
        "Ankara, Turkey": {"lat": 39.9334, "lon": 32.8597, "country": "Turkey", "pop": "5.5M", "detailed": False, "region": "Middle East"},
        "Cairo, Egypt": {"lat": 30.0444, "lon": 31.2357, "country": "Egypt", "pop": "9.9M", "detailed": False, "region": "Middle East"},
        "Alexandria, Egypt": {"lat": 31.2001, "lon": 29.9187, "country": "Egypt", "pop": "5.0M", "detailed": False, "region": "Middle East"},

        "Beijing, China": {"lat": 39.9042, "lon": 116.4074, "country": "China", "pop": "21.5M", "detailed": False, "region": "East Asia"},
        "Shanghai, China": {"lat": 31.2304, "lon": 121.4737, "country": "China", "pop": "26.3M", "detailed": False, "region": "East Asia"},
        "Guangzhou, China": {"lat": 23.1291, "lon": 113.2644, "country": "China", "pop": "14.0M", "detailed": False, "region": "East Asia"},
        "Shenzhen, China": {"lat": 22.5431, "lon": 114.0579, "country": "China", "pop": "12.5M", "detailed": False, "region": "East Asia"},
        "Chengdu, China": {"lat": 30.5728, "lon": 104.0668, "country": "China", "pop": "16.3M", "detailed": False, "region": "East Asia"},
        "Hangzhou, China": {"lat": 30.2741, "lon": 120.1551, "country": "China", "pop": "10.3M", "detailed": False, "region": "East Asia"},
        "Wuhan, China": {"lat": 30.5928, "lon": 114.3055, "country": "China", "pop": "11.2M", "detailed": False, "region": "East Asia"},
        "Xi'an, China": {"lat": 34.3416, "lon": 108.9398, "country": "China", "pop": "12.9M", "detailed": False, "region": "East Asia"},
        "Nanjing, China": {"lat": 32.0603, "lon": 118.7969, "country": "China", "pop": "8.5M", "detailed": False, "region": "East Asia"},
        "Chongqing, China": {"lat": 29.5630, "lon": 106.5516, "country": "China", "pop": "30.0M", "detailed": False, "region": "East Asia"},
        "Tianjin, China": {"lat": 39.0842, "lon": 117.2009, "country": "China", "pop": "15.6M", "detailed": False, "region": "East Asia"},
        "Hong Kong, China": {"lat": 22.3193, "lon": 114.1694, "country": "China", "pop": "7.5M", "detailed": False, "region": "East Asia"},

        "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "pop": "13.9M", "detailed": False, "region": "East Asia"},
        "Osaka, Japan": {"lat": 34.6937, "lon": 135.5023, "country": "Japan", "pop": "2.7M", "detailed": False, "region": "East Asia"},
        "Yokohama, Japan": {"lat": 35.4437, "lon": 139.6380, "country": "Japan", "pop": "3.7M", "detailed": False, "region": "East Asia"},
        "Nagoya, Japan": {"lat": 35.1815, "lon": 136.9066, "country": "Japan", "pop": "2.3M", "detailed": False, "region": "East Asia"},
        "Sapporo, Japan": {"lat": 43.0618, "lon": 141.3545, "country": "Japan", "pop": "1.9M", "detailed": False, "region": "East Asia"},

        "Seoul, South Korea": {"lat": 37.5665, "lon": 126.9780, "country": "South Korea", "pop": "9.7M", "detailed": False, "region": "East Asia"},
        "Busan, South Korea": {"lat": 35.1796, "lon": 129.0756, "country": "South Korea", "pop": "3.4M", "detailed": False, "region": "East Asia"},
        "Incheon, South Korea": {"lat": 37.4563, "lon": 126.7052, "country": "South Korea", "pop": "3.0M", "detailed": False, "region": "East Asia"},

        "Bangkok, Thailand": {"lat": 13.7563, "lon": 100.5018, "country": "Thailand", "pop": "10.5M", "detailed": False, "region": "Southeast Asia"},
        "Chiang Mai, Thailand": {"lat": 18.7883, "lon": 98.9853, "country": "Thailand", "pop": "1.2M", "detailed": False, "region": "Southeast Asia"},
        "Singapore": {"lat": 1.3521, "lon": 103.8198, "country": "Singapore", "pop": "5.7M", "detailed": False, "region": "Southeast Asia"},
        "Kuala Lumpur, Malaysia": {"lat": 3.1390, "lon": 101.6869, "country": "Malaysia", "pop": "7.8M", "detailed": False, "region": "Southeast Asia"},
        "Jakarta, Indonesia": {"lat": -6.2088, "lon": 106.8456, "country": "Indonesia", "pop": "10.6M", "detailed": False, "region": "Southeast Asia"},
        "Surabaya, Indonesia": {"lat": -7.2575, "lon": 112.7521, "country": "Indonesia", "pop": "2.9M", "detailed": False, "region": "Southeast Asia"},
        "Manila, Philippines": {"lat": 14.5995, "lon": 120.9842, "country": "Philippines", "pop": "13.5M", "detailed": False, "region": "Southeast Asia"},
        "Cebu, Philippines": {"lat": 10.3157, "lon": 123.8854, "country": "Philippines", "pop": "0.9M", "detailed": False, "region": "Southeast Asia"},
        "Ho Chi Minh City, Vietnam": {"lat": 10.8231, "lon": 106.6297, "country": "Vietnam", "pop": "8.9M", "detailed": False, "region": "Southeast Asia"},
        "Hanoi, Vietnam": {"lat": 21.0278, "lon": 105.8342, "country": "Vietnam", "pop": "8.0M", "detailed": False, "region": "Southeast Asia"},
        "Yangon, Myanmar": {"lat": 16.8661, "lon": 96.1951, "country": "Myanmar", "pop": "5.2M", "detailed": False, "region": "Southeast Asia"},
        "Phnom Penh, Cambodia": {"lat": 11.5564, "lon": 104.9282, "country": "Cambodia", "pop": "2.1M", "detailed": False, "region": "Southeast Asia"},

        "Sydney, Australia": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "pop": "5.3M", "detailed": False, "region": "Oceania"},
        "Melbourne, Australia": {"lat": -37.8136, "lon": 144.9631, "country": "Australia", "pop": "5.0M", "detailed": False, "region": "Oceania"},
        "Brisbane, Australia": {"lat": -27.4698, "lon": 153.0251, "country": "Australia", "pop": "2.5M", "detailed": False, "region": "Oceania"},
        "Perth, Australia": {"lat": -31.9505, "lon": 115.8605, "country": "Australia", "pop": "2.0M", "detailed": False, "region": "Oceania"},
        "Adelaide, Australia": {"lat": -34.9285, "lon": 138.6007, "country": "Australia", "pop": "1.3M", "detailed": False, "region": "Oceania"},
        "Auckland, New Zealand": {"lat": -36.8485, "lon": 174.7633, "country": "New Zealand", "pop": "1.7M", "detailed": False, "region": "Oceania"},

        "São Paulo, Brazil": {"lat": -23.5505, "lon": -46.6333, "country": "Brazil", "pop": "12.3M", "detailed": False, "region": "South America"},
        "Rio de Janeiro, Brazil": {"lat": -22.9068, "lon": -43.1729, "country": "Brazil", "pop": "6.7M", "detailed": False, "region": "South America"},
        "Brasília, Brazil": {"lat": -15.7975, "lon": -47.8919, "country": "Brazil", "pop": "3.0M", "detailed": False, "region": "South America"},
        "Salvador, Brazil": {"lat": -12.9714, "lon": -38.5014, "country": "Brazil", "pop": "2.9M", "detailed": False, "region": "South America"},
        "Buenos Aires, Argentina": {"lat": -34.6037, "lon": -58.3816, "country": "Argentina", "pop": "15.0M", "detailed": False, "region": "South America"},
        "Lima, Peru": {"lat": -12.0464, "lon": -77.0428, "country": "Peru", "pop": "10.7M", "detailed": False, "region": "South America"},
        "Santiago, Chile": {"lat": -33.4489, "lon": -70.6693, "country": "Chile", "pop": "6.9M", "detailed": False, "region": "South America"},
        "Bogotá, Colombia": {"lat": 4.7110, "lon": -74.0721, "country": "Colombia", "pop": "10.9M", "detailed": False, "region": "South America"},
        "Caracas, Venezuela": {"lat": 10.4806, "lon": -66.9036, "country": "Venezuela", "pop": "2.9M", "detailed": False, "region": "South America"},
        "Quito, Ecuador": {"lat": -0.1807, "lon": -78.4678, "country": "Ecuador", "pop": "2.8M", "detailed": False, "region": "South America"},

        "Lagos, Nigeria": {"lat": 6.5244, "lon": 3.3792, "country": "Nigeria", "pop": "14.8M", "detailed": False, "region": "Africa"},
        "Kano, Nigeria": {"lat": 12.0022, "lon": 8.5920, "country": "Nigeria", "pop": "4.0M", "detailed": False, "region": "Africa"},
        "Johannesburg, South Africa": {"lat": -26.2041, "lon": 28.0473, "country": "South Africa", "pop": "5.6M", "detailed": False, "region": "Africa"},
        "Cape Town, South Africa": {"lat": -33.9249, "lon": 18.4241, "country": "South Africa", "pop": "4.6M", "detailed": False, "region": "Africa"},
        "Durban, South Africa": {"lat": -29.8587, "lon": 31.0218, "country": "South Africa", "pop": "3.9M", "detailed": False, "region": "Africa"},
        "Nairobi, Kenya": {"lat": -1.2921, "lon": 36.8219, "country": "Kenya", "pop": "4.4M", "detailed": False, "region": "Africa"},
        "Mombasa, Kenya": {"lat": -4.0435, "lon": 39.6682, "country": "Kenya", "pop": "1.2M", "detailed": False, "region": "Africa"},
        "Addis Ababa, Ethiopia": {"lat": 9.1450, "lon": 40.4897, "country": "Ethiopia", "pop": "3.4M", "detailed": False, "region": "Africa"},
        "Accra, Ghana": {"lat": 5.6037, "lon": -0.1870, "country": "Ghana", "pop": "2.5M", "detailed": False, "region": "Africa"},
        "Dar es Salaam, Tanzania": {"lat": -6.7924, "lon": 39.2083, "country": "Tanzania", "pop": "6.0M", "detailed": False, "region": "Africa"},
        "Casablanca, Morocco": {"lat": 33.5731, "lon": -7.5898, "country": "Morocco", "pop": "3.7M", "detailed": False, "region": "Africa"},
        "Tunis, Tunisia": {"lat": 36.8065, "lon": 10.1815, "country": "Tunisia", "pop": "2.6M", "detailed": False, "region": "Africa"},

        "Moscow, Russia": {"lat": 55.7558, "lon": 37.6173, "country": "Russia", "pop": "12.5M", "detailed": False, "region": "Europe/Asia"},
        "Saint Petersburg, Russia": {"lat": 59.9311, "lon": 30.3609, "country": "Russia", "pop": "5.3M", "detailed": False, "region": "Europe/Asia"},
        "Novosibirsk, Russia": {"lat": 55.0084, "lon": 82.9357, "country": "Russia", "pop": "1.6M", "detailed": False, "region": "Europe/Asia"},
        "Almaty, Kazakhstan": {"lat": 43.2220, "lon": 76.8512, "country": "Kazakhstan", "pop": "1.9M", "detailed": False, "region": "Central Asia"},
        "Astana, Kazakhstan": {"lat": 51.1605, "lon": 71.4704, "country": "Kazakhstan", "pop": "1.2M", "detailed": False, "region": "Central Asia"},
        "Tashkent, Uzbekistan": {"lat": 41.2995, "lon": 69.2401, "country": "Uzbekistan", "pop": "2.5M", "detailed": False, "region": "Central Asia"},

        "Mexico City, Mexico": {"lat": 19.4326, "lon": -99.1332, "country": "Mexico", "pop": "9.2M", "detailed": False, "region": "North America"},
        "Guadalajara, Mexico": {"lat": 20.6597, "lon": -103.3496, "country": "Mexico", "pop": "1.5M", "detailed": False, "region": "North America"},
        "Monterrey, Mexico": {"lat": 25.6866, "lon": -100.3161, "country": "Mexico", "pop": "1.1M", "detailed": False, "region": "North America"},
        "Guatemala City, Guatemala": {"lat": 14.6349, "lon": -90.5069, "country": "Guatemala", "pop": "2.9M", "detailed": False, "region": "North America"},
    }

@st.cache_data(ttl=3600)
def load_pakistan_aqi():
    return {
        "Islamabad": {
            "winter": 85, "summer": 60, "pollen": "High",
            "monthly": {1:95, 2:88, 3:75, 4:65, 5:55, 6:50, 7:45, 8:48, 9:52, 10:68, 11:82, 12:90},
            "sources": ["Vehicular emissions", "Dust", "Agricultural burning"],
            "health_advice": "Use N95 masks during winter smog season"
        },
        "Rawalpindi": {
            "winter": 120, "summer": 80, "pollen": "Very High",
            "monthly": {1:140, 2:130, 3:110, 4:95, 5:75, 6:65, 7:60, 8:62, 9:70, 10:90, 11:115, 12:135},
            "sources": ["Traffic", "Industrial", "Construction dust"],
            "health_advice": "Avoid outdoor activities during peak traffic hours"
        },
        "Lahore": {
            "winter": 200, "summer": 120, "pollen": "Moderate",
            "monthly": {1:250, 2:230, 3:180, 4:140, 5:110, 6:95, 7:85, 8:90, 9:105, 10:150, 11:210, 12:240},
            "sources": ["Industrial", "Vehicular", "Crop burning", "Dust"],
            "health_advice": "World's most polluted city - avoid travel Nov-Feb"
        },
        "Karachi": {
            "winter": 130, "summer": 90, "pollen": "Low",
            "monthly": {1:150, 2:140, 3:120, 4:100, 5:85, 6:75, 7:70, 8:72, 9:80, 10:105, 11:135, 12:145},
            "sources": ["Port emissions", "Traffic", "Industrial"],
            "health_advice": "Coastal winds help - mornings are cleaner"
        },
        "Peshawar": {
            "winter": 110, "summer": 75, "pollen": "Moderate",
            "monthly": {1:125, 2:115, 3:95, 4:80, 5:65, 6:55, 7:50, 8:52, 9:60, 10:85, 11:105, 12:120},
            "sources": ["Traffic", "Brick kilns", "Dust"],
            "health_advice": "Brick kiln season (Dec-Feb) is hazardous"
        },
    }

@st.cache_data(ttl=3600)
def load_pollen_data():
    return {
        "Rawalpindi": {
            "mar": 850, "apr": 1200, "may": 600,
            "level": "Very High",
            "species": ["Paper Mulberry", "Cannabis", "Eucalyptus", "Acacia"],
            "impact": "Severe for asthma patients",
            "peak_season": "March-April"
        },
        "Islamabad": {
            "mar": 720, "apr": 950, "may": 480,
            "level": "High",
            "species": ["Paper Mulberry", "Pines", "Grasses", "Olive"],
            "impact": "High for sensitive individuals",
            "peak_season": "March-April"
        },
    }

@st.cache_data(ttl=86400)
def load_who_facilities():
    """Load WHO health facilities with proper error handling"""
    try:
        facilities = [
            {"name": "PIMS Hospital", "lat": 33.6958, "lon": 73.0492, "city": "Islamabad",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "051-9261170", "address": "Sector G-8/3, Islamabad", "country": "Pakistan"},
            {"name": "Polyclinic Hospital", "lat": 33.7104, "lon": 73.0892, "city": "Islamabad",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": False, "emergency": True,
             "phone": "051-9213880", "address": "Sector G-6/2, Islamabad", "country": "Pakistan"},
            {"name": "Shifa International", "lat": 33.6990, "lon": 73.0730, "city": "Islamabad",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "051-8464646", "address": "Sector H-8/4, Islamabad", "country": "Pakistan"},
            {"name": "Benazir Bhutto Hospital", "lat": 33.5731, "lon": 73.0131, "city": "Rawalpindi",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "051-9330301", "address": "Murree Road, Rawalpindi", "country": "Pakistan"},
            {"name": "DHQ Hospital", "lat": 33.5651, "lon": 73.0169, "city": "Rawalpindi",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "051-9270301", "address": "Sadiqabad, Rawalpindi", "country": "Pakistan"},
            {"name": "Holy Family Hospital", "lat": 33.5700, "lon": 73.0200, "city": "Rawalpindi",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "051-9290301", "address": "Satellite Town, Rawalpindi", "country": "Pakistan"},
            {"name": "Jinnah Hospital", "lat": 31.5204, "lon": 74.3587, "city": "Lahore",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "042-99231400", "address": "Johar Town, Lahore", "country": "Pakistan"},
            {"name": "Mayo Hospital", "lat": 31.5580, "lon": 74.3148, "city": "Lahore",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "042-99211100", "address": "Nila Gumbad, Lahore", "country": "Pakistan"},
            {"name": "Services Hospital", "lat": 31.5400, "lon": 74.3400, "city": "Lahore",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": False, "emergency": True,
             "phone": "042-99203412", "address": "Jail Road, Lahore", "country": "Pakistan"},
            {"name": "JPMC", "lat": 24.8607, "lon": 67.0011, "city": "Karachi",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "021-99201300", "address": "Rafiqui Shaheed Road, Karachi", "country": "Pakistan"},
            {"name": "Aga Khan Hospital", "lat": 24.8923, "lon": 67.0730, "city": "Karachi",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "021-111-911-911", "address": "Stadium Road, Karachi", "country": "Pakistan"},
            {"name": "Lady Reading Hospital", "lat": 34.0151, "lon": 71.5249, "city": "Peshawar",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "091-9216200", "address": "GT Road, Peshawar", "country": "Pakistan"},

            {"name": "AIIMS Delhi", "lat": 28.5672, "lon": 77.2100, "city": "New Delhi",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "011-26588500", "address": "Ansari Nagar, New Delhi", "country": "India"},
            {"name": "Fortis Hospital", "lat": 28.4566, "lon": 77.0729, "city": "New Delhi",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "011-47135000", "address": "Vasant Kunj, New Delhi", "country": "India"},
            {"name": "Lilavati Hospital", "lat": 19.0505, "lon": 72.8286, "city": "Mumbai",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "022-26751000", "address": "Bandra, Mumbai", "country": "India"},

            {"name": "Mayo Clinic", "lat": 44.0224, "lon": -92.4668, "city": "Rochester",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "+1-507-284-2511", "address": "200 First St SW, Rochester, MN", "country": "USA"},
            {"name": "Cleveland Clinic", "lat": 41.5034, "lon": -81.6083, "city": "Cleveland",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "+1-216-444-2200", "address": "9500 Euclid Ave, Cleveland, OH", "country": "USA"},
            {"name": "Johns Hopkins", "lat": 39.2963, "lon": -76.5920, "city": "Baltimore",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "+1-410-955-5000", "address": "1800 Orleans St, Baltimore, MD", "country": "USA"},

            {"name": "St Thomas Hospital", "lat": 51.4995, "lon": -0.1187, "city": "London",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "+44-20-7188-7188", "address": "Westminster Bridge Rd, London", "country": "UK"},
            {"name": "Guy's Hospital", "lat": 51.5035, "lon": -0.0869, "city": "London",
             "type": "Hospital", "oxygen": True, "icu": True, "ventilator": True, "emergency": True,
             "phone": "+44-20-7188-7188", "address": "Great Maze Pond, London", "country": "UK"},
        ]

        if facilities:
            df = pd.DataFrame(facilities)
            required_cols = ['name', 'lat', 'lon', 'city', 'type', 'oxygen', 'icu', 'ventilator',
                           'emergency', 'phone', 'address', 'country']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = None
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading facilities: {str(e)}")
        return pd.DataFrame(columns=['name', 'lat', 'lon', 'city', 'type', 'oxygen', 'icu',
                                     'ventilator', 'emergency', 'phone', 'address', 'country'])

@st.cache_data(ttl=1800)
def fetch_nasa_fires():
    """Fetch real-time fire data"""
    MAPS_KEY = st.secrets["MAPS_KEY"]
    try:
        url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAPS_KEY}/VIIRS_NOAA20_NRT/1/60.0,23.0,77.0,37.0"
        df = pd.read_csv(url)
        if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
            return df[['latitude', 'longitude', 'brightness', 'confidence']]
    except:
        pass
    return pd.DataFrame(columns=['latitude', 'longitude', 'brightness', 'confidence'])

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth"""
    try:
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 6371 * 2 * asin(sqrt(a))
    except:
        return 0

def get_emergency_num(country):
    """Get emergency number by country"""
    nums = {
        "Pakistan": "1122", "India": "108", "Bangladesh": "999", "Nepal": "102", "Sri Lanka": "1990",
        "USA": "911", "Canada": "911", "UK": "999", "France": "112", "Germany": "112",
        "Italy": "112", "Spain": "112", "Netherlands": "112", "Switzerland": "144",
        "Sweden": "112", "Poland": "112", "Austria": "144", "Belgium": "112", "Denmark": "112",
        "Norway": "113", "Finland": "112", "Czech Republic": "155", "Hungary": "104",
        "Greece": "166", "Portugal": "112", "Ireland": "999",
        "UAE": "999", "Saudi Arabia": "997", "Qatar": "999", "Kuwait": "112",
        "Bahrain": "999", "Oman": "9999", "Iran": "115", "Turkey": "112", "Egypt": "123",
        "Iraq": "122", "Jordan": "911", "Lebanon": "140",
        "China": "120", "Japan": "119", "South Korea": "119", "Thailand": "1669",
        "Singapore": "995", "Malaysia": "999", "Indonesia": "118", "Philippines": "911",
        "Vietnam": "115", "Myanmar": "192", "Cambodia": "119",
        "Australia": "000", "New Zealand": "111",
        "Brazil": "192", "Argentina": "107", "Peru": "105", "Chile": "131",
        "Colombia": "123", "Venezuela": "171", "Ecuador": "911",
        "Nigeria": "112", "South Africa": "10177", "Kenya": "999", "Morocco": "150",
        "Ethiopia": "907", "Ghana": "193", "Tanzania": "114", "Tunisia": "190",
        "Russia": "103", "Kazakhstan": "103", "Uzbekistan": "103",
        "Mexico": "065", "Guatemala": "123"
    }
    return nums.get(country, "112")

def get_seasonal_data(city_key, cities, pak_aqi, pollen_data):
    """Get seasonal air quality data for any city"""
    try:
        city_name = city_key.split(',')[0]
        country = cities[city_key]["country"]
        month = datetime.now().month

        if city_name in pak_aqi:
            data = pak_aqi[city_name]
            pm25 = data["monthly"].get(month, data["winter"])
            pollen = data["pollen"]

            if month in [3,4,5] and city_name in pollen_data:
                pollen = pollen_data[city_name]["level"]

            return {
                "pm25": pm25, "pollen": pollen, "smog": pm25 > 150,
                "season": "Winter" if month in [11,12,1,2] else ("Spring" if month in [3,4,5] else "Summer"),
                "region": "South Asia", "source": "Pakistan EPA 2021-2024", "detailed": True,
                "health_advice": data.get("health_advice", "")
            }

        region_patterns = {
            "India": ("South Asia", 80), "Bangladesh": ("South Asia", 85), "Nepal": ("South Asia", 60), "Sri Lanka": ("South Asia", 45),
            "USA": ("North America", 25), "Canada": ("North America", 15), "Mexico": ("North America", 35),
            "UK": ("Europe", 25), "France": ("Europe", 22), "Germany": ("Europe", 20), "Italy": ("Europe", 25),
            "Spain": ("Europe", 23), "Netherlands": ("Europe", 18), "Switzerland": ("Europe", 15),
            "Sweden": ("Europe", 12), "Poland": ("Europe", 30), "Austria": ("Europe", 18),
            "Belgium": ("Europe", 20), "Denmark": ("Europe", 15), "Norway": ("Europe", 12),
            "Finland": ("Europe", 10), "Czech Republic": ("Europe", 25), "Hungary": ("Europe", 28),
            "Greece": ("Europe", 30), "Portugal": ("Europe", 18), "Ireland": ("Europe", 15),
            "UAE": ("Middle East", 70), "Saudi Arabia": ("Middle East", 75), "Qatar": ("Middle East", 65),
            "Kuwait": ("Middle East", 80), "Bahrain": ("Middle East", 65), "Oman": ("Middle East", 60),
            "Iran": ("Middle East", 85), "Turkey": ("Middle East", 55), "Egypt": ("Middle East", 90),
            "Iraq": ("Middle East", 95), "Jordan": ("Middle East", 50), "Lebanon": ("Middle East", 45),
            "China": ("East Asia", 60), "Japan": ("East Asia", 20), "South Korea": ("East Asia", 35),
            "Thailand": ("Southeast Asia", 45), "Singapore": ("Southeast Asia", 30), "Malaysia": ("Southeast Asia", 35),
            "Indonesia": ("Southeast Asia", 40), "Philippines": ("Southeast Asia", 35),
            "Vietnam": ("Southeast Asia", 45), "Myanmar": ("Southeast Asia", 50), "Cambodia": ("Southeast Asia", 40),
            "Australia": ("Oceania", 15), "New Zealand": ("Oceania", 12),
            "Brazil": ("South America", 35), "Argentina": ("South America", 30), "Peru": ("South America", 40),
            "Chile": ("South America", 35), "Colombia": ("South America", 30), "Venezuela": ("South America", 35),
            "Ecuador": ("South America", 35),
            "Nigeria": ("Africa", 70), "South Africa": ("Africa", 35), "Kenya": ("Africa", 45),
            "Morocco": ("Africa", 50), "Ethiopia": ("Africa", 55), "Ghana": ("Africa", 60),
            "Tanzania": ("Africa", 40), "Tunisia": ("Africa", 45),
            "Russia": ("Europe/Asia", 35), "Kazakhstan": ("Central Asia", 55), "Uzbekistan": ("Central Asia", 60)
        }

        region, base = region_patterns.get(country, ("Global", 50))

        if month in [11, 12, 1, 2]:
            factor = 1.4 if region in ["South Asia", "East Asia"] else 1.2
        elif month in [5, 6, 7, 8]:
            factor = 0.9 if region in ["Middle East", "South Asia"] else 0.8
        else:
            factor = 1.0

        return {
            "pm25": base * factor,
            "pollen": "Moderate",
            "smog": base * factor > 100,
            "season": "Winter" if month in [11,12,1,2] else ("Summer" if month in [5,6,7,8] else "Spring/Autumn"),
            "region": region,
            "source": f"WHO {region} Guidelines",
            "detailed": False,
            "health_advice": f"Based on {region} regional air quality patterns"
        }
    except Exception as e:
        return {
            "pm25": 50, "pollen": "Low", "smog": False,
            "season": "Unknown", "region": "Unknown",
            "source": "Default", "detailed": False,
            "health_advice": "Data unavailable"
        }

async def fetch_aqi_data(session, lat, lon):
    """Fetch real-time AQI data from OpenWeatherMap"""
    if not WEATHER_API_KEY:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
        async with session.get(url, timeout=10) as resp:
            data = await resp.json()
            if 'list' in data and data['list']:
                return {
                    'aqi': data['list'][0]['main']['aqi'],
                    'pm25': data['list'][0]['components'].get('pm2_5', 0),
                    'pm10': data['list'][0]['components'].get('pm10', 0),
                    'no2': data['list'][0]['components'].get('no2', 0),
                    'o3': data['list'][0]['components'].get('o3', 0),
                    'so2': data['list'][0]['components'].get('so2', 0)
                }
    except:
        pass
    return None

def calculate_risk(aqi_data, seasonal, condition, severity, travel_mode="Flight", vehicle_type="AC Vehicle"):
    """Calculate comprehensive health risk score - FIXED with vehicle_type parameter"""
    try:
        if aqi_data and aqi_data.get('pm25', 0) > 0:
            pm25 = (aqi_data['pm25'] + seasonal['pm25']) / 2
        else:
            pm25 = seasonal['pm25']

        base_risk = (pm25 / 15) * 15

        condition_multipliers = {
            "Asthma": 2.0,
            "COPD": 2.8,
            "Allergies": 1.6,
            "Healthy": 1.0,
            "Bronchitis": 2.2,
            "Heart Disease": 2.5,
            "Pregnancy": 1.4
        }
        mult = condition_multipliers.get(condition, 1.0)

        sev_mult = 1 + (severity - 1) * 0.35

        pollen_add = 0
        if seasonal['pollen'] in ["High", "Very High"] and condition in ["Asthma", "Allergies", "Bronchitis"]:
            pollen_add = 40 if seasonal['pollen'] == "Very High" else 25

        travel_mult = 1.0
        if travel_mode == "Flight":
            travel_mult = 1.0
        elif travel_mode in ["Train", "Bus"]:
            travel_mult = 1.2
        elif travel_mode == "Car": 
            if vehicle_type == "Non-AC Vehicle":
                travel_mult = 1.4  
            elif vehicle_type == "Electric Vehicle":
                travel_mult = 1.1 
            else:  
                travel_mult = 1.25

        total = (base_risk * mult * sev_mult * travel_mult) + pollen_add
        return min(total, 500), pm25
    except Exception as e:
        return 100, 50  

def get_risk_level(score):
    """Get risk level description and recommendations"""
    if score < 50:
        return "Good", "🟢", "Air quality is satisfactory. No health risk.", "Safe for all travelers"
    elif score < 100:
        return "Moderate", "🟡", "Air quality is acceptable. Sensitive individuals should reduce prolonged outdoor exertion.", "Caution for sensitive groups"
    elif score < 150:
        return "Unhealthy for Sensitive Groups", "🟠", "Members of sensitive groups may experience health effects.", "Reduce outdoor activities"
    elif score < 200:
        return "Unhealthy", "🟠", "Everyone may begin to experience health effects.", "Wear N95 mask, limit outdoor time"
    elif score < 300:
        return "Very Unhealthy", "🔴", "Health warnings of emergency conditions.", "Avoid outdoor travel. Stay indoors."
    else:
        return "Hazardous", "🟣", "Health alert: everyone may experience more serious health effects.", "DO NOT TRAVEL - Medical emergency risk"

def get_travel_recommendation(start_risk, end_risk, start_city, end_city):
    """Generate travel recommendation based on risk comparison"""
    try:
        if end_risk < start_risk * 0.7:
            improvement = ((start_risk - end_risk) / start_risk) * 100
            return "RECOMMENDED", f"✅ ROUTE HIGHLY RECOMMENDED - {improvement:.0f}% cleaner air at destination", "green"
        elif end_risk < start_risk * 0.9:
            improvement = ((start_risk - end_risk) / start_risk) * 100
            return "RECOMMENDED", f"✅ ROUTE RECOMMENDED - {improvement:.0f}% improvement in air quality", "green"
        elif end_risk > start_risk * 1.3:
            increase = ((end_risk - start_risk) / start_risk) * 100
            return "NOT RECOMMENDED", f"⚠️ HIGH RISK - {increase:.0f}% worse air quality at destination", "red"
        elif end_risk > start_risk * 1.1:
            increase = ((end_risk - start_risk) / start_risk) * 100
            return "CAUTION", f"⚡ PROCEED WITH CAUTION - {increase:.0f}% higher risk at destination", "orange"
        else:
            return "COMPARABLE", "⚡ COMPARABLE RISK - Air quality similar to origin", "yellow"
    except:
        return "UNKNOWN", "Unable to calculate recommendation", "gray"



