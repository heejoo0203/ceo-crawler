
# CEO Photo Crawler 사용 설명서


---

# 📌 1. 프로젝트 다운로드(두 가지 방법 중 선택)

## ✅ 1-1. Git을 모른다면 (가장 쉬운 방법)
1. 팀에서 공유한 GitHub 링크로 들어간다.
2. 우측 상단 **초록색 `Code` 버튼 클릭**
3. **Download ZIP** 선택
4. ZIP 파일 다운로드 후 **압축 해제**
5. 해제된 폴더가 바로 프로젝트 폴더입니다.

## ✅ 1-2. Git 사용 가능할 경우
```
git clone <레포지토리 주소>
```

---

# 📌 2. 실행 전 준비물

프로젝트 폴더 안에 아래 파일들이 있어야 합니다:

- `ceo-crawler.py`
- `photo.py`
- `requirements.txt`
- `haarcascade_frontalface_default.xml`  (이미 포함됨)
- `input_ceo_list_중복제거.xlsx`  (팀 공유 파일)
- `input_ceo_list_원본.xlsx`       (팀 공유 파일)

⚠ 두 엑셀 파일(.xlsx)은 GitHub에 포함되지 않습니다.  
→ **팀에서 제공한 파일을 반드시 프로젝트 폴더에 직접 넣어주세요.**

⚠ 아래 파일명은 절대 변경하면 안 됩니다.
- `input_ceo_list_중복제거.xlsx`
- `input_ceo_list_원본.xlsx`

---

# 📌 3. 프로그램 설치 준비

(컴퓨터에 Python이 설치되어 있어야 합니다.)

1. 프로젝트 폴더에서 **Shift + 우클릭 → PowerShell 창 열기**
2. 아래 명령어 입력

```
pip install -r requirements.txt
```

---

# 📌 4. 프로그램 실행

## ✅ Step 1 — CEO 사진 자동 크롤링 실행
```
python ceo-crawler.py
```

→ 사진이 자동으로 `output_photos` 폴더에 저장됩니다.  
→ 파일 이름은 **PersonID.png** 형태입니다.

---

## ✅ Step 2 — 엑셀에 사진 자동 삽입
```
python photo.py
```

실행이 끝나면 아래 파일이 자동 생성됩니다:

### ✔ `input_ceo_list_원본_이미지삽입.xlsx`  
→ 이것이 최종 결과물입니다.

---

# 📌 5. 프로젝트 폴더 구조

```
project/
 ├─ ceo-crawler.py
 ├─ photo.py
 ├─ requirements.txt
 ├─ haarcascade_frontalface_default.xml
 ├─ input_ceo_list_중복제거.xlsx
 ├─ input_ceo_list_원본.xlsx
 ├─ output_photos/          
 ├─ output_temp_baidu/      
 └─ logs/                   
```

---

# ❓ Q&A (문제 발생 시 해결)

---

### ❗ Q1. dlib 설치 오류가 나서 `pip install -r requirements.txt`가 안 돼요.

dlib는 Windows에서 pip로 설치가 잘 안 되는 경우가 많습니다.

### ✔ 해결방법(직접 다운로드 방식)

1. 아래 사이트 접속  
   🔗 **https://dlib.net/**
2. 페이지 상단의 **“Download”** 버튼 클릭
3. Windows용 dlib 파일(.zip 또는 .tar.bz2)을 다운로드
4. 압축 해제
5. PowerShell에서 해당 폴더로 이동 후 아래 명령 실행

```
python setup.py install
```

6. 설치 완료 후 다시 다음 실행  
```
pip install -r requirements.txt
```

---

### ❗ Q2. photo.py 실행했는데 엑셀에 사진이 안 들어가요.

다음 항목을 반드시 확인하세요:

- `output_photos` 폴더에 해당 PersonID.png 존재?
- 엑셀 D열(PersonID)이 파일명과 정확히 일치?
- 엑셀 파일명을 변경하지 않았는가?

---

### ❗ Q3. requirements 설치가 실패해요.

1. 컴퓨터에 Python이 제대로 설치됐는지 확인  
2. PowerShell/명령 프롬프트를 관리자 권한으로 열기  
3. 그래도 안 되면 Python 버전을 3.10~3.11로 재설치

---
