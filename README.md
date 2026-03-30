# 🏆 Aero-Rescue AI Global

An advanced, data-driven web application for analyzing and ranking environmental safety across multiple metrics. Built with Streamlit, Python, and modern AI technologies.
  
## 📋 Overview

The Aero-Rescue AI is a comprehensive analytics platform that processes global environmental statistics and generates detailed safety insights, rankings, and visualizations. It features an intuitive web interface with real-time data processing and interactive analytics.

## ✨ Key Features

### 📊 Advanced Analytics
* **Multi-Metric Scoring System** - Weighted formula considering AQI, Thermal Anomalies, Wind Speed, and Humidity
* **Performance Tier Classification** - Automatic categorization into Elite Safe, Strong Safe, Average, and Hazard tiers
* **Statistical Insights** - Highest, lowest, and average risk scores with comprehensive breakdowns
* **Category Leaders** - Identifies top safe zones in each individual metric

### 🎯 Interactive Visualizations
* **Score Distribution Chart** - Visual representation of risk distribution using Folium
* **Real-time Search** - Instant global location search functionality
* **Tier Filtering** - Filter regions by performance tier
* **Location Detail Cards** - Click any region to view complete metric breakdown

### 💾 Data Management
* **API Integration Support** - Accepts live data from NASA and OpenWeatherMap
* **Export Functionality** - Download analyzed results as CSV
* **Session Management** - Secure data handling with Streamlit sessions

### 🎨 Modern UI/UX
* **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
* **Animated Counters** - Smooth number animations for statistics
* **Dark Theme** - Professional cyberpunk-inspired interface
* **Intuitive Navigation** - Clean, user-friendly layout

## 🚀 Technology Stack
* **Backend:** Streamlit (Python)
* **Data Processing:** Pandas, aiohttp
* **Frontend:** HTML5, CSS3, JavaScript
* **Visualization:** Folium
* **AI Framework:** CrewAI, Groq LPU

## 📦 Installation

### Prerequisites
* Python 3.8 or higher
* pip package manager

### Setup

Clone the repository
```bash
git clone [https://github.com/HamadAliRaza/Aero-Rescue-AI.git](https://github.com/HamadAliRaza/Aero-Rescue-AI.git)
cd Aero-Rescue-AI
Install dependencies

Bash
pip install streamlit pandas folium crewai groq
Run the application

Bash
streamlit run app.py
Access the application
Open your browser and navigate to: http://localhost:8501

📖 Usage
Input Data Format
Your live API data processes the following columns:

Location Name	AQI Score	Thermal Data	Wind Speed	Humidity
String	Numeric	Numeric	Numeric	Numeric
Performance Score Formula
Score = (Thermal Data × 2.0) + (AQI Score × 1.5) + (Wind Speed × 1.2) + (Humidity × 1.0) - (Precipitation × 1.0)

This weighted formula emphasizes:

Thermal Data (2.0x) - High value on immediate fire threats

AQI Score (1.5x) - Heavily penalizes poor air quality

Wind Speed (1.2x) - Values the spread potential of hazards

Humidity (1.0x) - Standard respiratory metric

Precipitation (-1.0x) - Reduces overall airborne risk

Performance Tiers
Elite Safe: Score ≤ 50% of average risk

Strong Safe: Score ≤ 75% of average risk

Average Risk: Score ≥ 85% of average risk

Hazardous: Score ≥ 125% of average risk

🎯 Features in Detail
Search & Filter
Real-time search by location name

Filter by performance tier (Elite Safe, Strong Safe, Average Risk, Hazardous)

Instant results with smooth animations

Interactive Location Cards
Click any region to view detailed breakdown

Shows all individual metrics

Modal overlay with professional design

Visual Analytics
Interactive map showing score distribution across ranges

Category leader cards for top performers

Animated statistics cards

Export Capabilities
One-click CSV export

Preserves all calculated fields

Formatted for further analysis

📁 Project Structure
Plaintext
Aero-Rescue-AI/
├── app.py                      # Streamlit application (backend/frontend)
├── agents/
│   └── health_analyst.py       # AI reasoning logic
├── .env                        # Environment variables
├── data_fetcher.py             # Basic API script
├── map_generator.py            # Advanced visualization script
├── README.md                   # Documentation
└── safe_routes.csv             # Sample output
🎓 Learning Outcomes
This project demonstrates proficiency in:

Full-Stack Web Development - Streamlit backend with modern frontend

Data Analysis - Pandas for data manipulation and statistics

UI/UX Design - Responsive, accessible interface design

Algorithm Development - Custom scoring and classification systems

Software Architecture - Clean, maintainable code structure

Problem Solving - Real-world health analytics application

🔮 Future Enhancements
🌍 Location comparison feature (side-by-side analysis)

📈 Historical data tracking and trend analysis

📊 Advanced visualizations (radar charts, heat maps)

🧭 Safe route formation optimizer

📄 PDF report generation

🗄️ Database integration for persistent storage

🔑 User authentication and saved analyses

🔌 API endpoints for external integration

👨‍💻 Author
Hamad Ali Raza

GitHub: @HamadAliRaza

Project Link: Aero-Rescue AI Global

📄 License
This project is open source and available under the MIT License.

🙏 Acknowledgments
Inspired by modern health analytics platforms

Built as a demonstration of full-stack AI development capabilities

Designed for educational and portfolio purposes


Would you like to do the **FinAgent Pro** README now using this exact layout?
