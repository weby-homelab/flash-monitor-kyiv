# FLASH MONITOR KYIV (v1.2 Classic)

**Fully autonomous power monitoring and security system for Kyiv.**

---

## 🆕 What's New in v1.2 Classic?

This version has become **completely independent**. `flash-monitor-kyiv` no longer requires external APIs from other projects to fetch schedules. All processes — from gathering DTEK/Yasno data to generating complex analytics — now happen locally within the project.

### Key Updates:
- **Built-in Schedule Parser:** Direct integration with Yasno and GitHub (DTEK) sources.
- **"Plan vs Fact" Analytics:** Automatic comparison of real outages with scheduled plans on the dashboard and in reports.
- **Smart Text Reports:** New algorithm for merging intervals across midnight and intelligent Telegram message updates.
- **Full Autonomy:** All services (Web UI, background monitoring, report generators) operate within a single project environment.

---

## 🚀 Key Features

### 💡 Light Monitoring
- **Real-time Heartbeat:** Voltage tracking via IoT signals (push mechanism).
- **Switching Accuracy:** Automatic calculation of schedule deviations (delay or early power restoration).
- **Visualization:** Generation of daily and weekly charts in a signature dark theme.

### 🛡️ Security & Environment
- **Air Alerts:** Instant alert status (Kyiv/Region) and integrated live map.
- **Air Quality (AQI):** Real-time PM2.5, PM10 levels, and radiation background (Location: Borshchahivka).
- **Weather:** Current temperature, humidity, and wind parameters.

### 📱 Web Dashboard (PWA)
- Modern adaptive interface in HomeLab style (#1E122A).
- Sound and Push notifications for status changes.
- Full PWA support (installable on your smartphone's home screen).

---

## 🛠 Tech Stack
- **Backend:** Python 3.11, Flask, Gunicorn.
- **Analytics:** Matplotlib (chart rendering), BeautifulSoup4 (parsing).
- **Data:** JSON-based persistence (no heavy DB required).
- **Infra:** Docker + Docker Compose, Systemd.

---

## 📦 Installation & Setup

### 1. Clone the repository:
```bash
git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
cd flash-monitor-kyiv
git checkout classic
```

### 2. Configure environment:
Create a `.env` file and add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHANNEL_ID=your_chat_id
DATA_DIR=.
```

### 3. Run with Docker:
```bash
docker compose up -d
```

---

## 📜 License
Distributed under the **MIT** License.

<p align="center">
  ✦ 2026 WEBy Home Lab ✦<br>
  <i>Automate everything you do twice. Monitor everything that matters.</i>
</p>
