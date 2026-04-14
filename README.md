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
  <img src="https://img.shields.io/badge/Branch-main_(Docker)-2496ed?style=for-the-badge&logo=docker&logoColor=white" alt="Branch Main">
  <img src="https://img.shields.io/docker/v/webyhomelab/flash-monitor-kyiv?style=for-the-badge&logo=docker&logoColor=white&label=Docker%20Hub" alt="Docker Hub Version">
  <img src="https://img.shields.io/docker/pulls/webyhomelab/flash-monitor-kyiv?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Pulls">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docs/assets/dashboard_preview.jpg" alt="Dashboard Preview" width="100%">
</p>

# СВІТЛО⚡️ БЕЗПЕКА (FLASH MONITOR KYIV) - Docker Edition [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

**Flash Monitor Kyiv** — це професійна автономна система моніторингу критичної інфраструктури та екологічної безпеки. Проєкт забезпечує прецизійний моніторинг електропостачання в реальному часі, інтелектуальну обробку графіків відключень (DTEK/Yasno), відстеження повітряних тривог, якості повітря (AQI) та радіаційного фону.

Ця гілка (`main`) містить **Docker Edition** проєкту — максимально ізольовану версію, оптимізовану для швидкого розгортання в будь-якому оточенні.

> **Статус проєкту:** Stable v3.4.0 (Docker Optimized)
> **Архітектура:** FastAPI (Asynchronous) + Background Workers + Docker Compose + JSON Flat-DB
> **Бренд:** Weby Homelab

---

## 🛠 Технологічний стек (Docker Edition)
- **Runtime:** Python 3.12 (slim-bookworm) у контейнері.
- **Web-Core:** FastAPI з підтримкою асинхронних WebSockets та Server-Sent Events (SSE).
- **Backend-Logic:** Модульна архітектура з розподілом обов'язків між API та фоновими процесами (Light Service).
- **Data Persistence:** Docker Volumes для збереження стану (`data/`), конфігурацій та історії без ризику втрати даних при оновленні контейнера.
- **CI/CD:** Автоматична збірка для архітектур `linux/amd64` та `linux/arm64` (Raspberry Pi, Apple Silicon, Server).

---

## 🚀 Ключові інновації та алгоритми

### 🎛 Панель Керування (Admin Panel)
Повністю автономний веб-інтерфейс у стилі **Glassmorphism** для керування всіма аспектами системи без необхідності редагування конфігураційних файлів через SSH.
<p align="center">
  <img src="docs/assets/Admin-control-panel-1.png" alt="Admin Panel 1" width="32%">
  <img src="docs/assets/Admin-control-panel-2.png" alt="Admin Panel 2" width="32%">
  <img src="docs/assets/Admin-control-panel-3.png" alt="Admin Panel 3" width="32%">
</p>

*   **Асинхронна швидкодія:** Новий асинхронний кеш унеможливлює дедлоки та "зависання" при одночасному записі даних фоновими воркерами та зверненнях користувачів.
*   **Інтелектуальні бекапи:** Створення ручних та автоматичних точок відновлення конфігурації. Миттєве відновлення системи в один клік з автоматичним рестартом внутрішніх служб контейнера.
*   **Гнучке налаштування джерел:** Зміна пріоритету між Yasno, GitHub або підключення власного Custom JSON URL. Кнопка примусової синхронізації графіків з миттєвим оновленням Telegram-звітів.
*   **Повна Гео-адаптація:** Налаштування координат (Lat/Lon) для точної локальної погоди, ID станції SaveEcoBot та вибіркове керування відображенням віджетів.
*   **Безпека (Zero-Trust):** Впроваджено строгу валідацію шляхів (Path Traversal Protection) та безпечну генерацію Access Keys при першому старті.

### 🤫 Режим «Інформаційний спокій» (Quiet Mode)
Унікальний алгоритм, що мінімізує "інформаційний шум" у стабільні періоди. Система автоматично переходить у стан спокою, якщо за останні 24 години не було відключень, а в отриманих планах на наступну добу немає жодних обмежень. Це позбавляє канал непотрібних щоденних звітів, коли енергосистема працює без збоїв.

### 🚨 Safety Net (Мережа безпеки)
Інтерактивний механізм швидкого реагування на втрату зв'язку з пристроєм моніторингу. Якщо затримка вхідного Push-сигналу перевищує 35 секунд, адміністратор отримує запит у Telegram з інтерактивними кнопками (`🔴 Світло зникло`, `🛠 Технічний збій`, `🤷‍♂️ Не знаю`). Це запобігає публікації хибних алертів у публічному каналі при проблемах з інтернет-з'єднанням.

### ⚖️ Логіка «False Always Wins»
Гібридна система обробки графіків відключень. Якщо хоча б одне з джерел (Yasno або GitHub-mirror) вказує на ймовірне відключення, система відображає його як пріоритетне. Старі записи про реальні відключення ніколи не затираються новими "чистими" планами, що забезпечує 100% чесну історію подій у базі даних.

---

## 📱 Приклади реальних сповіщень у Telegram

