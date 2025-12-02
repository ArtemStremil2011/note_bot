from bot import TgBot
import asyncio
import signal
import sys

from config import TOKEN


async def main():
    try:
        print("Bot was started")
        bot = TgBot(TOKEN)
        await bot.start_bot()
    except KeyboardInterrupt:
        print("Bot was stopped gracefully")
    except Exception as e:
        print(f"Unexpected error: {e}")


def signal_handler(sig, frame):
    print("\nReceived interrupt signal. Shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot was stopped completely")