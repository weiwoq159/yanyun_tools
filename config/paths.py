from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
REWARD_TEMPLATE_DIR = TEMPLATES_DIR / "reward"

MODELS_DIR = BASE_DIR / "models"
DEBUG_OUTPUT_DIR = BASE_DIR / "debug" / "output"



