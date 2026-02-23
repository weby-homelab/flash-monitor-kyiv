# FLASH MONITOR KYIV (v1.2 Docker Edition)

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous Docker-based power monitoring and security system for Kyiv.**

The **main** branch is designed for quick and reliable deployment in a containerized environment. This version provides full control over the energy and security situation by analyzing real network data and official schedules locally.

🔗 **Live Monitoring:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Heartbeat Tracking:** Real-time power monitoring via IoT signals (Push API).
- **"Plan vs Fact" Analytics:** Automatic comparison of real outages with scheduled plans on the dashboard.
- **Schedule Accuracy:** Deviation calculation (delay or early power restoration) for each event.
- **Visualization:** Generation of signature style daily and weekly charts.

### 🛡️ Security & Environment (Borshchahivka)
- **Air Alerts:** Instant status and integrated live map of Kyiv and the region.
- **Air Quality (AQI):** Real-time PM2.5, PM10 levels, and radiation background (Location: Symyrenka).
- **Weather:** Current temperature, humidity, and wind parameters.

### 🔔 Telegram Notifications
- **Intelligent Reports:** Dynamically updated text schedules.
- **Merge Logic:** Smart merging of power intervals crossing midnight.
- **Automation:** Forced morning reports and instant status change notifications.

---

## 🐳 Quick Start with Docker

The project is fully dockerized for stable operation on any server.

**Official Image:** `webyhomelab/flash-monitor:latest`

### Docker Compose
```yaml
services:
  web:
    image: webyhomelab/flash-monitor:latest
    container_name: flash-monitor-web
    restart: unless-stopped
    ports:
      - "5050:5050"
    volumes:
      - ./data:/app/data
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data

  worker:
    image: webyhomelab/flash-monitor:latest
    container_name: flash-monitor-worker
    restart: unless-stopped
    command: python run_background.py
    volumes:
      - ./data:/app/data
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data
```

---

## 🛠 Tech Stack
- **Backend:** Python 3.11, Flask, Gunicorn.
- **Analytics:** Matplotlib (chart rendering), BeautifulSoup4 (local parsing).
- **Containerization:** Docker + Docker Compose.

---

## 📜 License
Distributed under the **MIT** License.

<p align="center">
  ✦ 2026 WEBy Home Lab ✦<br>
  <i>Automate everything you do twice. Monitor everything that matters.</i>
</p>
