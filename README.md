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
  <img src="https://img.shields.io/badge/Branch-Classic_(Bare--Metal)-FFD700?style=for-the-badge&logo=linux&logoColor=black" alt="Branch Classic">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# СВІТЛО⚡️ БЕЗПЕКА (FLASH MONITOR KYIV) - Bare-Metal Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** — це професійна автономна система моніторингу критичної інфраструктури та екологічної безпеки. Проєкт забезпевує моніторинг електропостачання в реальному часі, відстеження повітряних тривог, якості повітря (AQI) та радіаційного фону.

Ця гілка (`classic`) містить **Bare-Metal Edition** проєкту, призначену для роботи безпосередньо в системі (наприклад, через `systemd`), без використання Docker.

> **Статус проєкту:** Stable v3.3.0 (Core Refactoring & Fail-Safe Architecture)
> **Архітектура:** Python Flask + Background Workers + JSON Flat-DB + Systemd
> **Бренд:** Weby Homelab

---

## 🛡 Оновлення v3.3.0
*   **Data Access Layer (`storage.py`):** Впроваджено централізований модуль роботи з файловою системою. Усі операції читання/запису тепер атомарні та захищені `asyncio.Lock()` і `fcntl.flock`, що повністю усуває стан гонитви (Race Conditions) та пошкодження JSON-баз.
*   **Notification Service (`telegram_client.py`):** Створено єдиний клієнт для взаємодії з Telegram API з розумною резильєнтністю (автоматичні повторні спроби та відправка нового повідомлення при неможливості редагування старого через таймаути).
*   **Fail-Safe Quiet Mode:** Якщо під час "Інформаційного спокою" зникає зв'язок і адміністратор не відповідає протягом 5 хвилин, система автоматично "ігнорує" збій, щоб унеможливити хибні тривоги в каналі вночі.
*   **Modular State Machine:** Нескінченні цикли розщеплено на незалежні асинхронні блоки з глобальним перехопленням виключень `try...except`, завдяки чому моніторинг ніколи не зупиняється через зовнішні збої.


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
graph TD
    %% -- Styles --
    classDef cloud fill:#2d3436,stroke:#7b1fa2,stroke-width:2px,color:#fff
    classDef local fill:#2d3436,stroke:#1565c0,stroke-width:2px,color:#fff
    classDef service fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff
    classDef security fill:#d63031,stroke:#ff7675,stroke-width:2px,color:#fff
    classDef network fill:#00b894,stroke:#81ecec,stroke-width:2px,color:#fff
    classDef external fill:#f39c12,stroke:#ffeaa7,stroke-width:2px,color:#000

    subgraph EXT ["🌐 Звнішній шар (Access Layer)"]
        direction TB
        WEB[PWA Dashboard]
        TG[Telegram Channel] --- BOT[Telegram Bot API]
    end

    subgraph PROD ["🖥️ Сервер HTZNR (PROD)"]
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

    subgraph Logic ["⚙️ Бізнес-логіка"]
        direction TB
        FN[False Always Wins]
        SN[Safety Net]
        QM[Quiet Mode]
    end

    subgraph SRC ["📡 Зовнішні джерела (API)"]
        direction TB
        YASNO[Yasno API]
        DTEK[GitHub ДТЕК]
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
