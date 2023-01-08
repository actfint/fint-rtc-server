#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from importlib_metadata import entry_points

from fint_rtc_server.logger import logger

session = {ep.name: ep.load() for ep in entry_points(group="fint_session")}

try:
    logger.info("Try load session manager plugin from group: fint_session")
    get_session_manager = session["get_session_manager"]
except KeyError:
    logger.info("No pathfinder session manager found, using local session manager")
    from fint_rtc_server.session.websocket_manager import get_session_manager
