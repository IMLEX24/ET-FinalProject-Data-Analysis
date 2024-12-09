from pathlib import Path

import pandas as pd


def load_data(path: Path) -> pd.DataFrame:
    raw_df = pd.read_csv(path, index_col=0)
    return raw_df
