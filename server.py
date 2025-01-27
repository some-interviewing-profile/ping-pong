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


paused = False
should_ping = False


def ping_server(endpoint, pong_time_ms):
    global paused, should_ping
    if paused:
        logger.info("paused")
        should_ping = True
        return

    logger.info("sleeping for %d ms", pong_time_ms)
    time.sleep(pong_time_ms / 1000)

    logger.info("pinging %s", endpoint)
    requests.get(endpoint)


@app.get("/ping")
async def ping_handler(background_tasks: BackgroundTasks):
    background_tasks.add_task(ping_server, settings.other_endpoint, settings.pong_time_ms)
    return "pong"


@app.post("/pause")
async def pause_handler():
    global paused
    paused = True


@app.post("/resume")
async def resume_handler(background_tasks: BackgroundTasks):
    global paused, should_ping
    if paused:
        paused = False
        if should_ping:
            should_ping = False
            background_tasks.add_task(ping_server, settings.other_endpoint, settings.pong_time_ms)
