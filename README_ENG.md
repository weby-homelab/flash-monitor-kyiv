<p align="center">
  <a href="README_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# FLASH MONITOR KYIV (v1.4.6 Autonomous Edition)

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous Docker-based power monitoring and security system for Kyiv.**

🔗 **Live Monitoring:** [flash.srvrs.top](https://flash.srvrs.top/)

📖 **Guide:** [Full setup and configuration from scratch](INSTRUCTIONS_INSTALL_ENG.md)

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Heartbeat Tracking:** Real-time power monitoring via IoT signals (Push API).
- **"Plan vs Fact" Analytics:** Automatic comparison of real outages with scheduled plans.
- **Schedule Accuracy:** Calculation of deviations (delays or early switches) for each event and displaying the next planned interval.
- **Visualization:** Daily and weekly charts.
- **UI/UX Design:** Adaptive Amethyst Mist theme with automatic Light/Dark mode and Glassmorphism.

### 🛡️ Security & Environment
- **Air Alerts:** Instant status and Telegram notifications for alert start/end in Kyiv.
- **Live Map:** Integrated air raid alert map for Kyiv and region.
- **Air Quality (AQI):** Real-time PM2.5, PM10, and radiation background.

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
