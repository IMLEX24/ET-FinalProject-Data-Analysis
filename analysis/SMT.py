import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .consts import SCREEN_HEIGHT, SCREEN_WIDTH, SMTConsts


# Utility code for plotting
def in_range(x, start, end):
    return x >= start and x <= end


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


def plot_middle(velocity, plot_data, threshold):
    data_x, data_y, out_x, out_y, threshold_lim, lines, centers = plot_data
    fig, ax = plt.subplots()
    ax.plot(velocity, "-o", alpha=0.8)
    ax.scatter(x=data_x, y=data_y, marker="x", color="r", s=100)
    ax.scatter(x=out_x, y=out_y, marker="x", color="k", s=100)
    for start, end in pairwise(threshold_lim):
        ax.axvspan(xmin=start, xmax=end, color="r", alpha=0.1)
    for start, end in pairwise(lines):
        ax.axvspan(xmin=start, xmax=end, color="g", alpha=0.3)
    for center in centers:
        ax.axvline(x=center, color="k", alpha=0.5)
    ax.axhline(y=threshold, color="k")
    return fig, ax


def calc_euc_velocity(df: pd.DataFrame):
    xs = df["x"].to_numpy()
    ys = df["y"].to_numpy()
    times = df["elapsed_time_s"].to_numpy()
    shift_xs = xs[1:]
    shift_ys = ys[1:]
    shift_times = times[1:]
    # calculate Euclidean distance
    deltaD = ((xs[:-1] - shift_xs) ** 2 + (ys[:-1] - shift_ys) ** 2) ** 0.5
    deltaTheta = deltaD

    deltaTime = shift_times - times[:-1]
    velocity = deltaTheta / deltaTime
    return velocity


# Calculate angular velocity
def calc_vel(df: pd.DataFrame, dist_eye2disp, use_ang_velo=True, plot=False):
    if use_ang_velo:
        velocity = calc_angular_velocity(df, dist_eye2disp)
    else:
        velocity = calc_euc_velocity(df)

    if plot:
        plt.plot(range(0, len(velocity)), velocity)
    return velocity


def calc_angular_velocity(df: pd.DataFrame, dist_eye2disp):
    xs = df["x"].to_numpy()
    ys = df["y"].to_numpy()
    times = df["elapsed_time_s"].to_numpy()

    # assume eye position(x,y) is on the center of the display
    centerOfDisp_x = SCREEN_HEIGHT / 2
    centerOfDisp_y = SCREEN_WIDTH / 2
    # Conver coordination from that top left of the display is (0,0)
    #  to that center of the display is (0,0,dist_eye2disp)
    converted_xs = xs + centerOfDisp_x
    converted_ys = ys + centerOfDisp_y
    converted_zs = np.zeros(len(converted_xs))
    converted_zs[:] = dist_eye2disp
    shift_xs = converted_xs[1:]
    shift_ys = converted_ys[1:]
    shift_zs = converted_zs[1:]
    shift_times = times[1:]

    # theta = arccos{innerProduct(vector_a, vector_b) / |a||b|}
    dist_a = np.sqrt(
        (converted_xs[:-1]) ** 2 + (converted_ys[:-1]) ** 2 + (converted_zs[:-1]) ** 2
    )  # |a|
    dist_b = np.sqrt((shift_xs) ** 2 + (shift_ys) ** 2 + (shift_zs) ** 2)  # |b|
    # innerProduct of vector_a and vector_b
    innerProduct_ab = np.sum(
        np.array(
            [
                converted_xs[:-1] * shift_xs,
                converted_ys[:-1] * shift_ys,
                converted_zs[:-1] * shift_zs,
            ]
        ).T,
        axis=1,
    )
    deltaTheta = np.arccos(innerProduct_ab / (dist_a * dist_b))  # theta
    deltaTime = shift_times - times[:-1]
    velocity = deltaTheta / deltaTime
    return velocity


def grouping_sac_cand(velocity, threshold):
    # funtion that detect saccade candidate according to threshold

    suc_or_other = velocity > threshold
    # Detect indexes that the value switch
    switch_indices = np.where(suc_or_other[:-1] != suc_or_other[1:])[0] + 1
    # Get head indexes of the each group
    group_start_indices = np.insert(switch_indices, 0, 0)
    # head of saccade
    suc_start_indices = group_start_indices[suc_or_other[group_start_indices]]

    group_lengths = np.diff(np.append(group_start_indices, len(suc_or_other)))
    suc_cand_lengths = group_lengths[suc_or_other[group_start_indices]]

    # handle saccade information with zipping
    sac_cand_info = zip(suc_start_indices, suc_cand_lengths)
    return sac_cand_info


