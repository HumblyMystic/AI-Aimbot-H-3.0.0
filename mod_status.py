# mod_status.py

from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt

class ModStatusUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mod Status UI")
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # Set the window to be always on top
        self.setGeometry(100, 100, 300, 200) # Set the initial size and position of the window

        # Create labels to display the status of each mod
        self.mod1_label = QLabel("Mod 1: On", self)
        self.mod1_label.setGeometry(50, 50, 200, 20) # Set the position and size of the label

        self.mod2_label = QLabel("Mod 2: Off", self)
        self.mod2_label.setGeometry(50, 80, 200, 20) # Set the position and size of the label

        # Update the status of the mods dynamically
        self.update_mod_status()

    def update_mod_status(self):
        # Update the status of the mods based on the actual status of your mods
        # You can retrieve the status of the mods from your mod files or variables
        mod1_status = "On"
        mod2_status = "Off"

        self.mod1_label.setText(f"Mod 1: {mod1_status}")
        self.mod2_label.setText(f"Mod 2: {mod2_status}")