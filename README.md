# filename-paste

폴더에서 복사한 **여러 파일의 이름을 구글 시트(또는 엑셀)에 한 번에, 아래로 한 줄씩 자동 입력**해 주는 Windows 프로그램입니다.
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

## 설정

`filename_paste.py` 상단 값을 수정합니다.

| 이름 | 기본값 | 설명 |
|---|---|---|
| `HOTKEY` | `"f8"` | 입력 실행 키 |
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

- Windows 전용입니다.
- 전역 키보드 훅(`keyboard` 라이브러리)을 쓰기 때문에 일부 백신이 exe를 오탐할 수 있습니다. 걱정되면 소스로 실행하세요.
- 입력이 끝나면 클립보드에 마지막 파일명이 남습니다.

## License

MIT
