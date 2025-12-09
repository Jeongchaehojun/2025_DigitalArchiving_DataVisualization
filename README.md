# 🎮 2025 롤드컵 벤픽 아카이브

> **데이터 스토리텔링 기반 월드 챔피언십 전략적 선택의 인터랙티브 아카이빙**

<p align="center">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/GitHub%20Pages-222222?style=for-the-badge&logo=github-pages&logoColor=white" alt="GitHub Pages">
</p>

---

## 🌐 라이브 데모

### 👉 [GitHub Pages에서 보기](https://jeongchaehojun.github.io/2025_DigitalArchiving_DataVisualization/)
### Django 서버 구축 코드와 별개로 "발표의 편의성"을 위해 깃허브 데모를 구현하여 게시하였습니다.
---

## 📖 프로젝트 소개

2025 LoL 월드 챔피언십 녹아웃 스테이지(8강~결승)의 **밴픽 전략**과 **경기 스토리**를 분석한 디지털 아카이빙 프로젝트입니다.

### 🎯 프로젝트 목표
- e스포츠 경기의 전략적 선택을 데이터 기반으로 아카이빙
- 밴픽 분석을 통한 게임 이해도 향상
- 인터랙티브한 데이터 시각화 제공

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 📖 **경기 스토리** | 8강~결승 각 세트별 밴픽 분석 및 경기 서사 |
| 📊 **챔피언 통계** | Tier Score, 픽률, 진영 선호도 분석 |
| 🏆 **결론** | "밴픽이 모든 것을 결정하지 않는다" |
| 🖼️ **팀 로고** | 8개 녹아웃 진출팀 로고 시각화 |

---

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| **Backend** | Django 5.x, Python 3.13 |
| **Frontend** | HTML5, CSS3 (커스텀 LoL 테마) |
| **Database** | SQLite |
| **Deployment** | GitHub Pages (정적 사이트) |
| **Data Processing** | python-docx, pandas |

---

## 📁 프로젝트 구조

```
📦 2025_DigitalArchiving_DataVisualization
├── 📂 main/                    # Django 앱
│   ├── models.py              # 데이터 모델
│   ├── views.py               # 뷰 로직
│   ├── templates/             # HTML 템플릿
│   └── management/commands/   # 데이터 로드 명령어
├── 📂 docs/                    # GitHub Pages 정적 사이트
│   ├── index.html             # 메인 페이지
│   ├── stories/               # 경기 스토리 페이지
│   └── champions/             # 챔피언 통계 페이지
├── 📂 myoneproject/            # Django 설정
├── 📄 db.sqlite3              # 데이터베이스
├── 📄 worlds_story.docx       # 원본 스토리 데이터
└── 📄 prechampions.csv        # 챔피언 통계 원본
```

---

## 🚀 로컬 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/Jeongchaehojun/2025_DigitalArchiving_DataVisualization.git
cd 2025_DigitalArchiving_DataVisualization
```

### 2. 의존성 설치
```bash
pip install django python-docx pandas
```

### 3. Django 서버 실행
```bash
python manage.py runserver
```

### 4. 브라우저에서 접속
```
http://localhost:8000
```

---

## 📊 분석 결과 요약

### 핵심 인사이트
> **"밴픽은 경기의 시작일 뿐, 끝을 결정하는 것은 선수들의 실력과 정신력이다."**

- 8강 젠지 vs 한화생명: 완벽한 밴픽에도 58분 혈전 끝 역전
- 4강 젠지 vs KT: 언더독 KT의 대이변
- 결승 KT vs T1: T1의 월즈 3연속 우승 달성

---

## 👥 팀원

| 이름 | 역할 |
|------|------|
| **정채호준** | 프로젝트 기획 & 개발 |
| **이*규** | 프로젝트 기획 & 개발 |

---

## 📜 라이선스

이 프로젝트는 교육 및 학습 목적으로 제작되었습니다.

---

<p align="center">
  <strong>2025 디지털 아카이빙 & 데이터 시각화 프로젝트</strong><br>
  <em>Data Storytelling Project</em>
</p>

