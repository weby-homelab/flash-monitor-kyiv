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
  <img src="https://img.shields.io/badge/Branch-Main_(Docker)-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Branch Main">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# СВІТЛО⚡️ БЕЗПЕКА (FLASH MONITOR KYIV) - Docker Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** is a professional, autonomous monitoring system for critical infrastructure and environmental safety. The project provides real-time power monitoring, air raid alerts tracking, air quality index (AQI), and radiation background levels.

This branch (`main`) contains the **Docker Edition** of the project, designed for fast, portable, and isolated deployment in any environment. If you need a bare-metal installation directly on the host system via `systemd`, use the `classic` branch.

> **Project Status:** Stable v3.2.1 (Total Control, Security & Async Edition)
> **Architecture:** Python FastAPI + Background Workers + JSON Flat-DB + Docker / Docker Compose
> **Brand:** Weby Homelab

---

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

### 🤫 "Quiet Mode" (Information Peace)
A unique algorithm that minimizes "information noise." The system automatically enters a quiet state if there have been no outages in the past 24 hours, and there are no planned outages in the schedule for the next 24 hours.

### 🚨 Safety Net
An interactive rapid response mechanism: if the heart-beat signal (Push) is delayed for more than 35 seconds, the administrator receives a Telegram prompt with action buttons (`🔴 Power Down`, `🛠 Technical Failure`, `🤷‍♂️ Don't Know`).

### ⚖️ "False Always Wins" Logic
A hybrid schedule processing system. If at least one source indicates an outage (`False`), the system displays it as the priority state. Old outage records are never overwritten by new "all-clear" plans.

---

## 📱 Real Telegram Message Examples

*   📊 **[Daily "Plan vs Fact" Report (Smart Daily Report)](https://t.me/svitlobot_Symyrenka22B/1230)**
*   📈 **[Weekly Analytics Summary](https://t.me/svitlobot_Symyrenka22B/1192)**
*   🔴 **[Power Outage Alert with Schedule Accuracy](https://t.me/svitlobot_Symyrenka22B/1209)**
*   🟢 **[Power Restoration Alert with Schedule Accuracy](https://t.me/svitlobot_Symyrenka22B/1212)**
*   ⚠️ **[Instant Alert on DTEK Schedule Change](https://t.me/svitlobot_Symyrenka22B/1222)**
*   🚨 **[Air Raid Alert Notification in Kyiv](https://t.me/svitlobot_Symyrenka22B/1196)**

---

## 📊 Dashboard Features (PWA)

Modern **Glassmorphism** interface, fully mobile-optimized:
*   **Live Status:** Real-time "Pulse" visualization (Power ON! / Power OFF!).
*   **Environmental Monitoring:** Temperature, Humidity, PM2.5/PM10 (via OpenMeteo/SaveEcoBot), and Radiation with interactive 24-hour history graphs.
*   **Schedule Bar:** A compact 24-hour visualization of planned outages.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    classDef access fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,rx:10,ry:10
    classDef network fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#7b1fa2,rx:5,ry:5
    classDef core fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32,rx:5,ry:5
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100,rx:10,ry:10
    classDef external fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#c2185b,rx:5,ry:5

    subgraph Access ["📡 ACCESS LAYER"]
        IoT["⚡ IoT SENSORS"]
        PWA["📱 PWA DASHBOARD"]
        ADM["💻 ADMIN PANEL"]
    end

    subgraph Network ["☁️ SECURITY MESH"]
        CF[("🔒 CLOUDFLARE TUNNEL")]
    end

    subgraph Core ["🚀 CORE ENGINE (Docker)"]
        direction TB
        WEB["🧪 FASTAPI SERVER"]
        WORKER["⚙️ BACKGROUND WORKER"]
    end

    subgraph Storage ["📦 PERSISTENCE (Docker Volume)"]
        JSON[("🗄️ JSON DATA MESH")]
    end

    subgraph Integration ["🔗 EXTERNAL ECOSYSTEM"]
        direction LR
        TG(("💬 TELEGRAM API"))
        DTEK["⚡ YASNO / DTEK / CUSTOM"]
        SAFE["🛡️ SAFETY API"]
    end

    IoT -->|Secure Push| CF
    PWA <-->|HTTPS| CF
    ADM <-->|Secure Token| CF
    CF <-->|Reverse Proxy| WEB
    WEB <-->|Async State Sync| JSON
    WORKER <-->|History Persistence| JSON
    WORKER -->|Auto-Report| TG
    WORKER -.->|Direct Sync| DTEK
    WEB -.->|Live Fetch| SAFE

    class IoT,PWA,ADM access
    class CF network
    class WEB,WORKER core
    class JSON storage
    class TG,DTEK,SAFE external
```

---

## 🛠 Tech Stack
- **Backend:** Python 3.12, FastAPI, Uvicorn.
- **Analytics:** Matplotlib, BeautifulSoup4.
- **Infra:** Docker & Docker Compose.

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

### Quick Start (Smart Bootstrap):
The system automatically initializes on the first run:
1.  Generates a unique `SECRET_KEY` and `ADMIN_TOKEN`.
2.  Creates the directory structure in `/app/data` (mounted in Docker Volume) with default v3 settings.
3.  Downloads up-to-date schedules for your power group.

---

## 📜 License
Distributed under the **MIT** license.

© 2026 Weby Homelab.
