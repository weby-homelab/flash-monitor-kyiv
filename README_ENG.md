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
  <img src="https://img.shields.io/badge/Branch-Classic_(Bare-Metal)-0984e3?style=for-the-badge&logo=docker&logoColor=white" alt="Branch Main">
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
graph TD
    %% -- Styles --
    classDef cloud fill:#2d3436,stroke:#7b1fa2,stroke-width:2px,color:#fff
    classDef local fill:#2d3436,stroke:#1565c0,stroke-width:2px,color:#fff
    classDef service fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff
    classDef security fill:#d63031,stroke:#ff7675,stroke-width:2px,color:#fff
    classDef network fill:#00b894,stroke:#81ecec,stroke-width:2px,color:#fff
    classDef external fill:#f39c12,stroke:#ffeaa7,stroke-width:2px,color:#000

    subgraph EXT ["🌐 External Layer"]
        direction TB
        WEB[PWA Dashboard]
        TG[Telegram Channel] --- BOT[Telegram Bot API]
    end

    subgraph PROD ["🖥️ Docker Container"]
        direction TB
        
        API[FastAPI /app.py]
        SVC[flash-monitor.service]
        BG[flash-background.service]
        LMN[light_service.py]

        subgraph Core ["🧠 Core Modules"]
            direction TB
            TC[telegram_client.py]
            ST[storage.py]
        end
        
        subgraph Data ["💾 Data Layer (JSON Flat-DB)"]
            direction TB
            STATE[(power_monitor_state.json)]
            CFG[(config.json)]
            LOGS[(event_log.json)]
            SCHED[(last_schedules.json)]
        end
        
        API --- SVC
        BG --- LMN
        
        LMN --- TC
        LMN --- ST
        API --- ST
        API --- TC
        
        ST --- STATE
        ST --- LOGS
        ST --- SCHED
        ST --- CFG
    end

    subgraph Logic ["⚙️ Application Logic"]
        direction TB
        FN[False Always Wins]
        SN[Safety Net]
        QM[Quiet Mode]
    end

    subgraph SRC ["📡 External Sources (API)"]
        direction TB
        YASNO[Yasno API]
        DTEK[GitHub DTEK]
        METEO[OpenMeteo]
        AQI[SaveEcoBot]
    end

    %% -- Connections between subgraphs --
    WEB ---> API
    TC --- BOT
    
    LMN --- Logic
    
    YASNO -.-> LMN
    DTEK -.-> LMN
    METEO -.-> SVC
    AQI -.-> SVC

    class TG,BOT,YASNO,DTEK,METEO,AQI external
    class SVC,BG service
    class STATE,CFG,LOGS,SCHED local
    class FN,SN,QM cloud
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
