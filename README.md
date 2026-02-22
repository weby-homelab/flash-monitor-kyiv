# ⚡️ Flash Monitor Kyiv

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.2.1-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Framework-white?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge" alt="Status">
</p>

---

**Flash Monitor Kyiv** — це інтелектуальна система моніторингу енергосистеми та безпекової ситуації в Києві. Проєкт автоматизує збір даних про відключення світла, повітряні тривоги та екологічний стан, об'єднуючи їх у єдиний PWA-додаток та розумний Telegram-канал.

🔗 **Живий моніторинг:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Ключові Особливості

### 💡 Енергомоніторинг 2.0
- **Heartbeat-технологія:** Відстеження наявності світла в реальному часі через систему пінгування.
- **Розумні звіти:** Автоматичне порівняння фактичних відключень з офіційними графіками (Yasno/DTEK).
- **Аналіз точності:** Розрахунок відхилень у хвилинах («Світло зникло на 5 хв раніше графіка»).

### 🛡️ Безпека та Екологія
- **Air Alert:** Миттєвий статус тривог для Києва та області з інтегрованою картою.
- **AQI Monitor:** Моніторинг якості повітря (PM2.5, PM10) та радіаційного фону.
- **Weather Insights:** Актуальна температура, вологість та напрямок вітру.

### 🔔 Smart Notifications
- **Live Reports:** Telegram-повідомлення, що оновлюються динамічно протягом дня (одне повідомлення — повна історія доби).
- **Visual Analytics:** Генерація денних та тижневих графіків «План vs Факт».

---

## 🛠 Технологічний Стек

*   **Backend:** Python 3, Flask, Gunicorn.
*   **Data Processing:** Pandas, Matplotlib, BeautifulSoup4.
*   **Frontend:** HTML5, CSS3 (Vanilla CSS), JavaScript.
*   **DevOps:** Systemd, Nftables (Port Redirection), Cloudflare Tunnels.

---

## 🏗 Архітектура Системи

Система побудована на мікросервісній ідеології, де кожен компонент виконує свою задачу. Взаємодія між ними показана на діаграмі нижче:

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
    subgraph Clients ["🌐 Рівень Клієнтів"]
        User("📱 PWA Веб-додаток<br/>(Dashboard)")
        IoT("⚡ IoT Пристрій<br/>(Heartbeat)")
    end

    subgraph Backend ["🚀 Центральний Backend (Port 5050)"]
        direction TB
        API("🖥️ Flask API Gateway<br/>(Request Handling)")
        Monitor("⚙️ Power Monitor Loop<br/>(Health Checks)")
        Scheduler("📅 Task Scheduler<br/>(Periodic Reports)")
    end

    subgraph DataSources ["📡 Зовнішні Джерела Даних"]
        Yasno("⚡ Yasno/DTEK API<br/>(Schedules)")
        OpenMeteo("🌡️ Open-Meteo API<br/>(Weather & AQI)")
        Alerts("📢 alerts.in.ua API<br/>(Air Alerts)")
    end

    subgraph Infrastructure ["📦 Інфраструктура"]
        JSON[("🗄️ JSON Storage<br/>(State & History)")]
        Telegram("💬 Telegram API<br/>(Smart Updates)")
    end

    %% -- Connections --
    User <-->|AJAX Requests| API
    IoT -->|Port 8889 -> NAT -> 5050| API
    
    API <-->|Sync Data| Yasno
    API <-->|Fetch AQI| OpenMeteo
    API <-->|Alert Status| Alerts

    API <-->|Persistence| JSON
    Monitor <-->|Sync State| JSON
    Scheduler -->|Read History| JSON

    Monitor -->|Smart Notify| Telegram
    Scheduler -->|Update Charts| Telegram

    %% -- Applying Classes --
    class User,IoT client
    class API core
    class Monitor,Scheduler logic
    class Yasno,OpenMeteo,Alerts external
    class JSON storage
    class Telegram notify
```

---

## ⚙️ Швидкий Старт

1. **Клонування та налаштування:**
   ```bash
   git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
   cd flash-monitor-kyiv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Налаштування `.env`:**
   ```env
   TELEGRAM_BOT_TOKEN="your_bot_token"
   TELEGRAM_CHANNEL_ID="your_test_channel_id"
   ```

3. **Запуск:**
   ```bash
   ./start.sh
   ```

---

## 📜 Ліцензія

Цей проєкт розповсюджується під ліцензією **MIT**. Ви можете вільно використовувати, копіювати та модифікувати код.

<p align="center">
  ✦ 2026 WEBy Home Lab ✦
</p>
