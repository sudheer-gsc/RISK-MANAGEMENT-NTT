import argparse
import json
from pathlib import Path

import joblib


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "risk_model.pkl"


def predict_risk(temperature, pressure, vibration):

    if vibration not in {"Low", "Medium", "High"}:
        raise ValueError(
            "Vibration must be Low, Medium, or High"
        )

    vibration_mapping = {
        "Low": 0,
        "Medium": 1,
        "High": 2
    }

    vibration_value = vibration_mapping[vibration]

    model = joblib.load(MODEL_PATH)

    result = model.predict([
        [
            float(temperature),
            float(pressure),
            vibration_value
        ]
    ])[0]

    return result


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--temperature",
        type=float,
        required=True
    )

    parser.add_argument(
        "--pressure",
        type=float,
        required=True
    )

    parser.add_argument(
        "--vibration",
        type=str,
        required=True
    )

    args = parser.parse_args()

    risk = predict_risk(
        args.temperature,
        args.pressure,
        args.vibration
    )

    print(
        json.dumps({
            "risk_level": risk
        })
    )


if __name__ == "__main__":
    main()