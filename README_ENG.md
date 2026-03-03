<p align="center">
  <a href="README_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# FLASH MONITOR KYIV (v1.11.3 Autonomous Edition)

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous Docker-based power monitoring and security system for Kyiv.**

Recent fixes and improvements (v1.11.3):
- **PWA / Manifest:** Added ID, orientation, extra 192/512 icons for better web app integration, and screenshots for manifest.
- **Reporting Logic:** Updated plan vs fact calculation in daily Telegram report. Plan fulfillment is now calculated up to the current minute, instead of only at the end of the day.
- **Forecast Logic:** Added display of next shutdown/startup time in Telegram messages.
- **Telegram Formatting:** Updated power outage notification format. Duration now shows "1d 5h" (if >24h), added detailed deviation calculation.
- **Alert Fix:** Fixed a bug causing false "Air Raid Alert Over" notifications.
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

## 📜 License
MIT License.

<p align="center">
  © 2026 <a href="https://github.com/weby-homelab/flash-monitor-kyiv">Weby Homelab</a><br>
  Made with ❤️ in Kyiv under air raid sirens and blackouts
</p>
