import os
import sys
import mlflow

import certifi
import pymongo

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipelines.training_pipeline import TrainingPipeline

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from networksecurity.constant.traning_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]


app = FastAPI(
    title="Network Security API",
    description="API for training and predicting network security",
    version="1.0.0"
)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocesor = load_object("final_model/preprocessor.pkl")
        model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        total = len(y_pred)
        phishing_count = int((y_pred == 1).sum())
        legit_count = int((y_pred == 0).sum())

        with mlflow.start_run(run_name="inference"):
            mlflow.log_metric("total_predictions", total)
            mlflow.log_metric("phishing_count", phishing_count)
            mlflow.log_metric("legit_count", legit_count)
            mlflow.log_metric("phishing_rate", phishing_count / total)

        os.makedirs('prediction_output', exist_ok=True)
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
    except Exception as e:
        raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    app_run(app, host="localhost", port=8000)

