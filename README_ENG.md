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
  <img src="https://img.shields.io/badge/Branch-main_(Docker)-2496ed?style=for-the-badge&logo=docker&logoColor=white" alt="Branch Main">
  <img src="https://img.shields.io/docker/v/webyhomelab/flash-monitor-kyiv?style=for-the-badge&logo=docker&logoColor=white&label=Docker%20Hub" alt="Docker Hub Version">
  <img src="https://img.shields.io/docker/pulls/webyhomelab/flash-monitor-kyiv?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Pulls">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docs/assets/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# POWER⚡️ SAFETY (FLASH MONITOR KYIV) - Docker Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** is a professional autonomous monitoring system for critical infrastructure and environmental safety. The project provides precision real-time electricity monitoring, intelligent outage schedule processing (DTEK/Yasno), air raid alert tracking, air quality (AQI), and radiation background levels.

This branch (`main`) contains the **Docker Edition** of the project — a fully containerized version optimized for rapid, one-step deployment in any environment.

> **Project Status:** Stable v3.4.0 (Docker Optimized)
> **Architecture:** Asynchronous FastAPI + Docker Compose + JSON Flat-DB
> **Brand:** Weby Homelab

---

## 🛠 Technology Stack (Docker Edition)
- **Runtime:** Python 3.12 (slim-bookworm) inside a container.
- **Web-Core:** FastAPI with WebSocket and SSE support.
- **Containerization:** Docker Compose with automatic volume mounting for state preservation (`data/`).
- **CI/CD:** Multi-arch builds (`amd64`/`arm64`) supporting Raspberry Pi and Cloud servers.

---

## 🚀 Core Innovations & Algorithms

...
  <img src="docs/assets/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="docs/assets/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="docs/assets/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Asynchronous Performance:** A new async caching mechanism eliminates deadlocks between the background worker and user requests.
*   **Smart Backups:** Instant one-click system recovery with automatic service restarts.
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

    subgraph Docker ["🐳 Docker Container"]
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

## 📥 Installation (Docker Edition)

### 1. Download Configuration
```bash
curl -O https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docker-compose.yml
```

### 2. Start
```bash
docker-compose up -d
```

### 3. Configuration
Once running, open your browser at `http://localhost:5050`. The system will guide you through setting up `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID` via the web UI (or you can pre-configure a `.env` file).

🔑 **Accessing the Admin Panel:**
```bash
docker exec -it flash-monitor-kyiv cat data/power_monitor_state.json | grep admin_token
```

---

💡 **Need maximum control?** Check out the [Bare-metal Edition (classic branch)](https://github.com/weby-homelab/flash-monitor-kyiv/tree/classic).

📖 **Documentation:**
* [Full Docker Guide](docs/INSTRUCTIONS_INSTALL_ENG.md)
* [Change History (CHANGELOG.md)](docs/CHANGELOG.md)

---
**✦ 2026 Weby Homelab ✦**
