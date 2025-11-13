import os
from pathlib import Path
import pandas as pd
# from loaders.blob_loader import BlobLoader
from loaders.model_loader import ModelArtifacts
from sqlmodel import Session, select, text
import pandas as pd
#import httpx
#import uuid
import os
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




async def fetch_latest_customers(session: Session, limit: int = 5):
    """
    Fetch the latest 5 customers with complete data from all tables.
    """
    query = text("""
        SELECT 
            c.id AS customer_id,
            b.MonthlyRevenue,
            u.MonthlyMinutes,
            u.OverageMinutes,
            cd.UnansweredCalls,
            cd.CustomerCareCalls,
            u.PercChangeMinutes,
            u.PercChangeRevenues,
            cd.ReceivedCalls,
            b.TotalRecurringCharge,
            d.CurrentEquipmentDays,
            cd.DroppedBlockedCalls,
            c.MonthsInService,
            c.ActiveSubs,
            c.RespondsToMailOffers,
            cd.RetentionCalls,
            cd.RetentionOffersAccepted,
            cd.MadeCallToRetentionTeam,
            c.ReferralsMadeBySubscriber,
            demo.CreditRating,
            demo.IncomeGroup,
            demo.Occupation,
            demo.PrizmCode,
            cd.TotalCalls
        FROM customer c
        JOIN demographics demo ON demo.customer_id = c.id
        JOIN device d ON d.customer_id = c.id
        JOIN billing b ON b.customer_id = c.id
        JOIN usage_minutes u ON u.customer_id = c.id
        JOIN call_details cd ON cd.customer_id = c.id
        ORDER BY c.created_at DESC
        LIMIT :limit
    """)
    result = session.exec(query, {"limit": limit})
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


