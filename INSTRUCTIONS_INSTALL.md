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
Створіть робочу директорію та необхідні файли:
```bash
mkdir -p flash-monitor/data/static
cd flash-monitor
```

### Створіть файл конфігурації `config.json`
Приклад конфігурації для Києва (вказавши свою групу, наприклад `GPV36.1`):
```json
{
  "settings": {
    "region": "kyiv",
    "groups": ["ваша_група"],
    "style": "list"
  },
  "sources": {
    "dtek": { "enabled": true },
    "yasno": { "enabled": true, "region_id": "25", "dso_id": "902" }
  }
}
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

## 3. Запуск системи
Використовуйте `docker-compose.yml` з репозиторію та запустіть контейнери:
```bash
docker compose pull && docker compose up -d
```
Після запуску дашборд буде доступний за портом `:5050`.

## 4. Налаштування моніторингу світла (Heartbeat)
Щоб графіки та статус світла почали працювати, вам потрібно налаштувати ваш IoT-пристрій (ESP8266/ESP32) або інший сервер на відправку "пульсу":

1. Дізнайтеся ваш секретний ключ (перебуваючи в папці flash-monitor):
   ```bash
   cat data/power_monitor_state.json | grep secret_key
   ```
2. Налаштуйте ваш пристрій на відправку GET-запиту кожну хвилину:
   `https://ваш-домен/api/push/ВАШ_СЕКРЕТНИЙ_КЛЮЧ`

---
✦ 2026 Weby Homelab ✦. Made with ❤️ in Kyiv under air raid sirens and blackouts
