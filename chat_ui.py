# import sys
# import os
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# import requests
# from client import ChatClient  # Your existing client code with ChatClient class


# class LoginDialog(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Chat Login")
#         self.setFixedSize(400, 300)
#         self.setStyleSheet("""
#             QDialog {
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
#                     stop:0 #2E3440, stop:1 #3B4252);
#                 color: #ECEFF4;
#             }
#             QLabel {
#                 color: #ECEFF4;
#                 font-size: 14px;
#                 font-weight: bold;
#             }
#             QLineEdit {
#                 background: #434C5E;
#                 border: 2px solid #4C566A;
#                 border-radius: 8px;
#                 padding: 10px;
#                 font-size: 14px;
#                 color: #ECEFF4;
#             }
#             QLineEdit:focus {
#                 border-color: #5E81AC;
#             }
#             QPushButton {
#                 background: #5E81AC;
#                 color: white;
#                 border: none;
#                 padding: 12px 24px;
#                 border-radius: 8px;
#                 font-size: 14px;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background: #81A1C1;
#             }
#             QPushButton:pressed {
#                 background: #4C566A;
#             }
#         """)

#         self.username = None
#         self.host = None
#         self.port = None
#         self.setup_ui()

#     def setup_ui(self):
#         layout = QVBoxLayout()

#         title = QLabel("Join Chat")
#         title.setAlignment(Qt.AlignCenter)
#         title.setStyleSheet("font-size: 24px; margin: 20px;")
#         layout.addWidget(title)

#         layout.addWidget(QLabel("Username:"))
#         self.username_input = QLineEdit()
#         self.username_input.setPlaceholderText("Enter your username")
#         layout.addWidget(self.username_input)

#         layout.addWidget(QLabel("Server Host:"))
#         self.host_input = QLineEdit()
#         self.host_input.setText("localhost")
#         self.host_input.setPlaceholderText("Server IP address")
#         layout.addWidget(self.host_input)

#         layout.addWidget(QLabel("Port:"))
#         self.port_input = QLineEdit()
#         self.port_input.setText("12345")
#         self.port_input.setPlaceholderText("Server port")
#         layout.addWidget(self.port_input)

#         self.connect_btn = QPushButton("Connect")
#         self.connect_btn.clicked.connect(self.connect_clicked)
#         layout.addWidget(self.connect_btn)

#         self.username_input.returnPressed.connect(self.connect_clicked)
#         self.host_input.returnPressed.connect(self.connect_clicked)
#         self.port_input.returnPressed.connect(self.connect_clicked)

#         self.setLayout(layout)
#         self.username_input.setFocus()

#     def connect_clicked(self):
#         username = self.username_input.text().strip()
#         host = self.host_input.text().strip()
#         port = self.port_input.text().strip()

#         if not username:
#             QMessageBox.warning(self, "Error", "Please enter a username")
#             return

#         if not host:
#             host = "localhost"

#         try:
#             port = int(port) if port else 12345
#         except ValueError:
#             QMessageBox.warning(self, "Error", "Invalid port number")
#             return

#         self.username = username
#         self.host = host
#         self.port = port
#         self.accept()


# class ChatWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.client = ChatClient()
#         self.current_chat = None  # 'user:username' or 'group:groupname'
#         self.chat_history = {}  # Store chat history for each conversation

#         self.setup_ui()
#         self.setup_connections()
#         self.setup_styles()

#     def setup_ui(self):
#         self.setWindowTitle("PyQt5 Chat Application")
#         self.setGeometry(100, 100, 1200, 800)

#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)

#         main_layout = QHBoxLayout()
#         central_widget.setLayout(main_layout)

#         left_panel = self.create_left_panel()
#         main_layout.addWidget(left_panel, 1)

#         right_panel = self.create_right_panel()
#         main_layout.addWidget(right_panel, 3)

#         self.status_bar = self.statusBar()
#         self.status_bar.showMessage("Not connected")

