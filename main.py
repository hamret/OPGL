# main.py
import subprocess
import time
import webbrowser
from pathlib import Path
from PIL import Image, ImageTk  # Pillow

import tkinter as tk
from tkinter import messagebox, filedialog

from config import (
    APK_PATHS,
    ICON_PATHS,
)
from config_runtime import load_runtime_config, save_runtime_config

BASE_DIR = Path(__file__).resolve().parent

# 런타임 설정 로드
RUNTIME_CONFIG = load_runtime_config()


# ---------- LDPlayer 경로 헬퍼 ----------

def get_ldplayer_path() -> str:
    return RUNTIME_CONFIG["paths"].get("LDPLAYER_PATH", "")


def get_adb_path() -> str:
    return RUNTIME_CONFIG["paths"].get("ADB_PATH", "")


def get_adb_device() -> str:
    return RUNTIME_CONFIG["paths"].get("ADB_DEVICE", "emulator-5554")


# ---------- LDPlayer / ADB 관련 ----------

def check_ldplayer_installed() -> bool:
    ld = get_ldplayer_path()
    adb = get_adb_path()
    if not ld or not adb:
        return False
    return Path(ld).exists() and Path(adb).exists()


def open_ldplayer_download_page():
    url = "https://kr.ldplayer.net"  # 공식 사이트[web:104]
    webbrowser.open(url)
    messagebox.showinfo(
        "LDPlayer 설치 필요",
        "LDPlayer가 설치되어 있지 않습니다.\n\n"
        "1) 브라우저에서 열린 LDPlayer 공식 사이트에서 설치 파일을 다운로드\n"
        "2) 설치 완료 후 통합 런처를 다시 실행해주세요.",
    )


def check_emulator_running() -> bool:
    adb_path = get_adb_path()
    if not Path(adb_path).exists():
        return False
    try:
        result = subprocess.run(
            [adb_path, "devices"],
            capture_output=True,
            text=True,
            check=False,
        )
        return get_adb_device() in result.stdout and "device" in result.stdout
    except Exception:
        return False


def launch_emulator():
    ld_path = get_ldplayer_path()
    try:
        subprocess.Popen([ld_path])
    except Exception as e:
        messagebox.showerror("에뮬 실행 실패", f"LDPlayer 실행에 실패했습니다.\n\n{e}")


def install_apk(apk_path: Path) -> bool:
    if not apk_path.exists():
        messagebox.showerror("APK 오류", f"APK 파일을 찾을 수 없습니다:\n{apk_path}")
        return False

    adb_path = get_adb_path()
    adb_dev = get_adb_device()

    print("[DEBUG] adb_path =", adb_path)
    print("[DEBUG] adb_device =", adb_dev)
    print("[DEBUG] apk_path =", apk_path)

    try:
        cmd = [
            adb_path,
            "-s",
            adb_dev,
            "install",
            "-r",
            str(apk_path),
        ]
        print("[DEBUG] cmd =", cmd)
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        messagebox.showerror("APK 설치 실패", f"APK 설치에 실패했습니다.\n\n{e}")
        return False



# ---------- LDPlayer 경로 설정 ----------

def ask_ldplayer_paths(root, status_label: tk.Label) -> bool:
    """
    LDPlayer.exe 경로를 사용자에게 입력받고,
    같은 폴더/하위 폴더에서 adb.exe 를 찾은 뒤 config.ini 에 저장.
    """
    global RUNTIME_CONFIG

    message = (
        "LDPlayer 설치 경로를 찾지 못했습니다.\n\n"
        "1. 바탕화면 또는 시작 메뉴에서 LDPlayer 아이콘을 우클릭 → '파일 위치 열기'\n"
        "2. 열리는 폴더에서 LDPlayer.exe 경로를 참고하세요.\n\n"
        "이제 'LDPlayer.exe 선택' 창에서 해당 실행 파일을 선택해주세요."
    )
    messagebox.showinfo("LDPlayer 경로 설정", message)

    exe_path = filedialog.askopenfilename(
        parent=root,
        title="LDPlayer.exe 선택",
        filetypes=[("EXE 파일", "*.exe"), ("모든 파일", "*.*")],
    )

    if not exe_path:
        status_label.config(text="LDPlayer 경로 설정이 취소되었습니다.", fg="#d9534f")
        return False

    exe_path = Path(exe_path)
    ld_dir = exe_path.parent

    # ADB 경로 추정
    candidate_adb = None
    try_dirs = [ld_dir] + [p for p in ld_dir.iterdir() if p.is_dir()]
    for sub in try_dirs:
        cand = sub / "adb.exe"
        if cand.exists():
            candidate_adb = cand
            break

    if candidate_adb is None:
        candidate_adb = ld_dir / "adb.exe"
        messagebox.showwarning(
            "ADB 경로 추정 실패",
            "LDPlayer 폴더에서 adb.exe 를 찾지 못했습니다.\n"
            "설치 구조에 따라 다를 수 있습니다.\n\n"
            f"임시로 다음 경로를 사용합니다:\n{candidate_adb}\n\n"
            "필요하다면 나중에 config.ini 파일에서 ADB_PATH 를 직접 수정하세요."
        )

    RUNTIME_CONFIG["paths"]["LDPLAYER_PATH"] = str(exe_path)
    RUNTIME_CONFIG["paths"]["ADB_PATH"] = str(candidate_adb)
    save_runtime_config(RUNTIME_CONFIG)

    status_label.config(text=f"LDPlayer 경로 설정 완료: {exe_path}", fg="#5cb85c")
    return True


