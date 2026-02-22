# СВІТЛО⚡БЕЗПЕКА

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="СВІТЛО⚡БЕЗПЕКА Dashboard Preview" width="100%">
</p>

<p align="center">
  <a href="https://hub.docker.com/r/webyhomelab/flash-monitor"><img src="https://img.shields.io/docker/v/webyhomelab/flash-monitor?style=for-the-badge&logo=docker&color=blue" alt="Docker Version"></a>
  <a href="https://hub.docker.com/r/webyhomelab/flash-monitor"><img src="https://img.shields.io/docker/pulls/webyhomelab/flash-monitor?style=for-the-badge&logo=docker&color=informational" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/Python-3.11-yellow?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

**СВІТЛО⚡БЕЗПЕКА** — це сучасна екосистема для моніторингу енергосистеми та безпекової ситуації в Києві. Проєкт об'єднує в собі heartbeat-трекінг електромережі, аналітику відповідності графікам Yasno/DTEK, систему сповіщення про повітряні тривоги та моніторинг якості повітря.

🔗 **Живий моніторинг:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Ключові Особливості

### 💡 Енергомоніторинг 2.0
- **Heartbeat Tracking:** Моніторинг наявності світла в реальному часі через IoT-сигнали.
- **Accuracy Analytics:** Розрахунок точності відключень відносно офіційних графіків у хвилинах.
- **Visual Statistics:** Автоматична генерація денних та тижневих графіків «План vs Факт».

### 🛡️ Безпека та Екологія (Борщагівка)
- **Air Alerts:** Миттєвий статус тривог для Києва та області з інтегрованою картою.
- **AQI Monitor:** Моніторинг якості повітря (PM2.5, PM10) та радіаційного фону (локація: Симиренка).
- **Weather Insights:** Актуальна температура, вологість та вітер.

### 🔔 Розумні Сповіщення
- **Dynamic Reports:** Одне повідомлення в Telegram на добу, що оновлюється кожні 10 хвилин.
- **Smart Logic:** Текстові графіки оновлюються в Telegram тільки при зміні офіційних даних.
- **Quiet Mode:** Текстові алерти про зміну статусу мережі без зайвого спаму.

---

## 🏗 Архітектура Системи

```mermaid
flowchart TD
    %% -- Style Definitions --
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b
    classDef core fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#616161
    classDef logic fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32
    classDef external fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#c2185b
    classDef storage fill:#efebe9,stroke:#4e342e,stroke-width:2px,color:#4e342e
    classDef notify fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#5e35b1

    subgraph Clients ["🌐 UI & IoT"]
        User("📱 PWA Dashboard<br/>(Refresh 60s)")
        IoT("⚡ IoT Device<br/>(Push 30s)")
    end

    subgraph Server ["🚀 Docker Container"]
        API["🖥️ Flask API Gateway<br/>(High-Load Ready)"]
        Monitor["⚙️ Background Engine<br/>(Monitor & Scheduler)"]
    end

    subgraph Infrastructure ["📦 Data & Notify"]
        JSON[("🗄️ JSON Storage<br/>(Persistence)")]
        Telegram("💬 Telegram API")
    end

    User <--> API
    IoT --> API
    API <--> JSON
    Monitor <--> JSON
    Monitor --> Telegram
    
    class User,IoT client
    class API core
    class Monitor logic
    class JSON storage
    class Telegram notify
```

---

## 🐳 Швидкий запуск (Docker Compose)

Найсучасніший спосіб розгорнути систему — використовувати готовий Docker-образ.

1. **Створіть файл `docker-compose.yml`**:
```yaml
services:
  web:
    image: webyhomelab/flash-monitor:latest
    container_name: flash-monitor-web
    restart: unless-stopped
    ports:
      - "5050:5050"
    volumes:
      - ./data:/app/data
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data

  worker:
    image: webyhomelab/flash-monitor:latest
    container_name: flash-monitor-worker
    restart: unless-stopped
    command: python run_background.py
    volumes:
      - ./data:/app/data
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data
```

2. **Запустіть систему**:
```bash
docker compose up -d
```

---

## 🛠 Технологічний Стек

*   **Backend:** Python 3.11, Flask, Gunicorn.
*   **Data:** Pandas, Matplotlib, BeautifulSoup4.
*   **Containerization:** Docker, Docker Compose.
*   **Infrastructure:** Cloudflare Tunnels, Systemd.

---

## 📜 Ліцензія

Розповсюджується під ліцензією **MIT**. 

<p align="center">
  2026 Розроблено з ❤️ під час блекаутів у Києві.
</p>
