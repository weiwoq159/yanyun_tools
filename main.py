from capture.dxcam_capture import DXCamCapture
from modules.reward.reward_detector import RewardDetector
from modules.reward.reward_actions import RewardActions

def main():
    capture = DXCamCapture()
    image = capture.capture_fullscreen()
    detector = RewardDetector()
    actions = RewardActions(window_rect_getter=lambda: get_window_rect(window))
    reward = detector.match_template_best(image, 'healing_card')

    print("yanyun_tools started", reward)


if __name__ == "__main__":
    main()
