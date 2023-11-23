# main_tensorrt_v2.py

from utils.general import cv2, non_max_suppression, xyxy2xywh
from models.common import DetectMultiBackend
from unittest import result
import cupy as cp
import numpy as np
import pandas as pd
import time
import torch
import win32api
import win32con

from config import aaMovementAmp, aaRightShift, aaAimKey, aaQuitKey, confidence, autoAimKey, headShotKey, cpsDisplay, visuals, centerOfScreen
import gameSelection

from PyQt5.QtWidgets import QApplication
from mod_status import ModStatusUI
import threading
from PyQt5.QtCore import QThread

class Toggle:
    def __init__(self):
        self.state = False
        self.prev_state = False

    def toggle(self, key_state):
        if key_state and not self.prev_state:
            self.state = not self.state
            self.prev_state = True
        elif not key_state:
            self.prev_state = False

def load_model():
    return DetectMultiBackend('yolov5s320Half.engine', device=torch.device('cuda'), dnn=False, data='', fp16=True)

class ProcessingThread(QThread):
    def __init__(self, camera, cWidth, cHeight, model):
        super().__init__()
        self.camera = camera
        self.cWidth = cWidth
        self.cHeight = cHeight
        self.model = model

def process_frames(camera, cWidth, cHeight, model):
    # Long-running processing task
    with torch.no_grad():
        while win32api.GetAsyncKeyState(aaQuitKey) == 0:
            npImg, targets = process_frame(camera, cWidth, cHeight, model)
    npImg = cp.array([camera.get_latest_frame()])
    if npImg.shape[3] == 4:
        npImg = npImg[:, :, :, :3]

    im = npImg / 255
    im = im.astype(cp.half)

    im = cp.moveaxis(im, 3, 1)
    im = torch.from_numpy(cp.asnumpy(im)).to('cuda')

    results = model(im)

    pred = non_max_suppression(results, confidence, confidence, 0, False, max_det=10)

    targets = []
    for i, det in enumerate(pred):
        s = ""
        gn = torch.tensor(im.shape)[[0, 0, 0, 0]]
        if len(det):
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()
                s += f"{n} {model.names[int(c)]}, "
            for *xyxy, conf, cls in reversed(det):
                targets.append((xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist() + [float(conf)])

    targets = pd.DataFrame(
        targets, columns=['current_mid_x', 'current_mid_y', 'width', "height", "confidence"])
    return npImg, targets

def aim_targets(targets, cWidth, cHeight, last_mid_coord):
    global autoAim, headshot_mode  # Declare the variables as global

    if centerOfScreen and len(targets) > 0:
        targets["dist_from_center"] = np.sqrt(
            (targets.current_mid_x - cWidth) ** 2 + (targets.current_mid_y - cHeight) ** 2)
        targets = targets.sort_values("dist_from_center")

    if last_mid_coord:
        targets['last_mid_x'] = last_mid_coord[0]
        targets['last_mid_y'] = last_mid_coord[1]
        targets['dist'] = np.linalg.norm(targets.iloc[:, [0, 1]].values - targets.iloc[:, [4, 5]], axis=1)
        targets.sort_values(by="dist", ascending=False)

    xMid = targets.iloc[0].current_mid_x + aaRightShift
    yMid = targets.iloc[0].current_mid_y

    box_height = targets.iloc[0].height
    headshot_offset = box_height * 0.38 if headshot_mode.state else box_height * 0.2

    mouseMove = [xMid - cWidth, (yMid - headshot_offset) - cHeight]

    # Check if the key for aiming is pressed and autoAim is toggled on
    if win32api.GetAsyncKeyState(aaAimKey) and autoAim.state:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(mouseMove[0] * aaMovementAmp),
                              int(mouseMove[1] * aaMovementAmp), 0, 0)

    last_mid_coord = [xMid, yMid]

    return last_mid_coord, autoAim.state, headshot_mode.state

def draw_visualization(npImg, targets):
    COLORS = np.random.uniform(0, 255, size=(1500, 3))
    npImg = cp.asnumpy(npImg[0])

    for i in range(0, len(targets)):
        halfW = round(targets["width"][i] / 2)
        halfH = round(targets["height"][i] / 2)
        midX = targets['current_mid_x'][i]
        midY = targets['current_mid_y'][i]
        (startX, startY, endX, endY) = int(midX + halfW), int(midY + halfH), int(midX - halfW), int(midY - halfH)

        idx = 0
        label = "{}: {:.2f}%".format("Human", targets["confidence"][i] * 100)
        cv2.rectangle(npImg, (startX, startY), (endX, endY), COLORS[idx], 2)
        y = startY - 15 if startY - 15 > 15 else startY + 15
        cv2.putText(npImg, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    return npImg

def main():
    global autoAim, headshot_mode
    
    # Create a separate thread for the processing task
    processing_thread = threading.Thread(target=process_frame, args=(camera, cWidth, cHeight, model))
    processing_thread.start()

    
    # Create an instance of ModStatusUI
    mod_status_ui = ModStatusUI()
    
    # Show the UI window
    mod_status_ui.show()

    camera, cWidth, cHeight = gameSelection.gameSelection()
    model = load_model()

    # Usage
    autoAim = Toggle()
    headshot_mode = Toggle()

    last_mid_coord = None
    count = 0
    sTime = time.time()

    with torch.no_grad():
        while win32api.GetAsyncKeyState(aaQuitKey) == 0:
            npImg, targets = process_frame(camera, cWidth, cHeight, model)

            # Move toggle updates outside the condition
            autoAim.toggle(win32api.GetKeyState(autoAimKey) & 0x8000)
            headshot_mode.toggle(win32api.GetKeyState(headShotKey) & 0x8000)

            if len(targets) > 0:
                last_mid_coord, _, _ = aim_targets(targets, cWidth, cHeight, last_mid_coord)

            if visuals:
                npImg = draw_visualization(npImg, targets)

            count += 1
            if (time.time() - sTime) > 1:
                if cpsDisplay:
                    print("CPS: {}".format(count))
                    print("Aimbot-{} | Headshot-{}".format(autoAim.state, headshot_mode.state))
                count = 0
                sTime = time.time()

            if visuals:
                cv2.imshow('Live Feed', npImg)
                if (cv2.waitKey(1) & 0xFF) == aaQuitKey:
                    exit()

    camera.stop()

if __name__ == "__main__":
    try:
        app = QApplication([])

        # Load model and initialize camera, cWidth, cHeight here
        model = load_model()
        camera = # Initialize your camera here
        cWidth = # Initialize cWidth here
        cHeight = # Initialize cHeight here

        ui = ModStatusUI(camera, cWidth, cHeight, model, process_frame)
        ui.show()

        main()
        app.exec_()
    except Exception as e:
        import traceback
        traceback.print_exception(type(e), e, e.__traceback__)
        print(str(e))
