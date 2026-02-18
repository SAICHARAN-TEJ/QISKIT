# ResQbit - Quantum Disaster Response System v3.0

Real-time disaster prediction and evacuation routing with free APIs.

## Features

- **Real-time Weather**: OpenWeatherMap API (free tier) or Jena historical dataset
- **Free Routing**: OSRM (OpenStreetMap) - no API key needed
- **Alert Notifications**: Discord webhooks + Email (Gmail SMTP)
- **Multi-type Prediction**: Heat Waves, Cyclones, Floods, Blizzards, Earthquakes
- **User Authentication**: Secure registration/login with SQLite database

## Free APIs Used

| Service | Free Limit | API Key |
|---------|-----------|---------|
| OpenWeatherMap | 60 calls/min, 1M/month | Required (free) |
| OSRM Routing | Unlimited | NO |
| Discord Webhooks | Unlimited | NO |
| Gmail SMTP | Unlimited | NO (use app password) |

## Local Development

```bash
# Clone
git clone https://github.com/SAICHARAN-TEJ/QISKIT.git
cd QISKIT

# Install dependencies
pip install -r requirements.txt

# Run web app
cd webapp
python app.py
```

## Configuration

```bash
# Weather API (free key from openweathermap.org)
set OPENWEATHERMAP_API_KEY=your_key

# Discord alerts
set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Email alerts (enable 2FA, generate app password)
set SENDER_EMAIL=your_email@gmail.com
set SENDER_PASSWORD=your_app_password
set RECIPIENT_EMAILS=alert@example.com
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page |
| `/dashboard` | GET | User dashboard (requires login) |
| `/api/predict` | POST | Disaster prediction |
| `/api/route` | POST | Evacuation route |
| `/api/register` | POST | User registration |
| `/api/login` | POST | User login |
| `/api/logout` | POST | User logout |
| `/api/status` | GET | API status |

## Project Structure

```
QISKIT/
├── src/
│   ├── disaster_system.py          # CLI system
│   └── data/
│       └── jena_climate_2009_2016.csv
├── webapp/
│   ├── app.py                      # Flask web app
│   ├── static/                     # CSS, JS
│   └── templates/                  # HTML templates
├── README.md
├── requirements.txt
├── Procfile
└── runtime.txt
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

- **No API keys**: Works without keys using Jena dataset
- **Database errors**: SQLite auto-creates on first run
