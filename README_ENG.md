<p align="center">
  <a href="README_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# СВІТЛО⚡БЕЗПЕКА (Light & Safety) [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest) DOCKER Edition

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
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="СВІТЛО⚡БЕЗПЕКА Dashboard Preview" width="100%">
</p>

**Autonomous Docker-based Power & Safety Monitoring System for Kyiv.**

**This project provides** full control over the energy and security situation by analyzing real network data and official DTEK/Yasno schedules locally.

🔗 **Live Dashboard:** [flash.srvrs.top](https://flash.srvrs.top/)

## 📚 Project Documentation
| File | Description |
| :--- | :--- |
| 📖 **[Installation and Setup Guide](INSTRUCTIONS_INSTALL_ENG.md)** | Main guide for deploying the system (Docker, environment variables, API). |
| 🔌 **[IoT Devices Setup](INSTRUCTIONS_ENG.md)** | Sketches and instructions for ESP8266/ESP32 microcontrollers (physical power presence sensors). |
| 🛠️ **[Development Guide](DEVELOPMENT_ENG.md)** | Architectural rules, security protocols, and code deployment instructions. |

---

## 🚀 Key Features

### 💡 Smart Power Monitoring
- **Smart Bootstrap:** Automatic deployment of current planned schedules for your specific group and region upon first launch.
- **Heartbeat Tracking & Manual Trigger:** Real-time power monitoring via IoT signals (`/api/push`) and instant manual status control (`/api/down`).
- **API Resilience:** Reliable local caching of schedules, protecting against DTEK/Yasno server downtimes.
- **"Plan vs Fact" Analytics:** Automatic comparison of actual outages with planned schedules directly on the dashboard.
- **Schedule Accuracy:** Calculation of deviations (late or early power restoration/outage) for every event.
- **Visualization:** Generation of daily and weekly analytical charts in a signature style.
- **UI/UX Design:** "Black-and-White" Glassmorphism theme with monospace fonts for clear, tabular reports.

### 🛡️ Safety & Environment
- **Air Raid Alerts:** Instant Telegram notifications about the start and end of air raid alerts in Kyiv.
- **Live Map:** Integrated interactive map of alerts for Kyiv and the region.
- **Air Quality (AQI):** Monitoring of PM2.5, PM10, and radiation background (location: Symyrenka).
- **Weather:** Current temperature, humidity, and wind parameters.

### 🔔 Telegram Notifications
- **Intelligent Reports:** Text-based schedule lists with right-aligned duration times (tabular-nums).
- **Morning Report (06:00):** Comprehensive overview of the situation for today and tomorrow (if available).
- **Evening/Instant Update:** Automatic dispatch of tomorrow's schedule immediately after its publication by DTEK.
- **Smart Merge:** Correct merging and calculation of overnight power intervals.

---

## 🏗 System Architecture [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

```mermaid
flowchart TD
    %% -- Style Definitions --
    classDef access fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,rx:10,ry:10
    classDef network fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#7b1fa2,rx:5,ry:5
    classDef core fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32,rx:5,ry:5
    classDef data fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100,rx:10,ry:10
    classDef external fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#c2185b,rx:5,ry:5

    %% -- Access Layer --
    subgraph Access ["📡 ACCESS LAYER"]
        IoT["⚡ <b>IoT SENSORS</b><br/>(Heartbeat Pulse)"]
        PWA["📱 <b>PWA DASHBOARD</b><br/>(Interactive UI)"]
    end

    %% -- Network Layer --
    subgraph Network ["☁️ SECURITY MESH"]
        CF[("🔒 <b>CLOUDFLARE TUNNEL</b><br/>(HTTPS / WAF / Domain)")]
    end

    %% -- Core Engine --
    subgraph Core ["🚀 CORE ENGINE (Docker)"]
        direction TB
        WEB["🧪 <b>FLASK SERVER</b><br/>(API & Web Engine)"]
        WORKER["⚙️ <b>BACKGROUND WORKER</b><br/>(Monitor & Scheduler)"]
    end

    %% -- Data Layer --
    subgraph Storage ["📦 PERSISTENCE"]
        JSON[("🗄️ <b>JSON DATA MESH</b><br/>(States / Logs / Cache)")]
    end

    %% -- External Ecosystem --
    subgraph Integration ["🔗 EXTERNAL ECOSYSTEM"]
        direction LR
        TG(("💬 <b>TELEGRAM<br/>BOT API</b>"))
        DTEK["⚡ <b>YASNO / DTEK</b><br/>(Local Parsing)"]
        SAFE["🛡️ <b>SAFETY API</b><br/>(AQI / Alerts)"]
    end

    %% -- Connections --
    IoT -->|Secure Push| CF
    PWA <-->|HTTPS| CF
    CF <-->|Reverse Proxy| WEB
    
    WEB <-->|State Sync| JSON
    WORKER <-->|History Persistence| JSON
    
    WORKER -->|Auto-Report| TG
    WORKER -.->|Direct Sync| DTEK
    WEB -.->|Live Fetch| SAFE

    %% -- Applying Styles --
    class IoT,PWA access
    class CF network
    class WEB,WORKER core
    class JSON storage
    class TG,DTEK,SAFE external
```

---

## 🐳 Quick Start via Docker

**Official Image:** `webyhomelab/flash-monitor-kyiv:latest`

### Docker Compose
```yaml
services:
  web:
    image: webyhomelab/flash-monitor-kyiv:latest
    container_name: flash-monitor-web
    ports: ["5050:5050"]
    volumes: ["./data:/app/data"]
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data

  worker:
    image: webyhomelab/flash-monitor-kyiv:latest
    container_name: flash-monitor-worker
    command: python run_background.py
    volumes: ["./data:/app/data"]
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data
```

---

## 💡 Tip for IoT Sensors (Heartbeat)

For sending Push signals, it is highly recommended to use the **HTTPS address of your domain** (e.g., via Cloudflare Tunnel) instead of a direct IP address:

*   **🛡️ Security:** HTTPS encrypts your secret key during transmission.
*   **🧩 Flexibility:** If you change servers, you won't need to reflash your hardware sensors — simply update the tunnel settings.

**Example:** `https://flash.srvrs.top/api/push/your_secret_key`

---

## 🛠 Tech Stack
- **Backend:** Python 3.11, Flask, Gunicorn.
- **Analytics:** Matplotlib, BeautifulSoup4.
- **Infra:** Docker, PWA (Progressive Web App).

---

## 📜 License
Distributed under the **MIT** License.

<p align="center">
  ✦ 2026 Weby Homelab ✦<br>
  Made with ❤️ in Kyiv under air raid sirens and blackouts
</p>

---
