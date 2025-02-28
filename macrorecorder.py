import sys
import time
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                            QPushButton, QLabel, QListWidget, QLineEdit, QMessageBox,
                            QInputDialog, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from pynput import mouse
import pyautogui

class MouseListenerThread(QThread):
    """Thread for listening to mouse clicks"""
    click_detected = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()
        self.running = False
        
    def run(self):
        self.running = True
        
        def on_click(x, y, button, pressed):
            if not self.running:
                return False
            
            if button == mouse.Button.left and pressed:
                self.click_detected.emit((x, y))
            
        with mouse.Listener(on_click=on_click) as listener:
            while self.running:
                time.sleep(0.1)
            listener.stop()
    
    def stop(self):
        self.running = False


class PlaybackThread(QThread):
    """Thread for playing back mouse clicks"""
    playback_step = pyqtSignal(int)  # Emits current step
    playback_finished = pyqtSignal()  # Signals when playback is done
    
    def __init__(self, clicks):
        super().__init__()
        self.clicks = clicks
        self.running = False
    
    def run(self):
        self.running = True
        total_clicks = len(self.clicks)
        
        for i, (x, y) in enumerate(self.clicks):
            if not self.running:
                break
                
            try:
                # Perform the click
                pyautogui.click(x, y)
                
                # Signal progress
                self.playback_step.emit(i)
                
                # Pause between clicks (unless it's the last one)
                if i < total_clicks - 1 and self.running:
                    time.sleep(3)  # 3 second pause
            except Exception as e:
                print(f"Error during playback: {str(e)}")
        
        # Signal that we're done
        if self.running:
            self.playback_finished.emit()
        
        self.running = False
    
    def stop(self):
        self.running = False


class MacroRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Recorder")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize variables
        self.recording = False
        self.clicks = []
        self.macros = {}
        self.current_macro_name = ""
        
        # Flag to indicate if stop button was clicked
        self.stop_button_clicked = False
        
        # Load saved macros if they exist
        self.load_macros_from_file()
        
        # Set up the UI
        self.setup_ui()
        
        # Set up mouse listener thread
        self.mouse_listener = MouseListenerThread()
        self.mouse_listener.click_detected.connect(self.add_click)
        
        # Playback thread (will be initialized during playback)
        self.playback_thread = None
    
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel for macro list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Macro list
        macro_group = QGroupBox("Saved Macros")
        macro_layout = QVBoxLayout()
        
        self.macro_list = QListWidget()
        self.macro_list.itemClicked.connect(self.select_macro)
        self.update_macro_list()
        
        macro_layout.addWidget(self.macro_list)
        macro_group.setLayout(macro_layout)
        left_layout.addWidget(macro_group)
        
        # Create right panel for controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Recording controls
        recording_group = QGroupBox("Recording Controls")
        recording_layout = QVBoxLayout()
        
        # Status display
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        recording_layout.addWidget(self.status_label)
        
        # Clicks display
        self.clicks_label = QLabel("Recorded clicks: 0")
        self.clicks_label.setAlignment(Qt.AlignCenter)
        recording_layout.addWidget(self.clicks_label)
        
        # Record and stop buttons
        buttons_layout = QHBoxLayout()
        
        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setFixedHeight(50)
        buttons_layout.addWidget(self.record_button)
        
        self.stop_button = QPushButton("Stop")
        # Connect stop button to custom slot that sets flag first, then calls stop_recording
        self.stop_button.clicked.connect(self.handle_stop_button_click)
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedHeight(50)
        buttons_layout.addWidget(self.stop_button)
        
        recording_layout.addLayout(buttons_layout)
        recording_group.setLayout(recording_layout)
        right_layout.addWidget(recording_group)
        
        # Macro controls
        macro_control_group = QGroupBox("Macro Controls")
        macro_control_layout = QVBoxLayout()
        
        self.current_macro_label = QLabel("Current Macro: None")
        macro_control_layout.addWidget(self.current_macro_label)
        
        # Macro name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Macro Name:"))
        self.macro_name_input = QLineEdit()
        name_layout.addWidget(self.macro_name_input)
        macro_control_layout.addLayout(name_layout)
        
        # Save and play buttons
        action_buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Macro")
        self.save_button.clicked.connect(self.save_macro)
        self.save_button.setEnabled(False)
        action_buttons_layout.addWidget(self.save_button)
        
        self.play_button = QPushButton("Play Macro")
        self.play_button.clicked.connect(self.play_macro)
        self.play_button.setEnabled(False)
        action_buttons_layout.addWidget(self.play_button)
        
        self.delete_button = QPushButton("Delete Macro")
        self.delete_button.clicked.connect(self.delete_macro)
        self.delete_button.setEnabled(False)
        action_buttons_layout.addWidget(self.delete_button)
        
        macro_control_layout.addLayout(action_buttons_layout)
        macro_control_group.setLayout(macro_control_layout)
        right_layout.addWidget(macro_control_group)
        
        # Add layouts to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])
        main_layout.addWidget(splitter)
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def handle_stop_button_click(self):
        """Handler for stop button clicks that sets a flag before stopping"""
        self.stop_button_clicked = True
        self.stop_recording()
    
    def start_recording(self):
        # Reset clicks
        self.clicks = []
        self.recording = True
        self.stop_button_clicked = False
        
        # Update UI
        self.status_label.setText("Status: Recording")
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.play_button.setEnabled(False)
        self.clicks_label.setText("Recorded clicks: 0")
        self.save_button.setEnabled(False)
        
        # Start mouse listener
        self.mouse_listener.start()
    
    def stop_recording(self):
        if not self.recording:
            return
        
        self.recording = False
        self.mouse_listener.stop()
        
        # If we have clicks and the last click was added AFTER the stop button was clicked,
        # we need to remove that last click
        if self.stop_button_clicked and len(self.clicks) > 0:
            self.clicks.pop()  # Remove the last click
            self.clicks_label.setText(f"Recorded clicks: {len(self.clicks)}")
        
        # Reset flag
        self.stop_button_clicked = False
        
        # Update UI
        self.status_label.setText("Status: Stopped")
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(len(self.clicks) > 0)
        
        # Show message with results
        if len(self.clicks) > 0:
            QMessageBox.information(self, "Recording Finished", 
                                  f"Recorded {len(self.clicks)} mouse clicks. You can now save this macro.")
    
    def add_click(self, position):
        # If stop button was clicked, don't add any more clicks
        if self.stop_button_clicked:
            print("Ignoring click due to stop button being clicked")
            return
            
        x, y = position
        self.clicks.append((x, y))
        self.clicks_label.setText(f"Recorded clicks: {len(self.clicks)}")
    
    def save_macro(self):
        name = self.macro_name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a name for the macro.")
            return
        
        if name in self.macros and self.current_macro_name != name:
            confirm = QMessageBox.question(self, "Confirm Overwrite", 
                                        f"A macro named '{name}' already exists. Do you want to overwrite it?",
                                        QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.No:
                return
        
        self.macros[name] = self.clicks
        self.current_macro_name = name
        self.current_macro_label.setText(f"Current Macro: {name}")
        self.save_macros_to_file()
        self.update_macro_list()
        self.play_button.setEnabled(True)
        
        QMessageBox.information(self, "Success", f"Macro '{name}' saved successfully.")
    
    def select_macro(self, item):
        name = item.text()
        self.current_macro_name = name
        self.macro_name_input.setText(name)
        self.current_macro_label.setText(f"Current Macro: {name}")
        self.clicks = self.macros[name]
        self.clicks_label.setText(f"Recorded clicks: {len(self.clicks)}")
        self.play_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.save_button.setEnabled(True)
    
    def update_macro_list(self):
        self.macro_list.clear()
        for name in sorted(self.macros.keys()):
            self.macro_list.addItem(name)
    
    def play_macro(self):
        if not self.current_macro_name or self.current_macro_name not in self.macros:
            QMessageBox.warning(self, "Warning", "Please select a macro to play.")
            return
        
        clicks = self.macros[self.current_macro_name]
        if not clicks:
            QMessageBox.warning(self, "Warning", "The selected macro has no recorded clicks.")
            return
        
        # Disable UI during playback
        self.record_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.macro_list.setEnabled(False)
        self.status_label.setText(f"Status: Playing macro '{self.current_macro_name}'")
        
        # Create and set up playback thread
        self.playback_thread = PlaybackThread(clicks)
        self.playback_thread.playback_step.connect(self.update_playback_status)
        self.playback_thread.playback_finished.connect(self.playback_completed)
        
        # Start the playback thread
        self.playback_thread.start()
    
    def update_playback_status(self, step_index):
        total_clicks = len(self.macros[self.current_macro_name])
        self.status_label.setText(f"Status: Playing macro '{self.current_macro_name}' - " 
                                f"Click {step_index + 1}/{total_clicks}")
    
    def playback_completed(self):
        # Update UI
        self.status_label.setText(f"Status: Ready - Playback of '{self.current_macro_name}' completed")
        
        # Re-enable UI
        self.record_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.macro_list.setEnabled(True)
        
        # Clean up thread
        self.playback_thread = None
    
    def delete_macro(self):
        if not self.current_macro_name or self.current_macro_name not in self.macros:
            return
        
        confirm = QMessageBox.question(self, "Confirm Deletion", 
                                     f"Are you sure you want to delete macro '{self.current_macro_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        
        del self.macros[self.current_macro_name]
        self.save_macros_to_file()
        self.update_macro_list()
        
        self.current_macro_name = ""
        self.current_macro_label.setText("Current Macro: None")
        self.macro_name_input.clear()
        self.clicks = []
        self.clicks_label.setText("Recorded clicks: 0")
        self.play_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.save_button.setEnabled(False)
    
    def save_macros_to_file(self):
        try:
            # Convert to serializable format
            serializable_macros = {}
            for name, clicks in self.macros.items():
                serializable_macros[name] = clicks
            
            with open('macros.json', 'w') as file:
                json.dump(serializable_macros, file)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save macros: {str(e)}")
    
    def load_macros_from_file(self):
        try:
            if os.path.exists('macros.json'):
                with open('macros.json', 'r') as file:
                    self.macros = json.load(file)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load macros: {str(e)}")
    
    def closeEvent(self, event):
        # Stop recording if active
        if self.recording:
            self.stop_recording()
            
        # Stop playback if active
        if self.playback_thread and self.playback_thread.isRunning():
            self.playback_thread.stop()
            self.playback_thread.wait()
            
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MacroRecorder()
    window.show()
    sys.exit(app.exec_()) 