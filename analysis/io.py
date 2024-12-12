from pathlib import Path

import pandas as pd


def load_path(results_root: Path) -> tuple[list[Path], list[Path]]:
    timer_subj_roots = []
    control_subj_roots = []

    results_root = Path("./results/subjects")
    for root in results_root.glob("trial_*"):
        if (root / "ignore_this").exists():
            continue
        if root.name.endswith("timer"):
            timer_subj_roots.append(root)
        else:
            control_subj_roots.append(root)
    return timer_subj_roots, control_subj_roots


def load_data(path: Path) -> pd.DataFrame:
    raw_df = pd.read_csv(path, index_col=0)
    return raw_df
