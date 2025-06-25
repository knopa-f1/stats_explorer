import pandas as pd
from pathlib import Path

from app.config import settings


def load_data() -> pd.DataFrame:
    return pd.read_csv(Path(settings.DATA_PATH))