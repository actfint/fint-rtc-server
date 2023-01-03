import os

from fps.logging import get_configured_logger

DEBUG_ON = os.getenv("FINT_DEBUG_ON") in ["true", "True"]

level = "info" if not DEBUG_ON else "debug"

logger = get_configured_logger(__package__, level)
