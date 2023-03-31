import logging
import time
import coloredlogs
from pathlib import Path
from logging.handlers import RotatingFileHandler

FILE_SIZE = 1024 * 1024 * 100
BACKUP_COUNT = 5


class Logger:
    @staticmethod
    def createLogger(log_path=Path("./logs/programs")):
        log_path.mkdir(parents=True, exist_ok=True)
        level = logging.DEBUG
        fileHandlerInfo = RotatingFileHandler(
            log_path / f"EsportsHelper{time.strftime('%b-%d-%H-%M')}.info.log",
            mode="a+",
            maxBytes=FILE_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
            
        )
        fileHandlerInfo.setLevel(logging.INFO)

        fileHandlerDebug = RotatingFileHandler(
            log_path / f"EsportsHelper{time.strftime('%b-%d-%H-%M')}.debug.log",
            mode="a+",
            maxBytes=FILE_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        fileHandlerDebug.setLevel(logging.DEBUG)

        logging.basicConfig(
            format="%(asctime)s %(levelname)s: %(message)s",
            level=level,
            handlers=[fileHandlerInfo, fileHandlerDebug]
        )
        return logging.getLogger("EsportsHelper")

log = Logger().createLogger()
coloredlogs.install(level='INFO', logger=log)