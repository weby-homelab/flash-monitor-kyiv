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

**Flash Monitor Kyiv** — це професійна автономна система моніторингу критичної інфраструктури та екологічної безпеки. Проєкт забезпевує моніторинг електропостачання в реальному часі, відстеження повітряних тривог, якості повітря (AQI) та радіаційного фону.

Ця гілка (`main`) містить **Docker Edition** проєкту, призначену для швидкого розгортання через Docker Compose.

> **Статус проєкту:** Stable v3.3.3 (Smart Anti-Spam & Core Refactoring)
> **Архітектура:** Python FastAPI + Background Workers + JSON Flat-DB + Docker / Docker Compose
> **Бренд:** Weby Homelab

---

## 🛡 Оновлення v3.3.3 (Smart Anti-Spam)
*   **Розумний Анти-Спам (Smart Anti-Spam):** Усунено зайве дублювання графічних щоденних звітів ("Моніторинг" та "Звіт") в "Активному Режимі" у дні, коли світло є стабільно всі 24 години і вже було опубліковане текстове привітання «Світла смуга триває». При виникненні бодай найменшого реального відключення графік відразу ж публікується в канал.
*   **Живе оновлення в Тихому Режимі:** Якщо активується Тихий Режим, щоденний звіт тепер продовжить оновлювати «лінію факту» на вже існуючому повідомленні, а не зависне.
*   **Data Access Layer (`storage.py`):** Впроваджено централізований модуль роботи з файловою системою. Усі операції читання/запису тепер атомарні та захищені `asyncio.Lock()` і `fcntl.flock`, що повністю усуває стан гонитви (Race Conditions) та пошкодження JSON-баз.
*   **Notification Service (`telegram_client.py`):** Створено єдиний клієнт для взаємодії з Telegram API з розумною резильєнтністю (автоматичні повторні спроби та відправка нового повідомлення при неможливості редагування старого через таймаути).
*   **Fail-Safe Quiet Mode:** Якщо під час "Інформаційного спокою" зникає зв'язок і адміністратор не відповідає протягом 5 хвилин, система автоматично "ігнорує" збій, щоб унеможливити хибні тривоги в каналі вночі.
*   **Modular State Machine:** Нескінченні цикли розщеплено на незалежні асинхронні blocks з глобальним перехопленням виключень `try...except`, завдяки чому моніторинг ніколи не зупиняється через зовнішні збої.


## 🚀 Ключові інновації (v3.2+)

### 🎛 Панель Керування (Admin Panel)
Повністю автономний веб-інтерфейс у стилі Glassmorphism для керування всіма аспектами системи без необхідності редагування конфігураційних файлів через SSH.

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Асинхронна швидкодія:** Новий асинхронний кеш (FastAPI) унеможливлює дедлоки та "зависання" при одночасному записі даних різними фоновими воркерами.
*   **Інтелектуальні бекапи:** Створення ручних та автоматичних точок відновлення конфігурації. Миттєве відновлення системи в один клік з авто-рестартом служб.
*   **Гнучке налаштування джерел:** Зміна пріоритету між Yasno, GitHub або підключення власного Custom JSON URL. Кнопка примусової синхронізації графіків.
*   **Повна Гео-адаптація:** Налаштування координат (Lat/Lon) для точної погоди, ID станції SaveEcoBot та керування відображенням віджетів.
*   **Безпека (Zero-Trust):** Усунуто LFI (Path Traversal) вразливості, забезпечено строгу перевірку шляхів до файлів. Ключі доступу генеруються безпечно при першому старті.

### 🤫 Режим «Інформаційний спокій» (Quiet Mode)
Унікальний алгоритм, що мінімізує "інформаційний шум". Система автоматично переходить у стан спокою, якщо за останні 24 години не було відключень, а в планах на завтра немає обмежень.

### 🚨 Safety Net (Мережа безпеки)
Інтерактивний механізм швидкого реагування: при затримці сигналу (Push) понад 35 секунд адміністратор отримує запит у Telegram з варіантами дій (`🔴 Світло зникло`, `🛠 Технічний збій`, `🤷‍♂️ Не знаю`).

### ⚖️ Логіка «False Always Wins»
Гібридна система обробки графіків. Якщо хоча б одне джерело вказує на відключення, система відображає його як пріоритетне. Старі записи про відключення ніколи не затираються "чистими" планами.

---

## 📱 Приклади реальних сповіщень у Telegram

