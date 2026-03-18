# Design Specification: Flash Monitor v2.0 - Quiet Mode and Admin Panel

**Date:** 2026-03-18  
**Topic:** Implementation of Information Quiet Mode and Web Admin Interface  
**Author:** Gemini CLI

---

## 1. Goal
To implement a "Quiet Mode" (Information Silence) for periods of power stability (48h past and 48h future) and a secure web-based admin panel for system state management, configuration editing, and log correction.

---

## 2. Quiet Mode (Information Silence)

### 2.1. Trigger Logic
- **Enter Quiet Mode (Auto):**
  - **Schedule Condition:** Next 48 hours (today + tomorrow) in `last_schedules.json` contain no planned outages (status `on`).
  - **History Condition:** Last 48 hours in `event_log.json` / `schedule_history.json` have no actual `down` events.
- **Exit Quiet Mode (Auto):**
  - **Schedule Change:** Any planned outage (`off` slot) appears in a schedule update.
  - **Actual Outage:** A `down` event is confirmed (see Confirmation Loop).
- **Manual Control:** Admin can force Quiet Mode ON/OFF via the admin panel.

### 2.2. Notifications
- **In Channel:**
  - "🔇 Система перейшла в режим інформаційного спокою (стабільність 48г+)."
  - "🔊 Увага! Виявлено зміни в графіку або фактичні відключення. Режим спокою вимкнено."
- **Critical Alerts:** Air raid alerts (м. Київ) are ALWAYS sent to the channel, regardless of Quiet Mode.

---

## 3. Safety Confirmation Loop

When a timeout (probable power loss) is detected while in Quiet Mode:
1. **Status:** Set `pending_confirmation = true`.
2. **Private Notification:** Send a message to Admin (Chat ID: 6313526220) with Inline Buttons:
   - `🔴 Світло зникло`
   - `🟢 Збій / Роботи`
3. **Wait Logic:** Wait **indefinitely** for the admin to click a button.
4. **Action (🔴):** Log `down` event, send report to public channel, exit Quiet Mode.
5. **Action (🟢):** Ignore event, clear `pending_confirmation`, stay in Quiet Mode.

---

## 4. Admin Panel (admin.srvrs.top)

### 4.1. Access & Security
- **Domain:** `admin.srvrs.top` (Proxy to localhost port 5051).
- **Authentication:** Secret URL token (`/admin?t=SECRET_TOKEN`).
- **Token Management:** Token generated once on setup, stored in `.env` (variable `ADMIN_TOKEN`).

### 4.2. Dashboard Features
- **System Health:** Display status of `Monitoring`, `Alerts`, and `Schedule` workers (uptime, last run time).
- **State Control:** 
  - Toggle `quiet_mode` (Auto/Forced Silence/Forced Active).
  - Confirm/Deny pending outages.
- **Config Editor:**
  - Form to edit `groups`, `region_id`, `dso_id`, `lat`, `lon` in `config.json`.
  - Save button triggers internal reload.
- **Service Management:** Buttons to trigger `systemctl restart flash-monitor.service` and `flash-background.service`.
- **Log Editor:**
  - View last 20 events from `event_log.json`.
  - Add new `up`/`down` event with custom timestamp.
  - Delete existing events.

---

## 5. Technical Implementation (Approach 1: Hybrid State Manager)

### 5.1. Data Layer
- Extend `power_monitor_state.json`:
  ```json
  {
    "quiet_mode": "auto",
    "quiet_status": "quiet",
    "pending_confirmation": false,
    "stability_start": 1773811666,
    "admin_token": "sk_adm_..."
  }
  ```

### 5.2. Service Updates
- `light_service.py`: Update `monitor_loop` and `schedule_loop` to handle Quiet Mode logic and Admin confirmation requests.
- `app.py`: Add `/admin` blueprint/routes for the web interface and API.

### 5.3. Frontend
- Single-page application (SPA) style admin panel integrated into Flask.
- Modern "Black-and-White" Glassmorphism UI (project standard).

---

## 6. Testing Strategy
- **Unit Tests:** Verify Quiet Mode trigger logic with mock schedules and history.
- **Integration Tests:** Mock Telegram Bot API to verify private messages and callback queries.
- **Manual Verification:** Test `admin.srvrs.top` access and state changes.
