import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from PIL import Image

from .consts import IDTConsts
from .draw import plot_fixations, plot_trial, plot_trial_heatmap
from .IDT import detect_fixations as detect_fixations_idt
from .io import load_data
from .preprocess import preprocess


class Subject:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.with_timer = root.name.endswith("timer")
        path = self.root / "trials_order.txt"
        with path.open(encoding="utf-8") as f:
            trials_order = json.load(f)
        self.trials_order = [0, *trials_order]  # add the first trial

        fname = self.root.name
        self.name = fname.split("_")[1]

        timestamp_str = fname.split("_")[2]
        timestamp = float(timestamp_str)
        self.timestamp = datetime.fromtimestamp(timestamp)

        self.all_trials = [0, 1, 2, 3, 4]
        self.valid_all()

    def valid_all(self) -> None:
        for trial_num in self.all_trials:
            self.load_data(trial_num)

    def __repr__(self) -> str:
        repr_str = (
            f"Subject(name={self.name}, timestamp={self.timestamp}, with_timer={self.with_timer})"
        )
        return repr_str

    def load_data(self, trial_num: int) -> pd.DataFrame:
        """Load and preprocesses the data.

        Returns:
        - pd.DataFrame: a dataframe with the following columns:
            - x: x coordinate
            - y: y coordinate
            - timestamp_s: timestamp in seconds
            - elapsed_time_s: elapsed time in seconds.

        """
        filename = f"trial_{trial_num}.csv"
        path = self.root / filename
        df = load_data(path)
        df = preprocess(df)
        return df

    def load_image(self, trial_num: int) -> Image.Image:
        # load image
        img_id = self.trials_order[trial_num]
        img_path = f"./images/Trial{img_id}.png"
        img = Image.open(img_path)
        return img

    def detect_fixations_idt(self, trial_num: int) -> pd.DataFrame:
        # detect fixations using IDT
        df = self.load_data(trial_num)
        points = df[["elapsed_time_s", "x", "y"]].values
        fixations = detect_fixations_idt(
            points,
            T_disp=IDTConsts.T_disp,
            T_dur=IDTConsts.T_dur,
        )
        fixation_df = pd.DataFrame(
            fixations, columns=["x", "y", "time_start", "time_end", "duration"]
        )
        return fixation_df

    def _get_title(self, trial_num: int) -> str:
        title = f"Subject: {self.name}, Trial {trial_num}"
        if self.with_timer:
            title += ", with timer"
        else:
            title += ", without timer"
        return title

    def plot_trial(self, trial_num: int) -> None:
        df = self.load_data(trial_num)
        img = self.load_image(trial_num)
        title = self._get_title(trial_num)
        plot_trial(df, img, title)

    def plot_trial_heatmap(self, trial_num: int) -> None:
        df = self.load_data(trial_num)
        img = self.load_image(trial_num)
        title = self._get_title(trial_num)
        plot_trial_heatmap(df, img, title)

    def plot_fixations_idt(self, trial_num: int) -> pd.DataFrame:
        img = self.load_image(trial_num)
        title = self._get_title(trial_num)
        fix_df = self.detect_fixations_idt(trial_num)
        title = f"{title} (IDT)"
        plot_fixations(fix_df, img, title)
        return fix_df
