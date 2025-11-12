import os
from dotenv import load_dotenv
# from loaders.model_loader import ModelArtifacts
from azure.storage.blob import BlobServiceClient
from utils.inference import ModelLoader


load_dotenv()

# Singleton pattern to load model once
_model_instance = None

def get_model_instance():
    global _model_instance
    if _model_instance is None:
        # Set up Azure credentials in env so MLflow can access artifacts
        account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        os.environ["AZURE_STORAGE_CONNECTION_STRING"] = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account_name};"
            f"AccountKey={account_key};"
            f"EndpointSuffix=core.windows.net"
        )

        url = f"https://{account_name}.blob.core.windows.net"
        service = BlobServiceClient(account_url=url, credential=account_key)

        loader = ModelLoader(config_path="/app/src/config/config.yaml")
        _model_instance = loader.load_latest_best_model()
    return _model_instance