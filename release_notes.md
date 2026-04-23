# Release v3.4.3

**Fixed Auto and Forced On Quiet Modes**
В цьому релізі виправлено критичну помилку логіки Режиму Тиші.

## Що нового / What's New:
🇺🇦 **Українська:**
- Виправлено логіку режиму **"Завжди ТИХО" (Forced On)**: Тепер система дійсно зберігає мовчання і не надсилає публічні сповіщення при зникненні пушів, навіть після 5-хвилинного очікування підтвердження.
- Виправлено логіку режиму **"Автоматично" (Auto)**: Якщо планових вимкнень немає, система коректно утримує тишу після зникнення світла, скасовуючи хибні тривоги по тайм-ауту.
- Оптимізовано прибирання повідомлень в Telegram під час роботи режиму тиші.

🇬🇧 **English:**
- Fixed the logic for **"Forced On"** Quiet Mode: The system now truly remains silent and does not send public outage notifications, even after the 5-minute admin confirmation timeout.
- Fixed the logic for **"Auto"** Quiet Mode: If there are no scheduled outages, the system correctly maintains silence after a power loss, cancelling false alarms instead of posting them after the timeout.
- Optimized the cleanup of Telegram messages during Quiet Mode finalization.