*   📊 **[Щоденний графік "План vs Факт" (Smart Daily Report)](https://t.me/svitlobot_Symyrenka22B/1230)**
*   📈 **[Тижнева аналітика відключень](https://t.me/svitlobot_Symyrenka22B/1192)**
*   🔴 **[Сповіщення про відключення світла з точністю до графіка](https://t.me/svitlobot_Symyrenka22B/1209)**
*   🟢 **[Сповіщення про увімкнення світла з точністю до графіка](https://t.me/svitlobot_Symyrenka22B/1212)**
*   ⚠️ **[Миттєвий алерт про зміну графіків від ДТЕК](https://t.me/svitlobot_Symyrenka22B/1222)**
*   🚨 **[Сповіщення про повітряну тривогу в місті](https://t.me/svitlobot_Symyrenka22B/1196)**

---

## 📊 Можливості дашборду (PWA)

Сучасний інтерфейс у стилі **Glassmorphism**, оптимізований для мобільних пристроїв:
*   **Live Status:** Візуалізація "Пульсу" системи (Світло Є! / Світло зникло!).
*   **Екологічний моніторинг:** Температура, вологість, PM2.5/PM10 (OpenMeteo/SaveEcoBot) та радіація з інтерактивними графіками за 24 години.
*   **Графік-бар:** Компактна 24-годинна шкала планових відключень.

---

## 🏗 Архітектура Системи

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

    subgraph TopLayer ["🌐 Інтерфейси доступу"]
        direction LR
        PWA["📱 PWA Dashboard"]:::client
        Admin["🔐 Admin Panel"]:::client
        Subscribers["📢 Telegram Channel"]:::client
    end

    CF["🌩️ Cloudflare Tunnel (Zero Trust)"]:::cloudflare

    PWA <-->|HTTPS / WSS| CF
    Admin <-->|HTTPS / JWT| CF

    subgraph CoreLayer ["🖥️ Серверне Ядро (Docker / systemd)"]
        direction TB

        subgraph Services ["⚙️ Системні Служби"]
            direction LR
            API["⚡ flash-monitor.service<br/>(FastAPI / app.py)"]:::server
            Worker["🔍 flash-background.service<br/>(light_service.py)"]:::server
        end

        subgraph Modules ["🛠 Внутрішні Модулі та Логіка"]
            direction LR
            Storage["storage.py<br/>(I/O Manager)"]:::module
            Reports["generate_*_report.py<br/>(Matplotlib)"]:::module
            TgClient["telegram_client.py<br/>(Bot Wrapper)"]:::module
            Rules["🧠 Алгоритми:<br/>• False Always Wins<br/>• Safety Net (30s)<br/>• Quiet Mode"]:::logic
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

    subgraph DataLayer ["💾 Сховище Даних (JSON Flat-DB)"]
        direction LR
        Config[("config.json")]:::db
        State[("power_monitor_state.json")]:::db
        Logs[("event_log.json")]:::db
        Sched[("last_schedules.json")]:::db
    end

    Storage <-->|Читання / Запис| DataLayer

    subgraph ExternalLayer ["📡 Зовнішні API та Шлюзи"]
        direction LR
        PushAPI["🔔 Web Push API"]:::ext_api
        TgAPI["🤖 Telegram Bot API"]:::ext_api
        Energy["⚡ Yasno / DTEK API"]:::ext_api
        Meteo["🌤 OpenMeteo / SaveEcoBot"]:::ext_api
    end

    API -->|Тригер пушів| PushAPI
    PushAPI -.->|Сповіщення| PWA
    
    TgClient -->|Відправка| TgAPI
    TgAPI -->|Пости & Графіки| Subscribers
    
    Energy -->|Парсинг розкладів| Worker
    Meteo -->|Запит погоди| API
    Meteo -->|AQI моніторинг| Worker
```

---

## 📥 Встановлення та розгортання

Проєкт має дві основні гілки:

1.  **`main` (Docker Edition):** Рекомендовано для швидкого старту.
    ```bash
    # 1. Завантажте docker-compose.yml
    curl -O https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docker-compose.yml

    # 2. Запустіть систему (образи автоматично стягнуться з Docker Hub)
    docker-compose up -d
    ```
2.  **`classic` (Bare-Metal Edition):** Для роботи безпосередньо в системі через `systemd`.

📖 **Повні інструкції:**
*   [Інструкція зі встановлення (Installation Guide)](INSTRUCTIONS_INSTALL.md)
*   [Детальне налаштування та конфігурація](INSTRUCTIONS.md)
*   [Правила розробки (Development Rules)](DEVELOPMENT.md)

---
**✦ 2026 Weby Homelab ✦**
