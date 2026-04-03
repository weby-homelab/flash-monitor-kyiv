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

> **Статус проєкту:** Stable v3.2.4 (Reliability & Resilience Update)
> **Архітектура:** Python Flask + Background Workers + JSON Flat-DB + Systemd
> **Бренд:** Weby Homelab

---

## 🛡 Оновлення v3.2.4
*   **Auto-Confirmation (Safety Net):** Автоматичне підтвердження відключення через 5 хвилин, якщо адмін не відповів на запит. Це запобігає "зависанню" системи в стані очікування під час Quiet Mode.
*   **Resilient Updates:** Якщо повідомлення в Telegram було видалене вручну, бот автоматично надішле нове замість спроби редагування старого.
*   **Quiet Mode Cleanup:** При переході в режим "Інформаційний спокій" бот автоматично видаляє активні графіки з каналу. При появі нових планів з відключеннями — миттєво "прокидається" в Active Mode.
*   **UI Consistency:** Джерело даних `Github` тепер відображається в Telegram як `ДТЕК` для зручності користувачів.

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

    %% -- External & Access Layer --
    TG[Telegram Channel] --- BOT[Telegram Bot API]
    WEB[PWA Dashboard] --- API[FastAPI /app.py]
    
    subgraph "HTZNR (PROD / Bare-Metal)"
        direction TB
        SVC[flash-monitor.service]
        BG[flash-background.service]
        
        API --- SVC
        BG --- LMN[light_service.py]
        
        subgraph "Data Layer (JSON Flat-DB)"
            STATE[(power_monitor_state.json)]
            CFG[(config.json)]
            LOGS[(event_log.json)]
            SCHED[(last_schedules.json)]
        end
        
        LMN --- STATE
        LMN --- LOGS
        LMN --- SCHED
        SVC --- CFG
        SVC --- STATE
    end

    %% -- External Sources --
    YASNO[Yasno API] -.-> LMN
    DTEK[GitHub DTEK] -.-> LMN
    METEO[OpenMeteo] -.-> SVC
    AQI[SaveEcoBot] -.-> SVC

    %% -- Application Logic --
    LMN --- FN[False Always Wins]
    LMN --- SN[Safety Net]
    LMN --- QM[Quiet Mode]

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
