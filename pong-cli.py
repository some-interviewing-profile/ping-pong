from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, FastAPI, Request
import logging
from pydantic_settings import BaseSettings
import requests
import time


logger = logging.getLogger("uvicorn.error")


class Settings(BaseSettings):
    do_initial_ping: bool
    other_endpoint: str
    pong_time_ms: int


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.do_initial_ping:
        ping_server(settings.other_endpoint, 0)
    yield


app = FastAPI(lifespan=lifespan)


def ping_server(endpoint, pong_time_ms):
    logger.info("sleeping for %d ms", pong_time_ms)
    time.sleep(pong_time_ms / 1000)

    logger.info("pinging %s", endpoint)
    requests.get(endpoint)


@app.get("/ping")
async def ping_handler(background_tasks: BackgroundTasks):
    background_tasks.add_task(ping_server, settings.other_endpoint, settings.pong_time_ms)
    return "pong"
