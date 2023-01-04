#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from importlib_metadata import entry_points

from fint_rtc_server.logger import logger

pkg = {ep.name: ep.load() for ep in entry_points(group="fint_multiuser")}

try:
    get_user_manager = pkg["get_user_manager"]

except KeyError:
    logger.info("No auth plugin found, using simple user manager")
    from fint_rtc_server.multiuser.manager import get_user_manager