#     def create_left_panel(self):
#         left_widget = QWidget()
#         left_layout = QVBoxLayout()

#         users_label = QLabel("Online Users")
#         users_label.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px 0;")
#         left_layout.addWidget(users_label)

#         self.users_list = QListWidget()
#         self.users_list.itemDoubleClicked.connect(self.user_double_clicked)
#         left_layout.addWidget(self.users_list)

#         groups_label = QLabel("Groups")
#         groups_label.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px 0;")
#         left_layout.addWidget(groups_label)

#         self.groups_list = QListWidget()
#         self.groups_list.itemDoubleClicked.connect(self.group_double_clicked)
#         left_layout.addWidget(self.groups_list)

#         group_buttons = QHBoxLayout()
#         self.create_group_btn = QPushButton("Create Group")
#         self.create_group_btn.clicked.connect(self.create_group)
#         group_buttons.addWidget(self.create_group_btn)

#         self.join_group_btn = QPushButton("Join Group")
#         self.join_group_btn.clicked.connect(self.join_group)
#         group_buttons.addWidget(self.join_group_btn)

#         left_layout.addLayout(group_buttons)

#         left_widget.setLayout(left_layout)
#         return left_widget

#     def create_right_panel(self):
#         right_widget = QWidget()
#         right_layout = QVBoxLayout()

#         self.chat_header = QLabel("Select a user or group to start chatting")
#         self.chat_header.setStyleSheet("font-weight: bold; font-size: 18px; padding: 10px; background: #4C566A; border-radius: 5px;")
#         self.chat_header.setAlignment(Qt.AlignCenter)
#         right_layout.addWidget(self.chat_header)

#         self.chat_display = QTextEdit()
#         self.chat_display.setReadOnly(True)
#         right_layout.addWidget(self.chat_display)

#         input_layout = QHBoxLayout()

#         self.message_input = QLineEdit()
#         self.message_input.setPlaceholderText("Type your message here...")
#         self.message_input.returnPressed.connect(self.send_message)
#         input_layout.addWidget(self.message_input)

#         self.send_btn = QPushButton("Send")
#         self.send_btn.clicked.connect(self.send_message)
#         input_layout.addWidget(self.send_btn)

#         self.file_btn = QPushButton("📎 File")
#         self.file_btn.clicked.connect(self.send_file)
#         input_layout.addWidget(self.file_btn)

#         right_layout.addLayout(input_layout)

#         self.message_input.setEnabled(False)
#         self.send_btn.setEnabled(False)
#         self.file_btn.setEnabled(False)

#         right_widget.setLayout(right_layout)
#         return right_widget

#     def setup_connections(self):
#         self.client.message_received.connect(self.on_message_received)
#         self.client.connection_status.connect(self.on_connection_status)
#         self.client.user_list_updated.connect(self.on_user_list_updated)
#         self.client.group_list_updated.connect(self.on_group_list_updated)
#         # Assuming your client has these signals, else comment out:
#         try:
#             self.client.file_received.connect(self.on_file_received)
#         except AttributeError:
#             pass
#         self.client.error_occurred.connect(self.on_error_occurred)

