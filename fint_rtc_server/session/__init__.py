import pkg_resources

from fint_rtc_server.logger import logger

session = {ep.name: ep.load() for ep in pkg_resources.iter_entry_points(group="fint_session")}

try:
    logger.info("Try load session manager plugin from group: fint_session")
    get_session_manager = session["get_session_manager"]
    logger.info("session manager plugin loaded")
except KeyError:
    logger.info("No pathfinder session manager found, using local session manager")
    from fint_rtc_server.session.websocket_manager import get_session_manager
