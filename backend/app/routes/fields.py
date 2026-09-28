import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import MachineField
from ..schemas.field import FieldCreate, FieldResponse, FieldUpdate


router = APIRouter(
    prefix="/fields",
    tags=["Machine Fields"]
)

ALLOWED_FIELD_TYPES = {
    "text",
    "number",
    "dropdown"
}


def serialize_field(field: MachineField):
    options = None

    if field.dropdown_options:
        options = json.loads(field.dropdown_options)

    return {
        "id": field.id,
        "field_name": field.field_name,
        "field_type": field.field_type,
        "required": field.required,
        "dropdown_options": options
    }


def validate_field_configuration(field_data):

    if field_data.field_type not in ALLOWED_FIELD_TYPES:
        raise HTTPException(
            status_code=400,
            detail="field_type must be text, number, or dropdown"
        )

    if field_data.field_type == "dropdown":

        if not field_data.dropdown_options:
            raise HTTPException(
                status_code=400,
                detail="Dropdown fields require options"
            )

    if field_data.field_type != "dropdown":

        if field_data.dropdown_options:
            raise HTTPException(
                status_code=400,
                detail="Only dropdown fields can have options"
            )


@router.post("/", response_model=FieldResponse)
def create_field(
    field_data: FieldCreate,
    db: Session = Depends(get_db)
):

    field_data.field_name = field_data.field_name.strip()

    if not field_data.field_name:
        raise HTTPException(
            status_code=400,
            detail="Field name cannot be empty"
        )

    validate_field_configuration(field_data)

    existing = (
        db.query(MachineField)
        .filter(
            MachineField.field_name == field_data.field_name
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="A field with this name already exists"
        )

    field = MachineField(
        field_name=field_data.field_name,
        field_type=field_data.field_type,
        required=field_data.required,
        dropdown_options=(
            json.dumps(field_data.dropdown_options)
            if field_data.dropdown_options
            else None
        )
    )

    db.add(field)
    db.commit()
    db.refresh(field)

    return serialize_field(field)


@router.get("/", response_model=list[FieldResponse])
def get_fields(
    db: Session = Depends(get_db)
):

    fields = (
        db.query(MachineField)
        .order_by(MachineField.id)
        .all()
    )

    return [
        serialize_field(field)
        for field in fields
    ]


@router.get("/{field_id}", response_model=FieldResponse)
def get_field(
    field_id: int,
    db: Session = Depends(get_db)
):

    field = (
        db.query(MachineField)
        .filter(MachineField.id == field_id)
        .first()
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    return serialize_field(field)


@router.put("/{field_id}", response_model=FieldResponse)
def update_field(
    field_id: int,
    field_data: FieldUpdate,
    db: Session = Depends(get_db)
):

    field = (
        db.query(MachineField)
        .filter(MachineField.id == field_id)
        .first()
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    new_name = (
        field_data.field_name.strip()
        if field_data.field_name is not None
        else field.field_name
    )

    new_type = (
        field_data.field_type
        if field_data.field_type is not None
        else field.field_type
    )

    new_required = (
        field_data.required
        if field_data.required is not None
        else field.required
    )

    new_options = (
        field_data.dropdown_options
        if field_data.dropdown_options is not None
        else (
            json.loads(field.dropdown_options)
            if field.dropdown_options
            else None
        )
    )

    if not new_name:
        raise HTTPException(
            status_code=400,
            detail="Field name cannot be empty"
        )

    if new_type not in ALLOWED_FIELD_TYPES:
        raise HTTPException(
            status_code=400,
            detail="field_type must be text, number, or dropdown"
        )

    if new_type == "dropdown" and not new_options:
        raise HTTPException(
            status_code=400,
            detail="Dropdown fields require options"
        )

    if new_type != "dropdown":
        new_options = None

    duplicate = (
        db.query(MachineField)
        .filter(
            MachineField.field_name == new_name,
            MachineField.id != field_id
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Another field with this name already exists"
        )

    field.field_name = new_name
    field.field_type = new_type
    field.required = new_required
    field.dropdown_options = (
        json.dumps(new_options)
        if new_options
        else None
    )

    db.commit()
    db.refresh(field)

    return serialize_field(field)


@router.delete("/{field_id}")
def delete_field(
    field_id: int,
    db: Session = Depends(get_db)
):

    field = (
        db.query(MachineField)
        .filter(MachineField.id == field_id)
        .first()
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    db.delete(field)
    db.commit()

    return {
        "message": "Field deleted successfully"
    }