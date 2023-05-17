import pytest
from doter.commands.clean import CleanupCommand, CleanupArgs
from doter.config import ConfigFile
from pathlib import Path
from functools import partial
import os
import shutil


from .common import CONFIG_FILE
from doter.commands.install import InstallCommand, InstallArgs

from .common import *


@pytest.fixture
def config_file():
    return ConfigFile.from_file(CONFIG_FILE)


def cmd_builder(cmd_name: str, items: "list[str]" = ()):
    if cmd_name == 'clean':
        args = CleanupArgs(config=CONFIG_FILE, items=items)
        return CleanupCommand(args)
    else:
        args = InstallArgs(config=CONFIG_FILE, items=items)
        return InstallCommand(args)


@pytest.fixture
def clean_cmd():
    yield partial(cmd_builder, "clean")
    try:
        shutil.rmtree(test1_src, ignore_errors=True)
        shutil.rmtree(test2_src, ignore_errors=True)
        shutil.rmtree(test_dir_src, ignore_errors=True)
    except:
        pass


@pytest.fixture
def install_cmd():
    yield partial(cmd_builder, "install")
    try:
        shutil.rmtree(test1_src, ignore_errors=True)
        shutil.rmtree(test2_src, ignore_errors=True)
        shutil.rmtree(test_dir_src, ignore_errors=True)
    except:
        pass


@pytest.mark.asyncio
async def test_clean_normal(clean_cmd, install_cmd, config_file):
    await install_cmd(["test1"])(config_file)
    assert test1_src.is_symlink()
    await clean_cmd(["test1"])(config_file)
    assert not test1_src.is_symlink()


@pytest.mark.asyncio
async def test_clean_all(install_cmd, clean_cmd, config_file):
    await install_cmd()(config_file)
    assert test1_src.is_symlink()
    assert test2_src.is_symlink()
    assert test_dir_src.is_symlink()
    await clean_cmd()(config_file)
    assert not test1_src.exists()
    assert not test2_src.exists()
    assert not test_dir_src.exists()


@pytest.mark.asyncio
async def test_clean_skip(install_cmd, clean_cmd, config_file):
    await install_cmd(["test1", "test2"])(config_file)
    assert test1_src.is_symlink()
    await clean_cmd(["test1"])(config_file)
    assert test2_src.exists()

