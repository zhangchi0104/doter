import pytest
import os, time
from doter.commands.install import InstallCommand, InstallArgs
from pathlib import Path
from doter.config import ConfigFile


from .common import *

@pytest.fixture
def app():
    yield InstallCommand(InstallArgs(config=CONFIG_FILE))


@pytest.fixture
def config_file():
    return ConfigFile.from_file(CONFIG_FILE)


@pytest.fixture
def app_with_test1():
    yield InstallCommand(InstallArgs(config=CONFIG_FILE, items=['test1']))


@pytest.fixture
def app_with_both():
    yield InstallCommand(
        InstallArgs(config=CONFIG_FILE, items=['test1', 'test2']))


@pytest.fixture
def app_with_dir(app: InstallCommand):
    yield InstallCommand(InstallArgs(config=CONFIG_FILE, items=["test_dir"]))


@pytest.mark.asyncio
async def test_install_single(app_with_test1: InstallCommand, config_file):
    await app_with_test1(config_file)
    assert test1_src.is_symlink() is True
    assert test1_src.exists() is True


@pytest.mark.asyncio
async def test_install_concurrent(app_with_both, config_file):
    start = time.time()
    await app_with_both(config_file)
    end = time.time()
    print(end - start)
    assert end - start - 2 < 0.1


@pytest.mark.asyncio
async def test_install_dir(app_with_dir, config_file):
    src_dir_path = Path('~/doter_test_dir').expanduser()
    await app_with_dir(config_file)
    res = src_dir_path.is_symlink() and src_dir_path.exists()
    assert res is True


@pytest.mark.asyncio
async def test_link_single(app_with_test1, config_file):
    app_with_test1.args = InstallArgs(items=['test1'],
                                      links_only=True,
                                      config=CONFIG_FILE)
    await app_with_test1(config_file)
    assert test1_src.is_symlink() == True
    assert test1_src.exists() == True


@pytest.mark.asyncio
async def test_link_dir(app_with_dir, config_file):
    app_with_test1.args = InstallArgs(items=['test_dir'],
                                      links_only=True,
                                      config=CONFIG_FILE)
    src_dir_path = Path('~/doter_test_dir').expanduser()
    await app_with_dir(config_file)
    res = src_dir_path.is_symlink() and src_dir_path.exists()
    assert res is True