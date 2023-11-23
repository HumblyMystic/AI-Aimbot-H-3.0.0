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