"""Entry point for the heartbeat service: python -m src"""

import logging

from src.config import HeartbeatSettings
from src.heartbeat import run_scheduler

settings = HeartbeatSettings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

run_scheduler(settings)
