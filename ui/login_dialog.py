from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .styles import LOGIN_DIALOG_STYLE


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Login")
        self.setFixedSize(600, 500)
        self.setStyleSheet(LOGIN_DIALOG_STYLE)

        self.username = None
        self.host = None
        self.port = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Join Chat")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; margin: 20px;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Server Host:"))
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        self.host_input.setPlaceholderText("Server IP address")
        layout.addWidget(self.host_input)

        layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit()
        self.port_input.setText("12345")
        self.port_input.setPlaceholderText("Server port")
        layout.addWidget(self.port_input)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_clicked)
        layout.addWidget(self.connect_btn)

        self.username_input.returnPressed.connect(self.connect_clicked)
        self.host_input.returnPressed.connect(self.connect_clicked)
        self.port_input.returnPressed.connect(self.connect_clicked)

        self.setLayout(layout)
        self.username_input.setFocus()

    def connect_clicked(self):
        username = self.username_input.text().strip()
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username")
            return

        if not host:
            host = "localhost"

        try:
            port = int(port) if port else 12345
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid port number")
            return

        self.username = username
        self.host = host
        self.port = port
        self.accept()