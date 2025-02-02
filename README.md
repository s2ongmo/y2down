# YouTube Downloader

유튜브 동영상을 **MP3** 혹은 **MP4** 형식으로 간편하게 다운로드할 수 있는 Flask 기반 도구입니다.

---

## 🚀 주요 기능
- **유튜브 링크 입력**: 원하는 동영상의 주소를 입력
- **지원 형식**:  
  - 🎵 **MP3 (오디오만)**  
  - 🎥 **MP4 (비디오)**  
- **빠르고 직관적인 사용성**: 간단한 폼 입력만으로 손쉽게 다운로드 가능

---

## 📦 설치 방법

1. **저장소 클론**
   ```bash
   git clone https://github.com/s2ongmo/y2down.git
   cd y2down
   ```
2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv myenv
   source myenv/bin/activate
   ```
3. **종속성 설치**
   ```bash
   pip install -r requirements.txt
   ```
4. **API 설정**  
   - [Google Cloud Console](https://console.cloud.google.com/)에서 **YouTube Data API v3**를 활성화하고 **API 키**를 발급받습니다.
   - 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음처럼 키를 저장합니다:
     ```bash
     YOUTUBE_API_KEY=발급받은_API_키
     ```
   - 이 키는 `python-dotenv`가 불러오며, 코드 내에서 자동으로 사용됩니다.

---

## 🛠️ 사용 방법

1. **애플리케이션 실행**  
   ```bash
   python app.py
   ```
2. **유튜브 링크 입력**  
   - 웹 브라우저에서 [http://127.0.0.1:5000/](http://127.0.0.1:5000/) (기본) 접속  
   - 폼에 유튜브 링크를 입력
3. **파일 형식 선택**  
   - MP3 (오디오)  
   - MP4 (비디오)  
4. **다운로드 완료**  
   - 지정된 폴더(기본: `downloads/`)에 완료된 파일이 생성됩니다.

---

## 💡 이 도구는?

- **동영상 오프라인 재생**: 유튜브 재생이 어려운 환경에서 동영상 또는 오디오를 미리 저장  
- **음악 감상**: 강의, 팟캐스트, 노래 등 오디오를 추출하여 MP3로 보관  
- **자료 수집**: 학습용 자료(강의·튜토리얼) 저장 시 편리

---

## ⚠️ 주의 사항
- **저작권**: 이 도구는 개인 용도로만 사용하시기 바랍니다. 저작권이 있는 콘텐츠를 무단으로 다운로드·배포하는 행위는 법적 문제가 발생할 수 있습니다.  
- **API 사용량**: YouTube Data API를 과도하게 사용하면 할당량 제한에 걸릴 수 있습니다. 적절히 관리해 주세요.

---

## 📝 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 오픈소스로 제공됩니다. 자유롭게 수정·배포하실 수 있으나, 라이선스 내용을 반드시 숙지하시기 바랍니다.

---

## 🤝 기여하기

- 이 프로젝트를 **포크** 한 뒤, 새로운 기능 추가나 버그 수정에 대한 **풀 리퀘스트**를 보내주세요.  
- 논의가 필요한 이슈나 버그는 **GitHub Issues**에 등록해 주세요.

---

## 📬 문의하기

- 질문이나 피드백은 **[leaveleave01@gmail.com](mailto:leaveleave01@gmail.com)** 또는 GitHub **Issues**를 통해 연락해 주시면 감사하겠습니다.

즐거운 다운로드 되세요! 😄