# 🌍 Aero-Rescue AI Global
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?logo=pandas&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-Interactive_Maps-77B829)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

An intelligent, data-driven travel companion designed to calculate environmental health risks, track real-time air quality, and ensure the safety of travelers with respiratory conditions globally.

## 📋 Overview

Aero-Rescue AI Global is a comprehensive health and travel safety platform. It evaluates real-time environmental threats—such as smog, pollen, and active wildfires—and cross-references them with a user's specific medical profile (e.g., Asthma, COPD) to generate a personalized Travel Safety Verdict. The platform covers over 200 cities across 80+ countries and integrates a global network of WHO-verified medical facilities.

## ✨ Key Features

### 🤖 Personalized Health Risk AI
* **Dynamic Risk Scoring** - Calculates a personalized risk score (0-500) based on PM2.5 levels, seasonal pollen, and user-specific medical multipliers.
* **Health Profiles** - Adapts warnings for specific conditions including Asthma, COPD, Allergies, Bronchitis, Heart Disease, and Pregnancy.
* **Travel Mode Impact** - Adjusts risk calculations based on how you travel (e.g., Flight, Train, AC vs. Non-AC Vehicles).

### 🌪️ Real-Time Environmental Tracking
* **Live AQI Integration** - Fetches real-time Air Quality Index and PM2.5/PM10 data via the OpenWeatherMap API.
* **NASA Wildfire Detection** - Pulls real-time satellite data from NASA FIRMS to detect active fires within a 150km radius of your route.
* **Historical Data Fallback** - Uses a rich, built-in database of seasonal air quality trends if live APIs are unavailable.

### 🏥 Global Emergency Network
* **Interactive Route Mapping** - Visualizes your journey, air quality zones, and nearby wildfires using `folium` maps.
* **WHO Facility Locator** - Automatically finds the nearest verified hospitals with ICU and Oxygen capabilities at your destination.
* **Automated Emergency Protocols** - Generates one-click access to local emergency numbers (e.g., 911, 112, 1122) based on the destination country.

### 🎨 Modern, Responsive UI/UX
* **Custom Styling** - Features a beautiful, cyberpunk-inspired glassmorphism design with animated CSS elements.
* **Visual Status Indicators** - Uses color-coded warning boxes, pulsing emergency buttons, and dynamic progress bars.

## 🚀 Technology Stack

* **Frontend framework:** Streamlit
* **Data Manipulation:** Pandas, NumPy
* **Mapping & GIS:** Folium, Streamlit-Folium
* **Asynchronous Networking:** `aiohttp`, `asyncio`, `requests`
* **External APIs:** OpenWeatherMap API, NASA FIRMS (VIIRS/NOAA-20)
* **Deployment Integration:** PyNgrok (for Google Colab)

## 📦 Installation & Setup

### Prerequisites
* Python 3.8 or higher
* `pip` package manager
* **OpenWeatherMap API Key** (Get a free key at [openweathermap.org](https://openweathermap.org/))

### Local Setup
Clone the repository:
```bash
git clone [https://github.com/HamadAliRaza/Aero-Rescue-AI.git](https://github.com/HamadAliRaza/Aero-Rescue-AI.git)
cd Aero-Rescue-AI
```
Install the required dependencies:

```Bash
pip install streamlit folium streamlit-folium pandas aiohttp requests numpy pillow
```
Set your API key as an environment variable:

Linux/Mac:

```Bash
export WEATHER_API_KEY="your_api_key_here"
```
Windows (Command Prompt):

```DOS
set WEATHER_API_KEY="your_api_key_here"
```
Run the application:

```Bash
streamlit run app.py
```
## 📖 Usage
Configure Your Journey: Select your Origin and Destination cities from the global sidebar.

Set Your Profile: Choose your travel mode, specific medical condition, and condition severity (1-5).

Simulate Scenarios (Optional): Toggle Wildfire, Smog, or Dust Storm events to see how environmental disasters would affect your route.

Analyze: Click "ANALYZE SAFE ROUTE" to fetch live API data and generate your health safety verdict, interactive map, and emergency action plan.

## 📁 Project Structure
Below is the organized directory layout for the Aero-Rescue AI platform.

```Plaintext
Aero-Rescue-AI/
├── app.py                      # Main Streamlit application and UI routing
├── requirements.txt            # Python dependencies list
├── README.md                   # Project documentation
└── data/                       # (Optional) Local caches for historical AQI
    └── static_city_data.json
```
## 🎓 Learning Outcomes
This project demonstrates proficiency in:

Asynchronous API Integration - Using aiohttp and asyncio to perform rapid, non-blocking calls to external weather APIs.

Data Science & GIS - Processing geographical coordinates and rendering complex data layers onto interactive Folium maps.

Algorithm Design - Creating a custom, weighted mathematical formula to calculate personal health risks based on multiple overlapping environmental variables.

UI/UX Engineering - Injecting custom CSS into Streamlit to completely overhaul the default look into a modern, production-ready web app.

## 🔮 Future Enhancements
Integrate flight API data to track actual flight paths and cabin pressure risks.

Add a user authentication system to save persistent medical profiles and emergency contacts.

Implement SMS notifications using Twilio to automatically alert emergency contacts if the "Activate Protocol" button is pressed.

## 👨‍💻 Author
Hamad Ali Raza

GitHub: [@HamadAliRaza](https://github.com/SyedHamadAliRaza714)

Project Link: [Aero-Rescue AI Repository](https://github.com/SyedHamadAliRaza714/Aero-Rescue-AI)
## 📄 License
This project is open source and available under the MIT License.

## 🙏 Acknowledgments
Live environmental data provided by OpenWeatherMap and NASA FIRMS.

Designed to assist vulnerable individuals in navigating our changing global climate safely.
