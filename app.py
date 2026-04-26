import sys
import time
import threading
from collections import deque
import yaml
import os

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QColorDialog, QSpinBox, QLineEdit
)
from PyQt6.QtGui import QColor
from pynput import keyboard
from sayodevice import SayoDevice

configPath = "./config/config.yml"

def loadConfig():
    if not os.path.exists(configPath):
        os.makedirs("./config", exist_ok=True)
        data = {
            "colorStart": "#0000ff",
            "colorEnd": "#ff0000",
            "bpmMin": 0,
            "bpmMax": 300,
            "keys": ["z", "x", "c"]
        }
        saveConfig(data)
        return data

    with open(configPath, "r") as f:
        config = yaml.safe_load(f)
        if "keys" not in config:
            config["keys"] = ["z", "x", "c"]
        return config

def saveConfig(data):
    with open(configPath, "w") as f:
        yaml.dump(data, f)

def hexToRgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

class LedBpmSync:
    def __init__(self):
        self.cfg = loadConfig()
        self.bpsTarget = 0.0
        self.bpsSmooth = 0.0
        self.lastInput = time.time()
        self.running = True

    def reloadConfig(self):
        self.cfg = loadConfig()

    def mapBpsToRgb(self, bps):
        # convert to BPS: (BPM * 4) / 60
        bpsMin = (self.cfg["bpmMin"] * 4) / 60
        bpsMax = (self.cfg["bpmMax"] * 4) / 60

        t = 0.0
        if bpsMax > bpsMin:
            t = (bps - bpsMin) / (bpsMax - bpsMin)

        t = max(0.0, min(t, 1.0))

        r1, g1, b1 = hexToRgb(self.cfg["colorStart"])
        r2, g2, b2 = hexToRgb(self.cfg["colorEnd"])

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        return (r, g, b)

    def updateLoop(self):
        try:
            with SayoDevice.open() as dev:
                print("device ready")
                while self.running:
                    now = time.time()
                    if now - self.lastInput > 0.15:
                        self.bpsTarget = 0.0
                    alpha = 0.15
                    self.bpsSmooth += (self.bpsTarget - self.bpsSmooth) * alpha
                    rgb = self.mapBpsToRgb(self.bpsSmooth)
                    try:
                        for key in range(3):
                            dev.set_key_light(
                                rgb,
                                brightness=100,
                                key_index=key,
                                save=False
                            )
                    except:
                        pass

                    time.sleep(0.02)
        except Exception as e:
            print("device error:", e)

class ConfigUI(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.ctrl = controller
        self.cfg = loadConfig()
        self.setWindowTitle("O3C Config")
        self.setFixedSize(300, 350)
        layout = QVBoxLayout()

        # color start
        self.btnStart = QPushButton(f"Start: {self.cfg['colorStart']}")
        self.btnStart.clicked.connect(self.pickStart)
        layout.addWidget(self.btnStart)

        # color end
        self.btnEnd = QPushButton(f"End: {self.cfg['colorEnd']}")
        self.btnEnd.clicked.connect(self.pickEnd)
        layout.addWidget(self.btnEnd)

        # bpm min
        layout.addWidget(QLabel("BPM Min (Base)"))
        self.spinMin = QSpinBox()
        self.spinMin.setRange(0, 2000)
        self.spinMin.setValue(self.cfg["bpmMin"])
        layout.addWidget(self.spinMin)

        # bpm max
        layout.addWidget(QLabel("BPM Max (Base)"))
        self.spinMax = QSpinBox()
        self.spinMax.setRange(1, 3000)
        self.spinMax.setValue(self.cfg["bpmMax"])
        layout.addWidget(self.spinMax)

        layout.addWidget(QLabel("Key Bindings (Key 1, 2, 3)"))
        keyLayout = QHBoxLayout()
        self.keyInputs = []
        for i in range(3):
            edit = QLineEdit()
            edit.setMaxLength(1)
            edit.setPlaceholderText(f"K{i+1}")
            edit.setText(self.cfg["keys"][i])
            edit.setFixedWidth(40)
            self.keyInputs.append(edit)
            keyLayout.addWidget(edit)
        layout.addLayout(keyLayout)

        # save
        btnSave = QPushButton("Save")
        btnSave.clicked.connect(self.save)
        layout.addWidget(btnSave)

        self.setLayout(layout)

    def pickStart(self):
        c = QColorDialog.getColor()
        if c.isValid():
            hexColor = c.name()
            self.cfg["colorStart"] = hexColor
            self.btnStart.setText(f"Start: {hexColor}")

    def pickEnd(self):
        c = QColorDialog.getColor()
        if c.isValid():
            hexColor = c.name()
            self.cfg["colorEnd"] = hexColor
            self.btnEnd.setText(f"End: {hexColor}")

    def save(self):
        self.cfg["bpmMin"] = self.spinMin.value()
        self.cfg["bpmMax"] = self.spinMax.value()
        self.cfg["keys"] = [edit.text().lower() for edit in self.keyInputs]
        saveConfig(self.cfg)
        self.ctrl.reloadConfig()
        print("config saved")

ctrl = LedBpmSync()
timestamps = deque()

def onPress(key):
    try:
        char = getattr(key, 'char', None)
        if char is None:
            return
        k = char.lower()
        if k not in ctrl.cfg["keys"]:
            return
    except:
        return

    now = time.time()
    timestamps.append(now)
    ctrl.lastInput = now

    while timestamps and now - timestamps[0] > 1.0:
        timestamps.popleft()

    ctrl.bpsTarget = len(timestamps)

updateThread = threading.Thread(target=ctrl.updateLoop, daemon=True)
updateThread.start()

listenerThread = threading.Thread(
    target=lambda: keyboard.Listener(on_press=onPress).run(),
    daemon=True
)
listenerThread.start()

app = QApplication(sys.argv)
ui = ConfigUI(ctrl)
ui.show()
sys.exit(app.exec())