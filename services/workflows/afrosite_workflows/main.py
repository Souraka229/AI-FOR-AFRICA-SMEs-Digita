import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("afrosite_workflows")


async def main() -> None:
    logger.info("Afrosite Temporal Worker service initialisé.")
    # Placeholder for Temporal worker initialization


if __name__ == "__main__":
    asyncio.run(main())