# ---------- 런처 로직 ----------

def run_blackroom(game_name: str, status_label: tk.Label):
    """검은방 N 실행 (APK 설치 + 실행)."""
    status_label.config(text=f"{game_name} 준비 중...", fg="#888888")
    status_label.update_idletasks()

    # 1) LDPlayer 설치/경로 확인
    if not check_ldplayer_installed():
        # 먼저 경로 설정 시도
        if not ask_ldplayer_paths(status_label.master, status_label):
            return
        if not check_ldplayer_installed():
            status_label.config(text="LDPlayer 미설치 - 다운로드 안내", fg="#d9534f")
            open_ldplayer_download_page()
            return

    # 2) 에뮬레이터 실행 확인
    if not check_emulator_running():
        status_label.config(text="LDPlayer 실행 중...", fg="#5bc0de")
        launch_emulator()
        time.sleep(5)

    # 3) APK 설치
    apk_path = APK_PATHS[game_name]
    status_label.config(text=f"{game_name} APK 설치 중...", fg="#5bc0de")
    status_label.update_idletasks()
    if not install_apk(apk_path):
        status_label.config(text=f"{game_name} 설치 실패", fg="#d9534f")
        return

    status_label.config(
        text=f"{game_name} 설치 완료 - LDPlayer에서 아이콘을 눌러 실행하세요.",
        fg="#5cb85c",
    )
    messagebox.showinfo(
        "설치 완료",
        f"{game_name} 설치가 완료되었습니다.\n\n"
        "이제 LDPlayer 창에서 해당 게임 아이콘을 눌러 실행해 주세요.",
    )


# ---------- UI ----------

