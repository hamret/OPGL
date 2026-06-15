# config_runtime.py
from pathlib import Path
import configparser

CONFIG_FILE = Path(__file__).resolve().parent / "config.ini"

DEFAULTS = {
    "paths": {
        "LDPLAYER_PATH": "",
        "ADB_PATH": "",
        "ADB_DEVICE": "emulator-5554",  # 필요하면 나중에 수정
    }
}


def load_runtime_config():
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE, encoding="utf-8")
    else:
        config.read_dict(DEFAULTS)

    if "paths" not in config:
        config["paths"] = DEFAULTS["paths"]
    return config


def save_runtime_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        config.write(f)