import pytest
import os, time
from ..app import DoterApp
from pathlib import Path

test1_src = Path('~/doter_test1').expanduser().absolute()
test1_dst = Path('./dotfiles/doter_test1').absolute()

test2_src = Path('~/doter_test2').expanduser().absolute()
test2_dst = Path('./dotfiles/doter_test2').absolute()


@pytest.fixture
def app():
    yield DoterApp('./doter/test/test.yml')


@pytest.fixture
def app_with_test1(app):
    test1_dst.touch()
    yield app
    test1_src.unlink()
    os.remove(test1_dst)


@pytest.fixture
def app_with_both(app):
    test1_dst.touch()
    test2_dst.touch()
    yield app
    test1_src.unlink()
    test2_src.unlink()
    os.remove(test1_dst)
    os.remove(test2_dst)


@pytest.mark.asyncio
async def test_install_single(app_with_test1):
    await app_with_test1.install('test1')
    assert test1_src.is_symlink() == True
    assert test1_src.exists() == True


@pytest.mark.asyncio
async def test_install_concurrent(app_with_both):
    start = time.time()
    await app_with_both.install('test1', 'test2')
    end = time.time()
    print(end - start)
    assert end - start - 2 < 0.1
