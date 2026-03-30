import asyncio

# Запуск ініціалізації для нових користувачів
import bootstrap
bootstrap.perform_cold_start_if_needed()

from light_service import monitor_loop, schedule_loop, alerts_loop, load_state

async def main():
    print("Starting Flash Monitor Background Services (Async)...")
    await load_state()
    
    # Run all loops concurrently
    await asyncio.gather(
        monitor_loop(),
        alerts_loop(),
        schedule_loop()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
