from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
import cv2
import os
import uuid
import sqlite3
from datetime import datetime
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULT_DIR = os.path.join(BASE_DIR, "results")
DB_PATH = os.path.join(BASE_DIR, "history.db")
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

app.mount("/results", StaticFiles(directory=RESULT_DIR), name="results")

model = YOLO(MODEL_PATH)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    resultfile TEXT,
    status TEXT,
    safe INTEGER,
    violation INTEGER,
    time TEXT
)
""")
conn.commit()


def center(box):
    x1, y1, x2, y2 = box
    return (x1 + x2) // 2, (y1 + y2) // 2


def helmet_on_head(person, helmets):
    px1, py1, px2, py2 = person
    head_y2 = py1 + int((py2 - py1) * 0.35)

    for h in helmets:
        hx1, hy1, hx2, hy2 = h
        hcx, hcy = center(h)

        if px1 < hcx < px2 and py1 < hcy < head_y2:
            return True

    return False


@app.get("/")
def home():
    return {"message": "Helmet Detection API Running"}


@app.post("/detect")
async def detect_helmet(file: UploadFile = File(...)):
    start_time = time.time()

    ext = file.filename.split(".")[-1].lower()

    if ext not in ["jpg", "jpeg", "png"]:
        return {"error": "Chỉ hỗ trợ ảnh jpg, jpeg, png"}

    file_name = f"{uuid.uuid4()}.jpg"
    upload_path = os.path.join(UPLOAD_DIR, file_name)
    result_path = os.path.join(RESULT_DIR, file_name)

    with open(upload_path, "wb") as f:
        f.write(await file.read())

    img = cv2.imread(upload_path)

    if img is None:
        return {"error": "Không đọc được ảnh"}

    h, w = img.shape[:2]

    if w > 960:
        scale = 960 / w
        img = cv2.resize(img, None, fx=scale, fy=scale)

    results = model.predict(
        img,
        conf=0.25,
        imgsz=416,
        verbose=False
    )

    result = results[0]
    result_img = img.copy()

    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()

    persons = []
    helmets = []

    for box, cls in zip(boxes, classes):
        x1, y1, x2, y2 = map(int, box)
        cls = int(cls)

        if cls == 0:
            persons.append([x1, y1, x2, y2])
        elif cls == 2:
            helmets.append([x1, y1, x2, y2])

    safe_count = 0
    violation_count = 0

    for person in persons:
        px1, py1, px2, py2 = person

        has_helmet = helmet_on_head(person, helmets)

        if has_helmet:
            safe_count += 1
            color = (0, 255, 0)
            label = "Safe"
        else:
            violation_count += 1
            color = (0, 0, 255)
            label = "No Helmet"

        cv2.rectangle(result_img, (px1, py1), (px2, py2), color, 3)
        cv2.putText(
            result_img,
            label,
            (px1, py1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    cv2.imwrite(result_path, result_img, [cv2.IMWRITE_JPEG_QUALITY, 80])

    status = "Vi phạm" if violation_count > 0 else "Không vi phạm"

    cursor.execute(
        """
        INSERT INTO history(filename,resultfile,status,safe,violation,time)
        VALUES(?,?,?,?,?,?)
        """,
        (
            file.filename,
            file_name,
            status,
            safe_count,
            violation_count,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        )
    )
    conn.commit()

    processing_time = round(time.time() - start_time, 2)

    return {
        "message": "Detect success",
        "result_image": f"http://127.0.0.1:8001/results/{file_name}",
        "safe": safe_count,
        "violation": violation_count,
        "status": status,
        "processing_time": processing_time
    }


@app.get("/history")
def get_history():
    cursor.execute("SELECT * FROM history ORDER BY id DESC")
    rows = cursor.fetchall()

    data = []

    for row in rows:
        id, filename, resultfile, status, safe, violation, time_value = row

        data.append({
            "id": id,
            "filename": filename,
            "resultfile": f"http://127.0.0.1:8001/results/{resultfile}",
            "status": status,
            "safe": safe,
            "violation": violation,
            "time": time_value
        })

    return data


@app.get("/statistics")
def get_statistics():
    cursor.execute("SELECT * FROM history")
    rows = cursor.fetchall()

    total = len(rows)
    violation = 0
    safe = 0

    for row in rows:
        status = row[3]

        if status == "Vi phạm":
            violation += 1
        else:
            safe += 1

    return {
        "total": total,
        "safe": safe,
        "violation": violation
    }


@app.delete("/history/{history_id}")
def delete_history(history_id: int):
    cursor.execute("SELECT resultfile FROM history WHERE id=?", (history_id,))
    row = cursor.fetchone()

    if row:
        resultfile = row[0]
        file_path = os.path.join(RESULT_DIR, resultfile)

        if os.path.exists(file_path):
            os.remove(file_path)

        cursor.execute("DELETE FROM history WHERE id=?", (history_id,))
        conn.commit()

        return {"message": "Đã xóa lịch sử"}

    return {"message": "Không tìm thấy lịch sử"}


@app.delete("/history")
def delete_all_history():
    cursor.execute("SELECT resultfile FROM history")
    rows = cursor.fetchall()

    for row in rows:
        file_path = os.path.join(RESULT_DIR, row[0])

        if os.path.exists(file_path):
            os.remove(file_path)

    cursor.execute("DELETE FROM history")
    conn.commit()

    return {"message": "Đã xóa toàn bộ lịch sử"}