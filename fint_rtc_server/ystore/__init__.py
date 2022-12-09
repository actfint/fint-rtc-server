import pkg_resources

from fint_rtc_server.logger import logger

pkg = {ep.name: ep.load() for ep in pkg_resources.iter_entry_points(group="fint_ystore")}

try:
    get_ystore_manager = pkg["get_ystore_manager"]

except KeyError:
    logger.info("No auth plugin found, using default room manager")
    from fint_rtc_server.ystore.manager import get_ystore_manager
