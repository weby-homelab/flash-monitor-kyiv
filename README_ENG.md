# FLASH MONITOR KYIV (v1.2 Classic — Bare-Metal Edition)

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/classic/dashboard_preview.jpg" alt="FLASH MONITOR Dashboard Preview" width="100%">
</p>

**Autonomous bare-metal power monitoring and security system for Kyiv.**

🔗 **Live Monitoring:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Heartbeat Tracking:** Real-time power monitoring via IoT signals (Push API).
- **"Plan vs Fact" Analytics:** Automatic comparison of real outages with scheduled plans.
- **Visualization:** Generation of daily and weekly charts in a dark theme.

### 🛡️ Security & Environment
- **Air Alerts:** Instant status and integrated live map.
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
- **Service Management:** Systemd (Ubuntu/Debian).

---

## 📜 License
MIT License.

<p align="center">
  © 2026 Weby Homelab — infrastructure that doesn’t give up.<br>Made with ❤️ in Kyiv under air raid sirens and blackouts...
</p>
