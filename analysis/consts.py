import json
from pathlib import Path

# Display settings
SCREEN_WIDTH: int = 1920  # defaults: 1920
SCREEN_HEIGHT: int = 1080  # defaults: 1080

# Experiment settings
TRIAL_DURATION: int = 20  # defaults: 20s

# Postprocess settings
TIME_WINDOW: int = 4  # defaults: 5s

# Misc settings
MASK_IMAGE_PATH = Path("./images/MaskTest.png")


class AlgoConsts:
    def export_to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.__dict__, f, indent=2)


# I-DT settings
class IDTConsts(AlgoConsts):
    def __init__(
        self,
        t_disp: int = 50, # defaults: 50
        t_dur: float = 0.1, # defaults: 0.1s
    ) -> None:
        self.T_disp = t_disp  # the dispersion threshold 1° of visual angle
        self.T_dur = t_dur  # 100  # generally 100-200ms


# SMT settings
class SMTConsts(AlgoConsts):
    def __init__(
        self,
        use_ang_velo: bool = True,
        dist_eye2disp: float = 50.0,  # cm,
        width: float = 10, 
        threshold: float = 0.2,
    ) -> None:
        self.USE_ANG_VELO = use_ang_velo
        self.DIST_EYE2DISP = dist_eye2disp
        self.WIDTH = width
        self.THRESHOLD = threshold
