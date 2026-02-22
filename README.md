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

## 📖 Про проєкт

**СВІТЛО⚡БЕЗПЕКА** (Flash Monitor Kyiv) — це інтелектуальна open-source екосистема, розроблена для киян, щоб забезпечити максимальну прозорість та передбачуваність у складних енергетичних умовах. 

Проєкт не просто моніторить світло — він аналізує поведінку енергомережі, порівнює її з офіційними планами Yasno/DTEK та надає користувачу миттєву, візуалізовану картину безпекової ситуації в місті.

🔗 **Живий моніторинг:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Ключові Особливості

### 💡 Розумний Енергомоніторинг 2.0
- **Heartbeat Tracking:** Використання IoT-сигналів для відстеження наявності світла в реальному часі з точністю до секунд.
- **Accuracy Analytics:** Інтелектуальний розрахунок відхилень. Система знає, на скільки хвилин раніше чи пізніше графіку відбулося перемикання.
- **Visual Statistics:** Автоматична генерація та оновлення (кожні 10 хв) денних та тижневих графіків «План vs Факт» прямо у ваш Telegram.

### 🛡️ Безпека та Екологія (Борщагівка)
- **Air Alerts:** Миттєвий статус та інтегрована карта повітряних тривог для Києва та області.
- **AQI Monitor:** Моніторинг якості повітря (PM2.5, PM10) та радіаційного фону в реальному часі (локація: Борщагівка, Симиренка).
- **Weather Insights:** Актуальна температура, вологість та параметри вітру для повного розуміння екологічної ситуації.

### 🔔 Smart Telegram Reporting
- **Dynamic Live Reports:** Одне повідомлення на добу, яке постійно оновлюється, зберігаючи історію чистою.
- **Change-Driven Updates:** Текстові графіки оновлюються лише тоді, коли змінюються дані від Yasno або ДТЕК.
- **Quiet Mode:** Розумні текстові сповіщення про зміну статусу без зайвого інформаційного шуму.

---

## 🐳 Docker версія

Для забезпечення максимальної портативності та стабільності, проєкт повністю докерезовано. Ви можете розгорнути власну інстанцію системи на будь-якому сервері за лічені секунди.

**Офіційний реєстр:** [webyhomelab/flash-monitor](https://hub.docker.com/r/webyhomelab/flash-monitor)

### Теги:
- `latest` — найсвіжіша стабільна версія.
- `v1.0.0` — перший офіційний стабільний реліз.

---

## 🏗 Архітектура Системи

Система базується на принципі розділення обов'язків (Separation of Concerns) та оптимізована для роботи в контейнеризованому середовищі:

```mermaid
flowchart LR
    %% -- Global Styles --
    classDef client fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0284c7,rx:10,ry:10
    classDef gateway fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#7c3aed,rx:5,ry:5
    classDef core fill:#dcfce7,stroke:#059669,stroke-width:2px,color:#059669,rx:5,ry:5
    classDef infra fill:#f1f5f9,stroke:#475569,stroke-width:2px,color:#475569,rx:5,ry:5
    classDef external fill:#fce7f3,stroke:#db2777,stroke-width:2px,color:#db2777,rx:5,ry:5

    %% -- 1. ACCESS LAYER --
    subgraph Access ["📡 ACCESS LAYER"]
        direction TB
        User("📱 <b>PWA Dashboard</b><br/>(React-like UI)")
        IoT("⚡ <b>IoT Sensors</b><br/>(Heartbeat Pulse)")
    end

    %% -- 2. NETWORK --
    Tunnel{{"☁️ <b>Cloudflare<br/>Tunnel</b>"}}

    %% -- 3. COMPUTE LAYER (Docker) --
    subgraph Compute ["🚀 COMPUTE CLUSTER"]
        direction TB
        
        subgraph WebNode ["🌐 Web Node (Port 5050)"]
            Gunicorn["🦄 <b>Gunicorn</b><br/>(4x Workers)"]
            Flask["🧪 <b>Flask API</b><br/>(REST / Cache)"]
        end

        subgraph WorkerNode ["⚙️ Worker Node"]
            Monitor["❤️ <b>Health Check</b><br/>(Real-time)"]
            Scheduler["📅 <b>Analytics</b><br/>(Cron Jobs)"]
        end
    end

    %% -- 4. DATA & INTEGRATION --
    subgraph DataMesh ["📦 DATA MESH"]
        direction TB
        JSON[("🗄️ <b>JSON Storage</b><br/>(Persistence)")]
        
        subgraph APIs ["🔗 External APIs"]
            direction LR
            Yasno(⚡ Yasno)
            Meteo(🌡️ Meteo)
            Alerts(📢 Alerts)
        end
    end

    %% -- 5. NOTIFICATION --
    Telegram(("💬 <b>Telegram<br/>Bot API</b>"))

    %% -- FLOWS --
    User <==>|HTTPS/WSS| Tunnel
    IoT -.->|POST /api/push| Tunnel
    
    Tunnel <==> Gunicorn
    Gunicorn <==> Flask
    
    Flask <-->|Read/Write| JSON
    Monitor & Scheduler <-->|Sync| JSON
    
    Flask --o|Fetch Data| APIs
    Monitor --o|Alert| Telegram
    Scheduler --o|Report| Telegram

    %% -- STYLING --
    class User,IoT client
    class Tunnel gateway
    class Gunicorn,Flask,Monitor,Scheduler core
    class JSON,APIs,Yasno,Meteo,Alerts infra
    class Telegram external
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

*   **Backend:** Python 3.11, Flask, Gunicorn (4 воркери для високої продуктивності).
*   **Data Science:** Pandas, Matplotlib (рендер графіків у темній темі).
*   **Containerization:** Docker, Docker Compose (ізоляція даних через volumes).
*   **Infrastructure:** Cloudflare Tunnels (безпечний доступ), Systemd (менеджмент сервісів).

---

## 📜 Ліцензія

Розповсюджується під ліцензією **MIT**. 

<p align="center">
  2026 Розроблено з ❤️ під час блекаутів у Києві.
</p>
