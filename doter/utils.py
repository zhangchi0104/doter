from asyncio import subprocess
from typing import List

from doter.exceptions import SubprocessError


async def sh(cmd: str):
    proc = await subprocess.create_subprocess_shell(
        cmd,
        stderr=subprocess.PIPE,
        shell=True,
    )
    _, stderr = await proc.communicate()
    retcode = proc.returncode
    if retcode != 0:
        raise SubprocessError(cmd, retcode, stderr)
