import logging
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler

FILE_SIZE = 1024 * 1024 * 100
BACKUP_COUNT = 5


class Logger:
    @staticmethod
    def createLogger(log_path=Path("./logs/programs")):
        log_path.mkdir(parents=True, exist_ok=True)
        level = logging.INFO
        fileHandler = RotatingFileHandler(
            log_path / f"EsportsHelper{time.strftime('%b-%d-%H-%M')}.log",
            mode="a+",
            maxBytes=FILE_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )

        logging.basicConfig(
            format="%(asctime)s %(levelname)s: %(message)s",
            level=level,
            handlers=[fileHandler, logging.StreamHandler()],
        )
        return logging.getLogger("EsportsHelper")

log = Logger().createLogger()