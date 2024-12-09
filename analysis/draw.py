import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL.Image import Image


def plot_trial(df: pd.DataFrame, img: Image, title: str) -> None:
    _fig, ax = plt.subplots(tight_layout=True)

    # plot image
    ax.imshow(img)

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
    ax.imshow(img)

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
    ax.imshow(img)

    sc = ax.scatter(
        fix_df["x"],
        fix_df["y"],
        # c=fix_df["time_start"],
        c="white",
        edgecolors="black",
        s=20,
    )
    ax.legend(*sc.legend_elements(), title="Elapsed Time (s)")
    ax.set_title(title)
    ax.set_xlabel("X-coordinate")
    ax.set_ylabel("Y-coordinate")
