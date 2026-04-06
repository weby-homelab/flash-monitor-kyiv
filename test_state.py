import asyncio
from light_service import state as l_state, load_state

async def main():
    print(f"Initial: {l_state.get('status')}")
    await load_state()
    print(f"After load: {l_state.get('status')}")

asyncio.run(main())