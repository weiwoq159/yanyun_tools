import cv2
import numpy as np


def to_gray(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def crop_region(image: np.ndarray, region: dict) -> np.ndarray:
    return image[region["y1"]:region["y2"], region["x1"]:region["x2"]]
