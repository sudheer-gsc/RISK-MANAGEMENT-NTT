import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Machine, MachineField
from ..schemas.machine import (
    MachineCreate,
    MachineResponse,
    MachineUpdate,
)


router = APIRouter(
    prefix="/machines",
    tags=["Machines"]
)


def get_configured_fields(db: Session):
    return (
        db.query(MachineField)
        .order_by(MachineField.id)
        .all()
    )


def validate_machine_values(
    values: dict,
    fields: list[MachineField]
):

    errors = {}

    configured_names = {
        field.field_name
        for field in fields
    }

    # Check required fields
    for field in fields:

        value = values.get(field.field_name)

        if field.required:

            if value is None or value == "":
                errors[field.field_name] = (
                    "This field is required"
                )

    # Check for fields that are not configured
    for key in values:

        if key not in configured_names:
            errors[key] = (
                "This field is not configured"
            )

    # Validate field data types
    for field in fields:

        if field.field_name not in values:
            continue

        value = values[field.field_name]

        if value is None or value == "":
            continue

        # Text validation
        if field.field_type == "text":

            if not isinstance(value, str):

                errors[field.field_name] = (
                    "Value must be text"
                )

        # Number validation
        elif field.field_type == "number":

            if isinstance(value, bool):

                errors[field.field_name] = (
                    "Value must be a number"
                )

            elif not isinstance(
                value,
                (int, float)
            ):

                errors[field.field_name] = (
                    "Value must be a number"
                )

        # Dropdown validation
        elif field.field_type == "dropdown":

            options = (
                json.loads(field.dropdown_options)
                if field.dropdown_options
                else []
            )

            if value not in options:

                errors[field.field_name] = (
                    f"Value must be one of: "
                    f"{', '.join(options)}"
                )

    if errors:

        raise HTTPException(
            status_code=400,
            detail=errors
        )


def serialize_machine(machine: Machine):

    return {
        "id": machine.id,
        "field_values": json.loads(
            machine.field_values
        )
    }


# CREATE MACHINE
@router.post(
    "/",
    response_model=MachineResponse
)
def create_machine(
    machine_data: MachineCreate,
    db: Session = Depends(get_db)
):

    fields = get_configured_fields(db)

    if not fields:

        raise HTTPException(
            status_code=400,
            detail=(
                "Create machine fields before "
                "creating machines"
            )
        )

    validate_machine_values(
        machine_data.field_values,
        fields
    )

    machine = Machine(
        field_values=json.dumps(
            machine_data.field_values
        )
    )

    db.add(machine)
    db.commit()
    db.refresh(machine)

    return serialize_machine(machine)


# GET ALL MACHINES
@router.get(
    "/",
    response_model=list[MachineResponse]
)
def get_machines(
    db: Session = Depends(get_db)
):

    machines = (
        db.query(Machine)
        .order_by(Machine.id)
        .all()
    )

    return [
        serialize_machine(machine)
        for machine in machines
    ]


# GET ONE MACHINE
@router.get(
    "/{machine_id}",
    response_model=MachineResponse
)
def get_machine(
    machine_id: int,
    db: Session = Depends(get_db)
):

    machine = (
        db.query(Machine)
        .filter(
            Machine.id == machine_id
        )
        .first()
    )

    if not machine:

        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    return serialize_machine(machine)


# UPDATE MACHINE
@router.put(
    "/{machine_id}",
    response_model=MachineResponse
)
def update_machine(
    machine_id: int,
    machine_data: MachineUpdate,
    db: Session = Depends(get_db)
):

    machine = (
        db.query(Machine)
        .filter(
            Machine.id == machine_id
        )
        .first()
    )

    if not machine:

        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    fields = get_configured_fields(db)

    validate_machine_values(
        machine_data.field_values,
        fields
    )

    machine.field_values = json.dumps(
        machine_data.field_values
    )

    db.commit()
    db.refresh(machine)

    return serialize_machine(machine)


# DELETE MACHINE
@router.delete(
    "/{machine_id}"
)
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db)
):

    machine = (
        db.query(Machine)
        .filter(
            Machine.id == machine_id
        )
        .first()
    )

    if not machine:

        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    db.delete(machine)
    db.commit()

    return {
        "message": "Machine deleted successfully"
    }