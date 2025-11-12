import os
from pathlib import Path
import pandas as pd
# from loaders.blob_loader import BlobLoader
from loaders.model_loader import ModelArtifacts
from dotenv import load_dotenv


load_dotenv()

def load_data_and_models(
    data_filename: str,
    models_dir: str | None = None,
):
    # Load additional data
    additional_data_dir = os.getenv("ADDITIONAL_DATA_FOLDER")

    if not additional_data_dir:
        raise ValueError("ADDITIONAL_DATA_FOLDER env variable not set")

    data_path = Path(additional_data_dir) / data_filename

    if not data_path.exists():
        raise FileNotFoundError(f"File {data_filename} not found in {additional_data_dir}")

    df = pd.read_csv(data_path)

    print(f"Additional data loaded from {data_path} (shape={df.shape})")

    # Load model artifacts
    models_dir = os.getenv("MODEL_DIR", "./models")

    ModelArtifacts.load(train_df=df)

    print(f"Model artifacts initialized from {models_dir}")

    # return df, ModelArtifacts.models


