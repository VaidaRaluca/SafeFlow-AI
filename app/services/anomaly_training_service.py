from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.services.anomaly_feature_service import AnomalyFeatureService
from app.core.config import settings

MIN_TRAINING_ROWS = 30

MODEL_DIR = settings.MODEL_DIR
GLOBAL_MODEL_FILENAME = settings.GLOBAL_MODEL_FILENAME


class AnomalyTrainingService:

    def __init__(self, db: Session) -> None:
        self.feature_service = AnomalyFeatureService(db)

    def train_global_model(self) -> dict[str, Any]:
        feature_rows = self.feature_service.build_global_training_dataset()

        if len(feature_rows) < MIN_TRAINING_ROWS:
            raise ValueError(
                f"Not enough safe transactions to train global model. "
                f"Required: {MIN_TRAINING_ROWS}, found: {len(feature_rows)}"
            )

        feature_columns = self.feature_service.get_feature_columns()

        training_df = pd.DataFrame(feature_rows)

        training_df = training_df[feature_columns]

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(training_df)

        model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42,
        )

        model.fit(scaled_features)

        model_path = self._get_global_model_path()

        MODEL_DIR.mkdir(parents=True, exist_ok=True)

        training_raw_scores = model.decision_function(scaled_features)

        model_score_min = float(training_raw_scores.min())
        model_score_max = float(training_raw_scores.max())
        joblib.dump(
            {
                "model": model,
                "scaler": scaler,
                "feature_columns": feature_columns,
                "training_rows": len(training_df),
                "model_type": "global",
                "model_score_min": model_score_min,
                "model_score_max": model_score_max,
            },
            model_path,
        )

        return {
            "model_type": "global",
            "training_rows": len(training_df),
            "feature_columns": feature_columns,
            "model_path": str(model_path),
            "message": "Global Isolation Forest model trained successfully",
        }

    @staticmethod
    def _get_global_model_path() -> Path:
        return MODEL_DIR / GLOBAL_MODEL_FILENAME