import pytest
import os, time
from doter.app import DoterApp
from pathlib import Path

test1_src = Path('~/doter_test1').expanduser().absolute()
test1_dst = Path('./test/doter_test1').absolute()

test2_src = Path('~/doter_test2').expanduser().absolute()
test2_dst = Path('./test/doter_test2').absolute()


@pytest.fixture
def app():
    yield DoterApp(config='./test/test.yml', dotfiles_dir='./test')


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
    await app_with_test1.link('test1')
    assert test1_src.is_symlink() == True
    assert test1_src.exists() == True

@pytest.mark.asyncio
async  def test_install_dir(app):
    src_dir_path = Path('~/doter_test_dir').expanduser()
    dst_dir_path = Path('./test/doter_test_dir')
    dst_dir_path.mkdir(exist_ok=True)
    Path(dst_dir_path / 'test_item').touch(exist_ok=True)
    await app.link('test_dir')
    res = src_dir_path.is_symlink() and src_dir_path.exists()
    if res == True:
        os.unlink(src_dir_path)
    os.remove(dst_dir_path / 'test_item')
    os.removedirs(dst_dir_path)
    assert res == True
    

