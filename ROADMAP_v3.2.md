# 🗺 Дорожня карта v3.2: Від Синхронності до Реактивності

## Етап 1: Фундамент (The Core & Logging)
**Ціль:** Створити асинхронне середовище та систему моніторингу.
1. **Міграція на FastAPI:** Заміна Flask на FastAPI + Uvicorn.
2. **Lifespan Management:** Впровадження asynccontextmanager для керування життєвим циклом фонових задач (заміна @app.on_event).
3. **Structured Logging:** Інтеграція structlog. Перехід від текстових логів до JSON-формату для легкого аналізу в Loki/Grafana.
4. **Health Check:** Створення ендпоінту /health для Docker-демона.

## Етап 2: Робота з даними та Стан (Async I/O & Models)
**Ціль:** Прибрати мікро-фризи при роботі з диском та типізувати дані.
1. **Pydantic v2 Models:** Створення схем для config.json, state.json та last_schedules.json. Це дасть миттєву валідацію та швидкий парсинг.
2. **Async File I/O:** Заміна всіх стандартних open() на aiofiles для читання/запису стану та логів подій.
3. **Centralized Cache:** Впровадження cachetools.TTLCache для різних типів даних (Power: 30s, Air Quality: 10m, Radiation: 15m).

## Етап 3: Двигун оновлень (The Async Parser)
**Ціль:** Паралелізація запитів та захист від падінь API.
1. **HTTPX Integration:** Перехід на httpx.AsyncClient з використанням Connection Pooling.
2. **Parallel Fetching:** Використання asyncio.gather для одночасного опитування Yasno, GitHub та Weather API.
3. **Circuit Breaker (v3.2.0):** Реалізація станів CLOSED, OPEN, HALF-OPEN для Yasno API. Захист системи від тайм-аутів при падінні зовнішніх серверів.
4. **Graceful Degradation:** Логіка повернення Stale-даних (старих графіків), якщо всі джерела недоступні.

## Етап 4: Реальний час (SSE & Communication)
**Ціль:** Економія батареї клієнтів та миттєві сповіщення.
1. **SSE Endpoint:** Створення /status/stream для PWA.
2. **Initial Burst Pattern:** Негайне відправлення поточного стану при підключенні нового клієнта.
3. **Memory Safety Subscribers:** Використання asyncio.Queue з put_nowait та очищенням «зомбі-підписників» через request.is_disconnected().
4. **Broadcast Logic:** Створення механізму «штовхання» оновлень всім клієнтам у момент зміни статусу (up/down).

## Етап 5: Фронтенд та PWA (Survival UI)
**Ціль:** Адаптація інтерфейсу до нових можливостей бекенду.
1. **SSE Client:** Заміна setInterval() на EventSource у JS.
2. **Source Metadata:** Відображення в UI статусу джерела даних (наприклад, плашка «⚠️ Дані з GitHub (Yasno лежить)»).
3. **E-Tag Support:** Налаштування HTTP-кешування для статичних ресурсів та JSON-статусів для економії 4G-трафіку (304 Not Modified).

## Етап 6: Деплой та Верифікація (Production Hardening)
**Ціль:** Безпечний запуск на HTZNR.
1. **Docker Alpine Update:** Оптимізація Dockerfile під асинхронний стек (мінімізація шарів).
2. **Zero-Tolerance Protocol:** Ручний контроль кожного кроку через git status та pytest.
3. **Prometheus Metrics:** Додавання інструментарію для Grafana (тривалість парсингу, кількість активних SSE-сесій).
