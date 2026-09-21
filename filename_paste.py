"""
파일명 자동 기입 프로그램 (Windows)

사용법
1. 이 프로그램을 실행해 둔다 (창은 켜둔 채로)
2. 폴더에서 파일 여러 개 선택 -> Ctrl+C
3. 구글 시트에서 시작할 칸을 클릭
4. F8 (또는 Ctrl+Alt+8) -> 파일명이 그 칸부터 아래로 한 줄씩 입력됨
5. 다른 폴더에서 다시 Ctrl+C -> 다음 칸(이어서 아래)에서 반복

종료: 창 닫기
"""
import os
import re
import time
import traceback

import keyboard
import win32clipboard as wc
import win32con
import winsound

# ===== 설정 =====
HOTKEYS = ["f8", "ctrl+alt+8"]  # 입력 실행 키 (여러 개 가능, 노트북은 Fn+F8)
STRIP_EXT = False  # True면 .jpg 같은 확장자 제거
SORT = True        # True면 이름순(숫자 자연 정렬)으로 입력
DELAY = 0.15       # 칸마다 대기 시간(초). 입력이 씹히면 0.3 정도로 올리세요
RATIO_OFFSET = 1   # 파일명에서 찾은 비율(1대1 등)을 오른쪽 몇 번째 칸에 입력할지. 0이면 입력 안 함
# 파일명에 이 단어가 있으면 "이미지_1대1"처럼 앞에 붙여서 입력 (드롭다운 항목 이름에 맞춤)
RATIO_PREFIXES = ["이미지", "카드뉴스"]
# ================

_last_set = None
_FKEYS = {f"f{i}" for i in range(1, 13)}


def beep(freq, ms):
    try:
        winsound.Beep(freq, ms)
    except Exception:
        pass


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
        print("[오류] 클립보드를 열 수 없어요. 잠시 후 다시 시도하세요.")
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


def find_ratio(name):
    """파일명에서 비율(1대1, 9대16, 1.91대1 등)을 찾아 드롭다운 항목 형태로 돌려준다."""
    m = re.search(r"(\d+(?:\.\d+)?)대(\d+(?:\.\d+)?)", name)
    if not m:
        return None
    ratio = m.group(0)
    for prefix in RATIO_PREFIXES:
        if prefix in name:
            return f"{prefix}_{ratio}"
    return ratio


def paste_here(text):
    if not set_text(text):
        return False
    time.sleep(0.05)
    keyboard.send("ctrl+v")
    time.sleep(DELAY)
    return True


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def run():
    print("[실행 키 감지됨]")
    try:
        names = read_names()
        if not names:
            beep(400, 300)
            print("복사된 파일이 없어요. 폴더에서 파일을 먼저 Ctrl+C 하세요.")
            return
        if STRIP_EXT:
            names = [os.path.splitext(n)[0] for n in names]
        if SORT:
            names.sort(key=natural_key)

        print(f"{len(names)}개 입력 중...")
        missing = []
        for n in names:
            if not paste_here(n):
                continue
            if RATIO_OFFSET > 0:
                ratio = find_ratio(n)
                if ratio:
                    for _ in range(RATIO_OFFSET):
                        keyboard.send("right")
                        time.sleep(0.05)
                    paste_here(ratio)
                    for _ in range(RATIO_OFFSET):
                        keyboard.send("left")
                        time.sleep(0.05)
                else:
                    missing.append(n)
            keyboard.send("down")
            time.sleep(0.05)
        if missing:
            print(f"[알림] 비율을 못 찾은 파일 {len(missing)}개 (비율 칸은 비워둠):")
            for n in missing:
                print("  -", n)
        beep(900, 150)
        print(f"완료: {len(names)}개")
    except Exception:
        print("[오류가 발생했어요] 아래 내용을 캡처해서 알려주세요.")
        traceback.print_exc()


def on_key(event):
    # 진단용: 기능키(F1~F12)가 눌릴 때만 이름을 표시
    if event.event_type == "down" and event.name in _FKEYS:
        print(f"[키 입력 확인] {event.name}")


def main():
    keyboard.hook(on_key)
    for hk in HOTKEYS:
        keyboard.add_hotkey(hk, run)
    keys = " 또는 ".join(h.upper() for h in HOTKEYS)
    print("=" * 40)
    print(" 파일명 자동 기입 프로그램 실행 중")
    print(" 1) 폴더에서 파일 선택 -> Ctrl+C")
    print(f" 2) 시트에서 시작할 칸 클릭 -> {keys}")
    print(" (노트북은 Fn+F8 을 눌러보세요)")
    print("=" * 40)
    keyboard.wait()


if __name__ == "__main__":
    main()
