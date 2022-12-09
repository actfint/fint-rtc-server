from pathlib import Path


class MultiuserManager(object):
    async def get_user_file_path(self, user, path, *args, **kwargs) -> Path:
        raise NotImplementedError

    async def get_user_server_location(self, user, *args, **kwargs) -> str:
        raise NotImplementedError
