from datetime import datetime, timedelta, timezone

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import json
from fastapi import FastAPI
import logging
from pydantic_settings import BaseSettings
import requests
import socket


logger = logging.getLogger("uvicorn.error")


class Settings(BaseSettings):
    do_initial_ping: bool
    other_endpoint: str
    pong_time_ms: int


settings = Settings(do_initial_ping=False, other_endpoint="")


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
    logger.info(
        "waiting for %d seconds before pinging back, scheduled for %s", seconds, date
    )
    scheduler.add_job(
        ping_server, args=[settings.other_endpoint], run_date=date, id="ping", misfire_grace_time=None
    )
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


CONFIGFILE = "config.json"


def main():
    try:
        with open(CONFIGFILE) as f:
            config = json.load(f)
            port1 = config["port1"]
            port2 = config["port2"]
            logger.info("running on port %d", port2)
            settings.do_initial_ping = True
            settings.other_endpoint = f"http://localhost:{port1}/ping"
            uvicorn.run(app, port=port2)
            return
    except Exception as e:
        logger.error("failed to read config file: %s", e)

    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.bind(("localhost", 0))
    port1 = s1.getsockname()[1]

    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s2.bind(("localhost", 0))

    port2 = s2.getsockname()[1]
    with open(CONFIGFILE, "w") as f:
        json.dump({
            "port1": port1,
            "port2": port2,
        }, f)
    settings.other_endpoint = f"http://localhost:{port2}/ping"

    logger.info("running on port %d", port1)
    uvicorn.run(app, fd=s1.fileno())


if __name__ == "__main__":
    main()
