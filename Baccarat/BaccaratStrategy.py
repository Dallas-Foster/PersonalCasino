# BaccaratStrategy.py

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
from BaccaratLogic import play_baccarat  # Ensure correct import


def generate_training_data(num_samples=10000, history_length=3):
    """
    Generates synthetic Baccarat game data with historical outcomes.
    Each sample includes the outcomes of the last 'history_length' games.

    Args:
        num_samples (int): Number of samples to generate.
        history_length (int): Number of past game outcomes to include as features.

    Returns:
        X (np.ndarray): Feature matrix.
        y (np.ndarray): Target vector.
        label_encoder (LabelEncoder): Fitted label encoder.
    """
    X = []
    y = []

    # Initialize history with 'Tie' to handle initial games
    history = ['Tie'] * history_length

    for _ in range(num_samples):
        # Simulate a game
        _, _, winner, _, _, _, _, _, _ = play_baccarat()

        # Append the last 'history_length' outcomes as features
        features = history.copy()
        X.append(features)
        y.append(winner)

        # Update history
        history.pop(0)
        history.append(winner)

    # Encode categorical features
    label_encoder = LabelEncoder()
    all_outcomes = ['Player', 'Banker', 'Tie']
    label_encoder.fit(all_outcomes)

    # Transform features and targets
    X_encoded = []
    for sample in X:
        encoded_sample = label_encoder.transform(sample)
        X_encoded.append(encoded_sample)

    X_encoded = np.array(X_encoded)
    y_encoded = label_encoder.transform(y)

    return X_encoded, y_encoded, label_encoder


def train_model(history_length=3):
    """
    Trains a neural network to predict Baccarat outcomes based on historical data.

    Args:
        history_length (int): Number of past game outcomes to include as features.

    Returns:
        model (MLPClassifier): Trained machine learning model.
        scaler (StandardScaler): Fitted scaler for feature normalization.
        label_encoder (LabelEncoder): Fitted label encoder.
    """
    X, y, label_encoder = generate_training_data(num_samples=10000, history_length=history_length)

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize scaler
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Initialize the model
    model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate the model
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    # Save both the model and the scaler and label encoder
    joblib.dump({'model': model, 'scaler': scaler, 'label_encoder': label_encoder}, "baccarat_model_with_history.pkl")

    return model, scaler, label_encoder


if __name__ == "__main__":
    # Optional: Train the model when this script is run directly
    train_model()
