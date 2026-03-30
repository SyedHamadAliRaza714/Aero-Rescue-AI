###🏆 Aero-Rescue AI Global

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]([INSERT_YOUR_STREAMLIT_LINK_HERE])

An advanced, AI-driven web application for analyzing environmental risks and ensuring travel safety for individuals with respiratory conditions. Built with Python, Streamlit, and modern AI frameworks.
  
##📋 Overview

Aero-Rescue AI is a comprehensive health and safety platform that processes real-time global environmental data and generates detailed risk insights, safe routing, and interactive geospatial visualizations. It features an intuitive web interface with autonomous AI processing and live data integration to protect vulnerable travelers.

✨ Key Features

##📊 Advanced Analytics

Multi-Metric Risk Assessment - Comprehensive analysis considering Air Quality Index (AQI), weather patterns, and active wildfires
Safety Tier Classification - Automatic categorization into Safe, Moderate Risk, and Hazardous zones based on WHO guidelines
Environmental Insights - Live tracking of threat levels with detailed medical action protocols
Hazard Identification - Pinpoints primary environmental threats in the selected destination

##🎯 Interactive Visualizations

Geospatial Hazard Map - Visual representation of safe zones and danger perimeters using Folium
Real-time Location Search - Instant environmental data retrieval for over 80+ countries
Dynamic Data Rendering - Immediate visual feedback on changing atmospheric conditions
Facility Locator - Identifies the nearest verified medical facilities on the interactive map

##💾 Data Management

Live API Integration - Asynchronous data fetching from NASA and OpenWeatherMap
Global Database - Processes international environmental metrics in real-time
Session Management - Secure and fast data handling within the Streamlit environment

##🎨 Modern UI/UX

Responsive Design - Works seamlessly on desktop, tablet, and mobile
Interactive Dashboards - Clean presentation of complex multi-agent AI reasoning
Warning Systems - High-contrast visual alerts for severe environmental threats
Intuitive Navigation - Clean, user-friendly layout designed for quick emergency access

##🚀 Technology Stack

Backend & Frontend: Streamlit (Python)
AI Processing: CrewAI, Groq LPU (Large Processing Unit)
Data Integration: aiohttp, REST APIs
Visualization: Folium, Pandas
Styling: Custom Streamlit UI elements

##📦 Installation

Prerequisites

Python 3.8 or higher
pip package manager

Setup

Clone the repository
```bash
git clone [https://github.com/HamadAliRaza/Aero-Rescue-AI.git](https://github.com/HamadAliRaza/Aero-Rescue-AI.git)
cd Aero-Rescue-AI
```
Install dependencies

```Bash
pip install -r requirements.txt
```
Set up Environment Variables
Create a .env file in the root directory and add your API keys:
```Bash
Ini, TOML
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
NASA_FIRMS_KEY=your_nasa_api_key
```
Run the application

```Bash
streamlit run app.py
```
Access the application
Open your browser and navigate to the local URL provided by Streamlit (usually http://localhost:8501)

📖 Usage

Input Data Format

Users simply input their intended travel destination. The system autonomously fetches:
LocationCoordinatesAQI StatusThermal AnomaliesCity/CountryLatitude/LongitudeNumeric (0-500)Active NASA Fire Data

Risk Assessment Logic

The AI processes data through a multi-agent framework:
Data Gatherer Agent - Pulls raw API metrics (Weather, Fires, Pollution).
Medical Analyst Agent - Compares raw data against WHO respiratory health guidelines.
Routing Agent - Determines safe perimeters and flags emergency facility locations.

Safety Tiers

Safe: Ideal conditions for individuals with Asthma/COPD.
Moderate: Precautionary measures advised; rescue inhalers should be accessible.
Hazardous: Travel highly discouraged; severe respiratory risk detected.
##🎯 Features in Detail

Search & Filter

Real-time search by global city or country
Instant results powered by Groq's high-speed LPUs

Interactive Risk Cards

View detailed breakdowns of specific pollutants (PM2.5, PM10, Ozone)
Modal overlays containing emergency WHO protocols

Visual Analytics

Interactive Folium map showing exact hazard perimeters
Animated indicators for active satellite thermal anomalies

##📁 Project Structure

Aero-Rescue-AI/
├── app.py                      # Main Streamlit application
├── agents/
│   ├── data_gatherer.py        # API fetching logic
│   └── health_analyst.py       # CrewAI reasoning logic
├── utils/
│   └── map_generator.py        # Folium visualization setup
├── requirements.txt            # Project dependencies
├── .env.example                # Environment variables template
└── README.md                   # Documentation

##🎓 Learning Outcomes

This project demonstrates proficiency in:
AI Engineering - Designing autonomous multi-agent systems using CrewAI
Full-Stack Python Development - Streamlit architecture and deployment
Data Engineering - Asynchronous API integration (aiohttp) and JSON parsing
Geospatial Analysis - Plotting live satellite data on interactive maps
Software Architecture - Clean, maintainable code structure for complex LLM tasks
Problem Solving - Developing "AI for Social Good" to address real-world health crises

##🔮 Future Enhancements

Mobile application port for on-the-go access
Integration with wearable health devices (Apple Watch, Fitbit)
Offline caching for limited-connectivity areas
Push notifications for sudden AQI drops in the user's vicinity
Multilingual support for global accessibility

##👨‍💻 Author

Hamad Ali Raza
GitHub: @HamadAliRaza
Project Link: Aero-Rescue AI Global

##📄 License

This project is open source and available under the MIT License.

##🙏 Acknowledgments

Inspired by the need for accessible "AI for Social Good" tools
Data provided by NASA FIRMS and OpenWeatherMap
Built as a demonstration of advanced multi-agent AI capabilities
