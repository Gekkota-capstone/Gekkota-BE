import numpy as np
import pandas as pd
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from shapely.geometry import Point

# service logic 에 추가할 것

# DB 연결 설정
load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# 데이터 로드
query = text("SELECT yolo_result FROM capstone.yolo_results ORDER BY yolo_result->>'timestamp'")
results = session.execute(query)
data = [row[0] for row in results]

hide_log = []
added_timestamps = set()
prev_info = {"timestamp": None, "no_box": False}

for i, yolo_data in enumerate(data):
    timestamp = yolo_data.get("timestamp")
    boxes = yolo_data.get("boxes", [])
    keypoints_list = yolo_data.get("keypoints", [[]])[0]  # keypoints[0]

    is_hiding = False
    hide_reason = ""
    low_conf_kpts = []

    if not boxes:
        if prev_info["no_box"]:
            for ts in [prev_info["timestamp"], timestamp]:
                if ts not in added_timestamps:
                    hide_log.append({
                        "timestamp": ts,
                        "reason": "연속된 박스 없음"
                    })
                    added_timestamps.add(ts)
        prev_info = {"timestamp": timestamp, "no_box": True}
        continue

    prev_info["no_box"] = False

    # 유효 키포인트 판단
    low_conf_kpts = [
        {"name": kp["name"], "conf": kp["conf"]}
        for kp in keypoints_list if kp["conf"] <= 0.3
    ]

    if len(low_conf_kpts) >= 6:
        is_hiding = True
        hide_reason = "low_conf >= 6"

    if is_hiding and timestamp not in added_timestamps:
        hide_log.append({
            "timestamp": timestamp,
            "reason": hide_reason,
            "low_conf": low_conf_kpts
        })
        added_timestamps.add(timestamp)

        if prev_info["no_box"] and prev_info["timestamp"] not in added_timestamps:
            hide_log.append({
                "timestamp": prev_info["timestamp"],
                "reason": f"뒤 프레임({timestamp})이 은신으로 판단됨 → 이전도 은신으로 간주"
            })
            added_timestamps.add(prev_info["timestamp"])

    prev_info = {"timestamp": timestamp, "no_box": False}

# 출력
print(f"📦 은신 프레임 수: {len(hide_log)}")
for log in hide_log:
    print(f"{log['timestamp']} - {log['reason']}")
    for kp in log.get("low_conf", []):
        print(f"  ↪ {kp['name']}: {kp['conf']:.3f}")