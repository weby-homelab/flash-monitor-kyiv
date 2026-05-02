# Release v3.4.8

**Stability & Visualization Fixes**
В цьому релізі виправлено проблему з відображенням повітряних тривог на графіках та підвищено загальну стабільність фонового процесу.

## Що нового / What's New:
🇺🇦 **Українська:**
- Повернуто яскраво-червоний колір (`#ef4444`) для повітряних тривог на щоденних та тижневих графіках для кращої видимості.
- Впроваджено атомарне блокування (atomic locks) для генерації звітів (`generate_daily_report.py`, `generate_weekly_report.py`, `generate_text_report.py`), щоб усунути стан гонитви (race conditions) та зависання воркера.
- Додано виведення поточного стану при старті з `flush=True` для миттєвого відображення логів сервісу в `journalctl`.

🇬🇧 **English:**
- Reverted the air raid alert color to bright red (`#ef4444`) on daily and weekly charts for better visibility.
- Implemented atomic file locks for report generation processes to prevent race conditions and background worker freezes.
- Added immediate startup state logging (`flush=True`) for better visibility in `journalctl`.
