#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

import os

from fps.logging import get_configured_logger

DEBUG_ON = os.getenv("FINT_DEBUG_ON") in ["true", "True"]

level = "info" if not DEBUG_ON else "debug"

logger = get_configured_logger(__package__, level)
