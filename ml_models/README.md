# ML Models

This directory contains trained machine learning models for the EduAutismo IA project.

## Directory Structure

```
ml_models/
├── behavioral_classifier/    # Behavioral classification models
│   ├── model.pkl             # Trained scikit-learn model
│   ├── scaler.pkl            # Feature scaler
│   └── metadata.json         # Model metadata and metrics
│
└── recommender/              # Activity recommendation system
    ├── model.pkl             # Recommendation model
    ├── embeddings.npy        # Activity embeddings
    └── metadata.json         # Model metadata
```

## Model Training

Models should be trained using the scripts in `scripts/ml/`:
```bash
python scripts/ml/train_behavioral_classifier.py
python scripts/ml/train_recommender.py
```

## Model Versioning

- Models are versioned using semantic versioning (e.g., v1.0.0)
- Each version includes metadata with training date, metrics, and parameters
- Production models are stored in S3 for deployment

## Usage

Models are loaded by the application services in `backend/app/services/`.
