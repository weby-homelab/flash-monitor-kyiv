<p align="center">
  <a href="INSTRUCTIONS_INSTALL_ENG.md">
    <img src="https://img.shields.io/badge/🇬🇧_English-00D4FF?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="INSTRUCTIONS_INSTALL.md">
    <img src="https://img.shields.io/badge/🇺🇦_Українська-FF4D00?style=for-the-badge&logo=readme&logoColor=white" alt="Українська версія">
  </a>
</p>

<br>

# 🛠 Flash Monitor Kyiv Installation Guide (Bare-Metal Edition) [![Latest Release](https://img.shields.io/github/v/release/weby-homelab/flash-monitor-kyiv)](https://github.com/weby-homelab/flash-monitor-kyiv/releases/latest)

This guide is intended for the installation of the stable Bare-Metal version (branch `classic`) directly on a server running **Ubuntu 24.04 LTS** (or Debian 12) using **Systemd**.

## 📌 Version & Stack
- **Version:** v3.2.2 (Classic)
- **Language:** Python 3.12+
- **Framework:** Flask + Gunicorn (Synchronous Stack)
- **Database:** JSON Flat-DB (File system)
- **Process Management:** Systemd

---

## 1. Server Preparation
Ensure your server is up to date and has Python 3.12 installed:
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.12 python3.12-venv python3-pip git nano
```

## 2. Cloning & Installation
```bash
# Navigate to the folder where the project will live (e.g., /opt or /root)
cd /opt
git clone https://github.com/weby-homelab/flash-monitor-kyiv.git
cd flash-monitor-kyiv

# IMPORTANT: Switch to the classic branch
git checkout classic

# Create and activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Environment Configuration
Create a `.env` file based on the example:
```bash
cp .env.example .env
nano .env
```
Minimum required parameters:
- `TELEGRAM_BOT_TOKEN` — Get it from @BotFather
- `TELEGRAM_CHANNEL_ID` — Your channel ID (starts with -100)

## 4. Autostart Configuration (Systemd)
Create two configuration files for the services. Replace `/opt/flash-monitor-kyiv` with your actual path.

### A) Dashboard Service (Web Interface)
Create the file `/etc/systemd/system/flash-monitor.service`:
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

### B) Background Service (Background Processes)
Create the file `/etc/systemd/system/flash-background.service`:
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

## 5. Activation & Verification
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now flash-monitor.service flash-background.service

# Check statuses
systemctl status flash-monitor.service
systemctl status flash-background.service
```

---

## 🔑 Getting Admin Access
After the first launch, the system automatically generates access tokens.
1. Find your `admin_token`:
   ```bash
   cat data/power_monitor_state.json | grep admin_token
   ```
2. Open the admin panel in your browser:
   `http://YOUR_SERVER_IP:5050/admin?t=YOUR_TOKEN`

---
✦ 2026 Weby Homelab ✦ — infrastructure that works in any conditions.
