# Quantum Disaster Response System v3.0

Real-time disaster prediction and evacuation routing with free APIs.

## Features

- **Real-time Weather**: OpenWeatherMap API (free tier) or Jena historical dataset
- **Free Routing**: OSRM (OpenStreetMap) - no API key needed
- **Alert Notifications**: Discord webhooks + Email (Gmail SMTP)
- **Multi-type Prediction**: Heat Waves, Cyclones, Floods, Blizzards, Earthquakes

## Free APIs Used

| Service | Free Limit | API Key |
|---------|-----------|---------|
| OpenWeatherMap | 60 calls/min, 1M/month | Required (free) |
| OSRM Routing | Unlimited | NO |
| Discord Webhooks | Unlimited | NO |
| Gmail SMTP | Unlimited | NO (use app password) |

## Installation

```bash
git clone https://github.com/SAICHARAN-TEJ/QISKIT.git
cd "disaster management final"
pip install -r requirements.txt
```

## Configuration (Optional)

Set environment variables to enable features:

```bash
# Weather API (free key from openweathermap.org)
set OPENWEATHERMAP_API_KEY=your_key

# Discord alerts (Server Settings > Integrations > Webhooks)
set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Email alerts (enable 2FA, generate app password)
set SENDER_EMAIL=your_email@gmail.com
set SENDER_PASSWORD=your_app_password
set RECIPIENT_EMAILS=alert@example.com

# Use live API data instead of Jena dataset
set DATA_SOURCE=api
set DEFAULT_CITY=New York
```

## Usage

```bash
cd src
python disaster_system.py
```

## Output

```
QUANTUM DISASTER RESPONSE SYSTEM v3.0
Real-time Weather | Free Routing | Alert Notifications
============================================================
[*] Initializing components...
[*] Fetching weather data...

[+] SENSOR READINGS:
    Pressure:   1012.34 mbar
    Temperature:22.50 degC
    Humidity:   65.20%
    Wind Speed: 5.20 m/s
    ...

[OK] System execution completed!
```

## Project Structure

```
disaster management final/
├── src/
│   ├── disaster_system.py          # Main system (all-in-one)
│   └── data/
│       └── jena_climate_2009_2016.csv
├── PRD.md
├── README.md
└── requirements.txt
```

## Disaster Detection

| Disaster | Conditions | Risk |
|----------|-----------|------|
| Heat Wave | Temp > 35C, Humidity > 60% | 70-95% |
| Cyclone | Wind > 15 m/s, P < 980 | 75-98% |
| Flood | Humidity > 90%, Temp > 5C | 65-90% |
| Blizzard | Temp < -5C, Wind > 8 m/s | 70-88% |
| Earthquake | Pressure < 970 mbar | 80% |

## Risk Levels

- CRITICAL (>=85%): Immediate evacuation
- HIGH (>=70%): Evacuate immediately  
- MEDIUM (>=50%): Prepare for evacuation
- LOW (<50%): No action needed

## Troubleshooting

- **No API keys**: System works without keys using Jena dataset
- **OSRM fails**: Falls back to quantum-inspired routing
- **Discord/Email not working**: Check webhook URL / Use Gmail app password
