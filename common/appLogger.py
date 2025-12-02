# common/appLogger.py
import logging
import os
from datetime import datetime

class AppLogger:
    def __init__(self, config):
        self.logger = logging.getLogger(config["name"])
        self.logger.setLevel(config.get("log_level", "INFO"))

        if not os.path.exists("logs"):
            os.makedirs("logs")

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File handler
        fh = logging.FileHandler(config.get("log_file", "logs/app.log"))
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Console
        if config.get("log_to_stdout"):
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.logger.error(msg)
    def warning(self, msg): self.logger.warning(msg)
    def debug(self, msg): self.logger.debug(msg)