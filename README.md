<p align="center">
  <a href="README_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="README.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# СВІТЛО⚡БЕЗПЕКА [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest) Autonomous Edition

<p align="center">
  <a href="https://github.com/weby-homelab/flash-monitor-kyiv/blob/main/LICENSE"><img src="https://img.shields.io/github/license/weby-homelab/flash-monitor-kyiv" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg?logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Bare_Metal-8B0000?style=flat&logo=linux&logoColor=white" alt="Platform Bare Metal">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/dashboard_preview.jpg" alt="СВІТЛО⚡БЕЗПЕКА Dashboard Preview" width="100%">
</p>

**Автономна Docker-система моніторингу електропостачання та безпеки Києва.**

**Проект забезпечує** повний контроль над енергетичною та безпековою ситуацією, аналізуючи реальні дані мережі та офіційні графіки Yasno/ДТЕК локально.

🔗 **Живий моніторинг:** [flash.srvrs.top](https://flash.srvrs.top/)

📖 **Інструкція:** [Встановлення та налаштування з нуля](INSTRUCTIONS_INSTALL.md)

---

## 🚀 Основні можливості

### 💡 Розумний Енергомоніторинг
- **Heartbeat Tracking:** Моніторинг світла в реальному часі через IoT-сигнали (Push API).
- **Аналітика «План vs Факт»:** Автоматичне порівняння реальних вимкнень із запланованими графіками прямо на дашборді.
- **Точність графіка:** Розрахунок відхилень (запізнення або раннє ввімкнення) для кожної події.
- **Візуалізація:** Генерація денних та тижневих чартів у фірмовому стилі.
- **UI/UX Дизайн:** Тема "Black-and-White" з ефектом Glassmorphism та моноширинними шрифтами для чітких звітів.

### 🛡️ Безпека та Екологія
- **Повітряні тривоги:** Миттєвий статус та сповіщення у Telegram про початок та відбій тривоги в м. Київ.
- **Live-карта:** Інтегрована мапа тривог Києва та області.
- **Якість повітря (AQI):** Моніторинг PM2.5, PM10 та радіаційного фону (локація: Симиренка).
- **Погода:** Актуальна температура, вологість та параметри вітру.

### 🔔 Сповіщення у Telegram
- **Інтелектуальні звіти:** Текстові графіки з вирівнюванням тривалості по правому краю (tabular-nums).
- **Morning Report (06:00):** Повний огляд ситуації на сьогодні та завтра (якщо доступно).
- **Evening/Instant Update:** Автоматичне надсилання завтрашнього графіка одразу після його публікації ДТЕК.
- **Smart Merge:** Коректне об'єднання нічних інтервалів.

---

## 🏗 Архітектура Системи [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

```mermaid
flowchart TD
    %% -- Style Definitions --
    classDef access fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,rx:10,ry:10
    classDef network fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#7b1fa2,rx:5,ry:5
    classDef core fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32,rx:5,ry:5
    classDef data fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100,rx:10,ry:10
    classDef external fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#c2185b,rx:5,ry:5

    %% -- Access Layer --
    subgraph Access ["📡 ACCESS LAYER"]
        IoT["⚡ <b>IoT SENSORS</b><br/>(Heartbeat Pulse)"]
        PWA["📱 <b>PWA DASHBOARD</b><br/>(Interactive UI)"]
    end

    %% -- Network Layer --
    subgraph Network ["☁️ SECURITY MESH"]
        CF[("🔒 <b>CLOUDFLARE TUNNEL</b><br/>(HTTPS / WAF / Domain)")]
    end

    %% -- Core Engine --
    subgraph Core ["🚀 CORE ENGINE (Docker)"]
        direction TB
        WEB["🧪 <b>FLASK SERVER</b><br/>(API & Web Engine)"]
        WORKER["⚙️ <b>BACKGROUND WORKER</b><br/>(Monitor & Scheduler)"]
    end

    %% -- Data Layer --
    subgraph Storage ["📦 PERSISTENCE"]
        JSON[("🗄️ <b>JSON DATA MESH</b><br/>(States / Logs / Cache)")]
    end

    %% -- External Ecosystem --
    subgraph Integration ["🔗 EXTERNAL ECOSYSTEM"]
        direction LR
        TG(("💬 <b>TELEGRAM<br/>BOT API</b>"))
        DTEK["⚡ <b>YASNO / DTEK</b><br/>(Local Parsing)"]
        SAFE["🛡️ <b>SAFETY API</b><br/>(AQI / Alerts)"]
    end

    %% -- Connections --
    IoT -->|Secure Push| CF
    PWA <-->|HTTPS| CF
    CF <-->|Reverse Proxy| WEB
    
    WEB <-->|State Sync| JSON
    WORKER <-->|History Persistence| JSON
    
    WORKER -->|Auto-Report| TG
    WORKER -.->|Direct Sync| DTEK
    WEB -.->|Live Fetch| SAFE

    %% -- Applying Styles --
    class IoT,PWA access
    class CF network
    class WEB,WORKER core
    class JSON storage
    class TG,DTEK,SAFE external
```

---

## 🐳 Швидкий запуск через Docker

**Офіційний образ:** `webyhomelab/flash-monitor-kyiv:latest`

### Docker Compose
```yaml
services:
  web:
    image: webyhomelab/flash-monitor-kyiv:latest
    container_name: flash-monitor-web
    ports: ["5050:5050"]
    volumes: ["./data:/app/data"]
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data

  worker:
    image: webyhomelab/flash-monitor-kyiv:latest
    container_name: flash-monitor-worker
    command: python run_background.py
    volumes: ["./data:/app/data"]
    environment:
      - TELEGRAM_BOT_TOKEN=your_token
      - TELEGRAM_CHANNEL_ID=your_channel_id
      - DATA_DIR=/app/data
```

---

## 💡 Порада для IoT-датчиків (Heartbeat)

Для надсилання Push-сигналів рекомендується використовувати **HTTPS-адресу вашого домену** (наприклад, через Cloudflare Tunnel) замість прямої IP-адреси:

*   **🛡️ Безпека:** HTTPS шифрує ваш секретний ключ під час передачі.
*   **🧩 Гнучкість:** При зміні сервера вам не потрібно перепрошивати датчики — достатньо змінити налаштування тунелю.

**Приклад:** `https://flash.srvrs.top/api/push/ваш_ключ`

---

## 🛠 Технологічний стек
- **Backend:** Python 3.11, Flask, Gunicorn.
- **Analytics:** Matplotlib, BeautifulSoup4.
- **Infra:** Docker, PWA (Progressive Web App).

---

## 🌐 Weby Homelab Ecosystem
[![Flash Monitor Kyiv](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv?label=flash-monitor-kyiv&color=blue&logo=github)](https://github.com/weby-homelab/flash-monitor-kyiv)
[![Light Monitor Kyiv](https://img.shields.io/github/v/release/weby-homelab/light-monitor-kyiv?label=light-monitor-kyiv&color=inactive&logo=github)](https://github.com/weby-homelab/light-monitor-kyiv)
[![Security Monitor Kyiv](https://img.shields.io/github/v/release/weby-homelab/security-monitor-kyiv?label=security-monitor-kyiv&color=inactive&logo=github)](https://github.com/weby-homelab/security-monitor-kyiv)

---

## 📜 Ліцензія
Розповсюджується під ліцензією **MIT**.

<p align="center">
  ✦ 2026 Weby Homelab ✦<br>
  Made with ❤️ in Kyiv under air raid sirens and blackouts
</p>

---

