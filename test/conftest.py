from pathlib import Path
from .common import *
import os
def pytest_sessionstart(session):
    test1_dst.touch()
    test2_dst.touch()
    test_dir_dst.mkdir(exist_ok=True)

def pytest_sessionfinish(session, exitstatus):

    test1_src.unlink()
    test2_src.unlink()
    test_dir_src.unlink()

    os.remove(test1_dst)
    os.remove(test2_dst)
    test_dir_dst.rmdir()