#     def setup_styles(self):
#         self.setStyleSheet("""
#             QMainWindow {
#                 background: #2E3440;
#                 color: #ECEFF4;
#             }
#             QWidget {
#                 background: #2E3440;
#                 color: #ECEFF4;
#             }
#             QListWidget {
#                 background: #3B4252;
#                 border: 1px solid #4C566A;
#                 border-radius: 5px;
#                 padding: 5px;
#                 selection-background-color: #5E81AC;
#             }
#             QListWidget::item {
#                 padding: 8px;
#                 border-radius: 3px;
#                 margin: 2px;
#             }
#             QListWidget::item:hover {
#                 background: #434C5E;
#             }
#             QListWidget::item:selected {
#                 background: #5E81AC;
#             }
#             QTextEdit {
#                 background: #3B4252;
#                 border: 1px solid #4C566A;
#                 border-radius: 5px;
#                 padding: 10px;
#                 font-size: 14px;
#             }
#             QLineEdit {
#                 background: #434C5E;
#                 border: 2px solid #4C566A;
#                 border-radius: 8px;
#                 padding: 10px;
#                 font-size: 14px;
#             }
#             QLineEdit:focus {
#                 border-color: #5E81AC;
#             }
#             QPushButton {
#                 background: #5E81AC;
#                 color: white;
#                 border: none;
#                 padding: 8px 16px;
#                 border-radius: 5px;
#                 font-size: 14px;
#                 font-weight: bold;
#             }
#             QPushButton:hover {
#                 background: #81A1C1;
#             }
#             QPushButton:pressed {
#                 background: #4C566A;
#             }
#             QPushButton:disabled {
#                 background: #4C566A;
#                 color: #6C7086;
#             }
#             QLabel {
#                 color: #ECEFF4;
#             }
#             QStatusBar {
#                 background: #3B4252;
#                 color: #ECEFF4;
#             }
#         """)

#     def connect_to_server(self, username, host, port):
#         success = self.client.connect_to_server(username, host, port)
#         if success:
#             self.setWindowTitle(f"Chat - {username}")

#     def user_double_clicked(self, item):
#         username = item.text()
#         if username != self.client.username:
#             self.current_chat = f"user:{username}"
#             self.chat_header.setText(f"Private Chat with {username}")
#             self.load_chat_history()
#             self.enable_input_controls()

#     def group_double_clicked(self, item):
#         group_name = item.text()
#         self.current_chat = f"group:{group_name}"
#         self.chat_header.setText(f"Group Chat: {group_name}")
#         self.load_chat_history()
#         self.enable_input_controls()

#     def enable_input_controls(self):
#         self.message_input.setEnabled(True)
#         self.send_btn.setEnabled(True)
#         self.file_btn.setEnabled(True)
#         self.message_input.setFocus()

#     def disable_input_controls(self):
#         self.message_input.setEnabled(False)
#         self.send_btn.setEnabled(False)
#         self.file_btn.setEnabled(False)

#     def send_message(self):
#         message = self.message_input.text().strip()
#         if not message or not self.current_chat:
#             return

#         chat_type, chat_name = self.current_chat.split(':', 1)

#         if chat_type == 'user':
#             success = self.client.send_private_message(chat_name, message)
#         elif chat_type == 'group':
#             success = self.client.send_group_message(chat_name, message)

#         if success:
#             self.add_message_to_chat(self.client.username, message, sent=True)
#             self.message_input.clear()

#     def send_file(self):
#         if not self.current_chat:
#             return

#         chat_type, chat_name = self.current_chat.split(':', 1)

#         if chat_type == 'group':
#             QMessageBox.information(self, "Info", "File sharing is only available in private chats")
#             return

#         file_path, _ = QFileDialog.getOpenFileName(
#             self, "Select file to send", "", "All Files (*)"
#         )

#         if file_path:
#             success = self.client.send_file(chat_name, file_path)
#             if success:
#                 filename = os.path.basename(file_path)
#                 self.add_message_to_chat(
#                     self.client.username,
#                     f"📎 Sent file: {filename}",
#                     sent=True
#                 )

#     def create_group(self):
#         group_name, ok = QInputDialog.getText(self, "Create Group", "Enter group name:")
#         if ok and group_name.strip():
#             self.client.create_group(group_name.strip())

#     def join_group(self):
#         if self.groups_list.count() == 0:
#             QMessageBox.information(self, "Info", "No groups available")
#             return

#         groups = [self.groups_list.item(i).text() for i in range(self.groups_list.count())]
#         group_name, ok = QInputDialog.getItem(self, "Join Group", "Select group to join:", groups, 0, False)
#         if ok and group_name:
#                 self.client.join_group(group_name)
                
