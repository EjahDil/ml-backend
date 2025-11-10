import os
from pathlib import Path
import pandas as pd
# from loaders.blob_loader import BlobLoader
from loaders.model_loader import ModelArtifacts
from dotenv import load_dotenv


load_dotenv()

def load_additional_data_with_artifacts(filename: str):

    additional_data_dir = os.getenv("ADDITIONAL_DATA_FOLDER")

    if not additional_data_dir:
        raise ValueError("ADDITIONAL_DATA_FOLDER env variable not set")

    data_dir = Path(additional_data_dir)
    data_path = data_dir / filename

    if not data_path.exists():
        raise FileNotFoundError(f"File {filename} not found in {data_dir}")

    df = pd.read_csv(data_path)
    ModelArtifacts.load(df)
    print(f"Additional data loaded and ML artifacts updated from {data_path}")

