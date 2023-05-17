class SubprocessError(Exception):
    def __init__(self, cmd: str, retcode: int, msg: str) -> None:
        self._retcode = retcode
        self._err_msg = msg
        self._cmd = cmd
        super().__init__(self.msg())

    def msg(self):
        return f"cmd '{self._cmd}' Exited with code {self._retcode}"

    @property
    def retcode(self):
        return self._retcode

    @property
    def err_msg(self):
        return self.msg

    @property
    def cmd(self):
        return self._cmd


class FileAlreadExistsError(Exception):
    def __init__(self, path: str):
        self._path = path

    def msg(self):
        return f"file '{self._path}' already "