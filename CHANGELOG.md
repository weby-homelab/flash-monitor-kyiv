# Changelog / Історія змін (Bilingual/Двомовний)

## [v3.3.6] - 2026-04-07
- **QA & Test Coverage:** Суттєво розширено базу тестів (з 9 до 37). / Significantly expanded test coverage.
- **Анти-спам та Стабільність:** Виправлено баг "холодного старту". / Fixed "cold start" bug.
- **Оптимізація Telegram API:** Інтелектуальна обробка "message is not modified". / Intelligent handling of Telegram errors.
- **Redirect Тестів:** Сповіщення під час "pytest" перенаправлені в приватний чат адміністратора. / Redirected test notifications to admin chat.

## [v3.3.5] - 2026-04-06
- **Дедуплікація Звітів:** Усунуто стан гонитви (race condition). / Resolved race condition.
- **Механізм Блокування:** Впроваджено файлові блокування ".lock" (cooldown 15s). / Added file locking mechanism.
- **Оптимізація Ресурсів:** Поділ логіки генерації щоденних та тижневих звітів. / Optimized report generation.

## [v3.3.4] - 2026-04-05
- **Manual Override Bypass:** Виправлено поведінку ручних команд. / Fixed manual override behavior.
- **Safety Net UI Persistence:** Збільшено таймаут кнопок адмін-панелі до 180 секунд. / Increased admin panel button timeout.
- **Smart Source Logic:** Виправлено відображення джерел на дашборді. / Fixed dashboard source label logic.

## [v3.3.3] - 2026-04-04
- **Smart Anti-Spam:** Розумне дублювання графіків у Telegram. / Implemented smart anti-spam for reports.
- **Data Access Layer:** Атомарні операції з JSON-базами (SafeStateContextAsync). / Atomic operations for JSON database.
- **Notification Service:** Резильєнтний клієнт Telegram. / Resilient Telegram client.
- **Modular State Machine:** Повна асинхронність моніторингу. / Fully asynchronous monitoring.

## [v3.2.0 - v3.3.2]
- Міграція на FastAPI, впровадження Pydantic-моделей, асинхронне I/O, Web Admin Panel (Glassmorphism), інфраструктурні зміни. / Migration to FastAPI, async I/O, Glassmorphism Web UI.
