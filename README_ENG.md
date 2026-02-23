# FLASH MONITOR KYIV (v1.2 Classic — Bare-Metal Edition)

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/classic/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous bare-metal power monitoring and security system for Kyiv.**

The **Classic** branch is specifically designed for direct installation on a Linux server or PC. It is a highly reliable implementation that runs as a system service, providing full control over data without extra virtualization layers.

🔗 **Live Monitoring:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Heartbeat Tracking:** Real-time power tracking via IoT signals (Push API).
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

## 🛠 Tech Stack
- **Backend:** Python 3.11, Flask, Gunicorn.
- **Analytics:** Matplotlib (chart rendering), BeautifulSoup4 (local parsing).
- **Service Management:** Systemd (Ubuntu/Debian).

---

## 📦 Installation & Setup (Bare-Metal)

### 1. Clone and Setup:
```bash
git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
cd flash-monitor-kyiv
git checkout classic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment:
Create a `.env` file and specify your credentials:
```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHANNEL_ID=your_chat_id
DATA_DIR=.
```

### 3. System Services Setup:
Create configuration files in `/etc/systemd/system/` for `flash-monitor.service` and `flash-background.service`, ensuring the correct paths to `venv` and your project.

---

## 📜 License
Distributed under the **MIT** License.

<p align="center">
  ✦ 2026 WEBy Home Lab ✦<br>
  <i>Automate everything you do twice. Monitor everything that matters.</i>
</p>
