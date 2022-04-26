from typing import List, Union, Type
from types import TracebackType
from shutil import get_terminal_size
import os
import asyncio
from pathlib import Path
from rich.traceback import Traceback
import signal


async def run_hooks(hooks: List[str], event_bus=None, name=None):
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
    for cmd in hooks:
        if name is not None and event_bus is not None:
            await event_bus.publish(
                'install/update',
                name=name,
                description=f"Executing hook: {cmd}",
            )
        proc = await asyncio.create_subprocess_shell(
            cmd.replace('~', home_dir),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
            shell=True)

        async def sigint_handler():
            proc.send_signal(signal.SIGINT)
            await proc.wait()

        event_bus.subscribe('install/sigint', sigint_handler)
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


def create_traceback(
    exc_type: Type[BaseException],
    exec_val: BaseException,
    traceback: Union[TracebackType, None]
):
    """
    create_traceback creates an traceback object in `rich`
    from an exception

    Args:
        exec_type (Type[BaseException]): Type of the Exception
        exec_val (BaseException): The execption instance
        traceback(TracebackType): Optional, the traceback object

    Returns
        Traceback (rich.traceback.Traceback): the printable traceback

    """ 
    width, _ = get_terminal_size((80, 20))
    return Traceback.from_exception(
        exc_type,
        exec_val,
        traceback,
        width=width,
        word_wrap=True,
        show_locals=True,
    )
