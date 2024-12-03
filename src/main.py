"""
This project is designed for the Inkplate 10 display. However, since the server code is only generating an image, it can
be easily adapted to other display sizes and resolution by adjusting the config settings, HTML template and
CSS stylesheet. This code is heavily adapted from my other project (MagInkCal) so do take a look at it if you're keen.
As a dashboard, there are many other things that could be displayed, and it can be done as long as you are able to
retrieve the information. So feel free to change up the code and amend it to your needs.
"""

import datetime
import os
import tempfile
import time
from datetime import datetime as dt
from typing import Optional

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from config import MagInkDashConfig
from ics_cal.ics import IcsModule
from owm.owm import OWMModule
from render.render import RenderHelper

cfg = MagInkDashConfig.get_config()

app = FastAPI(title="MagInkDashPlus Server", version="0.2.0")

logger = structlog.get_logger()

owmModule = OWMModule()
calModule = IcsModule()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get(
    "/test",
    summary="Background image for testing",
)
def get_background() -> FileResponse:
    return FileResponse("render/background.png", media_type="image/png")


@app.get("/image", summary="Rendered dashboard image")
def get_image() -> FileResponse:
    start_time = time.time()
    logger.info("Retrieving data...")

    # Retrieve Weather Data
    current_weather, hourly_forecast, daily_forecast = owmModule.get_weather(
        cfg.LAT, cfg.LNG, cfg.OWM_API_KEY, cfg.WEATHER_UNITS
    )

    # Retrieve Calendar Data
    currTime = dt.now(cfg.DISPLAY_TZ)
    currDate = currTime.date()
    calStartDatetime = cfg.DISPLAY_TZ.localize(dt.combine(currDate, dt.min.time()))
    calEndDatetime = cfg.DISPLAY_TZ.localize(
        dt.combine(
            currDate + datetime.timedelta(days=cfg.NUM_CAL_DATS_TO_SHOW - 1),
            dt.max.time(),
        )
    )
    eventList = calModule.get_events(
        currDate,
        cfg.ICS_URL,
        calStartDatetime,
        calEndDatetime,
        cfg.DISPLAY_TZ,
        cfg.NUM_CAL_DATS_TO_SHOW,
    )

    end_time = time.time()
    logger.info(
        f"Completed data retrieval in {round(end_time - start_time, 3)} seconds."
    )

    # TODO: delete=False leads to accumulating temporary files in /tmp but is currently needed because the FileResponse is async.
    with tempfile.NamedTemporaryFile(
        suffix=".png", delete_on_close=False, delete=False
    ) as tf:
        start_time = time.time()
        logger.info(f"Generating image...")

        renderService = RenderHelper(
            cfg.IMAGE_WIDTH, cfg.IMAGE_HEIGHT, cfg.ROTATE_ANGLE
        )
        renderService.process_inputs(
            currTime,
            current_weather,
            hourly_forecast,
            daily_forecast,
            eventList,
            cfg.NUM_CAL_DATS_TO_SHOW,
            tf.name,
        )

        end_time = time.time()
        logger.info(
            f"Completed image generation in {round(end_time - start_time, 3)} seconds, serving image now."
        )

        return FileResponse(tf.name, media_type="image/png")


if __name__ == "__main__":
    logger.info(f"Starting web server...")
    config = uvicorn.Config(app, host="127.0.0.1", port=5000, log_level="debug")
    server = uvicorn.Server(config)
    server.run()
