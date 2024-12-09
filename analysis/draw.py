import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from PIL.Image import Image

from .consts import SCREEN_HEIGHT, SCREEN_WIDTH


def imshow(ax: Axes, img: Image):
    ax.imshow(img, alpha=0.7)

def plot_trial(df: pd.DataFrame, img: Image, title: str) -> None:
    _fig, ax = plt.subplots(tight_layout=True)

    # plot image
    imshow(ax, img)

    # plot eye data
    sc = ax.scatter(
        df["x"],
        df["y"],
        c=df["elapsed_time_s"],
        cmap="viridis",
        s=10,
    )
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Elapsed Time (s)")  #

    # set title
    ax.set_title(title)


def plot_trial_heatmap(df: pd.DataFrame, img: Image, title: str) -> None:
    _fig, ax = plt.subplots(tight_layout=True)

    # plot image
    imshow(ax, img)

    # plot eye data as heatmap
    sns.kdeplot(
        x=df["x"],
        y=df["y"],
        fill=True,
        thresh=0.3,
        cbar=True,
        cmap="coolwarm",
        alpha=0.5,
        levels=30,
        ax=ax,
    )

    # set title
    ax.set_title(title)


def plot_fixations(fix_df: pd.DataFrame, img: Image, title: str) -> None:
    _fig, ax = plt.subplots(tight_layout=True)

    imshow(ax, img)

    _sc = ax.scatter(
        fix_df["x"],
        fix_df["y"],
        # c=fix_df["time_start"],
        c="white",
        edgecolors="black",
        s=20,
    )
    ax.set_title(title)
    ax.set_xlabel("X-coordinate")
    ax.set_ylabel("Y-coordinate")


def plot_scanpath(df_org: pd.DataFrame, img: Image, title: str) -> None:
    df = df_org.copy()
    min_time = df["duration"].min()
    max_time = df["duration"].max()

    # Normalize fixation durations to assign circle sizes proportionally
    size_range = (100, 600)
    df["size"] = (df["duration"] - min_time) / (max_time - min_time) * (
        size_range[1] - size_range[0]
    ) + size_range[0]

    # # Range for transparency of circle
    # alpha_range = (0.4, 0.8)
    # df['alpha'] = (df['duration'] - min_time) / (max_time - min_time) * (alpha_range[1] - alpha_range[0]) + alpha_range[0]

    # Plotting Fixations
    fig, ax = plt.subplots(tight_layout=True)
    # plt.figure(figsize=(12, 8))
    imshow(ax, img)

    # Scatter plot for fixations
    # plt.scatter(df['x'], df['y'], label='Fixations', marker='o', s=df['size'], color='purple', alpha=df['alpha'], edgecolor='white', linewidth= 0.4)
    sc = ax.scatter(
        df["x"],
        df["y"],
        label="Fixations",
        marker="o",
        s=df["size"],
        color="purple",
        alpha=0.4,
        edgecolor="white",
        linewidth=0.4,
    )

    # Plot saccades (lines between consecutive fixations)
    plotted_saccades = False  # Flag to add saccades label only once
    for i in range(1, len(df)):
        x1, y1 = df["x"].iloc[i - 1], df["y"].iloc[i - 1]
        x2, y2 = df["x"].iloc[i], df["y"].iloc[i]
        if not plotted_saccades:  # Add label for saccades only once
            ax.plot(
                [x1, x2],
                [y1, y2],
                color="cyan",
                linestyle="-",
                linewidth=1,
                alpha=0.8,
                label="Saccades",
            )
            plotted_saccades = True
        else:
            ax.plot(
                [x1, x2],
                [y1, y2],
                color="cyan",
                linestyle="-",
                linewidth=1,
                alpha=0.8,
            )

    # Titles and labels
    # plt.title(f'Fixation Visualization for {task_name} Task')
    ax.set_title(title)
    ax.set_xlabel("X-coordinate")
    ax.set_ylabel("Y-coordinate")
    ax.set_xlim(0, SCREEN_WIDTH)  # set x axis limits
    ax.set_ylim(SCREEN_HEIGHT, 0)  # set y axis limits
    ax.legend()
    ax.grid(False)
    ax.axis("on")
