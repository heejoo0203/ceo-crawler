# ================================================================
# CEO Photo Crawler – Clean Logging Version (loguru + tqdm)
# ================================================================

import os
import cv2
import dlib
import time
import random
import requests
import glob
import pandas as pd
import shutil
import numpy as np
from io import BytesIO
from PIL import Image
from tqdm import tqdm
from loguru import logger
from icrawler.builtin import BaiduImageCrawler
import logging
from colorama import Fore, Style, init as colorama_init



# ================================================================
# noisy logger 제거
# ================================================================

logging.getLogger("icrawler").setLevel(logging.CRITICAL)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.disable(logging.CRITICAL)

colorama_init(autoreset=True)   


# ================================================================
# 경로 설정
# ================================================================

TEMP_DIR = "output_temp_baidu"
OUTPUT_DIR = "output_photos"
LOG_DIR = "logs"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# ================================================================
# loguru 설정
# ================================================================

logger.remove()  # 기본 logger 제거
logger.add(
    os.path.join(LOG_DIR, "run_{time}.log"),
    level="INFO",
    encoding="utf-8",
    backtrace=False,
    diagnose=False
)
logger.add(lambda msg: print(msg, end=""), level="INFO")

logger.info("CEO Photo Crawler Initialized")


# ================================================================
# Excel Loader
# ================================================================

def load_ceo_excel(path="input_ceo_list_중복제거.xlsx"): #필요하면 엑셀 파일명 수정
    df = pd.read_excel(path)
    required = ["company", "ceo", "PersonID"]

    for col in required:
        if col not in df.columns:
            raise Exception(f"엑셀에 '{col}' 컬럼이 없습니다!")

    rows = []
    for idx, row in df.iterrows():
        rows.append((idx+1,
                     str(row["company"]).strip(),
                     str(row["ceo"]).strip(),
                     str(row["PersonID"]).strip()))

    logger.info(f"Excel loaded → {len(rows)} rows")
    return rows


# ================================================================
# 이미지 로드
# ================================================================

def open_image(path):
    try:
        return Image.open(path).convert("RGB")
    except:
        return None


# ================================================================
# Haar Cascade 로드
# ================================================================

opencv_data_path = os.path.join(os.path.dirname(cv2.__file__), "data")
haar_path = os.path.join(opencv_data_path, "haarcascade_frontalface_default.xml")

face_cascade = cv2.CascadeClassifier(haar_path)
if face_cascade.empty():
    logger.error("Haar cascade load failed!")
else:
    logger.info(f"Haar loaded: {haar_path}")


# ================================================================
# 얼굴 검출
# ================================================================

def detect_faces(img_pil):
    try:
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)
    except:
        return []

    faces = face_cascade.detectMultiScale(img, 1.2, 5)
    result = []

    for (x, y, w, h) in faces:
        result.append((x, y, x+w, y+h))
    return result


# ================================================================
# 얼굴 스코어링
# ================================================================

def score_face(box, w, h):
    x1, y1, x2, y2 = box
    fw, fh = x2-x1, y2-y1
    cx = (x1+x2)/2

    size_score = (fw * fh) / (w*h)
    center_score = 1 - (abs(cx - w/2) / (w/2))

    ratio = fw / fh
    ratio_penalty = 0.5 if ratio < 0.6 or ratio > 1.6 else 1.0

    return size_score * center_score * ratio_penalty


# ================================================================
# 얼굴 crop → 1024x1024
# ================================================================

def crop_1024(img, box):
    x1, y1, x2, y2 = box
    face = img.crop((x1, y1, x2, y2))
    face = face.resize((1024, 1024))
    return face


# ================================================================
# icrawler Baidu 이미지 다운로드
# ================================================================

def baidu_icrawler(company, ceo):
    keyword = f"{company} {ceo} 照片"
    logger.info(f"[Baidu] Searching: {keyword}")

    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    try:
        crawler = BaiduImageCrawler(storage={"root_dir": TEMP_DIR})
        crawler.crawl(keyword=keyword, max_num=20)

        files = glob.glob(os.path.join(TEMP_DIR, "*"))
        logger.info(f"[Baidu] Downloaded {len(files)} images")

        return files
    except Exception as e:
        logger.error(f"[Baidu ERROR] {e}")
        return []


# ================================================================
# 후보 중 가장 좋은 얼굴 선택
# ================================================================

def select_best_face(files):
    best_img = None
    best_box = None
    best_score = -1

    for file in files:
        img = open_image(file)
        if img is None:
            continue

        boxes = detect_faces(img)
        if not boxes:
            continue

        for box in boxes:
            s = score_face(box, img.width, img.height)
            if s > best_score:
                best_score = s
                best_box = box
                best_img = img

    if best_img:
        return best_img, best_box
    return None, None


# ================================================================
# 최종 저장
# ================================================================

def save_final(img, box, pid):
    try:
        face = crop_1024(img, box)
        path = os.path.join(OUTPUT_DIR, f"{pid}.png")
        face.save(path)
        return path
    except Exception as e:
        logger.error(f"[SAVE ERROR] {e}")
        return None


# ================================================================
# 단일 CEO 처리
# ================================================================

def process(company, ceo, pid):
    logger.info(f"<cyan>Processing:</cyan> {company} / {ceo} ({pid})")

    files = baidu_icrawler(company, ceo)

    img, box = select_best_face(files)
    if not img:
        logger.error(f"<red>No valid face found for PID={pid}</red>")
        tqdm.write(f"{Fore.RED}[FAILED]{Style.RESET_ALL} PID={pid}")
        return None

    out = save_final(img, box, pid)
    if out:
        logger.success(f"<green>Saved:</green> {out}")
        tqdm.write(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {pid} → saved")
    else:
        logger.error(f"<red>Save failed: PID={pid}</red>")
        tqdm.write(f"{Fore.RED}[FAILED]{Style.RESET_ALL} {pid} → save error")

    return out



# ================================================================
# 메인 (tqdm)
# ================================================================

def main():
    rows = load_ceo_excel()
    total = len(rows)

    logger.info("<magenta>=== START CRAWLING ===</magenta>")
    tqdm.write(Fore.CYAN + "Starting CEO Image Crawl...\n" + Style.RESET_ALL)

    for idx, company, ceo, pid in tqdm(rows, desc=f"{Fore.YELLOW}Processing CEOs{Style.RESET_ALL}", ncols=90):
        process(company, ceo, pid)
        time.sleep(random.uniform(0.8, 1.5))

    tqdm.write(Fore.GREEN + "\nAll completed!" + Style.RESET_ALL)
    logger.info("<green>=== ALL COMPLETED ===</green>")



if __name__ == "__main__":
    main()
