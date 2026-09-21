# filename-paste

폴더에서 복사한 **여러 파일의 이름을 구글 시트(또는 엑셀)에 한 번에, 아래로 한 줄씩 자동 입력**해 주는 Windows / macOS 프로그램입니다.
시트 주소·탭·열 설정이 없고, **클릭한 칸부터** 입력됩니다. 어떤 시트 파일이든 동작합니다.

## 사용법

1. 프로그램 실행 (창은 켜둔 채로)
2. 폴더에서 파일 여러 개 선택 → `Ctrl+C`
3. 시트에서 시작할 칸 클릭
4. `F8` → 그 칸부터 아래로 파일명 입력
5. 다른 폴더에서 다시 `Ctrl+C` → 이어서 아래 칸에서 `F8` 반복

입력 중에는 마우스/키보드를 건드리지 마세요.

## 설치

### A. exe (Python 불필요)
[Releases](../../releases)에서 `filename_paste.exe`를 받아 실행합니다.

### B. 소스로 실행
```bash
pip install -r requirements.txt
python filename_paste.py
```
또는 `run.bat` 더블클릭.

## macOS

윈도우와 별도 파일(`filename_paste_mac.py`)을 씁니다.

### 실행파일로 쓰기
[Releases](../../releases)에서 내 맥에 맞는 zip을 받습니다.
- 애플 실리콘(M1~M4): `filename_paste_mac_apple-silicon.zip`
- 인텔 맥: `filename_paste_mac_intel.zip`

zip을 풀고 `filename_paste_mac`을 **우클릭 → 열기**로 실행합니다. (서명되지 않은 앱이라 더블클릭하면 막힐 수 있습니다.) 터미널이 열리며 프로그램이 시작됩니다. 아래 권한 설정을 꼭 해주세요.

### 소스로 실행하기

```bash
python3 -m pip install --user -r requirements-mac.txt
python3 filename_paste_mac.py
```
또는 `run_mac.command` 더블클릭 (처음 한 번 `chmod +x run_mac.command` 필요).

**권한 설정 (처음 한 번)**: 시스템 설정 → 개인정보 보호 및 보안 → **손쉬운 사용**, **입력 모니터링**에 `터미널`(또는 iTerm)을 추가하고 켠 뒤 프로그램을 다시 실행하세요.

**사용**: Finder에서 파일 선택 → `Cmd+C` → 시트 칸 클릭 → `F8`(맥북은 `Fn+F8`) 또는 `Ctrl+Cmd+8`.
F8이 안 먹으면 `Fn+F8`을 누르거나, 시스템 설정 → 키보드에서 'F1, F2 등의 키를 표준 기능 키로 사용'을 켜세요.

## 설정

`filename_paste.py` 상단 값을 수정합니다.

| 이름 | 기본값 | 설명 |
|---|---|---|
| `HOTKEYS` | `["f8", "ctrl+alt+8"]` | 입력 실행 키 (여러 개 가능, 맥은 `"<f8>"` 형식) |
| `RATIO_OFFSET` | `1` | 파일명 속 비율(1대1 등)을 오른쪽 몇 번째 칸에 입력할지 (0이면 끔) |
| `STRIP_EXT` | `False` | `True`면 확장자 제거 |
| `SORT` | `True` | 이름순(숫자 자연 정렬)으로 입력 |
| `DELAY` | `0.15` | 칸마다 대기(초). 입력이 씹히면 `0.25`로 |

## exe 자동 빌드

태그를 push하면 GitHub Actions가 exe를 빌드해 Releases에 올립니다.
```bash
git tag v1.0.0
git push origin v1.0.0
```
Actions 탭에서 `Build exe`를 수동 실행(workflow_dispatch)할 수도 있습니다.

## 동작 방식

클립보드의 파일 목록을 읽어 파일명을 하나씩 클립보드에 넣고 `Ctrl+V` → `↓` 키를 대신 눌러 입력합니다.
경로 텍스트(`Ctrl+Shift+C`로 복사한 경로)도 지원하며 파일명만 추출합니다.

## 참고

- 맥 실행파일은 서명·공증이 안 돼 있어 처음 실행 시 보안 경고가 뜹니다. 우클릭 → 열기로 실행하세요.
- 전역 키보드 훅(`keyboard` 라이브러리)을 쓰기 때문에 일부 백신이 exe를 오탐할 수 있습니다. 걱정되면 소스로 실행하세요.
- 입력이 끝나면 클립보드에 마지막 파일명이 남습니다.

## License

MIT
