# config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# APK 파일 경로
APK_DIR = BASE_DIR / "apks"

APK_PATHS = {
    "검은방 1": APK_DIR / "roomofprey.apk",
    "검은방 2": APK_DIR / "roomofprey2_cert.apk",
    "검은방 3": APK_DIR / "roomofprey3_cert.apk",
    "검은방 4": APK_DIR / "imprison4_epfix.apk",
}

# 아이콘 경로
ICON_DIR = BASE_DIR / "icons"

ICON_PATHS = {
    "검은방 1": ICON_DIR / "1.png",
    "검은방 2": ICON_DIR / "2.png",
    "검은방 3": ICON_DIR / "3.png",
    "검은방 4": ICON_DIR / "4.png",
}