*   📊 **[Щоденний графік "План vs Факт" (Smart Daily Report)](https://t.me/svitlobot_Symyrenka22B/1230)** — інтелектуальна візуалізація збігів графіка з реальністю.
*   📈 **[Тижнева аналітика відключень](https://t.me/svitlobot_Symyrenka22B/1192)** — автоматична агрегація даних про тривалість та частоту відключень.
*   🔴 **[Сповіщення про відключення світла](https://t.me/svitlobot_Symyrenka22B/1209)** — миттєві алерти з точністю до графіка.
*   🟢 **[Сповіщення про увімкнення світла](https://t.me/svitlobot_Symyrenka22B/1212)** — підтвердження подачі напруги.
*   ⚠️ **[Миттєвий алерт про зміну графіків](https://t.me/svitlobot_Symyrenka22B/1222)** — сповіщення при виявленні змін у базах ДТЕК.
*   🚨 **[Сповіщення про повітряну тривогу](https://t.me/svitlobot_Symyrenka22B/1196)** — інтеграція з офіційними джерелами.

---

## 📊 Можливості дашборду (PWA)

Сучасний інтерфейс у стилі **Glassmorphism**, оптимізований для мобільних пристроїв:
*   **Live Status:** Візуалізація "Пульсу" системи (Світло Є! / Світло зникло!).
*   **Екологічний моніторинг:** Температура, вологість, PM2.5/PM10 (OpenMeteo/SaveEcoBot) та радіаційний фон з інтерактивними графіками.
*   **Графік-бар:** Компактна 24-годинна шкала планових відключень для швидкого планування дня.

---

## 🏗️ Архітектура системи

```mermaid
flowchart LR
    %% ================================================
    %% НОВА КОНЦЕПЦІЯ 2026 для README.md
    %% "End-to-End Pipeline" — динамічний потік даних
    %% Замість шарів — горизонтальний pipeline з чітким напрямком руху
    %% Ідеально виглядає в GitHub (темна/світла тема), чистий, сучасний, легко читається
    %% ================================================

    classDef external fill:#0f766e,stroke:#14b8a6,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef core fill:#1e293b,stroke:#22d3ee,stroke-width:3.5px,color:#fff,rx:14px,ry:14px
    classDef gateway fill:#7c3aed,stroke:#a78bfa,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef client fill:#1e293b,stroke:#60a5fa,stroke-width:3px,color:#fff,rx:16px,ry:16px
    classDef db fill:#1e293b,stroke:#ec4899,stroke-width:3px,color:#fff,rx:12px,ry:12px

    %% ====================== ЛІВА ЧАСТИНА: ДЖЕРЕЛА ДАНИХ ======================
    subgraph External ["🔌 Джерела даних"]
        direction TB
        Energy["⚡ Yasno / DTEK API<br>Розклади відключень"]:::external
        Meteo["🌤️ OpenMeteo + SaveEcoBot<br>Погода та AQI"]:::external
    end

    %% ====================== ЦЕНТР: CORE PIPELINE ======================
    subgraph Core ["⚙️ Flash Monitor Core<br>light_service.py + FastAPI"]
        direction TB

        Worker["🔄 Worker<br>flash-background.service"]:::core

        subgraph Processing ["Обробка та логіка"]
            direction LR
            Rules["🛡️ Rules Engine<br>False Always Wins • 30s Safety Net<br>Quiet Mode"]:::core
            Reports["📊 Reports Generator<br>Matplotlib charts"]:::core
            Storage["💾 Storage<br>JSON Flat-DB<br>config • state • logs • schedules"]:::db
        end

        API["🔌 FastAPI<br>flash-monitor.service<br>app.py"]:::core
        TgClient["🤖 Telegram Client"]:::core
    end

    %% ====================== ШЛЮЗ ======================
    subgraph Gateway ["🔐 Cloudflare Tunnel<br>Zero Trust + Reverse Proxy"]
        CF["☁️ Cloudflare Tunnel<br>порт 5050"]:::gateway
    end

    %% ====================== ПРАВА ЧАСТИНА: КЛІЄНТИ ======================
    subgraph Clients ["👥 Інтерфейси користувачів"]
        direction TB
        PWA["📱 PWA Dashboard"]:::client
        Admin["🛠️ Admin Panel"]:::client
        Telegram["📨 Telegram Channel<br>+ Push Notifications"]:::client
    end

    %% ====================== ПОТІК ДАНИХ (головна магістраль) ======================
    Energy & Meteo -->|Скрэйпінг + Fetch| Worker

    Worker -->|Перевірка правил| Rules
    Rules -->|Рішення| Worker

    Worker -->|Збереження| Storage
    Storage -->|Читання стану| Worker

    Worker -->|Генерація| Reports
    Worker -->|Сповіщення| TgClient
    Reports -->|Графіки| TgClient

    Worker <-->|REST + WebSocket| API

    API -->|Reverse Proxy| CF
    CF <-->|HTTPS + JWT / WSS| PWA
    CF <-->|HTTPS + JWT| Admin
    TgClient -->|Bot API| Telegram

    %% Додаткові push-сповіщення
    API -.->|Web Push API| PWA

    %% ====================== Стиль для заголовків підграфів ======================
    classDef subgraphTitle fill:#0f172a,stroke:none,color:#64748b,font-size:15px
```

---

## 📥 Швидкий старт (Docker)

1. **Завантажте конфігурацію:**
```bash
curl -O https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docker-compose.yml
```

2. **Запустіть контейнери:**
```bash
docker-compose up -d
```

3. **Верифікація:**
Система стане доступною за адресою `http://localhost:5050`. Первинний пароль адміністратора буде згенеровано в логах при першому старті.

📖 **Документація:**
* [Детальна інструкція Docker](docs/INSTRUCTIONS_INSTALL.md)
* [Історія змін (CHANGELOG.md)](docs/CHANGELOG.md)

---
**✦ 2026 Weby Homelab ✦**
