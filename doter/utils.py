from typing import List, Union
import os
import asyncio
from pathlib import Path


async def run_hooks(hooks: List[str]):
    """
    run_hooks execute hooks through the system shell
    asyncriously

    Args:
        hooks (List[str]): a series of commands to be executed

    Raises:
        RuntimeError: execution will be terminated when a command returns
            non zero
    """
    home_dir = os.getenv('HOME')
    if home_dir is None:
        raise RuntimeError('environment variable $HOME is not set')
    print(hooks)
    for cmd in hooks:
        proc = await asyncio.create_subprocess_shell(
            cmd.replace('~', home_dir),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
            shell=True)
        _, stderr = await proc.communicate()
        retcode = proc.returncode
        if retcode != 0:
            raise RuntimeError(
                f'Hook {cmd} exited with code {retcode}: {stderr.decode()}')


def link(dotfiles_dir: Union[str, Path], src: str, dst: str, force: bool):
    """
    link creates a symbolic link from dst to src
    dst are the files in dotfiles_dir

    Args:
        dotfiles_dir (str): the directory containing dotfiles
        src (str): the source file
        dst (str): the destination file
        force (bool): whether to overwrite existing files
    """
    abs_src = os.path.abspath(os.path.expanduser(src))
    abs_dst = os.path.join(dotfiles_dir, os.path.expanduser(dst))
    abs_dst = os.path.abspath(abs_dst)
    abs_src = Path(abs_src)
    if force and abs_src.is_symlink():
        abs_src.unlink()
        print(f"Unlinking {abs_src}")
    elif force and abs_src.is_file():
        os.remove(abs_src)
        print(f"Removing {abs_src}")
    elif force and abs_src.is_dir():
        os.removedirs(abs_src)
    abs_src.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(src=abs_dst, dst=abs_src)


async def sh(cmd: str):
    """
    sh executes a shell command
    """
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True)
    stdout, stderr = await proc.communicate()
    retcode = proc.returncode
    return retcode, stdout, stderr
