"""Stage 4: face detection & tracking (OpenCV) - drives framing, face-light, keyword masking."""
import os, sys, cv2, math, statistics
from common import *

SRC = sys.argv[1]
probe = jload(os.path.join(WORK, "probe.json"))
W, H, DUR, FPS = probe["w"], probe["h"], probe["dur"], probe["fps"]

cap = cv2.VideoCapture(SRC)
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cas2 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
yunet_path = os.path.join(ASSETS, "models/face_detection_yunet_2023mar.onnx")
yn = None
if os.path.exists(yunet_path):
    try:
        yn = cv2.FaceDetectorYN_create(yunet_path, "", (W // 3, H // 3), 0.6, 0.3, 5000)
    except Exception:
        yn = None

step = max(1, int(FPS * 0.5))          # sample every ~0.5s
max_samples = 500
samples = []
idx = 0
while True:
    ok = cap.grab()
    if not ok:
        break
    if idx % step == 0 and len(samples) < max_samples:
        ok, frame = cap.retrieve()
        if not ok:
            break
        small = cv2.resize(frame, (W // 3, H // 3))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        s = 3.0
        if yn is not None:
            yn.setInputSize((gray.shape[1], gray.shape[0]))
            _, det = yn.detect(frame_small_rgb if False else cv2.cvtColor(small, cv2.COLOR_BGR2RGB))
            all_f = [(int(d[0]), int(d[1]), int(d[2]), int(d[3])) for d in (det if det is not None else [])]
        else:
            faces_d = list(cas.detectMultiScale(gray, 1.12, 5, minSize=(int(0.10 * W / s), int(0.10 * H / s))))
            prof = list(cas2.detectMultiScale(gray, 1.12, 6, minSize=(int(0.10 * W / s), int(0.10 * H / s))))
            all_f = [(x, y, w, h) for (x, y, w, h) in faces_d] + \
                    [(x, y, w, h) for (x, y, w, h) in prof]
        if all_f:
            x, y, w, h = max(all_f, key=lambda f: f[2] * f[3])
            samples.append({"t": idx / FPS, "cx": (x + w / 2) * s, "cy": (y + h / 2) * s, "w": w * s, "h": h * s})
    idx += 1
cap.release()

print(f"FACES: detected in {len(samples)} samples")
if len(samples) < 3:
    fb = {"ok": False, "cx": W * 0.5, "cy": H * 0.38, "w": min(W, H) * 0.30, "h": min(W, H) * 0.30, "path": []}
    jsave(os.path.join(WORK, "faces.json"), fb)
    print("FACE: fallback (center-top)")
    sys.exit(0)

# global face box = medians
g = {"ok": True,
     "cx": statistics.median(f["cx"] for f in samples),
     "cy": statistics.median(f["cy"] for f in samples),
     "w": statistics.median(f["w"] for f in samples),
     "h": statistics.median(f["h"] for f in samples)}

# smooth center path (moving average over ~2.5s)
path = sorted(samples, key=lambda f: f["t"])
win = 5
sm = []
for i in range(len(path)):
    lo, hi = max(0, i - win), min(len(path), i + win + 1)
    sm.append({"t": path[i]["t"],
               "cx": sum(p["cx"] for p in path[lo:hi]) / (hi - lo),
               "cy": sum(p["cy"] for p in path[lo:hi]) / (hi - lo)})
g["path"] = sm
jsave(os.path.join(WORK, "faces.json"), g)
print(f"FACE BOX: cx={g['cx']:.0f} cy={g['cy']:.0f} w={g['w']:.0f} h={g['h']:.0f}")
