<p align="center">
  <a href="INSTRUCTIONS_INSTALL_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="INSTRUCTIONS_INSTALL.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# 🚀 Flash Monitor Kyiv Installation Guide [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

This project is now fully autonomous. It can either parse schedules itself or synchronize with another server.

## 1. Server Preparation (Ubuntu/Debian)
Install Docker and Docker Compose (if not already installed):
```bash
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose-plugin
```

## 2. File Structure Setup
Create the working directory and download the required files:
```bash
mkdir -p flash-monitor
cd flash-monitor
curl -O https://raw.githubusercontent.com/weby-homelab/flash-monitor-kyiv/main/docker-compose.yml
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

## 3. System Launch (Smart Bootstrap)
The system will automatically generate all necessary configuration files on the first launch:
```bash
docker compose pull && docker compose up -d
```
The dashboard will be available at port `:5050`.
The Admin Control Panel is available at `/admin`.

## 4. Access and Configuration
After the first launch, the system will automatically generate unique tokens for access and the API.

1. Find your `admin_token` (for Admin Panel access) and `secret_key` (for push signals):
   ```bash
   cat data/power_monitor_state.json | grep token
   cat data/power_monitor_state.json | grep secret_key
   ```
2. Go to the Admin Panel using the link:
   `https://your-domain/admin?t=YOUR_ADMIN_TOKEN`
3. All further settings (region, outage groups, delays) are made **directly through the web interface**.

## 5. Power Monitoring Setup (Heartbeat)
To enable power status and charts, configure your IoT device (ESP8266/ESP32, Mikrotik) or another server (e.g., Uptime Kuma) to send a "pulse".

Configure your device to send a GET request every minute:
`https://your-domain/api/push/YOUR_SECRET_KEY`

**Additional (Manual Override):**
Starting with version `v1.16.0`, you can manually trigger a power outage event (without waiting for a timeout) by sending a GET request to:
`https://your-domain/api/down/YOUR_SECRET_KEY`

---
✦ 2026 Weby Homelab ✦. Made with ❤️ in Kyiv under air raid sirens and blackouts
