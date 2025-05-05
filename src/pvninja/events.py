"""
Simple message objects used by *both* sides so you never duplicate JSON keys.
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import Literal

class ServerTick(BaseModel):
    type: Literal["tick"] = "tick"
    value: int            # seconds since server start

class ButtonCommand(BaseModel):
    type: Literal["cmd"] = "cmd"
    action: str
