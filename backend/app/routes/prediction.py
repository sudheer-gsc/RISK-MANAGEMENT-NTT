import json
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Machine


router = APIRouter(
    prefix="/prediction",
    tags=["Risk Prediction"]
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ML_SCRIPT = PROJECT_ROOT / "ml" / "predict.py"


@router.post("/{machine_id}")
def predict_machine_risk(
    machine_id: int,
    db: Session = Depends(get_db)
):

    # Find machine
    machine = (
        db.query(Machine)
        .filter(Machine.id == machine_id)
        .first()
    )

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    # Read dynamic machine values
    values = json.loads(
        machine.field_values
    )

    # Current ML model requires these fields
    required_ml_fields = [
        "Temperature",
        "Pressure",
        "Vibration"
    ]

    missing_fields = [
        field
        for field in required_ml_fields
        if field not in values
    ]

    if missing_fields:

        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "ML model requires "
                    "Temperature, Pressure, "
                    "and Vibration"
                ),
                "missing_fields": missing_fields
            }
        )

    # Convert values
    try:

        temperature = float(
            values["Temperature"]
        )

        pressure = float(
            values["Pressure"]
        )

        vibration = str(
            values["Vibration"]
        )

    except (ValueError, TypeError) as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Temperature, Pressure, "
                "or Vibration value"
            )
        ) from exc

    # Check ML script
    if not ML_SCRIPT.exists():

        raise HTTPException(
            status_code=500,
            detail="ML prediction script not found"
        )

    # Run local Python ML prediction
    try:

        result = subprocess.run(
            [
                sys.executable,
                str(ML_SCRIPT),
                "--temperature",
                str(temperature),
                "--pressure",
                str(pressure),
                "--vibration",
                vibration
            ],
            capture_output=True,
            text=True,
            check=True
        )

        prediction = json.loads(
            result.stdout.strip()
        )

    except subprocess.CalledProcessError as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "ML prediction failed: "
                + exc.stderr
            )
        ) from exc

    return {
        "machine_id": machine.id,
        "risk_level": prediction["risk_level"],
        "inputs_used": {
            "Temperature": temperature,
            "Pressure": pressure,
            "Vibration": vibration
        },
        "note": (
            "Additional dynamic fields are stored "
            "and available to the application, "
            "but the current ML model uses "
            "Temperature, Pressure, and Vibration."
        )
    }