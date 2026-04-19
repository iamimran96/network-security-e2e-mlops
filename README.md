# Network Security — Phishing URL Detection

An end-to-end MLOps project that detects phishing URLs using machine learning. The pipeline covers data ingestion from MongoDB, validation, transformation, model training with MLflow tracking, and a FastAPI inference server — all containerized with Docker and deployed via GitHub Actions CI/CD.

---

## Project Architecture

```
MongoDB
  └── Data Ingestion
        └── Data Validation (KS drift detection)
              └── Data Transformation (KNN Imputation)
                    └── Model Training (GridSearchCV + MLflow)
                          └── FastAPI App (predict + train endpoints)
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Storage | MongoDB Atlas |
| ML Pipeline | scikit-learn, KNNImputer, GridSearchCV |
| Experiment Tracking | MLflow |
| API | FastAPI, Uvicorn |
| Containerization | Docker |
| CI/CD | GitHub Actions + Docker Hub |
| Cloud Storage | AWS S3 |

---

## ML Models Trained

- Random Forest
- Decision Tree
- Gradient Boosting
- Logistic Regression
- AdaBoost Classifier

Best model is selected by test score and saved to `final_model/model.pkl`.

---

## Project Structure

```
networksecurity/
├── components/
│   ├── data_ingestion.py
│   ├── data_validation.py
│   ├── data_transformation.py
│   └── model_trainer.py
├── entity/
│   ├── config_entity.py
│   └── artifact_entity.py
├── pipelines/
│   └── training_pipeline.py
├── utils/
│   ├── main_utils/utils.py
│   └── ml_utils/
│       ├── model/estimator.py
│       └── metric/classification_metric.py
├── cloud/
│   └── s3_syncer.py
└── constant/
    └── traning_pipeline/__init__.py

data_schema/schema.yaml
final_model/
templates/
app.py
main.py
```

---

## Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd network-security
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set environment variables
Create a `.env` file:
```
MONGO_DB_URL=your_mongodb_connection_string
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

---

## Running the App

### Train the model
```bash
python3 main.py
```

### Start the API server
```bash
python3 app.py
```

API available at `http://localhost:8000`
- `GET /` — Redirects to docs
- `GET /train` — Triggers training pipeline
- `POST /predict` — Upload a CSV file for predictions

### View MLflow experiments
```bash
mlflow ui
```

---

## Docker

### Build and run locally
```bash
docker build -t networksecurity .
docker run -p 8080:8080 \
  -e MONGO_DB_URL=your_mongo_url \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_REGION=us-east-1 \
  networksecurity
```

---

## CI/CD — GitHub Actions

Pipeline triggers on every push to `main`:

1. **CI** — Lint and unit tests
2. **CD (Build)** — Builds Docker image and pushes to Docker Hub
3. **CD (Deploy)** — Pulls and runs latest image on self-hosted runner (EC2)

### GitHub Secrets required

| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `MONGODB_URL` | MongoDB connection string |
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |

