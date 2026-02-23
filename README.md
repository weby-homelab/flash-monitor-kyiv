# СВІТЛО⚡БЕЗПЕКА (v1.2 Classic — Bare-Metal Edition)

<p align="center">
  <img src="https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/classic/dashboard_preview.jpg" alt="СВІТЛО⚡БЕЗПЕКА Dashboard Preview" width="100%">
</p>

**Автономна bare-metal система моніторингу електропостачання та безпеки Києва.**

Гілка **Classic** розроблена спеціально для прямого встановлення на Linux-сервер. Це надійна реалізація, яка працює як системний сервіс та забезпечує повний контроль над даними.

🔗 **Живий моніторинг:** [flash.srvrs.top](https://flash.srvrs.top/)

---

## 🚀 Основні можливості

### 💡 Розумний Енергомоніторинг
- **Heartbeat Tracking:** Відстеження світла в реальному часі через IoT-сигнали (Push API).
- **Аналітика «План vs Факт»:** Автоматичне порівняння реальних вимкнень із запланованими графіками.
- **Точність графіка:** Розрахунок відхилень (запізнення/раннє ввімкнення) для кожної події.
- **Візуалізація:** Генерація денних та тижневих чартів у темній темі.

### 🛡️ Безпека та Екологія
- **Повітряні тривоги:** Миттєвий статус та інтегрована live-карта Києва.
- **Якість повітря (AQI):** Рівень PM2.5, PM10 та радіаційний фон.

---

## 🏗 Архітектура Системи (v1.2 Classic)

```mermaid
flowchart TD
    %% -- Style Definitions --
    classDef access fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,rx:10,ry:10
    classDef network fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#7b1fa2,rx:5,ry:5
    classDef core fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#616161,rx:5,ry:5
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
    subgraph Core ["🚀 CORE ENGINE (Bare-Metal)"]
        direction TB
        WEB["🧪 <b>SYSTEMD: FLASK</b><br/>(API & Web Engine)"]
        WORKER["⚙️ <b>SYSTEMD: WORKER</b><br/>(Monitor & Scheduler)"]
    end

    %% -- Data Layer --
    subgraph Storage ["📦 PERSISTENCE"]
        JSON[("🗄️ <b>JSON DATA MESH</b><br/>(Local Files)")]
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

## 💡 Порада для IoT-датчиків (Heartbeat)

Для надсилання Push-сигналів рекомендується використовувати **HTTPS-адресу вашого домену** (наприклад, через Cloudflare Tunnel) замість прямої IP-адреси:

*   **🛡️ Безпека:** HTTPS шифрує ваш секретний ключ під час передачі.
*   **🧩 Гнучкість:** При зміні сервера вам не потрібно перепрошивати датчики — достатньо змінити налаштування тунелю.

**Приклад:** `https://flash.srvrs.top/api/push/ваш_ключ`

---

## 📦 Встановлення та запуск (Bare-Metal)

### 1. Клонування та налаштування:
```bash
git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
cd flash-monitor-kyiv
git checkout classic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Налаштування середовища:
Створіть файл `.env`:
```env
TELEGRAM_BOT_TOKEN=ваш_токен
TELEGRAM_CHANNEL_ID=ваш_id_каналу
DATA_DIR=.
```

---

## 📜 Ліцензія
Розповсюджується під ліцензією **MIT**.

<p align="center">
  ✦ 2026 WEBy Home Lab ✦<br>
  <i>Автоматизуй усе, що робиш двічі. Монітор усе, що має значення.</i>
</p>
