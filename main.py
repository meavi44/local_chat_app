import sys
from PyQt5.QtWidgets import QApplication, QDialog
from ui.login_dialog import LoginDialog
from ui.chat_window import ChatWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        main_window = ChatWindow()
        main_window.show()

        main_window.connect_to_server(
            login_dialog.username,
            login_dialog.host,
            login_dialog.port
        )

        sys.exit(app.exec_())


if __name__ == "__main__":
    main()