import numpy as np
import pandas as pd


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Calculate Average Fixation Duration
    average_fixation_duration = df["duration"].mean()

    # 2. Calculate Saccade Lengths (distance between consecutive fixations)
    x_diff = df["x"].diff().iloc[1:]  # Differences in x coordinates
    y_diff = df["y"].diff().iloc[1:]  # Differences in y coordinates
    saccade_lengths = np.sqrt(
        x_diff**2 + y_diff**2
    )  # Euclidean distance between consecutive fixations

    # 3. Calculate the Average Saccade Length
    average_saccade_length = saccade_lengths.mean()

    # 4. Calculate Total Number of Fixations
    total_fixations = len(df)

    # 5. Calculate Total Scanpath Duration
    total_scanpath_duration = df["time_end"].max() - df["time_start"].min()

    # 6. Prepare metrics for display
    metrics = [
        [
            average_fixation_duration,
            average_saccade_length,
            total_fixations,
            total_scanpath_duration,
        ],
    ]
    metrics_df = pd.DataFrame(metrics)
    metrics_df.columns = [
        "Average Fixation Duration (seconds)",
        "Average Saccade Length (pixels)",
        "Total Number of Fixations",
        "Total Scanpath Duration (seconds)",
    ]

    return metrics_df
