<p align="center">
  <a href="INSTRUCTIONS_INSTALL_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="INSTRUCTIONS_INSTALL.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# 🚀 Інструкція зі встановлення Flash Monitor Kyiv [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

Цей проект тепер є повністю автономним. Він може як парсити графіки самостійно, так і синхронізуватися з іншим сервером.

## 1. Підготовка сервера (Ubuntu/Debian)
Встановіть Docker та Docker Compose (якщо ще не встановлено):
```bash
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose-plugin
```

## 2. Налаштування файлової структури
Створіть робочу директорію та завантажте необхідні файли:
```bash
mkdir -p flash-monitor
cd flash-monitor
curl -O https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docker-compose.yml
```

### Створіть файл оточення `.env`
```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_CHANNEL_ID=ід_вашого_каналу
# SCHEDULE_API_URL:
# 1. Залиште ПОРОЖНІМ для автономної роботи (сервер сам качатиме графіки)
# 2. Вкажіть URL (напр. http://ip:8889) для синхронізації з іншим сервером
SCHEDULE_API_URL=
```

## 3. Запуск системи (Smart Bootstrap)
Система автоматично згенерує всі необхідні файли конфігурації при першому запуску:
```bash
docker compose pull && docker compose up -d
```
Після запуску дашборд буде доступний за портом `:5050`. 
Панель керування (Admin Panel) доступна за адресою `/admin`.

## 4. Отримання доступів та налаштування
Після першого запуску система автоматично згенерує унікальні токени для доступу та API.

1. Дізнайтеся ваш `admin_token` (для доступу до панелі керування) та `secret_key` (для пуш-сигналів):
   ```bash
   cat data/power_monitor_state.json | grep token
   cat data/power_monitor_state.json | grep secret_key
   ```
2. Перейдіть до панелі керування за посиланням:
   `https://ваш-домен/admin?t=ВАШ_ADMIN_TOKEN`
3. Усі подальші налаштування (регіон, групи відключень, затримки) робляться **безпосередньо через веб-інтерфейс**.

## 5. Налаштування моніторингу світла (Heartbeat)
Щоб графіки та статус світла почали працювати, вам потрібно налаштувати ваш IoT-пристрій (ESP8266/ESP32, Mikrotik) або інший сервер (напр. Uptime Kuma) на відправку "пульсу".

Налаштуйте ваш пристрій на відправку GET-запиту кожну хвилину:
`https://ваш-домен/api/push/ВАШ_СЕКРЕТНИЙ_КЛЮЧ`

**Додатково (Ручне керування):** 
Починаючи з версії `v1.16.0`, ви можете примусово фіксувати зникнення світла (без очікування тайм-ауту) надіславши GET-запит на:
`https://ваш-домен/api/down/ВАШ_СЕКРЕТНИЙ_КЛЮЧ`

---
✦ 2026 Weby Homelab ✦. Made with ❤️ in Kyiv under air raid sirens and blackouts