#     def add_message_to_chat(self, sender, content, sent=False, timestamp=None):
#         if not timestamp:
#             from datetime import datetime
#             timestamp = datetime.now().strftime('%H:%M')

#         if self.current_chat not in self.chat_history:
#             self.chat_history[self.current_chat] = []

#         self.chat_history[self.current_chat].append({
#             'sender': sender,
#             'content': content,
#             'timestamp': timestamp,
#             'sent': sent
#         })

#         # Larger font size and bubble style
#         font_size = "16px"
#         max_width = "70%"

#         if sent:
#             # Your own messages, right aligned, blue bubble
#             message_html = f"""
#             <div style="display: flex; justify-content: flex-end; margin: 8px 0;">
#                 <div style="
#                     background-color: #5e4343;
#                     color: #5e4343;
#                     padding: 12px 18px;
#                     border-radius: 18px 18px 0 18px;
#                     max-width: {max_width};
#                     font-size: {font_size};
#                     word-wrap: break-word;
#                 ">
#                     {content}
#                     <div style="font-size: 10px; color: #D8DEE9; text-align: right; margin-top: 4px;">{timestamp}</div>
#                 </div>
#             </div>
#             """
#         else:
#             # Others' messages, left aligned, dark gray bubble, with sender name
#             message_html = f"""
#             <div style="display: flex; justify-content: flex-start; margin: 8px 0;">
#                 <div style="
#                     background-color: #5e4343;
#                     color: #5e4343;
#                     padding: 12px 18px;
#                     border-radius: 18px 18px 18px 0;
#                     max-width: {max_width};
#                     font-size: {font_size};
#                     word-wrap: break-word;
#                 ">
#                     <b style="color: #81A1C1;">{sender}</b><br>
#                     {content}
#                     <div style="font-size: 10px; color: #D8DEE9; margin-top: 4px;">{timestamp}</div>
#                 </div>
#             </div>
#             """

#         self.chat_display.append(message_html)
#         scrollbar = self.chat_display.verticalScrollBar()
#         scrollbar.setValue(scrollbar.maximum())


#     def load_chat_history(self):
#         self.chat_display.clear()

       

#         try:
#             if not self.current_chat:
#                 return

#             chat_type, name = self.current_chat.split(":", 1)

#             url = f"http://localhost:8000/messages/{self.client.username}"
#             response = requests.get(url)
#             if response.status_code == 200:
#                 messages = response.json()
#                 for msg in messages:
#                     sender = msg.get('sender')
#                     receiver = msg.get('receiver')
#                     content = msg.get('content')
#                     timestamp = msg.get('timestamp')
#                     is_group = msg.get('is_group', False)

#                 # Display only relevant messages
#                     if chat_type == 'user':
#                         if ((sender == name and receiver == self.client.username) or 
#                             (sender == self.client.username and receiver == name)):
#                             self.add_message_to_chat(sender, content, sent=(sender == self.client.username), timestamp=timestamp)

#                         elif chat_type == 'group':
#                             if is_group and msg.get('group') == name:
#                                 self.add_message_to_chat(sender, content, sent=(sender == self.client.username), timestamp=timestamp)

                

#         except Exception as e:
#             self.chat_display.append(f"❌ Error loading chat history: {str(e)}")


#     def on_message_received(self, message):
#         msg_type = message.get('type')

#         if msg_type == 'private_message':
#             sender = message.get('sender')
#             content = message.get('content')
#             timestamp = message.get('timestamp')

#             chat_key = f"user:{sender}"

#             if self.current_chat == chat_key:
#                 self.add_message_to_chat(sender, content, sent=False, timestamp=timestamp)
#             else:
#                 if chat_key not in self.chat_history:
#                     self.chat_history[chat_key] = []
#                 self.chat_history[chat_key].append({
#                     'sender': sender,
#                     'content': content,
#                     'timestamp': timestamp,
#                     'sent': False
#                 })
#                 self.show_notification(f"New message from {sender}", content)

