from app.db.session import SessionLocal
from app.services.anomaly_training_service import AnomalyTrainingService


def main() -> None:
    db = SessionLocal()

    try:
        training_service = AnomalyTrainingService(db)
        result = training_service.train_global_model()

        print("Training completed.")
        print(f"Model type: {result['model_type']}")
        print(f"Training rows: {result['training_rows']}")
        print(f"Model path: {result['model_path']}")

    finally:
        db.close()


if __name__ == "__main__":
    main()