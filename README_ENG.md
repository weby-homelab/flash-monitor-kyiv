<p align="center">
  <a href="README_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

<p align="center">
  <img src="https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv?style=for-the-badge&color=purple" alt="Latest Release">
  <img src="https://img.shields.io/badge/Branch-classic_(Bare--metal)-0984e3?style=for-the-badge&logo=linux&logoColor=white" alt="Branch Classic">
  <img src="https://img.shields.io/badge/OS-Ubuntu%20%2F%20Debian-E9433F?style=for-the-badge&logo=ubuntu&logoColor=white" alt="OS Ubuntu">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docs/assets/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# POWER⚡️ SAFETY (FLASH MONITOR KYIV) - Bare-metal Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** is a professional autonomous monitoring system for critical infrastructure and environmental safety. The project provides precision real-time electricity monitoring, intelligent outage schedule processing (DTEK/Yasno), air raid alert tracking, air quality (AQI), and radiation background levels.

This branch (`classic`) contains the **Bare-metal Edition** of the project, designed for direct installation on a Linux server (Ubuntu/Debian) using `systemd`. This is the preferred choice for users seeking maximum performance and granular control over system resources.

> **Project Status:** Stable v3.4.0 (Bare-metal Optimized)
> **Architecture:** Asynchronous FastAPI + systemd services + venv + JSON Flat-DB
> **Brand:** Weby Homelab

---

## 🛠 Technology Stack (Bare-metal Edition)
- **Runtime:** Python 3.10+ (3.12 recommended) running directly on the host OS.
- **Process Management:** Managed via `systemd` with dedicated unit files for the API and background workers, ensuring automatic restarts and logs aggregation via `journalctl`.
- **Web-Core:** FastAPI with an asynchronous event loop for near-zero latency when handling WebSockets and SSE streams.
- **Data Persistence:** Direct filesystem access for the JSON-based database, eliminating container I/O overhead.
- **Performance:** Optimized for low-resource environments (LXC, Raspberry Pi) due to the absence of virtualization layers.

---

## 🚀 Core Innovations & Algorithms

### 🎛 Admin Control Panel
A fully autonomous **Glassmorphism** web interface to manage all system aspects without the need for SSH or direct configuration file editing.
<p align="center">
  <img src="docs/assets/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="docs/assets/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="docs/assets/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Asynchronous Performance:** A new async caching mechanism eliminates deadlocks and "freezes" during simultaneous data writes by background workers and user interactions.
*   **Smart Backups:** Create manual and automatic restoration points. Instant one-click recovery with automatic `systemd` service restarts.
*   **Flexible Source Management:** Toggle priority between Yasno, GitHub, or connect your own Custom JSON URL. Includes a manual force-sync button for immediate Telegram report updates.
*   **Complete Geo-Adaptation:** Set precise Lat/Lon coordinates for accurate local weather, SaveEcoBot station ID, and selective widget visibility management.
*   **Security (Zero-Trust):** Implements strict Path Traversal protection and secure Access Key generation during initial bootstrap.

### 🤫 «Quiet Mode» (Information Calm)
A unique algorithm that minimizes "information noise" during stable grid periods. The system automatically enters a calm state if no outages occurred in the last 24 hours and no restrictions are planned for the upcoming day. This keeps your channel clean from redundant daily reports when everything is normal.

### 🚨 Safety Net
An interactive rapid response mechanism for monitoring device connection loss. If the incoming Push signal is delayed by more than 35 seconds, the administrator receives a Telegram request with interactive action buttons (`🔴 Power is out`, `🛠 Technical glitch`, `🤷‍♂️ I don't know`). This prevents false alarms from being published to the public channel.

### ⚖️ «False Always Wins» Logic
A hybrid schedule processing system. If at least one source (Yasno or GitHub mirror) indicates a probable outage, the system prioritizes it. Historical outage records are never overwritten by new "clean" plans, ensuring 100% data integrity and honest event history.

---

## 📱 Real-world Telegram Notification Examples

*   📊 **[Smart Daily Report (Plan vs Fact)](https://t.me/svitlobot_Symyrenka22B/1230)** — visualizes grid reality against planned schedules.
*   📈 **[Weekly Outage Analytics](https://t.me/svitlobot_Symyrenka22B/1192)** — automated data aggregation of outage duration and frequency.
*   🔴 **[Power Outage Alerts](https://t.me/svitlobot_Symyrenka22B/1209)** — instant notifications with schedule-aligned precision.
*   🟢 **[Power Restoration Alerts](https://t.me/svitlobot_Symyrenka22B/1212)** — confirmation of voltage stabilization.
*   ⚠️ **[Schedule Change Alerts](https://t.me/svitlobot_Symyrenka22B/1222)** — instant alerts when DTEK/Yasno databases are updated.
*   🚨 **[Air Raid Alerts](https://t.me/svitlobot_Symyrenka22B/1196)** — integration with official civil defense sources.

---

## 📊 Dashboard Capabilities (PWA)

A modern **Glassmorphism** interface optimized for mobile devices:
*   **Live Status:** Real-time system "Pulse" visualization (Power ON / Power OUT).
*   **Environmental Monitoring:** Temperature, humidity, PM2.5/PM10 (OpenMeteo/SaveEcoBot), and radiation levels with interactive charts.
*   **Schedule Bar:** A compact 24-hour visual scale of planned outages for efficient day planning.

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    %% ================================================
...

---

## 📥 Installation (Bare-metal)

1. **Clone and Checkout:**
```bash
git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
cd flash-monitor-kyiv
git checkout classic
```

2. **Environment Setup:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configuration:**
Copy `.env.example` to `.env` and provide your API tokens.

4. **Service Setup:**
Use the provided `systemd` unit files in the `scripts/` directory to enable and start the services.

📖 **Documentation:**
* [Linux Installation Guide](docs/INSTRUCTIONS_INSTALL_ENG.md)
* [Development Rules (DEVELOPMENT_ENG.md)](docs/DEVELOPMENT_ENG.md)

---
**✦ 2026 Weby Homelab ✦**
