# Ginppai Repo

필요한 기능은 챙기고, 불필요한 화면은 치웁니다. nogadamachine의 Ginppai 시리즈 **탈옥용 패키지 저장소**입니다.

```text
https://nogadamachine.github.io/Ginppai-Repo/
```

Sileo·Zebra·Cydia의 소스에 위 주소를 추가하세요. 루트풀과 루트리스 DEB를 함께 제공합니다. 비탈옥 기기는 이 APT 저장소를 추가하는 방식으로 설치하지 않으며, 각 프로젝트의 별도 DYLIB/SideStore 안내를 이용합니다.

| 트윅 | 주요 기능 | 공개 프로젝트 |
|---|---|---|
| Ginppai-Kakao-Customizer | 광고·탭 정리, 편의 설정, 선택적 국가 UI 패치, 프로필 사진·영상 원본 저장 | [소스와 배포](https://github.com/nogadamachine/Ginppai-Kakao-Customizer) |
| Ginppai-Kakao-iPad | 카카오톡 안에서 UIDevice가 iPad로 응답 | [소스와 배포](https://github.com/nogadamachine/Ginppai-Kakao-iPad) |

## 설치 파일 구분

- 탈옥 루트풀: `iphoneos-arm.deb`, `/Library/MobileSubstrate/DynamicLibraries/`.
- 탈옥 루트리스: `iphoneos-arm64.deb`, `/var/jb/Library/MobileSubstrate/DynamicLibraries/`.
- 비탈옥: 프로젝트 Releases의 `NonJailbreak.zip` 또는 `.dylib`. SideStore + LiveContainer에 넣거나 본인의 IPA에 주입한 뒤 SideStore로 서명합니다. SideStore는 DYLIB/DEB 자체를 단독 설치하지 않습니다.

두 DEB에 들어 있는 코드는 같은 arm64 DYLIB이며 설치 경로만 다릅니다. 지원되는 트윅 로더가 있어야 합니다. 커스터마이저는 **카카오톡 26.7.3, iOS 17 이상**이 필요하고, 국가 선택은 별도 UI 패치가 있어야 활성화됩니다.

**검증 구분:** 비탈옥 iOS 26.1 + LiveContainer 사용 환경을 기준으로 개발했습니다. DEB의 패키지 구조는 검사했지만 탈옥 기기 실사용은 미검증입니다. SideStore 직접 설치와 모든 iOS·앱 조합을 검증한 것은 아닙니다. 프로젝트별 상세 안내를 읽어 주세요.

## 저장소 갱신

DEB를 `debs/`에 넣은 다음 아래 명령으로 패키지 목록과 해시를 다시 만듭니다.

```bash
python3 generate.py
```

`Packages`, `Packages.gz`, `Packages.bz2`, `Release`와 `SHA256SUMS`가 만들어집니다. GitHub Pages는 `main` 브랜치 루트에서 제공합니다. `index.html`은 설치 안내이고 실제 APT 저장소 인덱스도 같은 주소에 있습니다.

이 저장소에는 카카오톡 앱·개인 인증서·계정 정보·프로필 미디어를 포함하지 않습니다. 만든이 **nogadamachine**. 비공식 프로젝트이며 Kakao와 관계없습니다.
