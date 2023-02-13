from dataclasses import dataclass

from pydantic import BaseModel, validator

from . import UIBase, UIEvent
from typing import Union, Literal
from enum import Enum


class InstallAction(str, Enum):
    INIT = "init"
    STEP = "step"
    ERROR = "error"
    DONE = "done"


class PayloadBase(BaseModel):
    name: str


class InitPayload(PayloadBase):
    total_steps: int


class StepPayload(PayloadBase):
    msg: str


class ErrorPayload(PayloadBase):
    error: Exception

    class Config:
        arbitrary_types_allowed = True


InstallUIPayload = Union[InitPayload, StepPayload, ErrorPayload, PayloadBase]
InstallUIEvent = UIEvent[InstallAction, InstallUIPayload]


class InstallUI(UIBase[InstallUIPayload]):
    def on_init(self, payload: InitPayload):
        print("Init", payload)

    def on_step(self, payload: StepPayload):
        print(payload)

    def on_done(self, payload: PayloadBase):
        print(payload)

    def on_error(self, payload: ErrorPayload):
        print("Err:", payload.error)
