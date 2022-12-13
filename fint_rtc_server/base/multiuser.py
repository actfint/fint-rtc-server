from pathlib import Path


class MultiuserManager(object):
    async def get_user_file_path(self, user, path, *args, **kwargs) -> Path:
        raise NotImplementedError
