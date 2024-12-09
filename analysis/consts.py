import json

# Display settings
SCREEN_WIDTH: int = 1920  # 2560
SCREEN_HEIGHT: int = 1080  # 1440


class AlgoConsts:
    def export_to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.__dict__, f, indent=2)


# I-DT settings
class IDTConsts(AlgoConsts):
    def __init__(self, t_disp: int = 50, t_dur: float = 0.1) -> None:
        self.T_disp = t_disp  # the dispersion threshold 1° of visual angle
        self.T_dur = t_dur  # 100  # generally 100-200ms


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
