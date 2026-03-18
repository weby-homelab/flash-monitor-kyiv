# Flash Monitor v2.0 - Quiet Mode and Admin Panel Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement "Quiet Mode" (Information Silence) for periods of power stability and a secure web-based admin panel for system management.

**Architecture:** Hybrid State Manager (Approach 1). Extend `power_monitor_state.json` with quiet-mode flags, update `light_service.py` with trigger logic and Telegram confirmation loop, and add `/admin` routes to `app.py`.

**Tech Stack:** Python (Flask), Telegram Bot API (Inline Buttons), HTML/CSS (Glassmorphism), JavaScript (Fetch API).

---

### Task 1: State Extension and Quiet Mode Calculation

**Files:**
- Modify: `flash-monitor-kyiv/light_service.py`
- Test: `flash-monitor-kyiv/tests/test_quiet_logic.py`

- [ ] **Step 1: Define new state fields and constant values**
- [ ] **Step 2: Implement `check_quiet_mode_eligibility()` function**
  - Logic: Check `schedule_history` (past 48h) and `last_schedules` (today + tomorrow).
- [ ] **Step 3: Update `schedule_loop()` to recalculate quiet mode status every 10 mins**
- [ ] **Step 4: Write tests for `check_quiet_mode_eligibility`**
- [ ] **Step 5: Run tests and commit**

---

### Task 2: Telegram Confirmation Loop (Safety Net)

**Files:**
- Modify: `flash-monitor-kyiv/light_service.py`
- Modify: `flash-monitor-kyiv/app.py` (callback handler)

- [ ] **Step 1: Implement `send_admin_confirmation(event_type, timestamp)`**
  - Uses `ADMIN_CHAT_ID` and Inline Buttons.
- [ ] **Step 2: Update `monitor_loop()` to trigger confirmation instead of public alert if in Quiet Mode**
- [ ] **Step 3: Implement Flask route `/api/admin/callback` to handle Telegram button clicks**
  - Handle "Confirm Outage" (🔴) and "Ignore/Glitch" (🟢).
- [ ] **Step 4: Test confirmation flow with mock requests**
- [ ] **Step 5: Commit**

---

### Task 3: Admin Panel - Foundation and Auth

**Files:**
- Modify: `flash-monitor-kyiv/app.py`
- Create: `flash-monitor-kyiv/templates/admin.html`
- Modify: `flash-monitor-kyiv/.env` (add `ADMIN_TOKEN`)

- [ ] **Step 1: Add `ADMIN_TOKEN` generation to `bootstrap.py` or `load_state`**
- [ ] **Step 2: Create `/admin` route in `app.py` with token verification**
- [ ] **Step 3: Create basic `admin.html` template with Glassmorphism style**
- [ ] **Step 4: Verify access via `http://localhost:5050/admin?t=TOKEN`**
- [ ] **Step 5: Commit**

---

### Task 4: Admin Panel - Core Functions (Config & Logs)

**Files:**
- Modify: `flash-monitor-kyiv/app.py` (API endpoints)
- Modify: `flash-monitor-kyiv/templates/admin.html` (UI)

- [ ] **Step 1: Implement API `GET /api/admin/config` and `POST /api/admin/config`**
- [ ] **Step 2: Implement Log Editor UI (Add/Delete events)**
- [ ] **Step 3: Implement Service Management API (Restart via systemctl)**
  - Note: Requires `sudo` permissions for the user running the script or a helper script.
- [ ] **Step 4: Final integration testing of all Admin Panel features**
- [ ] **Step 5: Commit**

---

### Task 5: Finalization and Deployment

- [ ] **Step 1: Update README.md with Admin Panel instructions**
- [ ] **Step 2: Clean up temporary files**
- [ ] **Step 3: Final full-system verification**
- [ ] **Step 4: Tag version v2.0.0 and commit**
