from asyncio import Queue
from rich.progress import Progress, SpinnerColumn, TextColumn, ProgressColumn, Task
from pydantic import BaseModel
from rich.text import Text
from . import UIBase, UIEvent, PayloadBase, ErrorPayload
from typing import Dict, Optional, Union, Type, Any
from enum import Enum


class InstallAction(str, Enum):
    INIT = "init"
    STEP = "step"
    ERROR = "error"
    DONE = "done"


class InitPayload(PayloadBase):
    total_steps: int


class StepPayload(PayloadBase):
    msg: str


InstallUIPayload = Union[InitPayload, StepPayload, ErrorPayload, PayloadBase]
InstallUIEvent = UIEvent[InstallAction, InstallUIPayload]


class InstallUI(UIBase[InstallUIPayload]):
    def __init__(self, queue: Queue):
        self._progress = Progress(
            SpinnerColumn(),
            CurrentProgressColumn(),
            TextColumn("{task.description}"),
        )
        self._name2id: Dict[str, int] = {}
        super().__init__(queue)

    def on_init(self, payload: InitPayload):
        task_id = self._progress.add_task(
            f"{payload.name}: Preparing",
            total=payload.total_steps,
        )
        self._name2id[payload.name] = task_id

    def on_step(self, payload: StepPayload):
        name = payload.name
        task_id = self._name2id[name]
        self._progress.update(task_id,
                              advance=1,
                              description=f"{payload.name}: f{payload.msg}")

    def on_done(self, payload: PayloadBase):
        task_id = self.get_task_id(payload.name)
        self._progress.update(task_id,
                              completed=True,
                              advance=0,
                              description=f"{payload.name}: Done")

    def on_error(self, payload: ErrorPayload):
        task_id = self.get_task_id(payload.name)
        self._progress.update(task_id,
                              completed=True,
                              description=f"{payload.name}: {payload.error}")
        self._progress.print(payload.error)

    def get_task_id(self, name: str):
        return self._name2id[name]

    def __enter__(self):
        self._progress.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ):
        self._progress.__exit__(exc_type, exc_val, exc_tb)


class CurrentProgressColumn(ProgressColumn):
    def render(self, task: "Task"):
        text = ""
        if not task.finished:
            text = f"{task.completed}/{task.total}"
            text = Text(text)
        else:
            text = f"{task.total}/{task.total}"
        return text