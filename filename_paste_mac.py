"""
파일명 자동 기입 프로그램 (macOS)

사용법
1. 터미널에서 이 프로그램을 실행해 둔다 (창은 켜둔 채로)
2. Finder에서 파일 여러 개 선택 -> Cmd+C
3. 구글 시트에서 시작할 칸을 클릭
4. F8 (맥북은 Fn+F8) 또는 Ctrl+Cmd+8 -> 파일명이 그 칸부터 아래로 한 줄씩 입력됨
5. 다른 폴더에서 다시 Cmd+C -> 이어서 아래 칸에서 반복

처음 한 번: 시스템 설정 > 개인정보 보호 및 보안 > '손쉬운 사용'과 '입력 모니터링'에
터미널(Terminal / iTerm)을 추가하고 켜야 합니다.
"""
import os
import re
import subprocess
import threading
import time
import traceback
import unicodedata

from AppKit import NSPasteboard, NSPasteboardTypeString, NSURL
from pynput import keyboard
from pynput.keyboard import Controller, Key

# ===== 설정 =====
HOTKEYS = ["<f8>", "<ctrl>+<cmd>+8"]  # 실행 키 (맥북은 F8 대신 Fn+F8)
STRIP_EXT = False  # True면 .jpg 같은 확장자 제거
SORT = True        # True면 이름순(숫자 자연 정렬)으로 입력
DELAY = 0.2        # 칸마다 대기 시간(초). 입력이 씹히면 0.35 정도로 올리세요
RATIO_OFFSET = 1   # 파일명에서 찾은 비율(1대1 등)을 오른쪽 몇 번째 칸에 입력할지. 0이면 입력 안 함
# 파일명에 이 단어가 있으면 "이미지_1대1"처럼 앞에 붙여서 입력 (드롭다운 항목 이름에 맞춤)
RATIO_PREFIXES = ["이미지", "카드뉴스"]
# ================

kb = Controller()
_lock = threading.Lock()
_last_set = None
_FKEYS = {f"f{i}" for i in range(1, 13)}


def beep():
    try:
        subprocess.Popen(["afplay", "/System/Library/Sounds/Ping.aiff"])
    except Exception:
        pass


def nfc(s):
    # 맥 파일명은 한글이 분리(NFD)돼 있을 수 있어 합쳐서(NFC) 통일
    return unicodedata.normalize("NFC", s)


def read_names():
    """클립보드에서 파일명 목록을 읽는다 (Finder 파일 복사 / 경로 텍스트 둘 다 지원)."""
    pb = NSPasteboard.generalPasteboard()
    try:
        urls = pb.readObjectsForClasses_options_([NSURL], {"NSPasteboardURLReadingFileURLsOnlyKey": True})
    except Exception:
        urls = None
    if urls:
        return [nfc(os.path.basename(u.path())) for u in urls]

    text = pb.stringForType_(NSPasteboardTypeString)
    if not text or text == _last_set:  # 우리가 방금 넣은 값이면 무시
        return []
    names = []
    for line in str(text).splitlines():
        line = line.strip().strip('"')
        if line:
            names.append(nfc(re.split(r"[\\/]", line)[-1]))
    return names


def set_text(text):
    global _last_set
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    ok = pb.setString_forType_(text, NSPasteboardTypeString)
    _last_set = text
    return bool(ok)


def tap(key):
    kb.press(key)
    kb.release(key)
    time.sleep(0.05)


def paste_here(text):
    if not set_text(text):
        return False
    time.sleep(0.05)
    with kb.pressed(Key.cmd):
        kb.press("v")
        kb.release("v")
    time.sleep(DELAY)
    return True


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


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def run():
    if not _lock.acquire(blocking=False):
        return  # 이미 입력 중
    try:
        print("[실행 키 감지됨]")
        time.sleep(0.5)  # 누르고 있던 조합키를 뗄 시간
        names = read_names()
        if not names:
            print("복사된 파일이 없어요. Finder에서 파일을 먼저 Cmd+C 하세요.")
            return
        if STRIP_EXT:
            names = [os.path.splitext(n)[0] for n in names]
        if SORT:
            names.sort(key=natural_key)

        print(f"{len(names)}개 입력 중... (건드리지 마세요)")
        missing = []
        for n in names:
            if not paste_here(n):
                continue
            if RATIO_OFFSET > 0:
                ratio = find_ratio(n)
                if ratio:
                    for _ in range(RATIO_OFFSET):
                        tap(Key.right)
                    paste_here(ratio)
                    for _ in range(RATIO_OFFSET):
                        tap(Key.left)
                else:
                    missing.append(n)
            tap(Key.down)
        if missing:
            print(f"[알림] 비율을 못 찾은 파일 {len(missing)}개 (비율 칸은 비워둠):")
            for n in missing:
                print("  -", n)
        beep()
        print(f"완료: {len(names)}개")
    except Exception:
        print("[오류가 발생했어요] 아래 내용을 캡처해서 알려주세요.")
        traceback.print_exc()
    finally:
        _lock.release()


def trigger():
    # 리스너를 막지 않도록 별도 스레드에서 실행
    threading.Thread(target=run, daemon=True).start()


def on_press(key):
    # 진단용: 기능키(F1~F12)가 눌릴 때만 이름을 표시
    name = getattr(key, "name", None)
    if name in _FKEYS:
        print(f"[키 입력 확인] {name}")


def main():
    hotkeys = keyboard.GlobalHotKeys({hk: trigger for hk in HOTKEYS})
    hotkeys.start()
    keyboard.Listener(on_press=on_press).start()
    print("=" * 40)
    print(" 파일명 자동 기입 프로그램 실행 중 (Mac)")
    print(" 1) Finder에서 파일 선택 -> Cmd+C")
    print(" 2) 시트에서 시작할 칸 클릭 -> F8 (맥북은 Fn+F8)")
    print("    또는 Ctrl+Cmd+8")
    print("=" * 40)
    hotkeys.join()


if __name__ == "__main__":
    main()