def gen_sac_cand(sac_cand_info, eye_vel, width):
    # function that generate saccade candidate with width parameter

    # important things for process
    sac_cands = []
    non_saccade = []

    # not important so much, just for plot
    data_x = []
    data_y = []
    out_x = []
    out_y = []
    threshold_lim = []
    lines = []
    centers = []

    for start, length in sac_cand_info:
        start = int(start)
        length = int(length)
        length -= 1
        if length < 1:
            continue
        sac_cand = eye_vel[start : start + length]
        max_index = start + np.argmax(sac_cand)

        # center of saccade(candidate) period
        center = start + length / 2
        # Detect peaks over the fixation velocity threshold as candidates of saccades
        peak = np.max(sac_cand)
        #
        cand_range = (center - width, center + width)

        # Consider the candidates as real saccades if their peak is
        # within the saccade peak width from the center of the candidates.
        if in_range(max_index, *cand_range):
            sac_cands.append((start, length))
        else:
            non_saccade.append((start, length))

        # data for plot
        lines.append(cand_range[0])
        lines.append(cand_range[1])
        threshold_lim.append(start)
        threshold_lim.append(start + length)
        centers.append(center)
        if in_range(max_index, *cand_range):
            data_x.append(max_index)
            data_y.append(peak)
        else:
            out_x.append(max_index)
            out_y.append(peak)
    return (
        (sac_cands, non_saccade),
        (data_x, data_y, out_x, out_y, threshold_lim, lines, centers),
    )


# classify data period
def detect_fixations(
    df: pd.DataFrame,
    smt_consts: SMTConsts,
    plot: bool = False,
) -> pd.DataFrame:
    threshold = smt_consts.THRESHOLD
    width = smt_consts.WIDTH
    dist_eye2disp = smt_consts.DIST_EYE2DISP
    use_ang_velo = smt_consts.USE_ANG_VELO
    # calculate angular velocity
    velocity = calc_vel(df, dist_eye2disp, use_ang_velo, plot)
    # get saccade candidate
    sac_cand_info = grouping_sac_cand(velocity, threshold)
    ((sac_cands, _non_saccade), plot_data) = gen_sac_cand(sac_cand_info, velocity, width)

    # package it to DataFrame
    df_result = df.copy()
    times = df_result["elapsed_time_s"].to_numpy()
    df_result["label"] = "fixation"
    for start_sac, length in sac_cands:
        start_time = times[start_sac]
        end_time = times[start_sac + length]
        start = df_result["elapsed_time_s"] >= start_time
        end = df_result["elapsed_time_s"] <= end_time
        df_result.loc[start & end, "label"] = "saccade"

    if plot:
        plot_middle(velocity, plot_data, threshold)
    return df_result


def convert_data_into_fixations(df_org: pd.DataFrame) -> pd.DataFrame:
    df = df_org.copy()
    df = df.reset_index()

    labels = (df["label"] == "fixation").to_numpy()
    switch_indices = np.where(labels[:-1] != labels[1:])[0] + 1
    # Get head indexes of the each group
    group_start_indices = np.insert(switch_indices, 0, 0)
    # head of saccade
    fix_start_indices = group_start_indices[labels[group_start_indices]]

    group_lengths = np.diff(np.append(group_start_indices, len(labels)))

    fix_duration = group_lengths[labels[group_start_indices]]
    fixation_df = df.loc[fix_start_indices, ["x", "y"]].copy()
    fixation_df["duration"] = fix_duration

    return fixation_df


"""
    def detect_fixations_smt(self, trial_num: int) -> pd.DataFrame:
        # detect fixations using SMT
        df = self.load_data(trial_num)
        df = df[["elapsed_time_s", "x", "y"]]
        fixations_labels = detect_fixations_smt(
            df,
            threshold=SMTConsts.THRESHOLD,
            width=SMTConsts.WIDTH,
            dist_eye2disp=SMTConsts.DIST_EYE2DISP,
            use_ang_velo=SMTConsts.USE_ANG_VELO,
            plot=False,
        )
        return fixations_labels
        fixation_df = convert_data_into_fixations(fixations_labels)
        # mask = fixation_df["duration"] <= 0
        # fixation_df = fixation_df[~mask]

        return fixation_df

    def plot_fixations_smt(self, trial_num: int) -> pd.DataFrame:
        img = self.load_image(trial_num)
        title = self._get_title(trial_num)
        fix_df = self.detect_fixations_smt(trial_num)
        title = f"{title} (SMT)"
        plot_fixations(fix_df, img, title)
        return fix_df
"""
