import sys
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt

# Add project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio
import config

def list_output_devices():
    """Get list of available output devices from PulseAudio"""
    try:
        result = subprocess.run(["pactl", "list", "short", "sinks"],
                              capture_output=True, text=True, check=True)
        devices = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    devices.append(parts[1].strip())
        return devices if devices else ["No devices found"]
    except Exception as e:
        return [f"Error: {e}"]

def set_selected_sink(sink_name):
    """Update the selected output device"""
    audio.SINK_OUTPUT_DEVICE = sink_name
    # Save to config
    cfg = config.load_config()
    cfg["audio"]["output_device"] = sink_name
    config.save_config(cfg)

class WavePipe(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WavePipe v7 Loopback AutoLoad")
        self.setFixedSize(650, 550)

        layout = QVBoxLayout()
        self.label = QLabel("Status: ready")
        layout.addWidget(self.label)

        layout.addWidget(QLabel("Выберите устройство для наушников:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(list_output_devices())
        self.device_combo.currentTextChanged.connect(lambda text: set_selected_sink(text))
        layout.addWidget(self.device_combo)

        btn_init = QPushButton("Init audio")
        btn_init.clicked.connect(self.init_audio)
        layout.addWidget(btn_init)

        self.preset_state = True
        btn_toggle = QPushButton("Toggle Preset (Stream/NoSound)")
        btn_toggle.clicked.connect(self.toggle_preset)
        layout.addWidget(btn_toggle)

        for ch in audio.CHANNELS:
            ch_layout = QHBoxLayout()
            lbl = QLabel(ch)

            fader_you = QSlider(Qt.Horizontal)
            fader_you.setRange(0, 100)
            fader_you.setValue(audio.VOLUME_YOU_STATE.get(ch, 100))
            fader_you.valueChanged.connect(lambda val, ch=ch: audio.set_volume_you(ch, val))

            fader_stream = QSlider(Qt.Horizontal)
            fader_stream.setRange(0, 100)
            fader_stream.setValue(100)
            fader_stream.valueChanged.connect(lambda val, ch=ch: audio.set_volume_stream(ch, val))

            btn_mute = QPushButton("Mute")
            btn_mute.clicked.connect(lambda _, ch=ch: audio.mute_channel(ch))

            btn_unmute = QPushButton("Unmute")
            btn_unmute.clicked.connect(lambda _, ch=ch: audio.unmute_channel(ch))

            ch_layout.addWidget(lbl)
            ch_layout.addWidget(fader_you)
            ch_layout.addWidget(fader_stream)
            ch_layout.addWidget(btn_mute)
            ch_layout.addWidget(btn_unmute)
            layout.addLayout(ch_layout)

        self.setLayout(layout)

    def init_audio(self):
        audio.init_audio()
        self.label.setText("Status: audio initialized")

    def toggle_preset(self):
        if self.preset_state:
            for ch in audio.CHANNELS:
                audio.unmute_channel(ch)
            self.label.setText("Preset: Stream")
        else:
            for ch in audio.CHANNELS:
                audio.mute_channel(ch)
            self.label.setText("Preset: NoSound")
        self.preset_state = not self.preset_state

app = QApplication(sys.argv)
window = WavePipe()
window.show()
sys.exit(app.exec_())
