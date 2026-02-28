# 🚀 Flash Monitor Kyiv Installation Guide (v1.10.0)

This project is now fully autonomous. It can either parse schedules itself or synchronize with another server.

## 1. Server Preparation (Ubuntu/Debian)
Install Docker and Docker Compose (if not already installed):
```bash
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose-plugin
```

## 2. File Structure Setup
Create the working directory and required folders:
```bash
mkdir -p flash-monitor/data/static
cd flash-monitor
```

### Create `config.json` configuration file
Example configuration for Kyiv (replace `your_group` with your outage group, e.g., `GPV36.1`):
```json
{
  "settings": {
    "region": "kyiv",
    "groups": ["your_group"],
    "style": "list"
  },
  "sources": {
    "dtek": { "enabled": true },
    "yasno": { "enabled": true, "region_id": "25", "dso_id": "902" }
  }
}
```

### Create `.env` environment file
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
# SCHEDULE_API_URL:
# 1. Leave EMPTY for autonomous mode (server will fetch schedules itself)
# 2. Provide URL (e.g. http://ip:8889) to sync from another server
SCHEDULE_API_URL=
```

## 3. System Launch
Use the `docker-compose.yml` from the repository and start the containers:
```bash
docker compose pull && docker compose up -d
```
The dashboard will be available at port `:5050`.

## 4. Power Monitoring Setup (Heartbeat)
To enable power status and charts, configure your IoT device (ESP8266/ESP32) or another server to send a "pulse":

1. Find your unique secret key (while inside the flash-monitor folder):
   ```bash
   cat data/power_monitor_state.json | grep secret_key
   ```
2. Configure your device to send a GET request every minute:
   `https://your-domain/api/push/YOUR_SECRET_KEY`

---
© 2026 Weby Homelab. Made with ❤️ in Kyiv under air raid sirens and blackouts
