import cv2
import numpy as np

from vision.image_utils import to_gray
from vision.schema import TemplateMatchResult


def match_template_all(
    search_image: np.ndarray,
    template_image: np.ndarray,
    template_name: str,
    method: int = cv2.TM_CCOEFF_NORMED,
    offset_x: int = 0,
    offset_y: int = 0,
    threshold: float = 0.82,
) -> list[TemplateMatchResult]:
    search_gray = to_gray(search_image)
    template_gray = to_gray(template_image)

    sh, sw = search_gray.shape[:2]
    th, tw = template_gray.shape[:2]

    if th > sh or tw > sw:
        return []

    result = cv2.matchTemplate(search_gray, template_gray, method)
    ys, xs = np.where(result >= threshold)

    matches = []
    for x, y in zip(xs, ys):
        score = float(result[y, x])
        matches.append(
            TemplateMatchResult(
                name=template_name,
                found=True,
                score=score,
                x1=x + offset_x,
                y1=y + offset_y,
                x2=x + tw + offset_x,
                y2=y + th + offset_y,
            )
        )
    return matches
