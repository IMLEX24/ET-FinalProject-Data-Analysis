import pandas as pd

from .consts import SCREEN_HEIGHT, SCREEN_WIDTH
from .logger_config import logger


def is_valid_data(raw_df: pd.DataFrame) -> None:
    """Check if the data is valid."""
    # check if the data is valid
    if raw_df.shape[0] == 0:
        msg = "The data is empty."
        raise ValueError(msg)
    if not raw_df["timestamp_us"].is_monotonic_increasing:
        msg = "The timestamps are not in increasing order."
        raise ValueError(msg)


def _drop_invalid(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops rows with invalid values in the 'validity' column.
    """
    # drop invalid rows
    invalid_mask = raw_df["validity"] == "Invalid"
    valid_df = raw_df[~invalid_mask].copy()
    valid_df = valid_df.drop(["validity"], axis=1)
    if sum(invalid_mask) > 0:
        logger.info("invalid: %d samples are dropped", sum(invalid_mask))
    return valid_df


def _drop_blink_rows(valid_df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops rows with invalid values in the 'value' column.
    """
    blink_mask = (valid_df["x"] <= 0) | (valid_df["y"] <= 0)
    no_blink_df = valid_df[~blink_mask]
    if sum(blink_mask) > 0:
        logger.info("blink: %d samples are dropped", sum(blink_mask))
    return no_blink_df


def _drop_out_of_screen(no_blink_df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops rows with invalid values in the 'value' column.
    """
    out_of_scr_mask = (no_blink_df["x"] > SCREEN_WIDTH) | (no_blink_df["y"] > SCREEN_HEIGHT)
    if sum(out_of_scr_mask) > 0:
        logger.info("out of screen: %d samples are dropped", sum(out_of_scr_mask))
    et_df = no_blink_df[~out_of_scr_mask].copy()
    return et_df


def _edit_time_stamp(et_df: pd.DataFrame) -> pd.DataFrame:
    # Edit time stamp to seconds
    et_df["timestamp_s"] = et_df["timestamp_us"] * 1e-6
    start_time = et_df["timestamp_s"].iloc[0]

    # Calculate elapsed time
    et_df["elapsed_time_s"] = et_df["timestamp_s"] - start_time

    return et_df


def preprocess(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Preprocesses the data.
    Returns:
    - pd.DataFrame: a dataframe with the following columns:
        - x: x coordinate
        - y: y coordinate
        - timestamp_s: timestamp in seconds
        - elapsed_time_s: elapsed time in seconds
    """
    # check if the data is valid
    is_valid_data(raw_df)
    valid_df = _drop_invalid(raw_df)
    no_blink_df = _drop_blink_rows(valid_df)
    et_df = _drop_out_of_screen(no_blink_df)
    et_df = _edit_time_stamp(et_df)

    return et_df
