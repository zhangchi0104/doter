import pytest
import os, time
from doter.commands.install import InstallCommand, InstallArgs
from pathlib import Path
from doter.config import ConfigFile

test1_src = Path('~/doter_test1').expanduser().absolute()
test1_dst = Path('./test/doter_test1').absolute()

test2_src = Path('~/doter_test2').expanduser().absolute()
test2_dst = Path('./test/doter_test2').absolute()

from .common import CONFIG_FILE

@pytest.fixture
def app():
    yield InstallCommand(InstallArgs(config=CONFIG_FILE))


@pytest.fixture
def config_file():
    return ConfigFile.from_file(CONFIG_FILE)


@pytest.fixture
def app_with_test1():
    test1_dst.touch()
    yield InstallCommand(InstallArgs(config=CONFIG_FILE, items=['test1']))

    test1_src.unlink()
    os.remove(test1_dst)


@pytest.fixture
def app_with_both():
    test1_dst.touch()
    test2_dst.touch()
    yield InstallCommand(
        InstallArgs(config=CONFIG_FILE, items=['test1', 'test2']))
    try:
        test1_src.unlink()
        test2_src.unlink()
        os.remove(test1_dst)
        os.remove(test2_dst)
    except FileNotFoundError:
        pass


@pytest.fixture
def app_with_dir(app: InstallCommand):
    src_dir_path = Path('~/doter_test_dir').expanduser()
    dst_dir_path = Path('./test/doter_test_dir')
    dst_dir_path.mkdir(parents=True, exist_ok=True)
    Path(dst_dir_path / 'test_item').touch(exist_ok=True)
    dst_dir_path.mkdir(exist_ok=True, parents=True)
    yield InstallCommand(InstallArgs(config=CONFIG_FILE, items=["test_dir"]))
    try:
        os.unlink(src_dir_path)
        import shutil
        shutil.rmtree(dst_dir_path)
    except FileNotFoundError:
        pass


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