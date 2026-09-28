from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "risk_model.pkl"


def calculate_risk(temperature, pressure, vibration):
    """
    Generate a synthetic risk label for training.
    """

    if temperature >= 80 or pressure >= 120 or vibration == "High":
        return "High"

    if temperature >= 65 or pressure >= 100 or vibration == "Medium":
        return "Medium"

    return "Low"


def generate_dataset():
    """
    Generate synthetic machine data locally.
    """

    rng = np.random.default_rng(42)

    temperatures = rng.uniform(40, 110, 1500)
    pressures = rng.uniform(60, 150, 1500)
    vibration_values = rng.integers(0, 3, 1500)

    vibration_names = np.array([
        "Low",
        "Medium",
        "High"
    ])

    vibration_labels = vibration_names[vibration_values]

    labels = [
        calculate_risk(
            temperature,
            pressure,
            vibration
        )
        for temperature, pressure, vibration
        in zip(
            temperatures,
            pressures,
            vibration_labels
        )
    ]

    X = np.column_stack([
        temperatures,
        pressures,
        vibration_values
    ])

    y = np.array(labels)

    return X, y


def main():

    print("Generating synthetic machine data...")

    X, y = generate_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("Training Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print()
    print("Model trained successfully.")
    print(f"Test accuracy: {accuracy:.2%}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()