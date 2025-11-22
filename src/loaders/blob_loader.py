from azure.storage.blob import BlobServiceClient
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class BlobLoader:
    def __init__(self, container_name: str = None):
        self.conn_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        self.container_name = container_name or os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
        if not self.container_name:
            raise ValueError("Container name must be provided either via argument or AZURE_STORAGE_CONTAINER_NAME env var")

        self.client = BlobServiceClient.from_connection_string(self.conn_str)

    def download(self, blob_path: str, local_path: str):
        container = self.client.get_container_client(self.container_name)
        blob = container.get_blob_client(blob_path)
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            data = blob.download_blob().readall()
            f.write(data)

