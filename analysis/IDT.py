import numpy as np


def detect_fixations(points, T_disp, T_dur):  # noqa: ANN001, ANN201, N803, PLR0914
    # Initialize fixation data
    fixations = []
    # initialize the moving window
    window_start = 0
    window_end = 0
    # data points
    n_points = len(points)

    while window_end < n_points:
        # calculate the moving window
        window_points = points[window_start : window_end + 1]
        x_max, x_min = np.max(window_points[:, 1]), np.min(window_points[:, 1])
        y_max, y_min = np.max(window_points[:, 2]), np.min(window_points[:, 2])
        # calculate the dispersion
        dispersion = (x_max - x_min) + (y_max - y_min)

        if dispersion <= T_disp:
            duration = (
                points[window_end, 0] - points[window_start, 0]
            )  # calculate the duration and change to ms
            if duration <= T_dur:
                window_end += 1  # the window moves to the right
            else:
                # Calculate fixation properties
                centroid_x = np.mean(window_points[:, 1])
                centroid_y = np.mean(window_points[:, 2])
                fixation_start = points[window_start, 0]
                fixation_end = points[window_end - 1, 0]
                fixation_duration = (
                    fixation_end - fixation_start
                )  # calculate the fixation duration and change to ms
                fixations.append(
                    [
                        centroid_x,
                        centroid_y,
                        fixation_start,
                        fixation_end,
                        fixation_duration,
                    ]
                )  # save the fixation datas
                window_start = window_end
        else:
            window_start += 1
            window_end = window_start

    return fixations
