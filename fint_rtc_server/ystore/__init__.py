#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from importlib_metadata import entry_points

from fint_rtc_server.logger import logger

pkg = {ep.name: ep.load() for ep in entry_points(group="fint_ystore")}

try:
    get_ystore_manager = pkg["get_ystore_manager"]

except KeyError:
    logger.info("No ystore plugin found, using default room manager")
    from fint_rtc_server.ystore.manager import get_ystore_manager
