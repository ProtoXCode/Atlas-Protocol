import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

DEFAULT_LEVEL = os.getenv('ATLAS_LOG_LEVEL', 'INFO').upper()
LOG_DIR = Path(os.getenv('ATLAS_LOG_DIR', 'logs'))
LOG_DIR.mkdir(parents=True, exist_ok=True)

def configure_logging(level: str | int = DEFAULT_LEVEL) -> None:
    logger  =logging.getLogger()
    if logger.handlers:
        return

    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))

    fh = RotatingFileHandler(
        LOG_DIR / 'atlas.log', maxBytes=2_000_000, backupCount=3)
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s:%(lineno)d - %(message)s'))

    logger.addHandler(ch)
    logger.addHandler(fh)
