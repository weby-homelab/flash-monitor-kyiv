# FLASH MONITOR KYIV (v1.2 Docker Edition)

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous Docker-based power monitoring and security system for Kyiv.**

The **main** branch is designed for quick and reliable deployment in a containerized environment. It is the perfect solution for those running Docker on their server or in a HomeLab.

🔗 **Live Monitoring:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Heartbeat Tracking:** Real-time power monitoring via IoT signals (Push API).
- **"Plan vs Fact" Analytics:** Automatic comparison of real outages with scheduled plans on the dashboard.
- **Schedule Accuracy:** Deviation calculation (delay or early power restoration) for each event.
- **Visualization:** Generation of daily and weekly charts in a dark theme.

### 🛡️ Security & Environment (Borshchahivka)
- **Air Alerts:** Instant status and integrated live map of Kyiv and the region.
- **Air Quality (AQI):** Real-time PM2.5, PM10 levels, and radiation background (Location: Symyrenka).
- **Weather:** Current temperature, humidity, and wind parameters.

### 🔔 Telegram Notifications
- **Intelligent Reports:** Dynamically updated text schedules.
- **Merge Logic:** Smart merging of power intervals crossing midnight.
- **Automation:** Forced morning reports and instant status change notifications.

---

## 🏗 Tech Stack
- **Backend:** Python 3.11, Flask, Gunicorn.
- **Analytics:** Matplotlib (chart rendering), BeautifulSoup4 (local parsing).
- **Containerization:** Docker + Docker Compose.

---

## 📦 Installation & Setup (Docker)

### 1. Prepare Environment:
Create a `.env` file and specify your credentials:
```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHANNEL_ID=your_chat_id
DATA_DIR=/app/data
```

### 2. Run with Docker Compose:
```bash
docker compose up -d
```

The system will automatically pull the official image `webyhomelab/flash-monitor:latest` and start the Web UI on port `5050`.

---

## 📜 License
Distributed under the **MIT** License.

<p align="center">
  ✦ 2026 WEBy Home Lab ✦<br>
  <i>Automate everything you do twice. Monitor everything that matters.</i>
</p>
