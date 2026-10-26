import cv2, numpy as np, subprocess, os
from extract_screen import find_screen_quad, warp, order_pts
FF = "./venv/lib/python3.14/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1"
VID = "/Users/rust/work/dante-super-sport/doc/media/VID_20261021_175126.mp4"
names = {
 "main":30, "fast_start":85, "fast_start_splits":95, "splits_popup":725, "splits_popup_time":660,
 "race_setup":120, "history":1225, "workout_info":540, "athlete":1305, "wifi_list":1335,
 "wifi_password":1345, "wifi_connected":1320, "options":1375, "time_popup":1410,
 "program_create":785, "active_workout":170, "active_start":745, "exit_dialog":465,
 "rest":1110, "finish":1170, "active_idle":300, "active_compare":405,
}
def frame(t):
    p = f"full/f_{t}.jpg"
    if not os.path.exists(p):
        subprocess.run([FF, "-loglevel", "error", "-y", "-ss", str(t), "-i", VID, "-frames:v", "1", "-q:v", "2", p], check=True)
    return cv2.imread(p)
def good_quad(img):
    q, _ = find_screen_quad(img)
    if q is None: return None
    q = order_pts(q)
    w = (np.linalg.norm(q[1]-q[0]) + np.linalg.norm(q[2]-q[3])) / 2
    h = (np.linalg.norm(q[3]-q[0]) + np.linalg.norm(q[2]-q[1])) / 2
    asp = w / h
    if 0.53 <= asp <= 0.60 and h > 1100: return q
    return None
os.makedirs("final_screens", exist_ok=True)
for n, t in names.items():
    img = frame(t)
    used = None
    for dt in (0, -3, 3, -6, 6, -10, 10, -15, 15, -20, 20):
        q = good_quad(frame(t + dt))
        if q is not None:
            used = dt; break
    if q is None:
        print("FAILED", n); continue
    cv2.imwrite(f"final_screens/{n}.jpg", warp(img, q), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(n, "quad from dt", used)
