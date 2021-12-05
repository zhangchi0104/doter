import pytest
from doter.app import DoterApp
from pathlib import Path
import os

test1_src = Path('~/doter_test1').expanduser().absolute()
test1_dst = Path('./test/test_files/doter_test1').absolute()

test2_src = Path('~/doter_test2').expanduser().absolute()
test2_dst = Path('./test/test_files/doter_test2').absolute()

test_dir_src = Path('~/doter_test_dir').expanduser().absolute()
test_dir_dst = Path('./tests/test_files/doter_test_dir').absolute()


@pytest.fixture
def app():
    yield DoterApp(config='./test/test.yml', dotfiles_dir='./test/test_files')


@pytest.mark.asyncio
async def test_clean_normal(app):
    await app.link('test1')
    assert test1_src.is_symlink()
    await app.clean('test1')
    assert not test1_src.is_symlink()


@pytest.mark.asyncio
async def test_clean_all(app):
    await app.link()
    assert test1_src.is_symlink()
    assert test2_src.is_symlink()
    assert test_dir_src.is_symlink()
    await app.clean()
    assert not test1_src.exists()
    assert not test2_src.exists()
    assert not test_dir_src.exists()


@pytest.mark.asyncio
async def test_clean_skip(app):
    test1_src.touch()
    await app.clean('test1')
    assert test1_src.exists()
    os.remove(test1_src)
