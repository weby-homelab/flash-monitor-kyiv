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
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docs/assets/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# POWER⚡️ SAFETY (FLASH MONITOR KYIV) - Bare-metal Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** is a professional autonomous monitoring system for critical infrastructure and environmental safety. The project provides real-time electricity monitoring, air raid alerts tracking, air quality (AQI), and radiation background levels.

This branch (`classic`) contains the **Bare-metal Edition** of the project, designed for running as a systemd service.

> **Project Status:** Stable v3.3.8 (Stable & Test-Covered)
> **Architecture:** Python FastAPI + Background Workers + JSON Flat-DB + Bare Metal / systemd
> **Brand:** Weby Homelab

---

## Project History
For a complete history of updates, changes, and bug fixes, please refer to the [CHANGELOG.md](docs/CHANGELOG.md).

## 🚀 Core Innovations (v3.2+)

### 🎛 Admin Control Panel
A fully autonomous Glassmorphism web interface to manage all aspects of the system without the need to edit configuration files via SSH.

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Asynchronous Performance:** The new async caching mechanism (FastAPI) completely eliminates deadlocks when multiple background workers write data simultaneously.
*   **Smart Backups:** Create manual and automatic restore points for your configuration. Instant one-click recovery with automatic service restart.
*   **Flexible Source Management:** Change priority between Yasno, GitHub, or connect your own Custom JSON URL. Includes a manual force-sync button.
*   **Complete Geo-Adaptation:** Set coordinates (Lat/Lon) for accurate weather, SaveEcoBot station ID, and toggle widget visibility.
*   **Security (Zero-Trust):** Fixed LFI (Path Traversal) vulnerabilities by implementing strict path validation. Access keys are safely generated during bootstrap.

---

---

## 🚀 Core Innovations (v3.2+)

### 🎛 Admin Control Panel
A fully autonomous **Glassmorphism** web interface to manage all aspects of the system without the need to edit configuration files via SSH.

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Asynchronous Performance:** The new async caching mechanism (FastAPI) eliminates deadlocks and "freezes" during simultaneous data writes by background workers.
*   **Smart Backups:** Create manual and automatic restore points for your configuration. Instant one-click recovery with automatic service restart.
*   **Flexible Source Management:** Change priority between Yasno, GitHub, or connect your own Custom JSON URL. Manual force-sync button for schedules.
*   **Complete Geo-Adaptation:** Set coordinates (Lat/Lon) for accurate weather, SaveEcoBot station ID, and toggle widget visibility.
*   **Security (Zero-Trust):** Fixed LFI (Path Traversal) vulnerabilities with strict path validation. Access keys are safely generated during the first bootstrap.

### 🤫 «Quiet Mode» (Information Calm)
A unique algorithm that minimizes "information noise." The system automatically enters a calm state if there were no outages in the last 24 hours and no restrictions are planned for tomorrow. Ideal for stable periods of the power grid.

### 🚨 Safety Net
An interactive rapid response mechanism: if the Push signal is delayed for more than 35 seconds, the administrator receives a request in Telegram with action options (`🔴 Power is out`, `🛠 Technical glitch`, `🤷‍♂️ I don't know`). This prevents false alarms in the public channel.

### ⚖️ «False Always Wins» Logic
A hybrid schedule processing system. If at least one source indicates an outage, the system displays it as a priority. Old outage records are never overwritten by "clean" plans, ensuring an honest event history.

---

## 📱 Real-world Telegram Notification Examples

*   📊 **[Daily "Plan vs Fact" Chart (Smart Daily Report)](https://t.me/svitlobot_Symyrenka22B/1230)**
*   📈 **[Weekly Outage Analytics](https://t.me/svitlobot_Symyrenka22B/1192)**
*   🔴 **[Outage notification with schedule precision](https://t.me/svitlobot_Symyrenka22B/1209)**
*   🟢 **[Power restoration notification with schedule precision](https://t.me/svitlobot_Symyrenka22B/1212)**
*   ⚠️ **[Instant alert about schedule changes from DTEK](https://t.me/svitlobot_Symyrenka22B/1222)**
*   🚨 **[Air raid alert in the city](https://t.me/svitlobot_Symyrenka22B/1196)**

---

## 📊 Dashboard Capabilities (PWA)

A modern **Glassmorphism** interface optimized for mobile devices:
*   **Live Status:** Visualizing the system "Pulse" (Power is ON! / Power is OUT!).
*   **Environmental Monitoring:** Temperature, humidity, PM2.5/PM10 (OpenMeteo/SaveEcoBot), and radiation with interactive charts for the last 24 hours.
*   **Schedule Bar:** A compact 24-hour scale of planned outages.

---

## 🏗️ System Architecture

Flash Monitor is a power outage monitoring system with automatic notifications.

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

## 📥 Installation & Setup

The project has two main branches:

1.  **`main` (Docker Edition):** Recommended for a quick start.
    ```bash
    # 1. Download docker-compose.yml
    curl -O https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docker-compose.yml

    # 2. Run the system (images are pulled automatically from Docker Hub)
    docker-compose up -d
    ```
2.  **`classic` (Bare-Metal Edition):** For running directly on the host system via `systemd`.

📖 **Complete Documentation:**
*   [Installation Guide (Step-by-Step)](docs/INSTRUCTIONS_INSTALL_ENG.md)
*   [Detailed Configuration Setup](docs/INSTRUCTIONS_ENG.md)
*   [Development Rules & Guidelines](docs/DEVELOPMENT_ENG.md)
