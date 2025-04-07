from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QTextEdit
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import subprocess
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser

class VoiceRecognitionThread(QThread):
    command_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = True

    def run(self):
        while self.running:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)

            try:
                command = self.recognizer.recognize_google(audio).lower()
                self.command_received.emit(command)
            except sr.UnknownValueError:
                self.command_received.emit("Sorry, I didn't catch that.")
            except sr.RequestError:
                self.command_received.emit("Speech service is unavailable.")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Application Manager")
        self.setGeometry(300, 300, 600, 500)
        self.setWindowIcon(QIcon(r"C:\Users\dell\Pictures\Captain_America_Shield.webp"))
        self.setStyleSheet("background-color: #1e1e2f; color: white;")

        layout = QVBoxLayout()

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        label = QLabel("Welcome to Your Application Manager", self)
        label.setFont(QFont("Arial", 18, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #ff79c6;")
        layout.addWidget(label)

        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #282a36; color: #f8f8f2;")
        layout.addWidget(self.console)

        self.greet_user()

        buttons = {
            "Open VS Code": self.open_vscode,
            "Open YouTube": self.open_youtube,
            "Open ChatGPT": self.open_chatgpt,
            "Open All": self.open_all
        }

        for btn_text, btn_function in buttons.items():
            button = QPushButton(btn_text)
            button.clicked.connect(btn_function)
            button.setFont(QFont("Arial", 12))
            button.setStyleSheet("background-color: #6272a4; color: white; padding: 10px; border-radius: 10px;")
            layout.addWidget(button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.voice_thread = VoiceRecognitionThread()
        self.voice_thread.command_received.connect(self.process_command)
        self.voice_thread.start()

    def greet_user(self):
        current_hour = datetime.datetime.now().hour
        if current_hour < 12:
            self.speak("Good morning! How can I assist you today?")
        elif 12 <= current_hour < 18:
            self.speak("Good afternoon! How is your day going?")
        else:
            self.speak("Good evening! What would you like me to do?")

    def speak(self, text):
        self.console.append(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def open_vscode(self):
        self.speak("Opening Visual Studio Code")
        subprocess.Popen([r"C:\\Users\\dell\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"])

    def open_youtube(self):
        self.speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    def open_chatgpt(self):
        self.speak("Opening ChatGPT")
        webbrowser.open("https://chat.openai.com")

    def open_all(self):
        self.speak("Opening all applications")
        self.open_vscode()
        self.open_youtube()
        self.open_chatgpt()

    def process_command(self, command):
        self.console.append(f"Command Received: {command}")

        if "jarvis" in command:
            self.speak("How can I assist you?")
        elif "open code" in command:
            self.open_vscode()
        elif "open youtube" in command:
            self.open_youtube()
        elif "open chatgpt" in command:
            self.open_chatgpt()
        elif "open all" in command:
            self.open_all()
        elif "exit" in command or "quit" in command:
            self.speak("Exiting the application")
            self.voice_thread.stop()
            sys.exit(0)

    def closeEvent(self, event):
        self.voice_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
