from enum import Enum
from . import UIBase, UIEvent, PayloadBase, ErrorPayload
from typing import Union
from rich.console import Console


class CleanupAction(str, Enum):
    DONE = "done"
    ERROR = "error"


CleanupUIPayload = Union[PayloadBase, ErrorPayload]
CleanupUIEvent = UIEvent[CleanupAction, CleanupUIPayload]


class CleanupUI(UIBase[CleanupUIPayload]):
    def __init__(self):
        self._console = Console()

    def on_done(self, payload: PayloadBase):
        item = payload.name
        self._console.print(f"Done removing: `{item}`")

    def on_error(self, payload: ErrorPayload):
        err = payload.error
        self._console.print_exception(err)
