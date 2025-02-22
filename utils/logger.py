import logging
import os

APP_ENV = os.getenv("APP_ENV", "development").lower()
IS_PROD = APP_ENV == "production"

logger = logging.getLogger("app")
logger.setLevel(logging.INFO if IS_PROD else logging.DEBUG)

log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s ==> %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

if IS_PROD:
    file_handler = logging.FileHandler("app.log", mode="a")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

logger.info(f"Logging initialized in {APP_ENV} mode")
