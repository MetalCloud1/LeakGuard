from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    serialize=True,  # JSON para que Loki pueda parsear
    level="INFO",
    enqueue=True,
)
