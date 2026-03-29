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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    /* Global Styles */
    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Main Title with Gradient Text */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .subtitle {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #64748b;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Metric Cards with Glassmorphism */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 0.5rem 0;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }

    /* Success Box with Pulse Animation */
    .success-box {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 10px 25px rgba(0, 184, 148, 0.3);
        animation: pulse 2s infinite;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Warning Box */
    .warning-box {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 10px 25px rgba(253, 203, 110, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Danger Box with Shake Animation */
    .danger-box {
        background: linear-gradient(135deg, #d63031 0%, #e84393 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 10px 25px rgba(214, 48, 49, 0.3);
        animation: shake 0.5s;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(116, 185, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Facility Cards with Hover Effect */
    .facility-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .facility-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        border-color: #667eea;
    }

    /* Stat Cards */
    .stat-card {
        background: #ffffff;
        border-left: 5px solid #667eea;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transform: translateX(5px);
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    /* Emergency Button */
    .emergency-btn {
        background: linear-gradient(135deg, #d63031 0%, #e84393 100%) !important;
        animation: pulse 2s infinite;
    }

    /* Animations */
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 184, 148, 0.4); }
        50% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(0, 184, 148, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 184, 148, 0); }
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }

    /* Highlight Text */
    .highlight {
        background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
        color: #1e293b;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }

    /* Risk Level Badges */
    .risk-badge-good {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    .risk-badge-moderate {
        background: linear-gradient(135deg, #fdcb6e 0%, #f39c12 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    .risk-badge-unhealthy {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    .risk-badge-hazardous {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    /* Progress Bar Customization */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }

    /* Selectbox and Input Styling */
    .stSelectbox, .stTextInput, .stSlider {
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }

    /* Divider Styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 2rem 0;
    }

    /* Welcome Card */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }

    .welcome-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }

    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.1);
    }

    /* Emergency Protocol Cards */
    .emergency-card {
        background: white;
        border-left: 5px solid;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .emergency-card-warning {
        border-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }

    .emergency-card-info {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    }

    .emergency-card-success {
        border-color: #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    }
</style>
""", unsafe_allow_html=True)

cities = load_cities()
who_facilities = load_who_facilities()
pak_aqi = load_pakistan_aqi()
pollen_data = load_pollen_data()

st.markdown('<h1 class="main-title">🌍 Aero-Rescue AI Global</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">200+ Cities • 80+ Countries • Real-time Air Quality • Health Risk Assessment</p>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/lungs.png", width=80)
    st.title("🌐 Global Navigation")

    try:
        facility_count = len(who_facilities) if who_facilities is not None and not who_facilities.empty else 0
    except:
        facility_count = 0

    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.2rem; border-radius: 12px; margin-bottom: 1.5rem; color: white; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);'>
        <div style='font-size: 0.85rem; opacity: 0.9; margin-bottom: 0.5rem;'>📊 Global Coverage</div>
        <div style='font-size: 1.1rem; font-weight: 600;'>
            🌍 {} Countries<br>
            🏙️ {} Cities<br>
            🏥 {} Facilities
        </div>
    </div>
    """.format(len(set(c["country"] for c in cities.values())), len(cities), facility_count), unsafe_allow_html=True)

    countries = sorted(list(set([c["country"] for c in cities.values()])))

    col1, col2 = st.columns(2)
    with col1:
        c_from = st.selectbox("From", ["All"] + countries, key="c_from")
    with col2:
        c_to = st.selectbox("To", ["All"] + countries, key="c_to")

    from_cities = [k for k, v in cities.items() if v["country"] == c_from] if c_from != "All" else list(cities.keys())
    to_cities = [k for k, v in cities.items() if v["country"] == c_to] if c_to != "All" else list(cities.keys())

    current = st.selectbox(
        "🏙️ Origin City",
        from_cities,
        index=from_cities.index(st.session_state.current) if st.session_state.current in from_cities else 0,
        key="current"
    )
    destination = st.selectbox(
        "🎯 Destination City",
        to_cities,
        index=to_cities.index(st.session_state.destination) if st.session_state.destination in to_cities else 0,
        key="destination"
    )

    from_c = cities[current]["country"]
    to_c = cities[destination]["country"]

    if cities[current].get("detailed"):
        st.success("📊 Pakistan EPA Data (Detailed)")
    else:
        st.info(f"🌍 WHO Global Data")

    st.info(f"🛫 {from_c} → 🛬 {to_c}")

    st.divider()

    st.subheader("✈️ Travel Mode")

    if 'vehicle_type' not in st.session_state:
        st.session_state.vehicle_type = "AC Vehicle"

    travel_mode = st.radio(
        "Select mode",
        ["Flight", "Train", "Car", "Bus"],
        horizontal=True,
        key="sel_travel_mode",
        index=["Flight", "Train", "Car", "Bus"].index(st.session_state.sel_travel_mode)
    )

    vehicle_type = st.session_state.vehicle_type
    if travel_mode in ["Car", "Bus"]:
        vehicle_type = st.selectbox(
            "Vehicle Type",
            ["AC Vehicle", "Non-AC Vehicle", "Electric Vehicle"],
            key="vehicle_type_select",
            index=["AC Vehicle", "Non-AC Vehicle", "Electric Vehicle"].index(st.session_state.vehicle_type)
        )
        st.session_state.vehicle_type = vehicle_type

    st.divider()

    st.subheader("🏥 Health Profile")
    condition = st.selectbox(
        "Medical Condition",
        ["Asthma", "COPD", "Allergies", "Bronchitis", "Heart Disease", "Pregnancy", "Healthy"],
        key="condition",
        index=["Asthma", "COPD", "Allergies", "Bronchitis", "Heart Disease", "Pregnancy", "Healthy"].index(st.session_state.condition)
    )

    severity = st.slider(
        "Severity Level",
        1, 5,
        st.session_state.severity,
        key="severity"
    )

    risk_mult = {"Asthma": 2.0, "COPD": 2.8, "Allergies": 1.6, "Bronchitis": 2.2, "Heart Disease": 2.5, "Pregnancy": 1.4, "Healthy": 1.0}[condition]
    st.caption(f"Risk Multiplier: {risk_mult}x")

    st.divider()

    st.subheader("🚨 Emergency Contact")
    emergency_contact = st.text_input(
        "Phone Number",
        st.session_state.emergency_contact,
        key="emergency_contact"
    )

    st.divider()

    st.subheader("🔥 Environmental Factors")
    wildfire = st.checkbox("🔥 Wildfire Event (+80 PM2.5)", key="wild")
    smog = st.checkbox("🌫️ Smog Event (+100 PM2.5)", key="smog")
    dust_storm = st.checkbox("🌪️ Dust Storm (+60 PM2.5)", key="dust")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.results = None
            st.rerun()
    with col2:
        if st.button("📊 New Analysis", use_container_width=True, type="primary"):
            st.session_state.analysis_done = False
            st.rerun()

if current == destination:
    st.warning("⚠️ Please select different origin and destination cities")
else:
    if not st.session_state.analysis_done:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='stat-card'>
                <h3 style='color: #1e293b; margin-bottom: 0.5rem;'>🛫 {current}</h3>
                <p style='color: #64748b; line-height: 1.6;'>
                <span style='color: #667eea; font-weight: 600;'>Country:</span> {from_c}<br>
                <span style='color: #667eea; font-weight: 600;'>Population:</span> {cities[current]['pop']}<br>
                <span style='color: #667eea; font-weight: 600;'>Region:</span> {cities[current]['region']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-card'>
                <h3 style='color: #1e293b; margin-bottom: 0.5rem;'>🛬 {destination}</h3>
                <p style='color: #64748b; line-height: 1.6;'>
                <span style='color: #667eea; font-weight: 600;'>Country:</span> {to_c}<br>
                <span style='color: #667eea; font-weight: 600;'>Population:</span> {cities[destination]['pop']}<br>
                <span style='color: #667eea; font-weight: 600;'>Region:</span> {cities[destination]['region']}</p>
            </div>
            """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 ANALYZE SAFE ROUTE", type="primary", use_container_width=True):
                with st.spinner("🔍 Analyzing air quality data..."):
                    progress_bar = st.progress(0)

                    start_d = cities[current]
                    end_d = cities[destination]

                    current_travel_mode = st.session_state.sel_travel_mode
                    current_vehicle_type = st.session_state.get('vehicle_type', 'AC Vehicle')
                    current_condition = st.session_state.condition
                    current_severity = st.session_state.severity

                    progress_bar.progress(10)

                    async def get_data():
                        async with aiohttp.ClientSession() as session:
                            return await asyncio.gather(
                                fetch_aqi_data(session, start_d['lat'], start_d['lon']),
                                fetch_aqi_data(session, end_d['lat'], end_d['lon'])
                            )

                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        start_aqi, end_aqi = loop.run_until_complete(get_data())
                        loop.close()
                        api_status = "✅ Live OpenWeatherMap API"
                    except Exception as e:
                        start_aqi, end_aqi = None, None
                        api_status = "📊 Historical Data Mode"
                        st.info("Using historical air quality data (API not available)")

                    progress_bar.progress(40)
                    start_season = get_seasonal_data(current, cities, pak_aqi, pollen_data)
                    end_season = get_seasonal_data(destination, cities, pak_aqi, pollen_data)

                    if wildfire:
                        start_season['pm25'] += 80
                        end_season['pm25'] += 80
                    if smog:
                        start_season['pm25'] += 100
                        end_season['pm25'] += 100
                    if dust_storm:
                        start_season['pm25'] += 60
                        end_season['pm25'] += 60

                    progress_bar.progress(60)
                    start_risk, start_pm25 = calculate_risk(
                        start_aqi, start_season, current_condition, current_severity,
                        current_travel_mode, current_vehicle_type
                    )
                    end_risk, end_pm25 = calculate_risk(
                        end_aqi, end_season, current_condition, current_severity,
                        current_travel_mode, current_vehicle_type
                    )

                    start_lvl, start_emoji, start_msg, start_rec = get_risk_level(start_risk)
                    end_lvl, end_emoji, end_msg, end_rec = get_risk_level(end_risk)

                    progress_bar.progress(80)
                    dest_city_name = destination.split(',')[0]

                    nearby = pd.DataFrame()
                    try:
                        if who_facilities is not None and not who_facilities.empty:
                            nearby = who_facilities[who_facilities['city'] == dest_city_name].copy()

                            if nearby.empty:
                                who_facilities_copy = who_facilities.copy()
                                who_facilities_copy['dist'] = who_facilities_copy.apply(
                                    lambda r: haversine(end_d['lat'], end_d['lon'], r['lat'], r['lon']), axis=1
                                )
                                nearby = who_facilities_copy.nsmallest(5, 'dist')
                    except Exception as e:
                        st.warning(f"Could not load nearby facilities: {str(e)}")
                        nearby = pd.DataFrame()

                    progress_bar.progress(90)
                    fire_data = fetch_nasa_fires()
                    fires = []
                    if not fire_data.empty:
                        mid_lat = (start_d['lat'] + end_d['lat']) / 2
                        mid_lon = (start_d['lon'] + end_d['lon']) / 2
                        for _, f in fire_data.iterrows():
                            if haversine(mid_lat, mid_lon, f['latitude'], f['longitude']) < 150:
                                fires.append({
                                    'lat': f['latitude'],
                                    'lon': f['longitude'],
                                    'conf': f['confidence'],
                                    'bright': f['brightness']
                                })

                    rec_status, rec_msg, rec_color = get_travel_recommendation(start_risk, end_risk, current, destination)

                    progress_bar.progress(100)

                    st.session_state.results = {
                        'start_aqi': start_aqi, 'end_aqi': end_aqi,
                        'start_risk': start_risk, 'end_risk': end_risk,
                        'start_pm25': start_pm25, 'end_pm25': end_pm25,
                        'start_lvl': start_lvl, 'start_emoji': start_emoji,
                        'start_msg': start_msg, 'start_rec': start_rec,
                        'start_season': start_season, 'start_d': start_d,
                        'end_lvl': end_lvl, 'end_emoji': end_emoji,
                        'end_msg': end_msg, 'end_rec': end_rec,
                        'end_season': end_season, 'end_d': end_d,
                        'nearby': nearby, 'api_status': api_status,
                        'from_c': from_c, 'to_c': to_c,
                        'fires': fires, 'fire_count': len(fires),
                        'travel_mode': current_travel_mode,
                        'vehicle_type': current_vehicle_type,
                        'rec_status': rec_status, 'rec_msg': rec_msg, 'rec_color': rec_color,
                        'distance': haversine(start_d['lat'], start_d['lon'], end_d['lat'], end_d['lon'])
                    }
                    st.session_state.analysis_done = True
                    st.rerun()

    if st.session_state.analysis_done and st.session_state.results:
        r = st.session_state.results

        from_em = get_emergency_num(r['from_c'])
        to_em = get_emergency_num(r['to_c'])

        st.markdown("---")
        metric_cols = st.columns(5)
        metrics = [
            ("Data Source", r['api_status'], "📡"),
            ("Travel Mode", f"{r['travel_mode']} ({r.get('vehicle_type', 'N/A')})", "✈️"),
            ("Distance", f"{r['distance']:.0f} km", "📏"),
            ("Fire Alerts", f"{r['fire_count']} Active" if r['fire_count'] else "None", "🔥"),
            ("WHO Facilities", f"{facility_count} Global", "🏥")
        ]
        for col, (label, value, icon) in zip(metric_cols, metrics):
            with col:
                st.markdown(f"""
                <div style='text-align: center; padding: 1.2rem; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{icon}</div>
                    <div style='font-size: 0.85rem; color: #64748b; margin-bottom: 0.25rem;'>{label}</div>
                    <div style='font-size: 1rem; font-weight: 600; color: #1e293b;'>{value}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='info-box' style='margin-top: 1.5rem;'>
            <h4 style='margin-bottom: 0.5rem;'>🚨 Emergency Numbers</h4>
            <div style='display: flex; gap: 2rem; flex-wrap: wrap;'>
                <div><b>{r['from_c']}:</b> {from_em}</div>
                <div><b>{r['to_c']}:</b> {to_em}</div>
                <div><b>Your Contact:</b> {st.session_state.emergency_contact}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <h2 style='text-align: center; margin: 2rem 0; color: #1e293b;'>
            🛫 {current} <span style='color: #667eea;'>→</span> {destination}
        </h2>
        """, unsafe_allow_html=True)

        if r['start_season'].get('detailed'):
            st.success(f"📊 Pakistan EPA 2021-2024 Detailed Data for {current.split(',')[0]}")
        if r['end_season'].get('detailed'):
            st.success(f"📊 Pakistan EPA 2021-2024 Detailed Data for {destination.split(',')[0]}")

        st.header("📊 Air Quality Risk Assessment")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📍 Origin: {current.split(',')[0]}")

            risk_class = "risk-badge-good" if r['start_risk'] < 50 else ("risk-badge-moderate" if r['start_risk'] < 150 else "risk-badge-unhealthy")
            st.markdown(f"<div class='{risk_class}' style='margin-bottom: 1rem;'>{r['start_lvl']}</div>", unsafe_allow_html=True)

            st.markdown(f"<h1 style='text-align: center; font-size: 4rem; margin: 1rem 0;'>{r['start_emoji']}</h1>", unsafe_allow_html=True)

            st.progress(min(r['start_risk'] / 500, 1.0))
            st.markdown(f"<p style='text-align: center; color: #64748b;'><b>Risk Score: {r['start_risk']:.0f}/500</b></p>", unsafe_allow_html=True)

            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                cols = st.columns(2)
                with cols[0]:
                    st.metric("PM2.5", f"{r['start_pm25']:.1f} μg/m³")
                    st.metric("Live AQI", f"{r['start_aqi']['aqi']}/5" if r['start_aqi'] else "N/A")
                with cols[1]:
                    st.metric("Season", r['start_season']['season'])
                    st.metric("Pollen", r['start_season']['pollen'])
                st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("📋 Detailed Information"):
                st.write(f"**Data Source:** {r['start_season']['source']}")
                st.write(f"**Region:** {r['start_season']['region']}")
                if r['start_season'].get('health_advice'):
                    st.info(f"💡 {r['start_season']['health_advice']}")
                if r['start_season']['smog']:
                    st.error("⚠️ SMOG ALERT: High pollution season")

            st.info(f"🩺 {r['start_msg']}")

        with col2:
            st.subheader(f"🏁 Destination: {destination.split(',')[0]}")

            risk_class = "risk-badge-good" if r['end_risk'] < 50 else ("risk-badge-moderate" if r['end_risk'] < 150 else ("risk-badge-unhealthy" if r['end_risk'] < 300 else "risk-badge-hazardous"))
            st.markdown(f"<div class='{risk_class}' style='margin-bottom: 1rem;'>{r['end_lvl']}</div>", unsafe_allow_html=True)

            st.markdown(f"<h1 style='text-align: center; font-size: 4rem; margin: 1rem 0;'>{r['end_emoji']}</h1>", unsafe_allow_html=True)

            st.progress(min(r['end_risk'] / 500, 1.0))
            st.markdown(f"<p style='text-align: center; color: #64748b;'><b>Risk Score: {r['end_risk']:.0f}/500</b></p>", unsafe_allow_html=True)

            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                cols = st.columns(2)
                with cols[0]:
                    st.metric("PM2.5", f"{r['end_pm25']:.1f} μg/m³")
                    st.metric("Live AQI", f"{r['end_aqi']['aqi']}/5" if r['end_aqi'] else "N/A")
                with cols[1]:
                    st.metric("Season", r['end_season']['season'])
                    st.metric("Pollen", r['end_season']['pollen'])
                st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("📋 Detailed Information"):
                st.write(f"**Data Source:** {r['end_season']['source']}")
                st.write(f"**Region:** {r['end_season']['region']}")
                if r['end_season'].get('health_advice'):
                    st.info(f"💡 {r['end_season']['health_advice']}")
                if r['end_season']['smog']:
                    st.error("⚠️ SMOG ALERT: High pollution season")

            st.info(f"🩺 {r['end_msg']}")

        st.markdown("---")
        st.header("🧭 Travel Safety Verdict")

        if r['rec_color'] == "green":
            st.markdown(f'<div class="success-box">{r["rec_msg"]}</div>', unsafe_allow_html=True)
        elif r['rec_color'] == "red":
            st.markdown(f'<div class="danger-box">{r["rec_msg"]}</div>', unsafe_allow_html=True)
            if r['end_risk'] > 250:
                st.error("🚨 CRITICAL WARNING: Medical emergency risk at destination. Consult doctor before travel.")
        else:
            st.markdown(f'<div class="warning-box">{r["rec_msg"]}</div>', unsafe_allow_html=True)

        if r['fire_count'] > 0:
            st.error(f"""
            🔥 **WILDFIRE ALERT**: {r['fire_count']} active fire(s) detected within 150km of your route!
            This may significantly impact air quality during travel.
            """)

        st.markdown("---")
        st.header("🗺️ Clean Air Route Map")

        center = [(r['start_d']['lat'] + r['end_d']['lat'])/2, (r['start_d']['lon'] + r['end_d']['lon'])/2]
        zoom = 3 if r['distance'] > 3000 else (4 if r['distance'] > 1500 else 5)

        m = folium.Map(location=center, zoom_start=zoom, tiles='CartoDB positron')

        route_color = "green" if r['rec_color'] == "green" else ("red" if r['rec_color'] == "red" else "orange")
        folium.PolyLine(
            [[r['start_d']['lat'], r['start_d']['lon']], [r['end_d']['lat'], r['end_d']['lon']]],
            color=route_color, weight=6, opacity=0.9, tooltip=f"Risk Level: {r['end_lvl']}"
        ).add_to(m)

        folium.Marker(
            [r['start_d']['lat'], r['start_d']['lon']],
            popup=f"<b>{current}</b><br>Risk: {r['start_lvl']}<br>PM2.5: {r['start_pm25']:.1f}",
            icon=folium.Icon(color='blue', icon='plane-departure', prefix='fa')
        ).add_to(m)

        folium.Marker(
            [r['end_d']['lat'], r['end_d']['lon']],
            popup=f"<b>{destination}</b><br>Risk: {r['end_lvl']}<br>PM2.5: {r['end_pm25']:.1f}",
            icon=folium.Icon(color='red', icon='plane-arrival', prefix='fa')
        ).add_to(m)

        for f in r['fires']:
            folium.CircleMarker(
                [f['lat'], f['lon']],
                radius=10,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.7,
                popup=f"🔥 Wildfire<br>Confidence: {f['conf']}<br>Brightness: {f['bright']}"
            ).add_to(m)

        try:
            if r['nearby'] is not None and not r['nearby'].empty:
                for _, row in r['nearby'].iterrows():
                    color = 'green' if row['type'] == 'Hospital' else 'orange'
                    icon = 'hospital' if row['type'] == 'Hospital' else 'plus'
                    folium.Marker(
                        [row['lat'], row['lon']],
                        popup=f"""
                        <b>{row['name']}</b><br>
                        Type: {row['type']}<br>
                        Phone: {row['phone']}<br>
                        {'🟢 Oxygen' if row['oxygen'] else '🔴 No Oxygen'}<br>
                        {'🚨 24/7 Emergency' if row['emergency'] else '⏰ Limited Hours'}
                        """,
                        icon=folium.Icon(color=color, icon=icon, prefix='fa')
                    ).add_to(m)
        except Exception as e:
            st.warning("Could not display all facilities on map")

        st_folium(m, width=1000, height=600)

        st.markdown("---")
        st.header(f"🏥 Medical Facilities Near {destination.split(',')[0]}")

        try:
            if r['nearby'] is not None and not r['nearby'].empty:
                for _, row in r['nearby'].iterrows():
                    with st.container():
                        st.markdown('<div class="facility-card">', unsafe_allow_html=True)
                        fcol1, fcol2, fcol3, fcol4 = st.columns([2, 2, 2, 2])

                        with fcol1:
                            icon = "🏥" if row['type'] == 'Hospital' else "💊"
                            st.subheader(f"{icon} {row['name']}")
                            st.caption(f"📍 {row.get('address', row['city'])}, {row.get('country', '')}")

                        with fcol2:
                            st.write(f"📞 **{row['phone']}**")
                            st.write(f"**Type:** {row['type']}")

                        with fcol3:
                            services = []
                            if row['oxygen']: services.append("🟢 Oxygen")
                            if row['icu']: services.append("🏥 ICU")
                            if row['ventilator']: services.append("🔌 Ventilator")
                            if row['emergency']: services.append("🚨 24/7")
                            st.write("**Services:**")
                            for s in services:
                                st.write(s)

                        with fcol4:
                            if row.get('dist'):
                                st.write(f"📏 **{row['dist']:.1f} km** from destination")
                            st.write(f"**City:** {row['city']}")

                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No WHO-listed facilities found in this city. Contact local emergency services.")
                st.info(f"🚨 Emergency Number for {r['to_c']}: **{to_em}**")
        except Exception as e:
            st.error(f"Error displaying facilities: {str(e)}")
            st.info(f"🚨 Emergency Number for {r['to_c']}: **{to_em}**")

        st.markdown("---")
        st.header("🚨 Emergency Action Protocol")

        ecol1, ecol2, ecol3 = st.columns(3)

        with ecol1:
            st.markdown("""
            <div class='emergency-card emergency-card-warning'>
                <h4 style='color: #92400e; margin-bottom: 1rem;'>📞 Emergency Numbers</h4>
                <p style='color: #78350f; line-height: 1.8;'>
                <b>Origin ({}):</b><br>{}<br><br>
                <b>Destination ({}):</b><br>{}<br><br>
                <b>Your Contact:</b><br>{}</p>
            </div>
            """.format(r['from_c'], from_em, r['to_c'], to_em, st.session_state.emergency_contact), unsafe_allow_html=True)

        with ecol2:
            st.markdown("""
            <div class='emergency-card emergency-card-info'>
                <h4 style='color: #1e40af; margin-bottom: 1rem;'>💊 Medical Kit</h4>
                <ul style='color: #1e3a8a; line-height: 2;'>
                    <li>Rescue inhaler (2x)</li>
                    <li>N95/N99 masks (pack)</li>
                    <li>Pulse oximeter</li>
                    <li>Prescription meds</li>
                    <li>Antihistamines</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with ecol3:
            st.markdown("""
            <div class='emergency-card emergency-card-success'>
                <h4 style='color: #065f46; margin-bottom: 1rem;'>✅ Pre-Travel Checklist</h4>
                <ul style='color: #064e3b; line-height: 2;'>
                    <li>Doctor consultation</li>
                    <li>Travel insurance</li>
                    <li>Hospital locations saved</li>
                    <li>Air quality app installed</li>
                    <li>Emergency contacts shared</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button(f"🚨 ACTIVATE EMERGENCY PROTOCOL - Call {to_em}", type="primary", use_container_width=True, key="emergency_btn"):
            nearest_hospital = "Search local hospitals"
            try:
                if r['nearby'] is not None and not r['nearby'].empty:
                    nearest_hospital = r['nearby'].iloc[0]['name']
            except:
                pass

            st.markdown(f"""
            <div class='danger-box'>
                <h2>🚨 EMERGENCY PROTOCOL ACTIVATED</h2>
                <p><b>Dialing:</b> {to_em}</p>
                <p><b>Location:</b> {destination}</p>
                <p><b>Condition:</b> {st.session_state.condition} (Severity: {st.session_state.severity}/5)</p>
                <p><b>Notifying:</b> {st.session_state.emergency_contact}</p>
                <p><b>Nearest Hospital:</b> {nearest_hospital}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.header("📚 Integrated Data Sources")

        dcol1, dcol2, dcol3 = st.columns(3)

        with dcol1:
            st.subheader("🇵🇰 Pakistan (Primary)")
            st.write("✅ **Pakistan EPA Air Quality**")
            st.caption("2021-2024 | 12 cities | Monthly PM2.5")
            st.write("✅ **WHO Health Facilities**")
            st.caption("20 hospitals + 4 pharmacies")
            st.write("✅ **Pollen Monitoring Study**")
            st.caption("2023 | Rawalpindi/Islamabad/Lahore")

        with dcol2:
            st.subheader("🌍 Global Coverage")
            st.write("🌐 **OpenWeatherMap API**")
            st.caption("Real-time global AQI")
            st.write("🛰️ **NASA FIRMS**")
            st.caption("Active fire detection")
            st.write("📊 **WHO Regional Data**")
            st.caption("80+ countries baseline")

        with dcol3:
            st.subheader("🏥 Medical Network")
            st.write("🏥 **WHO Facilities Database**")
            st.caption("Verified hospitals worldwide")
            st.write("🚑 **Emergency Numbers**")
            st.caption("Country-specific services")
            st.write("💊 **Pharmacy Network**")
            st.caption("24/7 medication access")

if not st.session_state.analysis_done:
    st.markdown("""
    <div class='welcome-card'>
        <h1 style='position: relative; z-index: 1;'>👋 Welcome to Aero-Rescue AI Global</h1>
        <p style='font-size: 1.3rem; position: relative; z-index: 1; opacity: 0.95;'>Your intelligent companion for safe travel with respiratory conditions</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size: 3.5rem; margin-bottom: 1rem;'>🌍</div>
            <h3 style='color: #1e293b; margin-bottom: 0.5rem;'>Global Coverage</h3>
            <p style='color: #64748b;'>200+ cities across 80+ countries with real-time air quality data</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size: 3.5rem; margin-bottom: 1rem;'>🏥</div>
            <h3 style='color: #1e293b; margin-bottom: 0.5rem;'>Medical Network</h3>
            <p style='color: #64748b;'>WHO-verified hospitals and pharmacies with emergency services</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size: 3.5rem; margin-bottom: 1rem;'>🤖</div>
            <h3 style='color: #1e293b; margin-bottom: 0.5rem;'>AI Risk Assessment</h3>
            <p style='color: #64748b;'>Personalized health risk analysis based on your medical profile</p>
        </div>
        """, unsafe_allow_html=True)

    st.info("👈 **Get Started:** Select your origin and destination cities from the sidebar, then click 'ANALYZE SAFE ROUTE'")

