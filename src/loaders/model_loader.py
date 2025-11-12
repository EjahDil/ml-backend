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


# import joblib
# from pathlib import Path
# from .blob_loader import BlobLoader
# from ml.feature_engineering import FeatureEngineering
# import os
# import yaml
# from dotenv import load_dotenv
# import pandas as pd

# load_dotenv()

# class ModelArtifacts:
#     model = None
#     fe = None
#     model_name = None
#     version = None

#     @classmethod
#     def load(cls, train_df: pd.DataFrame):
#         if cls.model and cls.fe:
#             return

#         # Load model as you already do
#         loader = BlobLoader()
#         model_blob = os.getenv("MODEL_BLOB_PATH")
#         local_model = Path(os.getenv("LOCAL_MODEL_PATH", "/tmp/model.pkl"))
#         loader.download(model_blob, local_model)

#         cls.model = joblib.load(local_model)

#         # Initialize FE (load config)
#         BASE_DIR = Path(__file__).resolve().parent.parent
#         CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
#         with open(CONFIG_FILE, "r") as f:
#             config = yaml.safe_load(f)
            
#         cls.fe = FeatureEngineering(config, unknown_token="_UNK_")

#         # Fit FE on the training data (or representative sample)
#         cls.fe.fit(train_df)


import joblib
from pathlib import Path
from ml.feature_engineering import FeatureEngineering
# import os
import yaml
import pandas as pd

from pathlib import Path
import joblib
import yaml
import pandas as pd

# class ModelArtifacts:
#     models = {}  # dictionary: model_id -> model object
#     fe = None
#     model_names = []  # list of loaded model IDs (optional)

#     @classmethod
#     def load(cls, train_df: pd.DataFrame, models_dir: str = "./models", num_models: int = 2):

#         if cls.models and cls.fe:
#             return

#         models_path = Path(models_dir)

#         # Find all model files matching pattern *_model.pkl
#         model_files = list(models_path.glob("*_model.pkl"))
        
#         if not model_files:
#             raise FileNotFoundError(f"No model files found in {models_dir}")

#         # Sort by modification time descending (latest first)
#         model_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

#         # Pick up to num_models latest files
#         latest_models = model_files[:num_models]

#         # Load models
#         for model_file in latest_models:
#             # Extract model_id from filename
#             model_id = model_file.stem.replace("_model", "")

#             cls.models[model_id] = joblib.load(model_file)

#         # Load FE config (same for all models, adjust if needed)
#         BASE_DIR = Path(__file__).resolve().parent.parent
#         CONFIG_FILE = BASE_DIR / "config" / "config.yaml"

#         with open(CONFIG_FILE, "r") as f:
#             config = yaml.safe_load(f)

#         cls.fe = FeatureEngineering(config, unknown_token="_UNK_")

#         # Fit FE on training df (once)
#         cls.fe.fit(train_df)

#         # Keep track of loaded model IDs
#         cls.model_names = list(cls.models.keys())


import re
import joblib
import yaml
import pandas as pd
from pathlib import Path


# class ModelArtifacts:
#     models = {}
#     fe = None
#     model_name = None

#     @classmethod
#     def load(cls, train_df: pd.DataFrame, models_dir: str = "./models"):
#         """
#         Load the latest trained model and initialize feature engineering.
#         """

#         if cls.models and cls.fe:
#             return

#         models_path = Path(models_dir)
#         model_files = sorted(
#             models_path.glob("*_model.pkl"),
#             key=lambda f: f.stat().st_mtime,
#             reverse=True
#         )

#         if not model_files:
#             raise FileNotFoundError(f"No model files found in {models_dir}")

#         latest_model = model_files[0]

#         # Robust extraction of model ID using regex
#         match = re.search(r"([^/\\]+)_model\.pkl$", latest_model.name)
#         if match:
#             model_id = match.group(1)
#         else:
#             # fallback: use filename without extension
#             model_id = latest_model.stem

#         # Load model safely
#         try:
#             cls.models[model_id] = joblib.load(latest_model)
#             cls.model_name = model_id
#         except Exception as e:
#             raise RuntimeError(f"Failed to load model {latest_model}: {e}")

#         # Load config
#         BASE_DIR = Path(__file__).resolve().parent.parent
#         CONFIG_FILE = BASE_DIR / "config" / "config.yaml"

#         if not CONFIG_FILE.exists():
#             raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

#         with open(CONFIG_FILE, "r") as f:
#             config = yaml.safe_load(f)

#         cls.fe = FeatureEngineering(config, unknown_token="_UNK_")
#         cls.fe.fit(train_df)

#         print(f"Successfully loaded model: {model_id} ({latest_model.name})")


class ModelArtifacts:
    model = None
    fe = None
    model_name = None

    @classmethod
    def load(cls, train_df: pd.DataFrame, models_dir: str = "./models"):
        if cls.model is not None and cls.fe is not None:
            return

        models_path = Path(models_dir)
        model_file = models_path / "model.pkl"

        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")

        BASE_DIR = Path(__file__).resolve().parent.parent
        config_file = BASE_DIR / "config" / "config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        cls.fe = FeatureEngineering(config, unknown_token="_UNK_")
        cls.fe.fit(train_df)

        cls.model = joblib.load(model_file)
        cls.model_name = "model"

        print(f"Successfully loaded model: model")




