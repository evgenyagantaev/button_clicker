import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSpinBox, QGroupBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
import pyautogui
import numpy as np

class ScreenSpy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Spy")
        self.setGeometry(100, 100, 800, 600)
        
        # Default screenshot area
        self.x1, self.y1, self.x2, self.y2 = 0, 0, 500, 500
        
        # Create the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create controls for screenshot area
        self.create_control_panel()
        
        # Create image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.image_label)
        
        # Set up timer for screenshots (5 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.take_screenshot)
        self.timer.start(5000)  # 5000 ms = 5 seconds
        
        # Take initial screenshot
        self.take_screenshot()
    
    def create_control_panel(self):
        control_group = QGroupBox("Screenshot Area")
        control_layout = QHBoxLayout()
        
        # X1 control
        x1_layout = QVBoxLayout()
        x1_label = QLabel("X1:")
        self.x1_spin = QSpinBox()
        self.x1_spin.setRange(0, 3000)
        self.x1_spin.setValue(self.x1)
        self.x1_spin.valueChanged.connect(self.update_x1)
        x1_layout.addWidget(x1_label)
        x1_layout.addWidget(self.x1_spin)
        
        # Y1 control
        y1_layout = QVBoxLayout()
        y1_label = QLabel("Y1:")
        self.y1_spin = QSpinBox()
        self.y1_spin.setRange(0, 3000)
        self.y1_spin.setValue(self.y1)
        self.y1_spin.valueChanged.connect(self.update_y1)
        y1_layout.addWidget(y1_label)
        y1_layout.addWidget(self.y1_spin)
        
        # X2 control
        x2_layout = QVBoxLayout()
        x2_label = QLabel("X2:")
        self.x2_spin = QSpinBox()
        self.x2_spin.setRange(0, 3000)
        self.x2_spin.setValue(self.x2)
        self.x2_spin.valueChanged.connect(self.update_x2)
        x2_layout.addWidget(x2_label)
        x2_layout.addWidget(self.x2_spin)
        
        # Y2 control
        y2_layout = QVBoxLayout()
        y2_label = QLabel("Y2:")
        self.y2_spin = QSpinBox()
        self.y2_spin.setRange(0, 3000)
        self.y2_spin.setValue(self.y2)
        self.y2_spin.valueChanged.connect(self.update_y2)
        y2_layout.addWidget(y2_label)
        y2_layout.addWidget(self.y2_spin)
        
        # Add refresh button
        refresh_button = QPushButton("Take Screenshot Now")
        refresh_button.clicked.connect(self.take_screenshot)
        
        # Add layouts to control panel
        control_layout.addLayout(x1_layout)
        control_layout.addLayout(y1_layout)
        control_layout.addLayout(x2_layout)
        control_layout.addLayout(y2_layout)
        control_layout.addWidget(refresh_button)
        
        control_group.setLayout(control_layout)
        self.main_layout.addWidget(control_group)
    
    def update_x1(self, value):
        self.x1 = value
    
    def update_y1(self, value):
        self.y1 = value
    
    def update_x2(self, value):
        self.x2 = value
    
    def update_y2(self, value):
        self.y2 = value
    
    def take_screenshot(self):
        try:
            # Calculate screenshot dimensions
            left = min(self.x1, self.x2)
            top = min(self.y1, self.y2)
            width = abs(self.x2 - self.x1)
            height = abs(self.y2 - self.y1)
            
            # Take the screenshot
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # Convert to QPixmap for display
            img = screenshot.convert("RGB")
            img_array = np.array(img)
            height, width, channels = img_array.shape
            bytes_per_line = channels * width
            
            q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Scale the image to fit the label while maintaining aspect ratio
            pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), 
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Display the screenshot
            self.image_label.setPixmap(pixmap)
            self.statusBar().showMessage(f"Screenshot taken at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenSpy()
    window.show()
    sys.exit(app.exec_()) 