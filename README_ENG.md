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
  <img src="https://img.shields.io/badge/OS-Ubuntu%2024.04%20LTS-E9433F?style=for-the-badge&logo=ubuntu&logoColor=white" alt="OS Ubuntu">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docs/assets/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# POWER⚡️ SAFETY (FLASH MONITOR KYIV) - Bare-metal Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** is a professional autonomous monitoring system for critical infrastructure and environmental safety. The project provides precision real-time electricity monitoring, intelligent outage schedule processing (DTEK/Yasno), air raid alert tracking, air quality (AQI), and radiation background levels.

This branch (`classic`) contains the **Bare-metal Edition** of the project, designed for direct deployment on a server running **Ubuntu 24.04 LTS** (or Debian 12) using **systemd** services.

> **Project Status:** Stable v3.4.0 (Bare-metal Optimized)
> **Architecture:** FastAPI + Gunicorn (Uvicorn Workers) + Background Services + Systemd
> **Brand:** Weby Homelab

---

## 🛠 Technology Stack (Bare-metal Edition)
- **Runtime:** Python 3.12+ running directly on the host OS.
- **Process Management:** Dual-stack `systemd` setup:
    *   `flash-monitor.service` — asynchronous Dashboard and API.
    *   `flash-background.service` — background monitoring, schedule parsing, and Telegram worker.
- **Web-Core:** FastAPI with WebSocket and SSE support via `gunicorn`.
- **Data Persistence:** Direct filesystem access for JSON Flat-DB, optimized for low-latency I/O.

---

## 🚀 Core Innovations & Algorithms

...
  <img src="docs/assets/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="docs/assets/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="docs/assets/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Asynchronous Performance:** A new async caching mechanism eliminates deadlocks between the background worker and user requests.
*   **Smart Backups:** Instant one-click system recovery with automatic system service restarts.
*   **Security (Zero-Trust):** Implements strict Path Traversal protection and secure path validation.

### 🤫 «Quiet Mode» (Information Calm)
A unique algorithm that minimizes "information noise." The system automatically enters a calm state if no outages occurred in the last 24 hours and no restrictions are planned for the upcoming day.

### ⚖️ «False Always Wins» Logic
A hybrid schedule processing system. If at least one source indicates an outage, the system prioritizes it. Historical records are never overwritten by "clean" plans.

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    classDef external fill:#0f766e,stroke:#14b8a6,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef core fill:#1e293b,stroke:#22d3ee,stroke-width:3.5px,color:#fff,rx:14px,ry:14px
    classDef gateway fill:#7c3aed,stroke:#a78bfa,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef client fill:#1e293b,stroke:#60a5fa,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef db fill:#1e293b,stroke:#ec4899,stroke-width:3px,color:#fff,rx:12px,ry:12px

    subgraph External ["🔌 Data Sources"]
        direction TB
        Energy["⚡ Yasno / DTEK API<br>Outage Schedules"]:::external
        Meteo["🌤️ OpenMeteo + SaveEcoBot<br>Weather & AQI"]:::external
    end

    subgraph Core ["⚙️ Flash Monitor Core<br>light_service.py + FastAPI"]
        direction TB
        Worker["🔄 Worker<br>flash-background.service"]:::core
        API["🔌 FastAPI<br>flash-monitor.service"]:::core
        Storage["💾 Storage<br>JSON Flat-DB"]:::db
    end

    subgraph Gateway ["🔐 Cloudflare Tunnel"]
        CF["☁️ Cloudflare Tunnel<br>Reverse Proxy"]:::gateway
    end

    subgraph Clients ["👥 Clients"]
        direction TB
        PWA["📱 PWA Dashboard"]:::client
        Admin["🛠️ Admin Panel"]:::client
        Telegram["📨 Telegram Bot"]:::client
    end

    Energy & Meteo --> Worker
    Worker --> Storage
    Worker <--> API
    API --> CF
    CF <--> PWA & Admin
    Worker --> Telegram
```

---

## 📥 Installation (Bare-metal Edition)

### 1. System Preparation
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.12 python3.12-venv python3-pip git nano
```

### 2. Clone and Setup Environment
```bash
git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
cd flash-monitor-kyiv
git checkout classic

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration
Create `.env` and provide your tokens:
```bash
cp .env.example .env
nano .env
```

### 4. Systemd Setup (Unit Files)
Create `/etc/systemd/system/flash-monitor.service` (Dashboard):
```ini
[Service]
ExecStart=/path/to/project/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker --workers 4 -b 0.0.0.0:5050 app.main:app
```
Create `/etc/systemd/system/flash-background.service` (Worker):
```ini
[Service]
ExecStart=/path/to/project/venv/bin/python -m app.run_background
```

### 5. Activation
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now flash-monitor.service flash-background.service
```

🔑 **Accessing the Admin Panel:**
After startup, retrieve the token:
```bash
cat data/power_monitor_state.json | grep admin_token
```
URL: `http://IP:5050/admin?t=YOUR_TOKEN`

---
**✦ 2026 Weby Homelab ✦**
