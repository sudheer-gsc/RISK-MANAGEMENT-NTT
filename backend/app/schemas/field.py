from typing import Optional

from pydantic import BaseModel, Field


class FieldCreate(BaseModel):
    field_name: str = Field(min_length=1, max_length=100)
    field_type: str
    required: bool = False
    dropdown_options: Optional[list[str]] = None


class FieldUpdate(BaseModel):
    field_name: Optional[str] = None
    field_type: Optional[str] = None
    required: Optional[bool] = None
    dropdown_options: Optional[list[str]] = None


class FieldResponse(BaseModel):
    id: int
    field_name: str
    field_type: str
    required: bool
    dropdown_options: Optional[list[str]] = None