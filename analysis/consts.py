# Display settings
SCREEN_WIDTH: int = 1920  # 2560
SCREEN_HEIGHT: int = 1080  # 1440


# I-DT settings
class IDTConsts:
    T_disp: int = 50  # the dispersion threshold 1° of visual angle
    T_dur: float = 0.1  # 100  # generally 100-200ms


class SMTConsts:
    USE_ANG_VELO: bool = True
    DIST_EYE2DISP: int = 50  # cm
    WIDTH: int = 8
    THRESHOLD: float = 0.015
