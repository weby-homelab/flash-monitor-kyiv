import os
import json
import time
from datetime import datetime
import subprocess
import shutil

# Отримуємо директорії
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(APP_DIR, "data"))

def perform_cold_start_if_needed():
    event_file = os.path.join(DATA_DIR, "event_log.json")
    sched_file = os.path.join(DATA_DIR, "last_schedules.json")
    history_file = os.path.join(DATA_DIR, "schedule_history.json")
    config_file = os.path.join(DATA_DIR, "config.json")

    # Якщо дані вже є, це не перший старт
    if os.path.exists(event_file) and os.path.exists(sched_file):
        return

    # Захист від гонки (race condition) при одночасному старті кількох контейнерів
    lock_file = os.path.join(DATA_DIR, ".bootstrap.lock")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(lock_file):
        print("⏳ Ініціалізація вже виконується іншим процесом. Очікуємо...")
        for _ in range(30):
            time.sleep(1)
            if os.path.exists(event_file) and os.path.exists(sched_file):
                return
        print("⚠️ Тайм-аут очікування ініціалізації. Продовжуємо...")

    try:
        with open(lock_file, "w") as f:
            f.write("locked")
    except Exception:
        pass

    print("🚀 Виявлено новий запуск (Cold Start)! Ініціалізація бази даних для поточного регіону...")
    
    # Створюємо потрібні папки
    os.makedirs(os.path.join(DATA_DIR, "static"), exist_ok=True)

    # 1. Перевіряємо/Копіюємо config.json, якщо його немає
    if not os.path.exists(config_file):
        default_config = os.path.join(APP_DIR, "config.json")
        if os.path.exists(default_config):
            shutil.copy2(default_config, config_file)
            print("✅ Базовий config.json скопійовано.")
        else:
            print("❌ Базовий config.json не знайдено!")
            return

    # 2. Створюємо точку відліку (світло є прямо зараз)
    if not os.path.exists(event_file):
        now_ts = time.time()
        # Для сумісності з часовою зоною Києва, як у всьому проєкті
        from zoneinfo import ZoneInfo
        now_dt = datetime.fromtimestamp(now_ts, tz=ZoneInfo("Europe/Kyiv"))
        
        start_event = [{
            "timestamp": now_ts,
            "event": "up",
            "date_str": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "note": "Initial Startup"
        }]
        with open(event_file, "w") as f:
            json.dump(start_event, f, indent=2)
        print("✅ event_log.json ініціалізовано.")

    # 3. Створюємо порожню історію графіків
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            json.dump({}, f)
        print("✅ schedule_history.json ініціалізовано.")

    # 4. Примусово завантажуємо планові графіки на зараз
    if not os.path.exists(sched_file):
        try:
            from parser_service import update_local_schedules
            print("⏳ Завантаження планових графіків згідно з config.json...")
            update_local_schedules(config_file, sched_file)
            print("✅ last_schedules.json успішно згенеровано!")
        except Exception as e:
            print(f"❌ Помилка завантаження першого графіку: {e}")
            # Створюємо пустий файл, щоб не блокувати подальшу роботу
            with open(sched_file, "w") as f:
                json.dump({}, f)

    # 5. Примусово генеруємо картинки та статистику
    print("🎨 Генерація перших дашбордів...")
    try:
        subprocess.run(["python3", "generate_daily_report.py", "--no-send"], cwd=APP_DIR, check=True)
        subprocess.run(["python3", "generate_weekly_report.py", "--no-send"], cwd=APP_DIR, check=True)
        print("✅ Дашборди успішно згенеровано.")
    except Exception as e:
        print(f"❌ Помилка генерації перших дашбордів: {e}")

    try:
        os.remove(lock_file)
    except Exception:
        pass

    print("🎉 Ініціалізація (Smart Bootstrap) завершена!")

if __name__ == "__main__":
    perform_cold_start_if_needed()
