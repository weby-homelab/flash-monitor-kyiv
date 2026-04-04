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
  <img src="https://img.shields.io/badge/Branch-Main_(Docker)-0984e3?style=for-the-badge&logo=docker&logoColor=white" alt="Branch Main">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# СВІТЛО⚡️ БЕЗПЕКА (FLASH MONITOR KYIV) - Docker Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** is a professional, autonomous monitoring system for critical infrastructure and environmental safety. The project provides real-time power monitoring, air raid alerts tracking, air quality index (AQI), and radiation background levels.

This branch (`main`) contains the **Docker Edition** of the project, designed for quick deployment via Docker Compose.

> **Project Status:** Stable v3.3.0 (Core Refactoring & Fail-Safe Architecture)
> **Architecture:** Python FastAPI + Background Workers + JSON Flat-DB + Docker / Docker Compose
> **Brand:** Weby Homelab

---

## 🛡 Update v3.3.0
*   **Data Access Layer (`storage.py`):** Introduced a centralized storage module. All file I/O operations are now atomic and protected by `asyncio.Lock()` and `fcntl.flock`, completely eliminating race conditions and JSON database corruption.
*   **Notification Service (`telegram_client.py`):** Created a unified Telegram API client with smart resilience, automatically handling timeouts and sending new messages when editing fails.
*   **Fail-Safe Quiet Mode:** If the connection drops during "Information Peace" and the admin doesn't respond within 5 minutes, the system automatically ignores the glitch, preventing any false night alarms in the public channel.
*   **Modular State Machine:** The infinite loops have been split into independent asynchronous blocks with global `try...except` handling, ensuring the monitoring service never crashes from external API failures.


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

## 🏗 System Architecture

```mermaid
flowchart TB
    %% Colors & Styles
    classDef client fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef cloudflare fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef server fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef module fill:#334155,stroke:#475569,stroke-width:1px,color:#e2e8f0,rx:5px,ry:5px
    classDef db fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef ext_api fill:#334155,stroke:#64748b,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef logic fill:#0f172a,stroke:#eab308,stroke-width:1px,color:#fde68a,rx:5px,ry:5px,stroke-dasharray: 5 5

    subgraph TopLayer ["🌐 Access Interfaces"]
        direction LR
        PWA["📱 PWA Dashboard"]:::client
        Admin["🔐 Admin Panel"]:::client
        Subscribers["📢 Telegram Channel"]:::client
    end

    CF["🌩️ Cloudflare Tunnel (Zero Trust)"]:::cloudflare

    PWA <-->|HTTPS / WSS| CF
    Admin <-->|HTTPS / JWT| CF

    subgraph CoreLayer ["🖥️ Core Server (Docker / systemd)"]
        direction TB

        subgraph Services ["⚙️ System Services"]
            direction LR
            API["⚡ flash-monitor.service<br/>(FastAPI / app.py)"]:::server
            Worker["🔍 flash-background.service<br/>(light_service.py)"]:::server
        end

        subgraph Modules ["🛠 Internal Modules & Logic"]
            direction LR
            Storage["storage.py<br/>(I/O Manager)"]:::module
            Reports["generate_*_report.py<br/>(Matplotlib)"]:::module
            TgClient["telegram_client.py<br/>(Bot Wrapper)"]:::module
            Rules["🧠 Algorithms:<br/>• False Always Wins<br/>• Safety Net (30s)<br/>• Quiet Mode"]:::logic
        end

        API <-->|State Sync| Worker
        Worker -.-> Rules
        Worker --> Reports
        Worker --> TgClient
        Reports --> TgClient
        API --> Storage
        Worker --> Storage
    end

    CF <-->|Reverse Proxy - Port 5050| API

    subgraph DataLayer ["💾 Data Storage (JSON Flat-DB)"]
        direction LR
        Config[("config.json")]:::db
        State[("power_monitor_state.json")]:::db
        Logs[("event_log.json")]:::db
        Sched[("last_schedules.json")]:::db
    end

    Storage <-->|Read / Write| DataLayer

    subgraph ExternalLayer ["📡 External APIs & Gateways"]
        direction LR
        PushAPI["🔔 Web Push API"]:::ext_api
        TgAPI["🤖 Telegram Bot API"]:::ext_api
        Energy["⚡ Yasno / DTEK API"]:::ext_api
        Meteo["🌤 OpenMeteo / SaveEcoBot"]:::ext_api
    end

    API -->|Trigger Push| PushAPI
    PushAPI -.->|Notification| PWA
    
    TgClient -->|Send| TgAPI
    TgAPI -->|Posts & Charts| Subscribers
    
    Energy -->|Scrape Schedules| Worker
    Meteo -->|Fetch Weather| API
    Meteo -->|AQI Monitoring| Worker
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
*   [Installation Guide (Step-by-Step)](INSTRUCTIONS_INSTALL_ENG.md)
*   [Detailed Configuration Setup](INSTRUCTIONS_ENG.md)
*   [Development Rules & Guidelines](DEVELOPMENT_ENG.md)

---
**✦ 2026 Weby Homelab ✦**
