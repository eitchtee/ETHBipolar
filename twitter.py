import asyncio

from twikit import Client
from config import USERNAME, PASSWORD, EMAIL

LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(LOOP)

CLIENT = Client("pt-BR")


def start():
    return LOOP.run_until_complete(
        CLIENT.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
    )


def run_async_twittar(msg):
    return LOOP.run_until_complete(twittar(msg))


def cleanup():
    LOOP.close()


async def twittar(msg: str):
    await CLIENT.create_tweet(text=msg)
