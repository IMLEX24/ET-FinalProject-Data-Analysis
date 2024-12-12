import json
from datetime import datetime
from pathlib import Path
from typing import Literal

import pandas as pd
from PIL import Image

from .consts import IDTConsts, SMTConsts
from .draw import plot_fixations, plot_scanpath, plot_trial, plot_trial_heatmap
from .IDT import detect_fixations as detect_fixations_idt
from .io import load_data
from .preprocess import preprocess
from .SMT import convert_data_into_fixations
from .SMT import detect_fixations as detect_fixations_smt
from .utils import log_ts

AlgoType = Literal["IDT", "SMT"]


class Subject:
    def __init__(
        self,
        root: Path,
        idt_consts: IDTConsts = IDTConsts(),
        smt_consts: SMTConsts = SMTConsts(),
        valid_exp: bool = True,
    ) -> None:
        self.root = root
        self.valid_exp = valid_exp

        # constants
        self.idt_consts = idt_consts
        self.smt_consts = smt_consts

        # load trials order
        path = self.root / "trials_order.txt"
        with path.open(encoding="utf-8") as f:
            trials_order = json.load(f)
        self.task_order = [0, *trials_order]  # add the first trial

        # load properties from file name
        fname = self.root.name

        self.with_timer = fname.endswith("timer")

        self.name = fname.split("_")[1]

        timestamp_str = fname.split("_")[2]
        timestamp = float(timestamp_str)
        self.timestamp = datetime.fromtimestamp(timestamp)

        self.all_trials = [0, 1, 2, 3, 4]
        self.valid_all()

    def trial_num_to_task_id(self, order: int) -> int:
        return self.task_order[order]

    def task_id_to_trial_num(self, trial_num: int) -> int:
        return self.task_order.index(trial_num)

    def valid_all(self) -> None:
        for trial_num in self.all_trials:
            self.load_data(trial_num)

    def __repr__(self) -> str:
        repr_str = f"Subject(name={self.name}, timestamp={self.timestamp}, with_timer={self.with_timer})"
        return repr_str

    @log_ts
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
        img_id = self.task_order[trial_num]
        img_path = f"./images/Trial{img_id}.png"
        img = Image.open(img_path)
        return img

    @log_ts
    def detect_fixations_idt(self, trial_num: int) -> pd.DataFrame:
        # detect fixations using IDT
        df = self.load_data(trial_num)
        points = df[["elapsed_time_s", "x", "y"]].values
        fixations = detect_fixations_idt(points, idt_consts=self.idt_consts)
        fixation_df = pd.DataFrame(
            fixations, columns=["x", "y", "time_start", "time_end", "duration"]
        )
        return fixation_df

    @log_ts
    def detect_fixations_smt(self, trial_num: int) -> pd.DataFrame:
        # detect fixations using SMT
        df = self.load_data(trial_num)
        df = df[["elapsed_time_s", "x", "y"]]
        fixations_labels = detect_fixations_smt(
            df,
            smt_consts=self.smt_consts,
            plot=False,
        )
        fixation_df = convert_data_into_fixations(fixations_labels)

        return fixation_df

    def _get_title_base(self, trial_num: int) -> str:
        title = f"Subject: {self.name}, Trial {trial_num}"
        if self.with_timer:
            title += ", with timer"
        else:
            title += ", without timer"
        return title

    def plot_trial(self, trial_num: int) -> None:
        df = self.load_data(trial_num)
        img = self.load_image(trial_num)
        title = self._get_title_base(trial_num)
        title = f"{title} (Raw)"
        plot_trial(df, img, title)

    def plot_trial_heatmap(self, trial_num: int) -> None:
        df = self.load_data(trial_num)
        img = self.load_image(trial_num)
        title = self._get_title_base(trial_num)
        title = f"{title} (Heatmap)"
        plot_trial_heatmap(df, img, title)

    def plot_fixations_idt(self, trial_num: int) -> pd.DataFrame:
        img = self.load_image(trial_num)
        title = self._get_title_base(trial_num)
        fix_df = self.detect_fixations_idt(trial_num)
        title = f"{title} (IDT)"
        plot_fixations(fix_df, img, title)
        return fix_df

    def plot_fixations(self, trial_num: int, algorithm: AlgoType) -> pd.DataFrame:
        if algorithm == "IDT":
            fix_df = self.detect_fixations_idt(trial_num)
        elif algorithm == "SMT":
            fix_df = self.detect_fixations_smt(trial_num)
        else:
            raise ValueError(f"Invalid algorithm: {algorithm}")
        img = self.load_image(trial_num)
        title = self._get_title_base(trial_num)
        title = "Fixations of " + title + f" ({algorithm})"
        plot_fixations(fix_df, img, title)
        return fix_df

    def plot_scanpath(self, trial_num: int, algo: AlgoType) -> pd.DataFrame:
        if algo == "IDT":
            fix_df = self.detect_fixations_idt(trial_num)
        elif algo == "SMT":
            fix_df = self.detect_fixations_smt(trial_num)
        else:
            raise ValueError(f"Invalid algorithm: {algo}")

        img = self.load_image(trial_num)
        title = self._get_title_base(trial_num)
        title = "Scanpath of " + title + f" ({algo})"
        plot_scanpath(fix_df, img, title)
        return fix_df

    def _plot_scanpath(self, fix_df: pd.DataFrame, trial_num: int) -> pd.DataFrame:
        img = self.load_image(trial_num)
        title = self._get_title_base(trial_num)
        title = "Scanpath of " + title
        plot_scanpath(fix_df, img, title)
        return fix_df
