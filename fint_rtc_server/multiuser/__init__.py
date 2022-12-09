import pkg_resources

from fint_rtc_server.logger import logger

pkg = {ep.name: ep.load() for ep in pkg_resources.iter_entry_points(group="fint_multiuser")}

try:
    get_user_manager = pkg["get_user_manager"]

except KeyError:
    logger.info("No auth plugin found, using simple user manager")
    from fint_rtc_server.multiuser.manager import get_user_manager