#         elif msg_type == 'group_message':
#             sender = message.get('sender')
#             group = message.get('group')
#             content = message.get('content')
#             timestamp = message.get('timestamp')

#             chat_key = f"group:{group}"

#             if self.current_chat == chat_key:
#                 self.add_message_to_chat(sender, content, sent=False, timestamp=timestamp)
#             else:
#                 if chat_key not in self.chat_history:
#                     self.chat_history[chat_key] = []
#                 self.chat_history[chat_key].append({
#                     'sender': sender,
#                     'content': content,
#                     'timestamp': timestamp,
#                     'sent': False
#                 })
#                 self.show_notification(f"New message in {group}", f"{sender}: {content}")

#         elif msg_type in ['create_group_response', 'join_group_response', 'file_sent_confirmation']:
#             success = message.get('success', True)
#             msg_content = message.get('message', '')

#             if success:
#                 QMessageBox.information(self, "Success", msg_content)
#             else:
#                 QMessageBox.warning(self, "Error", msg_content)

#     def on_connection_status(self, connected, message):
#         self.status_bar.showMessage(message)

#         if connected:
#             self.create_group_btn.setEnabled(True)
#             self.join_group_btn.setEnabled(True)
#         else:
#             self.disable_input_controls()
#             self.create_group_btn.setEnabled(False)
#             self.join_group_btn.setEnabled(False)
#             self.users_list.clear()
#             self.groups_list.clear()

#     def on_user_list_updated(self, users):
#         self.users_list.clear()
#         for user in users:
#             if user != self.client.username:
#                 self.users_list.addItem(user)

#     def on_group_list_updated(self, groups):
#         self.groups_list.clear()
#         for group in groups:
#             self.groups_list.addItem(group)

#     def on_file_received(self, file_info):
#         sender = file_info.get('sender')
#         filename = file_info.get('filename')
#         file_path = file_info.get('file_path')
#         timestamp = file_info.get('timestamp')

#         chat_key = f"user:{sender}"
#         file_message = f"📎 Received file: {filename}"

#         if self.current_chat == chat_key:
#             self.add_message_to_chat(sender, file_message, sent=False, timestamp=timestamp)
#         else:
#             if chat_key not in self.chat_history:
#                 self.chat_history[chat_key] = []
#             self.chat_history[chat_key].append({
#                 'sender': sender,
#                 'content': file_message,
#                 'timestamp': timestamp,
#                 'sent': False
#             })

#         reply = QMessageBox.question(
#             self, "File Received",
#             f"Received file '{filename}' from {sender}.\nOpen file location?",
#             QMessageBox.Yes | QMessageBox.No
#         )

#         if reply == QMessageBox.Yes:
#             import subprocess
#             import platform

#             if platform.system() == 'Windows':
#                 subprocess.run(['explorer', '/select,', file_path])
#             elif platform.system() == 'Darwin':  # macOS
#                 subprocess.run(['open', '-R', file_path])
#             else:  # Linux
#                 subprocess.run(['xdg-open', os.path.dirname(file_path)])

#     def on_error_occurred(self, error_message):
#         QMessageBox.critical(self, "Error", error_message)

#     def show_notification(self, title, message):
#         self.status_bar.showMessage(f"{title}: {message}", 3000)

#     def closeEvent(self, event):
#         if self.client.connected:
#             self.client.disconnect()
#         event.accept()


# def main():
#     app = QApplication(sys.argv)
#     app.setStyle('Fusion')

#     login_dialog = LoginDialog()
#     if login_dialog.exec_() == QDialog.Accepted:
#         main_window = ChatWindow()
#         main_window.show()

#         main_window.connect_to_server(
#             login_dialog.username,
#             login_dialog.host,
#             login_dialog.port
#         )

#         sys.exit(app.exec_())


# if __name__ == "__main__":
#     main()
