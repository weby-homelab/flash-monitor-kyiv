<p align="center">
  <a href="INSTRUCTIONS_INSTALL_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="INSTRUCTIONS_INSTALL.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# 🛠 Інструкція зі встановлення Flash Monitor Kyiv (Bare-Metal Edition) [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

Ця інструкція призначена для встановлення стабільної Bare-Metal версії (гілка `classic`) безпосередньо на сервер під керуванням **Ubuntu 24.04 LTS** (або Debian 12) за допомогою **Systemd**.

## 📌 Версія та Стек
- **Версія:** v3.4.0 (Stable)
- **Мова:** Python 3.12+
- **Фреймворк:** FastAPI + Gunicorn (Uvicorn Workers)
- **База даних:** JSON Flat-DB (File system)
- **Керування процесами:** Systemd

---

## 1. Підготовка сервера
Переконайтеся, що ваш сервер оновлений та має встановлений Python 3.12:
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.12 python3.12-venv python3-pip git nano
```

## 2. Клонування та встановлення
```bash
# Перейдіть у папку, де буде жити проект (напр. /opt або /root)
cd /opt
git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
cd flash-monitor-kyiv

# ВАЖЛИВО: Перейдіть на гілку classic
git checkout classic

# Створення та активація віртуального середовища
python3.12 -m venv venv
source venv/bin/activate

# Встановлення залежностей
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Конфігурація середовища
Створіть файл `.env` на основі прикладу:
```bash
cp .env.example .env
nano .env
```
Мінімально необхідні параметри:
- `TELEGRAM_BOT_TOKEN` — Отримайте у @BotFather
- `TELEGRAM_CHANNEL_ID` — ID вашого каналу (починається з -100)

## 4. Налаштування автозапуску (Systemd)
Створіть два конфігураційні файли для служб. Замініть `/opt/flash-monitor-kyiv` на ваш фактичний шлях.

### А) Служба Dashboard (Веб-інтерфейс)
Створіть файл `/etc/systemd/system/flash-monitor.service`:
```ini
[Unit]
Description=Flash Monitor Kyiv Dashboard
After=network.target

[Service]
User=root
WorkingDirectory=/opt/flash-monitor-kyiv
EnvironmentFile=/opt/flash-monitor-kyiv/.env
ExecStart=/opt/flash-monitor-kyiv/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker --workers 4 -b 0.0.0.0:5050 app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Б) Служба Background (Фонові процеси)
Створіть файл `/etc/systemd/system/flash-background.service`:
```ini
[Unit]
Description=Flash Monitor Kyiv Background Services
After=network.target

[Service]
User=root
WorkingDirectory=/opt/flash-monitor-kyiv
EnvironmentFile=/opt/flash-monitor-kyiv/.env
ExecStart=/opt/flash-monitor-kyiv/venv/bin/python -m app.run_background
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 5. Активація та Перевірка
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now flash-monitor.service flash-background.service

# Перевірка статусів
systemctl status flash-monitor.service
systemctl status flash-background.service
```

---

## 🔑 Отримання доступу до Адмінки
Після першого запуску система автоматично згенерує токени доступу.
1. Дізнайтеся ваш `admin_token`:
   ```bash
   cat data/power_monitor_state.json | grep admin_token
   ```
2. Відкрийте адмінку в браузері:
   `http://IP_ВАШОГО_СЕРВЕРА:5050/admin?t=ВАШ_ТОКЕН`

---
✦ 2026 Weby Homelab ✦ — інфраструктура, що працює в будь-яких умовах.
