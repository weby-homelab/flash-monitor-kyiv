<p align="center">
  <a href="README_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# FLASH MONITOR KYIV [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest) Autonomous Edition

<p align="center">
  <a href="https://hub.docker.com/r/webyhomelab/flash-monitor-kyiv"><img src="https://img.shields.io/docker/pulls/webyhomelab/flash-monitor-kyiv?logo=docker&logoColor=white" alt="Docker Pulls"></a>
  <a href="https://hub.docker.com/r/webyhomelab/flash-monitor-kyiv"><img src="https://img.shields.io/docker/image-size/webyhomelab/flash-monitor-kyiv/latest?logo=docker&logoColor=white" alt="Docker Image Size"></a>
  <a href="https://github.com/weby-homelab/flash-monitor-kyiv/commits/main"><img src="https://img.shields.io/github/last-commit/weby-homelab/flash-monitor-kyiv" alt="GitHub last commit"></a>
  <a href="https://github.com/weby-homelab/flash-monitor-kyiv/issues"><img src="https://img.shields.io/github/issues/weby-homelab/flash-monitor-kyiv" alt="GitHub issues"></a>
  <a href="https://github.com/weby-homelab/flash-monitor-kyiv/blob/main/LICENSE"><img src="https://img.shields.io/github/license/weby-homelab/flash-monitor-kyiv" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Platform Docker">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous Docker-based power monitoring and security system for Kyiv.**

🔗 **Live Monitoring:** [flash.srvrs.top](https://flash.srvrs.top/)

📖 **Guide:** [Full setup and configuration from scratch](INSTRUCTIONS_INSTALL_ENG.md)

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Smart Bootstrap:** Automatically provisions current scheduled outages for your specific group and region upon first startup.
- **Heartbeat Tracking & Manual Trigger:** Real-time power monitoring via IoT signals (`/api/push`) and instant manual outage triggering (`/api/down`).
- **API Resilience:** Robust local caching of schedules to protect against DTEK/Yasno server outages.
- **"Plan vs Fact" Analytics:** Automatic comparison of real outages with scheduled plans.
- **Schedule Accuracy:** Calculation of deviations (delays or early switches) for each event.
- **Visualization:** Daily and weekly charts.
- **UI/UX Design:** "Black-and-White" theme with Glassmorphism and tabular-nums fonts for precise text reports.

### 🛡️ Security & Environment
- **Air Alerts:** Instant status and Telegram notifications for alert start/end in Kyiv.
- **Live Map:** Integrated air raid alert map for Kyiv and region.
- **Air Quality (AQI):** Real-time PM2.5, PM10, and radiation background (Simyrenka location).
- **Weather:** Current temperature, humidity, and wind parameters.

### 🔔 Telegram Notifications
- **Intelligent Reports:** Dynamic text schedules with right-aligned durations.
- **Morning Report (06:00):** Full situational overview for today and tomorrow (if available).
- **Evening/Instant Update:** Automated delivery of tomorrow's schedule as soon as DTEK publishes it.
- **Smart Merge:** Correct handling of night-time intervals.

---

## 💡 Pro-Tip for IoT Sensors (Heartbeat)

It is highly recommended to use your **HTTPS domain address** (e.g., via Cloudflare Tunnel) for Push signals instead of a direct IP:

*   **🛡️ Security:** HTTPS encrypts your secret key during transmission.
*   **🧩 Flexibility:** If you migrate your server, you don't need to re-flash sensors — just update your Tunnel settings.

**Example:** `https://flash.srvrs.top/api/push/your_key`

---

## 🛠 Tech Stack
- **Backend:** Python 3.11, Flask, Gunicorn.
- **Containerization:** Docker + Docker Compose.

---

## 📜 License
MIT License.

<p align="center">
  ✦ 2026 Weby Homelab ✦<br>
  Made with ❤️ in Kyiv under air raid sirens and blackouts
</p>

---

