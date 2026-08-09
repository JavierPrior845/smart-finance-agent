import asyncio
from src.infrastructure.adapters.db.session import AsyncSessionLocal
from src.infrastructure.adapters.db.repositories.analytics_repository import AnalyticsRepository

async def main():
    async with AsyncSessionLocal() as session:
        repo = AnalyticsRepository(session)
        try:
            res = await repo.get_networth_history(months=6)
            print(res)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
