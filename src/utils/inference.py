import os
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
from dotenv import load_dotenv
import logging
import yaml

load_dotenv()

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

class ModelLoader:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.mlflow_config = self.config['mlflow']

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

        if not tracking_uri:
            raise EnvironmentError("MLFLOW_TRACKING_URI environment variable not set")

        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()

    def load_latest_best_model(self):
        experiment_name = self.mlflow_config['experiment_name']
        experiment = self.client.get_experiment_by_name(experiment_name)

        if experiment is None:
            raise ValueError(f"Experiment '{experiment_name}' not found")

        runs = self.client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="attributes.run_name LIKE 'best_model_%'",
            order_by=["attributes.start_time DESC"]
        )

        if not runs:
            raise ValueError("No best model runs found")

        latest_run = runs[0]
        run_id = latest_run.info.run_id
        logger.info(f"Loading latest best model from run ID: {run_id}")
        
        model_uri = f"runs:/{run_id}/best_model"
        
        model = mlflow.sklearn.load_model(model_uri)
        
        return model


# if __name__ == "__main__":

#     account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
#     account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

#     os.environ["AZURE_STORAGE_CONNECTION_STRING"] = (
#         f"DefaultEndpointsProtocol=https;"
#         f"AccountName={account_name};"
#         f"AccountKey={account_key};"
#         f"EndpointSuffix=core.windows.net"
#     )

#     url = f"https://{account_name}.blob.core.windows.net"
#     service = BlobServiceClient(account_url=url, credential=account_key)

#     try:
#         print("..."*60)
#         loader = ModelLoader(config_path='configs/train_config.yml')

#         # --- Fetch model ---
#         model = loader.load_latest_best_model()

#         # --- Predict on a sample dataset ---
#         sample_data = pd.read_csv("data/sample.csv")
#         predictions = model.predict(sample_data)

#         print("Predictions:")
#         print(predictions[:10])  # show first few predictions

#     except Exception as e:
#         logger.error(f"Error loading model or predicting: {str(e)}")