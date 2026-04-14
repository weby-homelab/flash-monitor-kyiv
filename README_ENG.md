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

**Flash Monitor Kyiv** is a professional autonomous monitoring system for critical infrastructure and environmental safety. The project provides real-time electricity monitoring, air raid alerts tracking, air quality (AQI), and radiation background levels.

This branch (`main`) contains the **Docker Edition** of the project, which is recommended for quick deployment and dependency isolation.

> **Project Status:** Stable v3.4.0 (Docker Optimized)
> **Architecture:** FastAPI + Background Workers + Docker Compose + JSON Flat-DB
> **Brand:** Weby Homelab

## 📜 Key Features
- **Containerized:** Full isolation via Docker.
- **Admin Panel:** Glassmorphism-style web interface.
- **Quiet Mode:** Intelligent notification suppression.
- **Safety Net:** Connection loss protection.
- **Analytics:** Automated graphical reports (Matplotlib).

---

## 🚀 Core Innovations (v3.2+)

### 🎛 Admin Control Panel
A fully autonomous **Glassmorphism** web interface to manage all aspects of the system without the need to edit configuration files via SSH.

<p align="center">
  <img src="docs/assets/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="docs/assets/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="docs/assets/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Asynchronous Performance:** The new async caching mechanism (FastAPI) eliminates deadlocks and "freezes" during simultaneous data writes by background workers.
*   **Smart Backups:** Create manual and automatic restore points for your configuration. Instant one-click recovery with automatic service restart.
*   **Flexible Source Management:** Change priority between Yasno, GitHub, or connect your own Custom JSON URL. Manual force-sync button for schedules.
*   **Complete Geo-Adaptation:** Set coordinates (Lat/Lon) for accurate weather, SaveEcoBot station ID, and toggle widget visibility.
*   **Security (Zero-Trust):** Fixed LFI (Path Traversal) vulnerabilities with strict path validation.

---

## 📱 Real-world Telegram Notification Examples

*   📊 **[Daily "Plan vs Fact" Chart (Smart Daily Report)](https://t.me/svitlobot_Symyrenka22B/1230)**
*   📈 **[Weekly Outage Analytics](https://t.me/svitlobot_Symyrenka22B/1192)**
*   🔴 **[Outage notification with schedule precision](https://t.me/svitlobot_Symyrenka22B/1209)**

---

## 📊 Dashboard Capabilities (PWA)

A modern **Glassmorphism** interface optimized for mobile devices:
*   **Live Status:** Visualizing the system "Pulse" (Power is ON! / Power is OUT!).
*   **Environmental Monitoring:** Temperature, humidity, PM2.5/PM10, and radiation.

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    %% ================================================
    %% NEW CONCEPT 2026 for README.md
    %% "End-to-End Pipeline" — dynamic data flow
    %% Horizontal pipeline with clear direction
    %% Clean, modern, easy to read in GitHub (dark/light themes)
    %% ================================================

    classDef external fill:#0f766e,stroke:#14b8a6,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef core fill:#1e293b,stroke:#22d3ee,stroke-width:3.5px,color:#fff,rx:14px,ry:14px
    classDef gateway fill:#7c3aed,stroke:#a78bfa,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef client fill:#1e293b,stroke:#60a5fa,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef db fill:#1e293b,stroke:#ec4899,stroke-width:3px,color:#fff,rx:12px,ry:12px

    %% ====================== LEFT SIDE: DATA SOURCES ======================
    subgraph External ["🔌 Data Sources"]
        direction TB
        Energy["⚡ Yasno / DTEK API<br>Outage Schedules"]:::external
        Meteo["🌤️ OpenMeteo + SaveEcoBot<br>Weather & AQI"]:::external
    end

    %% ====================== CENTER: CORE PIPELINE ======================
    subgraph Core ["⚙️ Flash Monitor Core<br>light_service.py + FastAPI"]
        direction TB

        Worker["🔄 Worker<br>flash-background.service"]:::core

        subgraph Processing ["Processing & Logic"]
            direction LR
            Rules["🛡️ Rules Engine<br>False Always Wins • 30s Safety Net<br>Quiet Mode"]:::core
            Reports["📊 Reports Generator<br>Matplotlib charts"]:::core
            Storage["💾 Storage<br>JSON Flat-DB<br>config • state • logs • schedules"]:::db
        end

        API["🔌 FastAPI<br>flash-monitor.service<br>app.py"]:::core
        TgClient["🤖 Telegram Client"]:::core
    end

    %% ====================== GATEWAY ======================
    subgraph Gateway ["🔐 Cloudflare Tunnel<br>Zero Trust + Reverse Proxy"]
        CF["☁️ Cloudflare Tunnel<br>port 5050"]:::gateway
    end

    %% ====================== RIGHT SIDE: CLIENTS ======================
    subgraph Clients ["👥 User Interfaces"]
        direction TB
        PWA["📱 PWA Dashboard"]:::client
        Admin["🛠️ Admin Panel"]:::client
        Telegram["📨 Telegram Channel<br>+ Push Notifications"]:::client
    end

    %% ====================== DATA FLOW (Main Trunk) ======================
    Energy & Meteo -->|Scraping + Fetch| Worker

    Worker -->|Rules Check| Rules
    Rules -->|Decision| Worker

    Worker -->|Storage| Storage
    Storage -->|Read State| Worker

    Worker -->|Generation| Reports
    Worker -->|Notifications| TgClient
    Reports -->|Charts| TgClient

    Worker <-->|REST + WebSocket| API

    API -->|Reverse Proxy| CF
    CF <-->|HTTPS + JWT / WSS| PWA
    CF <-->|HTTPS + JWT| Admin
    TgClient -->|Bot API| Telegram

    %% Additional push notifications
    API -.->|Web Push API| PWA

    %% ====================== Subgraph Title Style ======================
    classDef subgraphTitle fill:#0f172a,stroke:none,color:#64748b,font-size:15px
```

---

## 📥 Quick Start (Docker)

1. **Download docker-compose.yml:**
```bash
curl -O https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docker-compose.yml
```

2. **Start the system:**
```bash
docker-compose up -d
```

3. **Configuration:**
Open the web interface (port 5050 by default) and complete the initial setup via the Admin Panel.

📖 **Complete Documentation:**
* [Docker Installation Guide](docs/INSTRUCTIONS_INSTALL_ENG.md)
* [Telegram Bot Setup](docs/INSTRUCTIONS_ENG.md)

---
**✦ 2026 Weby Homelab ✦**
