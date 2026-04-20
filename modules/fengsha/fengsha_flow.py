import cv2

from capture.dxcam_capture import DXCamCapture
from modules.fengsha.fengsha_regions import F_PROMPT_REGION, INTERACTION_TEXT_REGION
class FengshaFlow:
    def __init__(self):
        self.dx = DXCamCapture()
        pass
    def check_first_step(self):
        img = self.dx.capture_game_region(F_PROMPT_REGION)
        cv2.imshow("img", img)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
        pass
    def check_second_step(self):
        pass

if __name__ == '__main__':
    f = FengshaFlow()
    f.check_first_step()