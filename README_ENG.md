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
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# POWER⚡️ SAFETY (FLASH MONITOR KYIV) - Bare-metal Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** is a professional autonomous monitoring system for critical infrastructure and environmental safety. The project provides real-time electricity monitoring, air raid alerts tracking, air quality (AQI), and radiation background levels.

This branch (`classic`) contains the **Bare-metal Edition** of the project, designed for running as a systemd service.

> **Project Status:** Stable v3.3.6 (Stable & Test-Covered)
> **Architecture:** Python FastAPI + Background Workers + JSON Flat-DB + Bare Metal / systemd
> **Brand:** Weby Homelab

---

## 🛡 Update v3.3.6 (Stable & Test-Covered)
*   **QA & Test Coverage:** Significantly expanded the test base (from 9 to 37). The project now has a robust safety net covering FastAPI endpoints, asynchronous data storage, and the Telegram Client.
*   **Anti-spam & Stability:** Fixed a "cold start" bug that caused false "Light Up" messages to be sent upon server restart.
*   **Telegram API Optimization:** Added intelligent handling of the `message is not modified` error. The system no longer creates duplicate reports if the chart content hasn't changed.
*   **Test Redirect:** During `pytest` runs, all notifications are automatically redirected to the admin's private chat, keeping the main channel clean.

## 🛡 Update v3.3.5 (Sync Optimization & Stability)
  *   **Report Deduplication:** Eliminated a race condition in the `schedule_loop` and `sync_schedules` background cycles that caused the generation of redundant and duplicate graphical reports in Telegram when update schedules collided.
  *   **Lock Mechanism (Lock & Cooldown):** Added a 15-second file locking system (`.lock`) for daily and weekly report generation processes. Now parallel Gunicorn workers no longer overload the system and Telegram API.
  *   **Resource Optimization:** The "Daily" and "Weekly" reports are now completely separated in the code, eliminating the chain reaction of subprocess launches.

  ## 🛡 Update v3.3.4 (Hotfixes)
  *   **Manual Override Bypass:** Fixed the behavior of manual power-off commands. Manual signals via API now always interrupt "Quiet Mode" and publish an alarm, bypassing automatic filters.
  *   **Safety Net UI Persistence:** Increased the response buttons timeout in the admin panel to 180 seconds (previously buttons disappeared after 30 seconds, not allowing enough time for admin confirmation).
  *   **Smart Source Logic:** Fixed a visual bug on the dashboard where the `[DTEK]` label was shown even when Yasno was prioritized. Now the chart footer correctly displays the actual data source used.

  ## 🛡 Update v3.3.3 (Smart Anti-Spam)
*   **Smart Anti-Spam:** Eliminated redundant daily graphical reports ("Monitoring" and "Report") in "Active Mode" on days when power is fully available for 24 hours, preventing unnecessary spam after a "100% light streak" text greeting is sent. The graph is immediately published to the channel if any real power outage occurs.
*   **Live Update in Quiet Mode:** Resolved an issue where the daily graphic report got "stuck" when Quiet Mode engaged. The system will now actively update the existing graphical report message in Telegram with the current "Fact" line and time.
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