def create_main_window():
    root = tk.Tk()
    root.title("피처폰 게임 통합 런처")
    root.geometry("900x480")
    root.resizable(False, False)
    root.configure(bg="#181818")

    MAX_ICON_WIDTH = 64
    MAX_ICON_HEIGHT = 64

    title_fg = "#ffffff"
    subtitle_fg = "#cccccc"
    bg_color = "#181818"
    card_bg = "#242424"
    card_border = "#3a3a3a"
    text_fg = "#ffffff"

    header_frame = tk.Frame(root, bg=bg_color)
    header_frame.pack(fill="x", pady=(20, 10))

    title = tk.Label(
        header_frame,
        text="피처폰 게임 통합 런처",
        font=("Malgun Gothic", 20, "bold"),
        fg=title_fg,
        bg=bg_color,
    )
    title.pack()

    subtitle = tk.Label(
        header_frame,
        text="LDPlayer 설치 후 원하는 게임을 선택하면 자동으로 설치 및 실행합니다.",
        font=("Malgun Gothic", 10),
        fg=subtitle_fg,
        bg=bg_color,
    )
    subtitle.pack(pady=(5, 0))

    card_frame = tk.Frame(root, bg=bg_color)
    card_frame.pack(pady=20)

    images = {}
    game_names = list(APK_PATHS.keys())

    status_label = tk.Label(
        root,
        text="준비 완료",
        font=("Malgun Gothic", 10),
        fg="#aaaaaa",
        bg=bg_color,
    )
    status_label.pack(pady=(0, 10))

    # 1x4 카드
    for idx, game_name in enumerate(game_names):
        row = 0
        col = idx

        card = tk.Frame(
            card_frame,
            bg=card_bg,
            highlightbackground=card_border,
            highlightthickness=1,
            width=200,
            height=160,
        )
        card.grid(row=row, column=col, padx=15, pady=10)
        card.grid_propagate(False)

        inner = tk.Frame(card, bg=card_bg)
        inner.pack(expand=True)

        # 아이콘
        icon_path = ICON_PATHS[game_name]
        img = None
        try:
            pil_img = Image.open(icon_path)
            pil_img.thumbnail((MAX_ICON_WIDTH, MAX_ICON_HEIGHT), Image.LANCZOS)
            img = ImageTk.PhotoImage(pil_img)
        except Exception as e:
            print(f"[WARN] 아이콘 로딩 실패: {icon_path} → {e}")
            img = None

        if img:
            images[game_name] = img
            icon_label = tk.Label(inner, image=img, bg=card_bg)
            icon_label.pack(pady=(12, 6))
        else:
            icon_label = tk.Label(
                inner,
                text="No Icon",
                fg=subtitle_fg,
                bg=card_bg,
            )
            icon_label.pack(pady=(20, 5))

        name_label = tk.Label(
            inner,
            text=game_name,
            font=("Malgun Gothic", 12, "bold"),
            fg=text_fg,
            bg=card_bg,
        )
        name_label.pack(pady=(0, 5))

        def make_cmd(g=game_name):
            return lambda: run_blackroom(g, status_label)

        btn = tk.Button(
            inner,
            text="실행",
            font=("Malgun Gothic", 10),
            width=12,
            command=make_cmd(),
            bg="#3d7bfd",
            fg="#ffffff",
            activebackground="#335fcc",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
        )
        btn.pack(pady=(0, 10))

    maker_label = tk.Label(
        root,
        text="현재 검은방 4편은 에피소드 DLC 문제로 인해 실행을 권장드리지 않습니다.",
        font=("Malgun Gothic", 10),
        fg="#aaaaaa",
        bg=bg_color,
    )
    maker_label.pack(pady=(0, 10))

    # 하단 LDPlayer 버튼 영역
    bottom_frame = tk.Frame(root, bg=bg_color)
    bottom_frame.pack(pady=(0, 5))

    def on_check_ldplayer():
        if check_ldplayer_installed():
            messagebox.showinfo("확인", "LDPlayer 가 이미 설정되어 있습니다.")
            status_label.config(text="LDPlayer 설치 확인 완료", fg="#5cb85c")
        else:
            status_label.config(text="LDPlayer 미설치 - 홈페이지로 이동", fg="#d9534f")
            open_ldplayer_download_page()

    check_btn = tk.Button(
        bottom_frame,
        text="LDPlayer 설치 확인",
        command=on_check_ldplayer,
        font=("Malgun Gothic", 9),
        bg="#444444",
        fg="#ffffff",
        activebackground="#555555",
        activeforeground="#ffffff",
        relief="flat",
        padx=12,
        pady=5,
        cursor="hand2",
    )
    check_btn.grid(row=0, column=0, padx=5)

    # 새 LDPlayer 경로 설정 버튼
    path_btn = tk.Button(
        bottom_frame,
        text="LDPlayer 경로 설정",
        command=lambda: ask_ldplayer_paths(root, status_label),
        font=("Malgun Gothic", 9),
        bg="#444444",
        fg="#ffffff",
        activebackground="#555555",
        activeforeground="#ffffff",
        relief="flat",
        padx=12,
        pady=5,
        cursor="hand2",
    )
    path_btn.grid(row=0, column=1, padx=5)

    maker_label = tk.Label(
        root,
        text="만든 사람: hamret",
        font=("Malgun Gothic", 10),
        fg="#aaaaaa",
        bg=bg_color,
    )
    maker_label.pack(pady=(0, 10))

    maker_label = tk.Label(
        root,
        text="게임 파일 제공: 불멸에 관하여 / https://gall.dcinside.com/mgallery/board/view/?id=buriedstars&no=10549",
        font=("Malgun Gothic", 10),
        fg="#aaaaaa",
        bg=bg_color,
    )
    maker_label.pack(pady=(0, 10))

    root.images = images
    return root


def main():
    root = create_main_window()
    root.mainloop()


if __name__ == "__main__":
    main()