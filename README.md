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

**Flash Monitor Kyiv** — це професійна автономна система моніторингу критичної інфраструктури та екологічної безпеки. Проєкт забезпечує моніторинг електропостачання в реальному часі, відстеження повітряних тривог, якості повітря (AQI) та радіаційного фону.

Ця гілка (`main`) містить **Docker Edition** проєкту, призначену для швидкого, портативного та ізольованого розгортання в будь-якому середовищі. Якщо вам потрібна інсталяція безпосередньо в систему через `systemd`, використовуйте гілку `classic` (Bare-Metal).

> **Статус проєкту:** Stable v3.2.3 (Security Patch, Silent Alerts & Stability)
> **Архітектура:** Python FastAPI + Background Workers + JSON Flat-DB + Docker / Docker Compose
> **Бренд:** Weby Homelab

---

## 🛡 Оновлення v3.2.3
*   **Безпека (LFI/SSRF Fix):** Закрито критичні вразливості Path Traversal для статичних файлів та SSRF для `custom_url` (обмеження протоколами HTTP/HTTPS).
*   **Захист від Timing Attacks:** API доступу (`push_api`, `down_api`, `admin_data`) тепер використовують безпечну перевірку ключів через `secrets.compare_digest()`.
*   **Виправлення стану гонитви (Race Conditions):** Застосовано безпечні транзакційні `async with state_mgr:` для обробки конкурентних запитів від Telegram Webhook та API.
*   **Витік пам'яті у SSE:** З'єднання для `/api/status/stream` більше не залишають "зомбі-підключень" у фоновому режимі (Memory Leak).
*   **Виправлення конфігурації тривог:** Сповіщення про тривоги за замовчуванням тепер вимкнено в JSON, а парсинг булевих значень виправлено.

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
    subgraph Access ["📱 Access Layer"]
        direction LR
        PWA["PWA Web Dashboard"]:::external
        ADM["Admin Control Panel"]:::external
        IoT["Ping Scripts / Sensors"]:::external
    end

    %% -- Security Perimeter --
    subgraph Security ["🛡️ Security Perimeter"]
        direction TB
        CF(("Cloudflare Tunnel WAF")):::security
    end

    %% -- Core Application (Docker) --
    subgraph Core ["🐳 Core Engine (Docker Edition)"]
        direction TB
        WEB["FastAPI Async Server (Uvicorn)"]:::service
        WORKER["Background Worker (Threads)"]:::service
        CACHE[("Async TTL Cache")]:::network
        JSON[("JSON Data Mesh (Volume)")]:::local
    end

    %% -- External APIs --
    subgraph API ["🔗 External Ecosystem"]
        direction TB
        TG(("Telegram API")):::external
        YASNO["YASNO/DTEK Schedules"]:::external
        WEATHER["OpenMeteo / SaveEcoBot"]:::external
    end

    %% -- Relationships --
    IoT -->|Heartbeat Push 30s| CF
    PWA <-->|Secure HTTPS| CF
    ADM <-->|Token Auth| CF

    CF <-->|Reverse Proxy| WEB
    
    WEB <-->|Read/Write| CACHE
    WEB <-->|Persist| JSON
    
    WORKER <-->|Persist| JSON
    WORKER -->|Alerts| TG
    WORKER -.->|Fetch Data| YASNO
    WORKER -.->|Fetch Data| WEATHER

    %% Layout adjustments
    CF ~~~ WEB
    JSON ~~~ TG
```

---

## 🛠 Технічний стек (Docker Edition)
- **Backend:** Python 3.12, **FastAPI**, Uvicorn (Асинхронний стек).
- **Analytics:** Matplotlib, BeautifulSoup4.
- **Infra:** Docker, Docker Compose.

### 💡 Чому FastAPI та Асинхронність? (Еволюція гілки Main)
В основі архітектури проєкту лежить **JSON Data Mesh** (використання плоских файлів замість SQL). У Docker-контейнерах одночасний доступ до цих файлів з боку Web-сервера та Background-воркера спричиняв I/O-блокування (Deadlocks). 
Тому гілка `main` була повністю переписана з Flask на **FastAPI**:
1. Впроваджено `asyncio.to_thread` — тепер запис файлів не блокує Event Loop, що забезпечує миттєву відповідь API навіть під час високих навантажень.
2. Дані кешуються в **Async TTL Cache** (RAM), мінімізуючи звернення до диска контейнера.
3. Додано сувору типізацію через **Pydantic Models**, що унеможливлює пошкодження JSON-файлів під час збоїв живлення сервера.
*(Для розгортання на "голому залізі" (Bare-Metal), де блокуваннями I/O ефективніше керує Systemd + Gunicorn, використовується синхронна гілка `classic`).*

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

### Швидкий старт (Smart Bootstrap):
Система автоматично ініціалізується при першому запуску:
1.  Генерує унікальні `SECRET_KEY` та `ADMIN_TOKEN`.
2.  Створює структуру папок у `/app/data` (змонтовано в Docker Volume) з дефолтними налаштуваннями v3.
3.  Завантажує актуальні графіки для вашої групи.

---

## 🤝 Контакти та розробка
Розробка ведеться **Weby Homelab**. Всі зміни вносяться згідно з **"Протоколом нульової толерантності до регресій"**.

© 2026 Weby Homelab.
