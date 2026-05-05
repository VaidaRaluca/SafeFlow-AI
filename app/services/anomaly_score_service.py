import uuid
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.repositories.transaction_repository import TransactionRepository
from app.services.anomaly_feature_service import AnomalyFeatureService
from app.core.config import settings

MODEL_PATH = settings.MODEL_PATH


class AnomalyScoreService:
    """
    anomaly_score:
    - 0.0 = normal
    - 1.0 = highly anomalous
    """

    def __init__(self, db: Session) -> None:
        self.transaction_repository = TransactionRepository(db)
        self.feature_service = AnomalyFeatureService(db)

    def calculate_anomaly_score_for_transaction(
        self,
        transaction_id: uuid.UUID,
    ) -> float:
        transaction = self.transaction_repository.get_transaction_by_id(transaction_id)

        if transaction is None:
            raise ValueError(f"Transaction not found: {transaction_id}")

        return self.calculate_anomaly_score(transaction)

    def calculate_anomaly_score(self, transaction) -> float:
        model_bundle = self._load_model_bundle()

        model = model_bundle["model"]
        scaler = model_bundle["scaler"]
        feature_columns = model_bundle["feature_columns"]
        model_score_min = model_bundle["model_score_min"]
        model_score_max = model_bundle["model_score_max"]

        feature_row = self.feature_service.build_feature_row(transaction)

        feature_df = pd.DataFrame([feature_row])
        feature_df = feature_df[feature_columns]

        scaled_features = scaler.transform(feature_df)

        raw_score = float(model.decision_function(scaled_features)[0])

        return self._convert_raw_score_to_anomaly_score(
            raw_score=raw_score,
            model_score_min=model_score_min,
            model_score_max=model_score_max,
        )

    def _load_model_bundle(self) -> dict[str, Any]:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Run: python -m scripts.train_anomaly_model"
            )

        model_bundle = joblib.load(MODEL_PATH)

        required_keys = {
            "model",
            "scaler",
            "feature_columns",
            "model_score_min",
            "model_score_max",
        }

        missing_keys = required_keys - set(model_bundle.keys())

        if missing_keys:
            raise ValueError(
                f"Model bundle is missing required keys: {missing_keys}. "
                "Retrain the model with the updated AnomalyTrainingService."
            )

        return model_bundle

    @staticmethod
    def _convert_raw_score_to_anomaly_score(
        raw_score: float,
        model_score_min: float,
        model_score_max: float,
    ) -> float:
        """
        IsolationForest decision_function:
        - higher raw_score = more normal
        - lower raw_score = more anomalous

        Project anomaly_score:
        - 0.0 = normal
        - 1.0 = anomalous
        """

        if model_score_max == model_score_min:
            return 0.5

        normalized_normality = (
            (raw_score - model_score_min)
            / (model_score_max - model_score_min)
        )

        anomaly_score = 1.0 - normalized_normality
        anomaly_score = max(0.0, min(1.0, anomaly_score))

        return round(anomaly_score, 4)