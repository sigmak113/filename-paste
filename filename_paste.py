"""
파일명 자동 기입 프로그램 (Windows)

사용법
1. 이 프로그램을 실행해 둔다 (창은 켜둔 채로)
2. 폴더에서 파일 여러 개 선택 -> Ctrl+C
3. 구글 시트에서 시작할 칸을 클릭
4. F8 -> 파일명이 그 칸부터 아래로 한 줄씩 입력됨
5. 다른 폴더에서 다시 Ctrl+C -> 다음 칸(이어서 아래)에서 F8 반복

종료: 창에서 Ctrl+C 또는 창 닫기
"""
import os
import re
import time

import keyboard
import win32clipboard as wc
import win32con
import winsound

# ===== 설정 =====
HOTKEY = "f8"      # 입력 실행 키
STRIP_EXT = False  # True면 .jpg 같은 확장자 제거
SORT = True        # True면 이름순(숫자 자연 정렬)으로 입력
DELAY = 0.15       # 칸마다 대기 시간(초). 입력이 씹히면 0.25 정도로 올리세요
# ================

_last_set = None


def _open_clipboard():
    for _ in range(20):
        try:
            wc.OpenClipboard()
            return True
        except Exception:
            time.sleep(0.05)
    return False


def read_names():
    """클립보드에서 파일명 목록을 읽는다 (파일 복사 / 경로 텍스트 둘 다 지원)."""
    if not _open_clipboard():
        return []
    try:
        if wc.IsClipboardFormatAvailable(win32con.CF_HDROP):
            paths = wc.GetClipboardData(win32con.CF_HDROP)
            return [os.path.basename(p) for p in paths]
        if wc.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text = wc.GetClipboardData(win32con.CF_UNICODETEXT)
            if text == _last_set:  # 우리가 방금 넣은 값이면 무시
                return []
            names = []
            for line in text.splitlines():
                line = line.strip().strip('"')
                if line:
                    names.append(re.split(r"[\\/]", line)[-1])
            return names
    finally:
        wc.CloseClipboard()
    return []


def set_text(text):
    global _last_set
    if not _open_clipboard():
        return False
    try:
        wc.EmptyClipboard()
        wc.SetClipboardData(win32con.CF_UNICODETEXT, text)
        _last_set = text
        return True
    finally:
        wc.CloseClipboard()


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def run():
    names = read_names()
    if not names:
        winsound.Beep(400, 300)
        print("복사된 파일이 없어요. 폴더에서 파일을 먼저 Ctrl+C 하세요.")
        return
    if STRIP_EXT:
        names = [os.path.splitext(n)[0] for n in names]
    if SORT:
        names.sort(key=natural_key)

    print(f"{len(names)}개 입력 중...")
    for n in names:
        if not set_text(n):
            continue
        time.sleep(0.05)
        keyboard.send("ctrl+v")
        time.sleep(DELAY)
        keyboard.send("down")
        time.sleep(0.05)
    winsound.Beep(900, 150)
    print(f"완료: {len(names)}개")


def main():
    keyboard.add_hotkey(HOTKEY, run, trigger_on_release=True)
    print("=" * 40)
    print(" 파일명 자동 기입 프로그램 실행 중")
    print(f" 1) 폴더에서 파일 선택 -> Ctrl+C")
    print(f" 2) 시트에서 시작할 칸 클릭 -> {HOTKEY.upper()}")
    print("=" * 40)
    keyboard.wait()


if __name__ == "__main__":
    main()
