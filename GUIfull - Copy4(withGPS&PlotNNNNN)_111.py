import sys
import serial
import cv2
import requests
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Serial Port Configuration
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException:
    ser = None
    print("Failed to open serial port!")

ESP32_CAM_URL = "http://10.21.93.7"  # ESP32-CAM Stream URL


class SerialReader(QThread): 
    data_received = pyqtSignal(str)

    def run(self):
        if ser is None:
            return
        while True:
            if ser.in_waiting:
                data = ser.readline().decode(errors='ignore').strip()
                self.data_received.emit(data)


class VideoThread(QThread):
    frame_received = pyqtSignal(QImage)

    def run(self):
        while True:
            try:
                response = requests.get(ESP32_CAM_URL + "/capture", timeout=1)
                if response.status_code == 200:
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    self.frame_received.emit(qimg)
            except requests.exceptions.RequestException:
                continue


class SensorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Data & ESP32-CAM")
        self.setFixedSize(1000, 900)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.layout = QGridLayout()

        # Sensor Labels
        self.gas_label = QLabel("Gas: 0", self)
        self.humidity_label = QLabel("Humidity: 0%", self)
        self.temp_label = QLabel("Temperature: 0 C", self)
        self.lat_label = QLabel("Latitude: N/A", self)
        self.lon_label = QLabel("Longitude: N/A", self)

        for label in [self.gas_label, self.humidity_label, self.temp_label, self.lat_label, self.lon_label]:
            label.setFont(QFont("Arial", 14, QFont.Bold))
            label.setStyleSheet("color: #333; padding: 10px; background-color: white; border-radius: 8px;")
            label.setFrameShape(QFrame.StyledPanel)

        self.layout.addWidget(self.gas_label, 0, 0)
        self.layout.addWidget(self.humidity_label, 0, 1)
        self.layout.addWidget(self.temp_label, 1, 0, 1, 2)
        self.layout.addWidget(self.lat_label, 2, 0)
        self.layout.addWidget(self.lon_label, 2, 1)

        # Rover Control Buttons
        rover_layout = QGridLayout()
        button_style = "background-color: #0078D7; color: white; padding: 10px; border-radius: 5px; font-size: 14px;"

        self.forward_button = QPushButton("Forward", self)
        self.forward_button.setStyleSheet(button_style)
        self.forward_button.clicked.connect(lambda: self.send_serial_command("Forward"))
        rover_layout.addWidget(self.forward_button, 0, 1)

        self.left_button = QPushButton("Left", self)
        self.left_button.setStyleSheet(button_style)
        self.left_button.clicked.connect(lambda: self.send_serial_command("Left"))
        rover_layout.addWidget(self.left_button, 1, 0)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setStyleSheet(button_style)
        self.stop_button.clicked.connect(lambda: self.send_serial_command("Stop"))
        rover_layout.addWidget(self.stop_button, 1, 1)

        self.right_button = QPushButton("Right", self)
        self.right_button.setStyleSheet(button_style)
        self.right_button.clicked.connect(lambda: self.send_serial_command("Right"))
        rover_layout.addWidget(self.right_button, 1, 2)

        self.backward_button = QPushButton("Backward", self)
        self.backward_button.setStyleSheet(button_style)
        self.backward_button.clicked.connect(lambda: self.send_serial_command("Backward"))
        rover_layout.addWidget(self.backward_button, 2, 1)

        self.mode_button = QPushButton("Mode", self)
        self.mode_button.setStyleSheet(button_style)
        self.mode_button.clicked.connect(lambda: self.send_serial_command("Mode"))
        rover_layout.addWidget(self.mode_button, 3, 1)

        self.layout.addLayout(rover_layout, 3, 0, 1, 2)

        # Camera Control Buttons
        cam_layout = QGridLayout()

        self.cam_up_button = QPushButton("Cam Up", self)
        self.cam_up_button.setStyleSheet(button_style)
        self.cam_up_button.clicked.connect(lambda: self.send_serial_command("Cam_Up"))
        cam_layout.addWidget(self.cam_up_button, 0, 1)

        self.cam_left_button = QPushButton("Cam Left", self)
        self.cam_left_button.setStyleSheet(button_style)
        self.cam_left_button.clicked.connect(lambda: self.send_serial_command("Cam_Left"))
        cam_layout.addWidget(self.cam_left_button, 1, 0)

        self.cam_reset_button = QPushButton("Cam Reset", self)
        self.cam_reset_button.setStyleSheet(button_style)
        self.cam_reset_button.clicked.connect(lambda: self.send_serial_command("Cam_Reset"))
        cam_layout.addWidget(self.cam_reset_button, 1, 1)

        self.cam_right_button = QPushButton("Cam Right", self)
        self.cam_right_button.setStyleSheet(button_style)
        self.cam_right_button.clicked.connect(lambda: self.send_serial_command("Cam_Right"))
        cam_layout.addWidget(self.cam_right_button, 1, 2)

        self.cam_down_button = QPushButton("Cam Down", self)
        self.cam_down_button.setStyleSheet(button_style)
        self.cam_down_button.clicked.connect(lambda: self.send_serial_command("Cam_Down"))
        cam_layout.addWidget(self.cam_down_button, 2, 1)

        self.layout.addLayout(cam_layout, 3, 4, 1, 2)

        # Video Feed
        self.video_label = QLabel(self)
        self.video_label.setStyleSheet("border: 2px solid #444; background-color: black;")
        self.layout.addWidget(self.video_label, 0, 4, 3, 2)

        # Real-Time Plot
        self.figure = plt.figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas, 4, 0, 1, 6)

        self.setLayout(self.layout)

        # Start Serial Thread
        self.serial_thread = SerialReader()
        self.serial_thread.data_received.connect(self.process_serial_data)
        self.serial_thread.start()

        # Start Video Thread
        self.video_thread = VideoThread()
        self.video_thread.frame_received.connect(self.update_video_frame)
        self.video_thread.start()

        self.latitudes = []
        self.longitudes = []

    def process_serial_data(self, data):
        print(f"Raw Data: {data}")
        if "Received Data:" in data:
            values = data.replace("Received Data: ", "").split()
            print(f"Parsed Values: {values}")
            if len(values) == 5:
                # Extract and plot latitude and longitude differences
                self.gas_label.setText(f"Gas: {values[0]}ppm")
                self.humidity_label.setText(f"Humidity: {values[1]}%")
                self.temp_label.setText(f"Temperature: {values[2]} C")
                self.lat_label.setText(f"Latitude: {values[3]}")
                self.lon_label.setText(f"Longitude: {values[4]}")

                # Capture the latitude and longitude, removing the decimal part
                lat = float(values[3])
                lon = float(values[4])  # Get the last 3 digits
                self.latitudes.append(lat)
                self.longitudes.append(lon)

                # Update the real-time plot
                self.plot_path()

    def update_video_frame(self, qimg):
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def send_serial_command(self, command):
        if ser and ser.is_open:
            print(f"Sending command: {command}")
            ser.write((command + "\n").encode())
            ser.flush()

    def keyPressEvent(self, event):
        key = event.text().lower()
        command_map = {'w': "Forward", 's': "Backward", 'a': "Left", 'd': "Right", 'f': "Stop", 'm': "Mode"}
        if key in command_map:
            self.send_serial_command(command_map[key])
        else:
            super().keyPressEvent(event)

    def plot_path(self):
    # Clear only the axes (not the entire figure) to optimize rendering
        ax = self.figure.gca()  # Get current axis
        ax.clear()
        
        if len(self.latitudes) > 0 and len(self.longitudes) > 0:
            # Plot the path with connected lines
            ax.plot(self.longitudes, self.latitudes, 'b-', marker='o', markersize=4)
            
            # Add the most recent point with a different color
            if len(self.latitudes) > 1:
                ax.plot(self.longitudes[-1], self.latitudes[-1], 'ro', markersize=6)
            
            # Set better axis limits - focus on the area with data
            # Add a small buffer around the data
            x_buffer = (max(self.longitudes) - min(self.longitudes)) * 0.1 if len(self.longitudes) > 1 else 0.001
            y_buffer = (max(self.latitudes) - min(self.latitudes)) * 0.1 if len(self.latitudes) > 1 else 0.001
            
            # Set limits with buffer
            ax.set_xlim(min(self.longitudes) - x_buffer, max(self.longitudes) + x_buffer)
            ax.set_ylim(min(self.latitudes) - y_buffer, max(self.latitudes) + y_buffer)
        
        ax.set_title("GPS Track")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True)
        self.canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = SensorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
