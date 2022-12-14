#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from importlib_metadata import entry_points

from fint_rtc_server.logger import logger

auth = {ep.name: ep.load() for ep in entry_points(group="fint_auth")}

try:
    User = auth["User"]
    current_user = auth["current_user"]
    update_user = auth["update_user"]
    websocket_auth = auth["websocket_auth"]


except KeyError:
    logger.info("No auth plugin found, using default noauth")
    from fint_rtc_server.auth.noauth import (
        User,
        current_user,
        update_user,
        websocket_auth,
    )
