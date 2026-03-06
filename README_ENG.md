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
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous Docker-based power monitoring and security system for Kyiv.**

Recent fixes and improvements:
- **v1.13.0:** Added support for custom haptic feedback for the PWA interface (works on Android and iOS 18+). Improved tactile user experience when interacting with notifications and charts.
- **v1.12.3:** Consolidated release. Finalized daily report format ("Plan vs Fact" in a single line, `🕐 Updated`), restored original copyright with GitHub link in the dashboard footer, and standardized documentation styling.
- **v1.12.0:** Updated daily graphical report format. Added detailed "Plan vs Fact" analytics with direct comparison (`✅ Fact` vs `⚡️ Plan`), compliance percentage calculation, and a specific update timestamp (`🕐 Updated`).
- **v1.11.7:** Updated the text format of the daily Telegram report for better Plan vs Fact analytics visualization.
- **Forecast Logic:** Added display of next shutdown/startup time in Telegram messages even if the exact schedule is missing (shows 'unknown').
- **Telegram Formatting:** Updated power outage notification format. Duration now shows "1d 5h" (if >24h), added detailed deviation calculation ("1h 8m later than scheduled") and forecast.
- **Alert Fix:** Fixed a bug where API timeouts or errors caused false "Air Raid Alert Over" notifications.
- **Reporting Logic:** New intelligent Telegram reporting schedule.
- **Performance:** Background loop frequency increased to 10 minutes.
- **Visual Style:** Implemented "Black-and-White" style (Glassmorphism, tabular-nums) for perfect alignment of text reports.
- **Merge Logic:** Fixed duration calculation for midnight-crossing intervals to ensure correct daily block display.
- **Dashboard:** Added tomorrow's schedule display with automatic day separation and improved "Plan vs Fact" visualization.
- **Reliability:** Centralized background loops in `run_background.py` to prevent redundant threads in Gunicorn.

🔗 **Live Monitoring:** [flash.srvrs.top](https://flash.srvrs.top/)

📖 **Guide:** [Full setup and configuration from scratch](INSTRUCTIONS_INSTALL_ENG.md)

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Heartbeat Tracking:** Real-time power monitoring via IoT signals (Push API).
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

## 🌐 Weby Homelab Ecosystem
[![Flash Monitor Kyiv](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv?label=flash-monitor-kyiv&color=blue&logo=github)](https://github.com/weby-homelab/flash-monitor-kyiv)
[![Light Monitor Kyiv](https://img.shields.io/github/v/release/weby-homelab/light-monitor-kyiv?label=light-monitor-kyiv&color=inactive&logo=github)](https://github.com/weby-homelab/light-monitor-kyiv)
[![Security Monitor Kyiv](https://img.shields.io/github/v/release/weby-homelab/security-monitor-kyiv?label=security-monitor-kyiv&color=inactive&logo=github)](https://github.com/weby-homelab/security-monitor-kyiv)

---

## 📜 License
MIT License.

<p align="center">
  ✦ 2026 Weby Homelab ✦<br>
  Made with ❤️ in Kyiv under air raid sirens and blackouts
</p>

---

### 📊 Update History

#### **v1.14.0** (2026-03-06)
- **Live Monitoring:** The transition to a new day now occurs at **06:00 AM**.
- **Night Buffer:** From 00:00 to 06:00 AM, the system continues to update yesterday's report for a complete daily summary.
- **Adaptive Terminology:** Message titles update automatically: **"Monitoring"** (before 12:00 PM) and **"Report"** (after 12:00 PM).
- **Optimization:** Improved "Plan vs Fact" calculation logic for correct statistics during midnight transitions.

#### **v1.13.0** (2026-02-28)
- Added support for custom haptic feedback for the PWA interface (Android and iOS 18+).
- Improved tactile interaction with charts and notifications.

