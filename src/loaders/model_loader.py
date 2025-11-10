# import pickle
# import joblib
# from pathlib import Path
# from .blob_loader import BlobLoader
# import os
# from dotenv import load_dotenv


# load_dotenv()

# class ModelArtifacts:
#     model = None
#     fe = None

#     @classmethod
#     def load(cls):
#         if cls.model and cls.fe:
#             return  # already loaded

#         loader = BlobLoader()

#         # Azure blob paths from env vars
#         model_blob = os.getenv(
#             "MODEL_BLOB_PATH",
#             "mlflow/1/models/m-1294491f521b479d96686a0db03633ee/artifacts/model.pkl"
#         )
#         fe_blob = os.getenv(
#             "FE_BLOB_PATH",
#             "mlflow/1/8855e82beb474da283e4832922211732/artifacts/mlflow-artifacts/feature_engineer.joblib"
#         )

#         # Local paths from env vars or defaults
#         local_model = os.getenv("LOCAL_MODEL_PATH", "/tmp/model.pkl")
#         local_fe = os.getenv("LOCAL_FE_PATH", "/tmp/feature_engineer.joblib")

#         loader.download(model_blob, local_model)
#         loader.download(fe_blob, local_fe)

#         cls.model = joblib.load(local_model)

#         cls.fe = joblib.load(local_fe)  


import joblib
from pathlib import Path
from .blob_loader import BlobLoader
from ml.feature_engineering import FeatureEngineering
import os
import yaml
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class ModelArtifacts:
    model = None
    fe = None
    model_name = None
    version = None

    @classmethod
    def load(cls, train_df: pd.DataFrame):
        if cls.model and cls.fe:
            return

        # ALWAYS load model locally from project models dir
        local_model = Path("./models/model.pkl")
        cls.model = joblib.load(local_model)

        # Load FE config
        BASE_DIR = Path(__file__).resolve().parent.parent
        CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)

        cls.fe = FeatureEngineering(config, unknown_token="_UNK_")

        # Fit FE on training df
        cls.fe.fit(train_df)


