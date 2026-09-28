from typing import Any

from pydantic import BaseModel


class MachineCreate(BaseModel):
    field_values: dict[str, Any]


class MachineUpdate(BaseModel):
    field_values: dict[str, Any]


class MachineResponse(BaseModel):
    id: int
    field_values: dict[str, Any]