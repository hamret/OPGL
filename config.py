from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    # PyInstaller로 빌드된 exe인 경우
    BASE_DIR = Path(sys._MEIPASS)
else:
    # 개발 환경 (py 파일로 실행)
    BASE_DIR = Path(__file__).resolve().parent

# LDPlayer 경로 (설치 후 실제 경로로 수정)
LDPLAYER_PATH = r"C:\Program Files\LDPlayer\LDPlayer.exe"
ADB_PATH = r"C:\Program Files\LDPlayer\LDPlayer4.0\adb.exe"
ADB_DEVICE = "127.0.0.1:5554"

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