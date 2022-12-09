from pathlib import Path


class BasePathfinder(object):
    async def get_server_location(self, user, experiment_id) -> str:
        raise NotImplementedError

    async def get_file_path(self, user, experiment_id, file_path) -> Path:
        raise NotImplementedError
