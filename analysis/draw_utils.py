from PIL import Image
import numpy as np


def make_mask(mask: np.ndarray, color: tuple[int, int, int]) -> np.ndarray:
    return (
        (mask[..., 0] == color[0])
        & (mask[..., 1] == color[1])
        & (mask[..., 2] == color[2])
    )


def get_timer_mask() -> tuple[tuple[int, int], tuple[int, int]]:
    mask = Image.open("./images/MaskTest.png")
    mask = np.array(mask)[..., :-1]
    red_mask = make_mask(mask, (255, 0, 0))
    y, x = np.where(red_mask)
    y_min, y_max = y.min(), y.max()
    x_min, x_max = x.min(), x.max()
    return (x_min, x_max), (y_min, y_max)


def get_left_mask() -> tuple[tuple[int, int], tuple[int, int]]:
    mask = Image.open("./images/MaskTest.png")
    mask = np.array(mask)[..., :-1]
    green_mask = make_mask(mask, (0, 255, 0))
    y, x = np.where(green_mask)
    y_min, y_max = y.min(), y.max()
    x_min, x_max = x.min(), x.max()
    return (x_min, x_max), (y_min, y_max)


def get_right_mask() -> tuple[tuple[int, int], tuple[int, int]]:
    mask = Image.open("./images/MaskTest.png")
    mask = np.array(mask)[..., :-1]
    blue_mask = make_mask(mask, (0, 0, 255))
    y, x = np.where(blue_mask)
    y_min, y_max = y.min(), y.max()
    x_min, x_max = x.min(), x.max()
    return (x_min, x_max), (y_min, y_max)
