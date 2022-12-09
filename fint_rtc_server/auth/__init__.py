import pkg_resources

from fint_rtc_server.logger import logger

auth = {ep.name: ep.load() for ep in pkg_resources.iter_entry_points(group="fint_auth")}

try:
    User = auth["User"]
    current_user = auth["current_user"]
    update_user = auth["update_user"]
    websocket_auth = auth["websocket_auth"]
    logger.info("auth plugin loaded")

except KeyError:
    logger.info("No auth plugin found, using default noauth")
    from fint_rtc_server.auth.noauth import (
        User,
        current_user,
        update_user,
        websocket_auth,
    )
