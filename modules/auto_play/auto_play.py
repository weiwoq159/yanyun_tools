import json
import time
import pydirectinput


class AutoPlay:
    def __init__(self, src=r"D:\work\mq\yanyun_tools\assets\music\kanong.json"):
        self.bpm = 120
        self.beat_seconds = 60 / self.bpm
        self.events = []

        pydirectinput.PAUSE = 0
        pydirectinput.FAILSAFE = False

        self.note_key_map = {
            "high": {
                "do": "q",
                "re": "w",
                "mi": "e",
                "fa": "r",
                "so": "t",
                "la": "y",
                "si": "u",
            },
            "mid": {
                "do": "a",
                "re": "s",
                "mi": "d",
                "fa": "f",
                "so": "g",
                "la": "h",
                "si": "j",
            },
            "low": {
                "do": "z",
                "re": "x",
                "mi": "c",
                "fa": "v",
                "so": "b",
                "la": "n",
                "si": "m",
            },
        }

        self.load_score(src)

    def load_score(self, src: str):
        with open(src, "r", encoding="utf-8") as json_file:
            score_data = json.load(json_file)

        self.bpm = score_data.get("tempo_bpm", 120)
        self.beat_seconds = 60 / self.bpm
        self.events = score_data.get("events", [])

    def sleep_beats(self, beats: float):
        time.sleep(self.beat_seconds * beats)

    def trigger_notes(self, notes: list[str], octave: str, press_seconds: float = 0.03) -> list[str]:
        octave = octave.strip().lower()
        normalized_notes = [note.strip().lower() for note in notes]
        keys = [self.note_key_map[octave][note] for note in normalized_notes]

        for key in keys:
            pydirectinput.keyDown(key)

        time.sleep(press_seconds)

        for key in keys:
            pydirectinput.keyUp(key)

        return keys

    def play_event(self, event: dict):
        notes = event.get("notes", [])
        octave = event.get("octave")
        duration_beats = event.get("duration_beats", 0)
        pause_beats = event.get("pause_beats", 0)

        total_beats = duration_beats + pause_beats

        if not notes or octave is None:
            self.sleep_beats(total_beats)
            return

        self.trigger_notes(notes, octave, press_seconds=0.03)
        self.sleep_beats(total_beats)

    def play_score(self):
        for index, event in enumerate(self.events, start=1):
            print(index, event)
            self.play_event(event)


if __name__ == "__main__":
    player = AutoPlay()
    player.play_score()