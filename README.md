# 대천사 심판: 30초 보스 레이드

과제 2 "내가 설계한 미니게임" 제출용. 순수 HTML/CSS/JS 한 파일(`index.html`)이며 외부 리소스·프레임워크·서버가 없어 GitHub Pages에 그대로 올리면 로그인 없이 바로 열립니다.

## 로컬에서 확인
`index.html`을 브라우저로 더블클릭해서 열면 됩니다(서버 불필요).

## GitHub Pages로 배포하기
1. GitHub에서 새 저장소를 만듭니다 (Public).
2. 이 폴더 내용을 그 저장소에 push 합니다.
   ```
   git remote add origin https://github.com/<본인계정>/<저장소명>.git
   git branch -M main
   git push -u origin main
   ```
3. 저장소 **Settings → Pages**에서 Source를 `main` 브랜치, 루트(`/`) 폴더로 설정합니다.
4. 몇 분 뒤 `https://<본인계정>.github.io/<저장소명>/` 로 접속되면 배포 완료입니다. 새 시크릿 창에서 열어 로그인 요구 없이 바로 게임이 뜨는지 확인하세요 (T02-C01).

## 소스 저장소 URL(커밋 고정) 만드는 법
1. push 후 커밋 해시를 확인: `git log -1 --format=%H`
2. 제출 URL 형식: `https://github.com/<계정>/<저장소>/blob/<40자리 커밋 해시>/index.html`
   (주의: `/commit/<해시>/index.html`이 아니라 `/blob/<해시>/index.html`입니다. `/commit/...`은 커밋 diff 페이지라 뒤에 파일 경로를 붙여도 파일이 열리지 않습니다.)

## 폴더 구성
- `index.html` — 제출용 게임 본체 (이 파일 하나가 결과물의 전부)
- `tests/` — 자동 검증 스크립트(Playwright). 채점 대상이 아니며, 콘솔 에러 0건·10분 안정성 등을 확인한 기록용입니다.
- `SUBMISSION.md` — 제출 폼에 붙여넣을 문구 초안 (재현법 4줄, AI/본인 판단 3줄, 카드3 20회 기록표)

## 게임 안의 "테스트 도구" 패널
공개 화면 하단 `<details>` 접이식 패널에 있습니다. 카드3(난이도 A/B 자동 기록)와 카드4(저장값 비우기/손상시키기 증빙)를 직접 눈으로 확인·기록할 수 있게 만든 보조 도구이며, 일반 플레이에는 영향을 주지 않습니다.
