from fastapi import APIRouter, Depends, HTTPException, Request, status
import pandas as pd
from sqlmodel import Session, select
from schemas.churn_input import ChurnInput
from models.model import User, Prediction, PredictionLog, Feedback, MLModel
from controllers.middleware.auth import get_current_user, get_session
from schemas.schema import PredictionRead, PredictionRequest
from typing import List
from loaders.model_loader import ModelArtifacts
from sqlmodel import delete
from utils.get_model import get_model_instance


router = APIRouter(prefix="/predict", tags=["Prediction"])

### Optimized prediction endpoint
@router.post("/", summary="Predict Customer Churn", response_model=dict)
def predict_churn(
    data: ChurnInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    print(f"Prediction request made by user: {current_user.username}")

    df = pd.DataFrame([data.model_dump()])

    # Check if models are loaded and pick the latest model
    if not ModelArtifacts.models or not ModelArtifacts.model_names:
        raise HTTPException(status_code=500, detail="Models are not loaded")

    latest_model_id = ModelArtifacts.model_names[0]
    latest_model = ModelArtifacts.models[latest_model_id]

    # Transform input features
    X = ModelArtifacts.fe.transform(df)

    # Predict using the latest model
    y_pred = latest_model.predict(X)[0]
    prob = float(latest_model.predict_proba(X)[0, 1])

    # Try to find the MLModel record by model name (latest_model_id)
    model_record = session.exec(
        select(MLModel).where(MLModel.name == latest_model_id)
    ).first()

    # If not found, create it
    if not model_record:
        model_record = MLModel(
            name=latest_model_id,
            version="unknown",
            description=f"Auto-created record for model {latest_model_id}"
        )
        session.add(model_record)
        session.commit()
        session.refresh(model_record)

    # Store prediction with the model_id foreign key
    prediction_record = Prediction(
        user_id=current_user.id,
        input_data=df.to_json(),
        prediction=int(y_pred),
        probability=prob,
        model_id=model_record.id
    )

    session.add(prediction_record)
    session.commit()
    session.refresh(prediction_record)

    # Log prediction request metadata
    log_record = PredictionLog(
        prediction_id=prediction_record.id,
        user_id=current_user.id,
        request_ip=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    session.add(log_record)
    session.commit()

    return {
        "user": current_user.username,
        "prediction": int(y_pred),
        "probability": prob,
        "prediction_id": prediction_record.id,
        "model_version": latest_model_id
    }




@router.post("/predict-from-call-session/", summary="Predict churn from call session data")
def predict_from_call_session(
    request: PredictionRequest,
    session: Session = Depends(get_session)
):
    # Extract external_customer_id from request data
    external_customer_id = request.customer_id

    if external_customer_id is None:
        raise HTTPException(status_code=400, detail="Missing customer_id")

    # If user_id is passed, convert, else set None
    # user_id_str = request.current_user.get("id") if request.current_user else None
    # user_id = UUID(user_id_str) if user_id_str else None

    # Data for prediction
    df = pd.DataFrame([request.data])

    X = ModelArtifacts.fe.transform(df)
    y_pred = ModelArtifacts.model.predict(X)[0]
    prob = float(ModelArtifacts.model.predict_proba(X)[0, 1])

    prediction_record = Prediction(
        external_customer_id=external_customer_id,
        input_data=df.to_json(),
        prediction=int(y_pred),
        probability=prob
    )
    session.add(prediction_record)
    session.commit()
    session.refresh(prediction_record)

    return {
        "external_customer_id": external_customer_id,
        "prediction": int(y_pred),
        "probability": prob,
        "prediction_id": prediction_record.id,
        "model_version": ModelArtifacts.version
    }



### Optimized prediction endpoint
@router.post("/best_model", summary="Predict Customer Churn", response_model=dict)
def predict_churn(
    data: ChurnInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    print(f"Prediction request made by user: {current_user.username}")

    df = pd.DataFrame([data.model_dump()])

    # Load model singleton
    model = get_model_instance()
    
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Predict directly, assuming model includes all preprocessing
    y_pred = model.predict(df)[0]
    prob = float(model.predict_proba(df)[0, 1])

    # Save or get MLModel record
    latest_model_id = "best_model"  # or extract model version from MLflow run info if needed
    model_record = session.exec(
        select(MLModel).where(MLModel.name == latest_model_id)
    ).first()

    if not model_record:
        model_record = MLModel(
            name=latest_model_id,
            version="unknown",
            description=f"Auto-created record for model {latest_model_id}"
        )
        session.add(model_record)
        session.commit()
        session.refresh(model_record)

    prediction_record = Prediction(
        user_id=current_user.id,
        input_data=df.to_json(),
        prediction=int(y_pred),
        probability=prob,
        model_id=model_record.id
    )
    session.add(prediction_record)
    session.commit()
    session.refresh(prediction_record)

    log_record = PredictionLog(
        prediction_id=prediction_record.id,
        user_id=current_user.id,
        request_ip=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    session.add(log_record)
    session.commit()

    return {
        "user": current_user.username,
        "prediction": int(y_pred),
        "probability": prob,
        "prediction_id": prediction_record.id,
        "model_version": latest_model_id
    }






# Endpoint to list all predictions

@router.get("/predictions/", response_model=List[PredictionRead])
def list_predictions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all predictions in the database.
    
    Authentication is required, but predictions are not user-specific.
    """
    predictions = session.exec(select(Prediction)).all()
    return predictions



# Endpoint: Get a single prediction

@router.get("/predictions/{prediction_id}", response_model=PredictionRead)
def get_prediction(
    prediction_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # endpoint still protected
):
    """
    Retrieve a single prediction by its ID.
    
    Authentication is required, but predictions are not user-specific.
    """
    prediction = session.get(Prediction, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction



@router.delete("/predictions/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(
    prediction_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    prediction = session.get(Prediction, prediction_id)

    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Delete feedbacks linked to the prediction
    session.exec(delete(Feedback).where(Feedback.prediction_id == prediction_id))
    
    session.delete(prediction)
    session.commit()