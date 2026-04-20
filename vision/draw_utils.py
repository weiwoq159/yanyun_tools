import cv2
import numpy as np


def draw_match_boxes(image: np.ndarray, matches: list) -> np.ndarray:
    vis = image.copy()

    for match in matches:
        if not getattr(match, "found", True):
            continue

        cv2.rectangle(
            vis,
            (match.x1, match.y1),
            (match.x2, match.y2),
            (0, 0, 255),
            2
        )

        text = f"{match.name} {match.score:.3f}"
        cv2.putText(
            vis,
            text,
            (match.x1, max(match.y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

    return vis
