import numpy as np
import pandas as pd

from .consts import TIME_WINDOW, TRIAL_DURATION
from .draw_utils import get_left_mask, get_right_mask
from .metrics import calculate_metrics
from .subject import Subject
from .utils import log_ts

# ----


def _get_tr_idx(org_df: pd.DataFrame) -> np.ndarray:
    fix_df = org_df.copy()
    left_mask = get_left_mask()
    right_mask = get_right_mask()

    # classify fixations to left or right
    left_fix_cond = (
        (fix_df["x"] >= left_mask[0][0])
        & (fix_df["x"] <= left_mask[0][1])
        & (fix_df["y"] >= left_mask[1][0])
        & (fix_df["y"] <= left_mask[1][1])
    )

    right_fix_cond = (
        (fix_df["x"] >= right_mask[0][0])
        & (fix_df["x"] <= right_mask[0][1])
        & (fix_df["y"] >= right_mask[1][0])
        & (fix_df["y"] <= right_mask[1][1])
    )

    # -1 for left, 1 for right, 0 for other
    fix_df["fixation_area"] = np.where(
        left_fix_cond, -1, np.where(right_fix_cond, 1, 0)
    )

    # get transition between left and right
    transitions = fix_df["fixation_area"].diff().ne(0)
    transitions = transitions[transitions].index.to_numpy()
    return transitions


# devide fixation dataframe with time window
@log_ts
def _divide_fixation_df(fix_df: pd.DataFrame, t: int) -> pd.DataFrame:
    # divide fixation data within time window
    min_t, max_t = t, t + TIME_WINDOW
    divided_df = fix_df[
        (fix_df["time_start"] >= min_t) & (fix_df["time_start"] <= max_t)
    ]
    return divided_df

@log_ts
def _calc_tr_nb_for_time_window(fix_df: pd.DataFrame, t: int):
    # get number transitions for time window
    divided_df = _divide_fixation_df(fix_df, t)
    transitions = _get_tr_idx(divided_df)
    return transitions.shape[0]

@log_ts
def calc_transitions_trial(fix_df: pd.DataFrame):
    # get number transitions for each trial
    transitions = []
    for t in range(0, TRIAL_DURATION, TIME_WINDOW):
        transitions.append(_calc_tr_nb_for_time_window(fix_df, t))
    return transitions

@log_ts
def calc_mean_trans_nb(subj: Subject):
    # get mean number of transitions for all trials
    transisions = []
    for trial_num in range(1, 5):
        idt_df = subj.detect_fixations_idt(trial_num)
        trans = calc_transitions_trial(idt_df)
        transisions.append(trans)
    mean_transitions_nb = np.array(transisions).mean(axis=0)
    return mean_transitions_nb


# ----
@log_ts
def _calc_metrics_for_time_window(fix_df: pd.DataFrame, t: int):
    min_t, max_t = t, t + TIME_WINDOW
    divided_df = fix_df[
        (fix_df["time_start"] >= min_t) & (fix_df["time_start"] <= max_t)
    ]
    metrics_df = calculate_metrics(divided_df)
    return metrics_df


@log_ts
def _calc_metrics_all_time_window(fix_df: pd.DataFrame) -> pd.DataFrame:
    metrics_df = _calc_metrics_for_time_window(fix_df, 0)
    for t in range(TIME_WINDOW, TRIAL_DURATION, TIME_WINDOW):
        metrics_df = pd.concat([metrics_df, _calc_metrics_for_time_window(fix_df, t)])
    metrics_df = metrics_df.reset_index(drop=True)
    return metrics_df


@log_ts
def calc_mean_nb_of_fixes_for_time_window_all_trial(subj: Subject) -> np.ndarray:
    total_nb_of_fixes_all_trial = []
    for i in subj.trials_order:
        fix_df = subj.detect_fixations_idt(i)
        metrics = _calc_metrics_all_time_window(fix_df)
        total_nb_of_fixes = metrics["Total Number of Fixations"].to_list()
        total_nb_of_fixes_all_trial.append(total_nb_of_fixes)
    return np.array(total_nb_of_fixes_all_trial).mean(axis=0)
