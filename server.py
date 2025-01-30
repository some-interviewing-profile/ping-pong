from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from pydantic_settings import BaseSettings
import requests


logger = logging.getLogger("uvicorn.error")


class Settings(BaseSettings):
    do_initial_ping: bool
    other_endpoint: str
    pong_time_ms: int


settings = Settings()


scheduler = AsyncIOScheduler()
delay = timedelta()


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler.start()
    if settings.do_initial_ping:
        ping_server(settings.other_endpoint)
    yield


app = FastAPI(lifespan=lifespan)


def ping_server(endpoint):
    logger.info("pinging %s", endpoint)
    requests.get(endpoint)


@app.get("/ping")
async def ping_handler():
    seconds = settings.pong_time_ms / 1000
    date = datetime.now() + timedelta(seconds=seconds)
    logger.info("waiting for %d seconds before pinging back, scheduled for %s", seconds, date)
    scheduler.add_job(ping_server, args=[settings.other_endpoint], run_date=date, id="ping")
    return "pong"


@app.post("/pause")
async def pause_handler():
    job = scheduler.get_job("ping")
    if job is not None and job.next_run_time is not None:
        global delay
        delay = job.trigger.get_next_fire_time(None, None) - datetime.now(timezone.utc)
        logger.info("when unpaused, ping back will be delayed by %s", delay)
        job.pause()

@app.post("/resume")
async def resume_handler():
    job = scheduler.get_job("ping")
    if job is not None and job.next_run_time is None:
        date = datetime.now() + delay
        logger.info("rescheduling ping back to %s, delayed by %s", date, delay)
        job.reschedule("date", run_date=date)
        job.resume()
