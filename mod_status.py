from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import numpy as np
import pandas as pd

class Worker(QThread):
    data_ready = pyqtSignal(np.ndarray, pd.DataFrame)

    def __init__(self, camera, cWidth, cHeight, model, process_frame):
        super().__init__()
        self.camera = camera
        self.cWidth = cWidth
        self.cHeight = cHeight
        self.model = model
        self.process_frame = process_frame

    def run(self):
        while True:
            npImg, targets = self.process_frame(self.camera, self.cWidth, self.cHeight, self.model)
            self.data_ready.emit(npImg, targets)

class ModStatusUI(QWidget):
    def __init__(self, camera, cWidth, cHeight, model, process_frame):
        super().__init__()
        self.setWindowTitle("Mod Status UI")
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # Set the window to be always on top
        self.setGeometry(100, 100, 300, 200) # Set the initial size and position of the window

        # Create labels to display the status of each mod
        self.mod1_label = QLabel("Mod 1: On", self)
        self.mod1_label.setGeometry(50, 50, 200, 20) # Set the position and size of the label

        self.mod2_label = QLabel("Mod 2: Off", self)
        self.mod2_label.setGeometry(50, 80, 200, 20) # Set the position and size of the label

        self.worker = Worker(camera, cWidth, cHeight, model, process_frame)
        self.worker.data_ready.connect(self.update_mod_status)
        self.worker.start()

    def update_mod_status(self, npImg, targets):
        mod1_status = get_mod_status("Mod 1")  # Replace with your logic to get the status of Mod 1
        mod2_status = get_mod_status("Mod 2")  # Replace with your logic to get the status of Mod 2

        self.mod1_label.setText(f"Mod 1: {mod1_status}")
        self.mod2_label.setText(f"Mod 2: {mod2_status}")

def get_mod_status(mod_name):
    # Replace this function with your logic to retrieve the status of each mod
    # You can fetch the status from mod files or variables
    # Return the status as a string, e.g., "On" or "Off"
    if mod_name == "Mod 1":
        return "On"
    elif mod_name == "Mod 2":
        return "Off"
    else:
        return "Unknown"
