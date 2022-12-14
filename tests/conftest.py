#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
from fint_test_app.app import create_app

from fint_rtc_server.auth import current_user, websocket_auth
from fint_rtc_server.auth.noauth import Anonymous
from fint_rtc_server.auth.noauth import current_user as project_current_user
from fint_rtc_server.auth.noauth import websocket_auth as project_websocket_auth
from fint_rtc_server.config import FintRTCServerConfig, get_config
from fint_rtc_server.multiuser import get_user_manager
from fint_rtc_server.multiuser.manager import UidMappedUserManager
from fint_rtc_server.multiuser.manager import (
    get_user_manager as project_get_user_manager,
)
from fint_rtc_server.session import get_session_manager
from fint_rtc_server.session.websocket_manager import (
    get_session_manager as project_get_session_manager,
)
from fint_rtc_server.ystore import get_ystore_manager
from fint_rtc_server.ystore.manager import (
    get_ystore_manager as project_get_ystore_manager,
)

pytest_plugins = "fps.testing.fixtures"
_here = Path(os.path.abspath(os.path.dirname(__file__)))


@pytest.fixture
def app():
    app = create_app()
    yield app


@pytest.fixture(scope="session")
def session_tmp_dir():
    tmpdir = tempfile.TemporaryDirectory()
    yield tmpdir.name


@pytest.fixture(scope="session")
def room_dir():
    tmpdir = tempfile.TemporaryDirectory()
    yield tmpdir.name


@pytest.fixture(scope="session")
def ipynb_file(session_tmp_dir):
    filename = "test.ipynb"
    user_file_path = asyncio.run(
        UidMappedUserManager(session_tmp_dir).get_user_file_path(Anonymous(), filename)
    )
    filepath = Path(session_tmp_dir) / user_file_path
    filepath.parent.mkdir(parents=True, exist_ok=True)

    example_ipynb_path = _here / "empty.ipynb"

    with open(example_ipynb_path, "rb") as f:
        c = f.read()

    with open(filepath, "wb") as f:
        f.write(c)
    yield filename, filepath.as_posix()


@pytest.fixture(scope="session")
def text_file(session_tmp_dir):
    filename = "test.txt"
    user_file_path = asyncio.run(
        UidMappedUserManager(session_tmp_dir).get_user_file_path(Anonymous(), filename)
    )
    filepath = Path(session_tmp_dir) / user_file_path
    filepath.parent.mkdir(parents=True, exist_ok=True)

    example_ipynb_path = _here / "empty.txt"

    with open(example_ipynb_path, "rb") as f:
        c = f.read()

    with open(filepath, "wb") as f:
        f.write(c)
    yield filename, filepath.as_posix()


@pytest.fixture
def config(session_tmp_dir, room_dir):
    yield FintRTCServerConfig.parse_obj(
        {
            "content_dir": session_tmp_dir,
            "room_dir": room_dir,
            "room_cleanup_wait_for": 0,
            "doc_save_wait_for": 0.1,
        }
    )


@pytest.fixture
def config_override(app, config):
    async def override_get_config():
        return config

    app.dependency_overrides[get_config] = override_get_config
    app.dependency_overrides[get_user_manager] = project_get_user_manager
    app.dependency_overrides[get_ystore_manager] = project_get_ystore_manager
    app.dependency_overrides[get_session_manager] = project_get_session_manager
    app.dependency_overrides[current_user] = project_current_user
    app.dependency_overrides[websocket_auth] = project_websocket_auth
