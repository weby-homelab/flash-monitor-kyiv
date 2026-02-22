# СВІТЛО⚡БЕЗПЕКА

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="СВІТЛО⚡БЕЗПЕКА Dashboard Preview" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Release-v1.0.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Framework-white?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge" alt="Status">
</p>

---

**СВІТЛО⚡БЕЗПЕКА** — це уніфікована інтелектуальна екосистема для моніторингу енергопостачання та безпекової ситуації в Києві. Проєкт поєднує в собі heartbeat-моніторинг електромережі, аналітику відповідності графікам відключень, систему раннього сповіщення про тривоги та екологічний моніторинг.

🔗 **Живий дашборд:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Ключові Особливості

### 💡 Розумний Енергомоніторинг
- **Reliable Heartbeat:** Обробка сигналів від IoT-пристроїв на порту `5050` з підтримкою високого навантаження.
- **Accuracy Tracking:** Автоматичний розрахунок точності відключень/включень відносно офіційних графіків у хвилинах.
- **Event Timeline:** Детальна історія подій з підрахунком тривалості кожного періоду.

### 🛡️ Безпека та AQI (Борщагівка)
- **Air Alerts:** Моніторинг статусу повітряних тривог (Київ/Область) з інтегрованою живою картою.
- **Ecological Monitor:** Дані в реальному часі про AQI, PM2.5, PM10, температуру та вологість (локація: Симиренка).
- **Radiation Background:** Постійний контроль радіаційного фону (мкЗв/год).

### 🔔 Інтелектуальні Telegram-звіти
- **Live Graphic Report:** Денний графік «План vs Факт», що оновлюється кожні 10 хвилин у тому самому повідомленні.
- **Smart Text Schedules:** Текстові розклади (Yasno/DTEK) оновлюються кожні 30 хвилин у період з 06:00 до 22:30. Повідомлення редагується лише за наявності реальних змін у даних.
- **Instant Alerts:** Миттєві текстові сповіщення про зміну статусу мережі з аналізом наступних подій за графіком.

---

## 🏗 Архітектура Системи

Система базується на принципі розділення обов'язків (Separation of Concerns) для забезпечення максимальної стабільності:

```mermaid
flowchart TD
    %% -- Style Definitions --
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b
    classDef core fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#616161
    classDef logic fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32
    classDef external fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#c2185b
    classDef storage fill:#efebe9,stroke:#4e342e,stroke-width:2px,color:#4e342e
    classDef notify fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#5e35b1

    %% -- Nodes --
    subgraph Clients ["🌐 User Interface"]
        User("📱 PWA Dashboard<br/>(Auto-refresh 60s)")
        IoT("⚡ IoT Device<br/>(Push every 30s)")
    end

    subgraph WebService ["🚀 Flask Web App (Port 5050)"]
        API["🖥️ API Gateway<br/>(4 Workers / High-Load Ready)"]
        Cache["💾 Thread-Safe Cache<br/>(TTL 60s)"]
    end

    subgraph BackendService ["⚙️ Background Engine"]
        Monitor["📡 Monitor Loop<br/>(Outage Detection)"]
        Scheduler["📅 Task Scheduler<br/>(10m Graphic / 30m Text)"]
    end

    subgraph Infrastructure ["📦 Data & Notify"]
        JSON[("🗄️ Storage<br/>(State/History/IDs)")]
        Telegram("💬 Telegram API")
    end

    %% -- Connections --
    User <-->|GET| API
    IoT -->|Push| API
    API --- Cache
    API <-->|Read/Write| JSON
    Monitor <-->|State Sync| JSON
    Scheduler -->|Read History| JSON
    Monitor & Scheduler -->|Notify| Telegram
    
    class User,IoT client
    class API,Cache core
    class Monitor,Scheduler logic
    class JSON storage
    class Telegram notify
```

---

## 🛠 Технологічний Стек

*   **Runtime:** Python 3.10+
*   **Web Server:** Flask, Gunicorn (Multi-worker configuration)
*   **Graphics:** Matplotlib (Custom dark-theme renders)
*   **PWA:** Service Worker v4 (Aggressive caching with force-update)
*   **Security:** Systemd isolation, Cloudflare Tunneling

---

## ⚙️ Розгортання (Deployment)

1. **Системні сервіси:**
   Проєкт потребує запуску двох незалежних сервісів:
   - `flash-monitor.service`: Обробка HTTP-запитів та Dashboard.
   - `flash-background.service`: Моніторинг та оновлення звітів.

2. **Налаштування `.env`:**
   ```env
   TELEGRAM_BOT_TOKEN="bot_token"
   TELEGRAM_CHANNEL_ID="channel_id"
   ```

3. **Запуск:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

---

## 📜 Ліцензія

Розповсюджується під ліцензією **MIT**. 

<p align="center">
  2026 Розроблено з ❤️ під час блекаутів у Києві.
</p>
