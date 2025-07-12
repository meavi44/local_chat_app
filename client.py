# import sys
# import json
# import socket
# import threading
# import struct
# from datetime import datetime

# import requests  # <-- Added

# from PyQt5.QtCore import QTimer, pyqtSignal, QObject
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
#                              QWidget, QTextEdit, QLineEdit, QPushButton, QListWidget,
#                              QLabel, QInputDialog, QMessageBox)

# # --- Chat Client ---
# class ChatClient(QObject):
#     message_received = pyqtSignal(dict)
#     connection_status = pyqtSignal(bool, str)
#     user_list_updated = pyqtSignal(list)
#     group_list_updated = pyqtSignal(list)
#     error_occurred = pyqtSignal(str)

#     def __init__(self):
#         super().__init__()
#         self.socket = None
#         self.connected = False
#         self.username = None
#         self.host = 'localhost'
#         self.port = 12345
#         self.receive_thread = None

#     def connect_to_server(self, username, host='localhost', port=12345):
#         try:
#             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.socket.connect((host, port))
#             self.connected = True
#             self.username = username
#             self.host = host
#             self.port = port

#             join_message = {'type': 'join', 'username': username}
#             self.send_message(join_message)

#             self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
#             self.receive_thread.start()

#             self.connection_status.emit(True, f"Connected to {host}:{port}")
#             return True
#         except Exception as e:
#             self.connection_status.emit(False, f"Connection failed: {str(e)}")
#             return False

#     def disconnect(self):
#         self.connected = False
#         if self.socket:
#             try:
#                 self.socket.close()
#             except:
#                 pass
#         self.connection_status.emit(False, "Disconnected")

#     def send_message(self, message):
#         if self.connected and self.socket:
#             try:
#                 data = json.dumps(message).encode('utf-8')
#                 length_prefix = struct.pack('!I', len(data))
#                 self.socket.send(length_prefix + data)
#                 return True
#             except Exception as e:
#                 self.error_occurred.emit(f"Failed to send message: {str(e)}")
#                 return False
#         return False

#     def receive_message(self):
#         try:
#             length_data = self.socket.recv(4)
#             if not length_data:
#                 return None
#             message_length = struct.unpack('!I', length_data)[0]
#             message_data = b''
#             while len(message_data) < message_length:
#                 chunk = self.socket.recv(message_length - len(message_data))
#                 if not chunk:
#                     return None
#                 message_data += chunk
#             return json.loads(message_data.decode('utf-8'))
#         except Exception as e:
#             self.error_occurred.emit(f"Error receiving message: {str(e)}")
#             return None

#     def receive_messages(self):
#         while self.connected:
#             message = self.receive_message()
#             if message is None:
#                 break
#             self.process_received_message(message)
#         self.connected = False
#         self.connection_status.emit(False, "Connection lost")

#     def process_received_message(self, message):
#         msg_type = message.get('type')
#         if msg_type == 'join_response':
#             if not message.get('success'):
#                 self.error_occurred.emit(message.get('message'))
#             else:
#                 self.request_user_list()
#                 self.request_group_list()
#         elif msg_type in ['private_message', 'group_message']:
#             self.message_received.emit(message)
#         elif msg_type == 'user_list':
#             self.user_list_updated.emit(message.get('users', []))
#         elif msg_type == 'group_list':
#             self.group_list_updated.emit(message.get('groups', []))
#         elif msg_type == 'error':
#             self.error_occurred.emit(message.get('message'))

#     def send_private_message(self, recipient, content):
#         message = {
#             'type': 'private_message',
#             'recipient': recipient,
#             'sender': self.username,
#             'content': content,
#             'timestamp': datetime.now().isoformat()
#         }
#         return self.send_message(message)

#     def send_group_message(self, group, content):
#         message = {
#             'type': 'group_message',
#             'group': group,
#             'sender': self.username,
#             'content': content,
#             'timestamp': datetime.now().isoformat()
#         }
#         return self.send_message(message)

#     def create_group(self, group_name):
#         return self.send_message({'type': 'create_group', 'group_name': group_name})

#     def join_group(self, group_name):
#         return self.send_message({'type': 'join_group', 'group_name': group_name})

#     def request_user_list(self):
#         return self.send_message({'type': 'get_users'})

#     def request_group_list(self):
#         return self.send_message({'type': 'get_groups'})


# # --- UI ---
# class ChatWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.client = None
#         self.current_chat = None
#         self.init_ui()

#     def init_ui(self):
#         self.setWindowTitle("TCP Chat App")
#         self.setGeometry(100, 100, 800, 600)

#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         layout = QHBoxLayout(central_widget)

#         left_panel = QWidget()
#         left_layout = QVBoxLayout(left_panel)

#         conn_layout = QHBoxLayout()
#         self.host_input = QLineEdit("localhost")
#         self.port_input = QLineEdit("12345")
#         self.connect_btn = QPushButton("Connect")
#         self.connect_btn.clicked.connect(self.connect_to_server)

#         conn_layout.addWidget(QLabel("Host:"))
#         conn_layout.addWidget(self.host_input)
#         conn_layout.addWidget(QLabel("Port:"))
#         conn_layout.addWidget(self.port_input)
#         conn_layout.addWidget(self.connect_btn)
#         left_layout.addLayout(conn_layout)

#         left_layout.addWidget(QLabel("Online Users:"))
#         self.users_list = QListWidget()
#         self.users_list.itemClicked.connect(self.select_user)
#         left_layout.addWidget(self.users_list)

#         self.group_chat_btn = QPushButton("Group Chat")
#         self.group_chat_btn.clicked.connect(self.open_group_chat)
#         self.group_chat_btn.setEnabled(False)
#         left_layout.addWidget(self.group_chat_btn)

#         layout.addWidget(left_panel, 1)

#         right_panel = QWidget()
#         right_layout = QVBoxLayout(right_panel)

#         self.chat_display = QTextEdit()
#         self.chat_display.setReadOnly(True)
#         right_layout.addWidget(self.chat_display)

#         input_layout = QHBoxLayout()
#         self.message_input = QLineEdit()
#         self.message_input.returnPressed.connect(self.send_message)
#         self.send_btn = QPushButton("Send")
#         self.send_btn.clicked.connect(self.send_message)
#         self.send_btn.setEnabled(False)
#         input_layout.addWidget(self.message_input)
#         input_layout.addWidget(self.send_btn)
#         right_layout.addLayout(input_layout)

#         layout.addWidget(right_panel, 2)

#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_users_list)

#     def connect_to_server(self):
#         if self.client and self.client.connected:
#             self.client.disconnect()
#             self.connect_btn.setText("Connect")
#             self.send_btn.setEnabled(False)
#             self.group_chat_btn.setEnabled(False)
#             self.timer.stop()
#             return

#         username, ok = QInputDialog.getText(self, 'Username', 'Enter your username:')
#         if not ok or not username:
#             return

#         host = self.host_input.text() or "localhost"
#         port = int(self.port_input.text() or "12345")

#         self.client = ChatClient()
#         self.client.connection_status.connect(self.on_connection_status)
#         self.client.message_received.connect(self.handle_message)
#         self.client.user_list_updated.connect(self.update_users_list_from_signal)
#         self.client.group_list_updated.connect(self.update_groups_list)
#         self.client.error_occurred.connect(self.show_error)

#         if self.client.connect_to_server(username, host, port):
#             self.connect_btn.setText("Disconnect")
#             self.send_btn.setEnabled(True)
#             self.group_chat_btn.setEnabled(True)
#             self.timer.start(5000)
#             QMessageBox.information(self, "Connected", f"Connected as {username}")

#     def on_connection_status(self, connected, message):
#         if not connected:
#             self.connect_btn.setText("Connect")
#             self.send_btn.setEnabled(False)
#             self.group_chat_btn.setEnabled(False)
#             self.timer.stop()
#         self.statusBar().showMessage(message)

#     def handle_message(self, message):
#         sender = message.get('sender', 'Unknown')
#         content = message.get('content', '')
#         timestamp = datetime.now().strftime("%H:%M:%S")

#         if message.get('type') == 'group_message' or message.get('is_group', False):
#             self.chat_display.append(f"[{timestamp}] {sender} (Group): {content}")
#         else:
#             self.chat_display.append(f"[{timestamp}] {sender}: {content}")

#     def send_message(self):
#         if not self.client or not self.client.connected:
#             return
#         content = self.message_input.text().strip()
#         if not content:
#             return
#         if self.current_chat == "group":
#             self.client.send_group_message("general", content)
#             self.chat_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] You (Group): {content}")
#         else:
#             if not self.current_chat:
#                 QMessageBox.warning(self, "No user selected", "Please select a user to chat with")
#                 return
#             self.client.send_private_message(self.current_chat, content)
#             self.chat_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] You -> {self.current_chat}: {content}")
#         self.message_input.clear()

#     def select_user(self, item):
#         username = item.text().split(' ')[0]
#         if self.client and username != self.client.username:
#             self.current_chat = username
#             self.setWindowTitle(f"TCP Chat App - Chatting with {username}")
#             self.load_chat_history(username=username)

#     def open_group_chat(self):
#         group_name, ok = QInputDialog.getText(self, "Group Chat", "Enter group name:")
#         if ok:
#             group_name = group_name or "general"
#             self.current_chat = group_name
#             self.setWindowTitle(f"TCP Chat App - Group: {group_name}")
#             self.load_chat_history(is_group=True)

#     def load_chat_history(self, username=None, is_group=False):
#         self.chat_display.clear()
#         try:
#             response = requests.get(f"http://localhost:8000/messages/{self.client.username}")
#             if response.status_code == 200:
#                 messages = response.json()
#                 for msg in reversed(messages):
#                     sender = msg.get('sender', 'Unknown')
#                     content = msg.get('content', '')
#                     timestamp = msg.get('timestamp', '')[11:19]
#                     is_group_msg = msg.get('is_group', False)
#                     receiver = msg.get('receiver', '')

#                     if not is_group_msg and username:
#                         if (sender == self.client.username and receiver == username) or \
#                            (sender == username and receiver == self.client.username):
#                             self.chat_display.append(f"[{timestamp}] {sender}: {content}")
#                     elif is_group and is_group_msg and receiver == self.current_chat:
#                         self.chat_display.append(f"[{timestamp}] {sender} (Group): {content}")
#         except Exception as e:
#             self.chat_display.append(f"Failed to load chat history: {str(e)}")

#     def update_users_list(self):
#         if self.client:
#             self.client.request_user_list()

#     def update_users_list_from_signal(self, users):
#         self.users_list.clear()
#         for user in users:
#             status = "🟢" if user.get('is_online') else "🔴"
#             self.users_list.addItem(f"{user['username']} {status}")

#     def update_groups_list(self, groups):
#         pass

#     def show_error(self, message):
#         QMessageBox.critical(self, "Error", message)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ChatWindow()
#     window.show()
#     sys.exit(app.exec_())








import sys
import json
import socket
import threading
import struct
from datetime import datetime

import requests

from PyQt5.QtCore import QTimer, pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTextEdit, QLineEdit, QPushButton, QListWidget,
                             QLabel, QInputDialog, QMessageBox, QDialog, QCheckBox,
                             QScrollArea, QGroupBox, QSplitter, QTabWidget,
                             QListWidgetItem, QFrame)
from PyQt5.QtGui import QFont, QIcon

# Import styles
from style import apply_styles

# --- Group Management Dialog ---
class GroupManagementDialog(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.selected_members = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Create Group")
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QVBoxLayout()
        
        # Group name input
        layout.addWidget(QLabel("Group Name:"))
        self.group_name_input = QLineEdit()
        layout.addWidget(self.group_name_input)
        
        # Members selection
        layout.addWidget(QLabel("Select Members:"))
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Get online users
        try:
            response = requests.get("http://localhost:8000/users")
            if response.status_code == 200:
                users = response.json()
                self.member_checkboxes = {}
                
                for user in users:
                    if user['username'] != self.client.username and user.get('is_online', False):
                        checkbox = QCheckBox(user['username'])
                        scroll_layout.addWidget(checkbox)
                        self.member_checkboxes[user['username']] = checkbox
        except:
            pass
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create Group")
        create_btn.clicked.connect(self.create_group)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def create_group(self):
        group_name = self.group_name_input.text().strip()
        if not group_name:
            QMessageBox.warning(self, "Error", "Please enter a group name")
            return
        
        selected_members = []
        for username, checkbox in self.member_checkboxes.items():
            if checkbox.isChecked():
                selected_members.append(username)
        
        if not selected_members:
            QMessageBox.warning(self, "Error", "Please select at least one member")
            return
        
        # Send create group request
        message = {
            'type': 'create_group',
            'group_name': group_name,
            'members': selected_members
        }
        
        if self.client.send_message(message):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to create group")

# --- Group Member Management Dialog ---
class GroupMemberDialog(QDialog):
    def __init__(self, client, group_info, parent=None):
        super().__init__(parent)
        self.client = client
        self.group_info = group_info
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Manage Group: {self.group_info['name']}")
        self.setModal(True)
        self.resize(400, 400)
        
        layout = QVBoxLayout()
        
        # Group info
        info_label = QLabel(f"Group: {self.group_info['name']}\nCreator: {self.group_info['creator']}")
        info_label.setStyleSheet("font-weight: bold; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(info_label)
        
        # Current members
        layout.addWidget(QLabel("Current Members:"))
        self.members_list = QListWidget()
        for member in self.group_info['members']:
            self.members_list.addItem(member)
        layout.addWidget(self.members_list)
        
        # Management buttons (only for creator)
        if self.group_info['is_creator']:
            button_layout = QHBoxLayout()
            
            add_btn = QPushButton("Add Member")
            add_btn.clicked.connect(self.add_member)
            
            remove_btn = QPushButton("Remove Member")
            remove_btn.clicked.connect(self.remove_member)
            
            button_layout.addWidget(add_btn)
            button_layout.addWidget(remove_btn)
            layout.addLayout(button_layout)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    def add_member(self):
        try:
            response = requests.get("http://localhost:8000/users")
            if response.status_code == 200:
                users = response.json()
                available_users = [u['username'] for u in users 
                                 if u['username'] not in self.group_info['members'] 
                                 and u.get('is_online', False)]
                
                if available_users:
                    username, ok = QInputDialog.getItem(
                        self, "Add Member", "Select user to add:", 
                        available_users, 0, False
                    )
                    if ok:
                        message = {
                            'type': 'add_member',
                            'group_name': self.group_info['name'],
                            'member': username
                        }
                        self.client.send_message(message)
                else:
                    QMessageBox.information(self, "Info", "No available users to add")
        except:
            QMessageBox.critical(self, "Error", "Failed to get user list")

    def remove_member(self):
        current_item = self.members_list.currentItem()
        if current_item:
            member = current_item.text()
            if member != self.group_info['creator']:
                reply = QMessageBox.question(
                    self, "Confirm", f"Remove {member} from group?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    message = {
                        'type': 'remove_member',
                        'group_name': self.group_info['name'],
                        'member': member
                    }
                    self.client.send_message(message)
            else:
                QMessageBox.warning(self, "Error", "Cannot remove group creator")

# --- Chat Client ---
class ChatClient(QObject):
    message_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    user_list_updated = pyqtSignal(list)
    group_list_updated = pyqtSignal(list)
    group_notification = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)
    file_received = pyqtSignal(dict)  
    def __init__(self):
        super().__init__()
        self.socket = None
        self.connected = False
        self.username = None
        self.host = 'localhost'
        self.port = 12345
        self.receive_thread = None

    def connect_to_server(self, username, host='localhost', port=12345):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            self.username = username
            self.host = host
            self.port = port

            join_message = {'type': 'join', 'username': username}
            self.send_message(join_message)

            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()

            self.connection_status.emit(True, f"Connected to {host}:{port}")
            return True
        except Exception as e:
            self.connection_status.emit(False, f"Connection failed: {str(e)}")
            return False

    def disconnect(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connection_status.emit(False, "Disconnected")

    def send_message(self, message):
        if self.connected and self.socket:
            try:
                data = json.dumps(message).encode('utf-8')
                length_prefix = struct.pack('!I', len(data))
                self.socket.send(length_prefix + data)
                return True
            except Exception as e:
                self.error_occurred.emit(f"Failed to send message: {str(e)}")
                return False
        return False

    def receive_message(self):
        try:
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            message_length = struct.unpack('!I', length_data)[0]
            message_data = b''
            while len(message_data) < message_length:
                chunk = self.socket.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk
            return json.loads(message_data.decode('utf-8'))
        except Exception as e:
            self.error_occurred.emit(f"Error receiving message: {str(e)}")
            return None

    def receive_messages(self):
        while self.connected:
            message = self.receive_message()
            if message is None:
                break
            self.process_received_message(message)
        self.connected = False
        self.connection_status.emit(False, "Connection lost")

    def process_received_message(self, message):
        msg_type = message.get('type')
        if msg_type == 'join_response':
            if not message.get('success'):
                self.error_occurred.emit(message.get('message'))
            else:
                self.request_user_list()
                self.request_group_list()
        elif msg_type in ['private_message', 'group_message']:
            self.message_received.emit(message)
        elif msg_type == 'user_list':
            self.user_list_updated.emit(message.get('users', []))
        elif msg_type == 'group_list':
            self.group_list_updated.emit(message.get('groups', []))
        elif msg_type in ['file_received', 'group_file_received']:  # Handle file messages
            print(f"DEBUG: File message received: {message.get('filename')}")  # Debug line
            self.file_received.emit(message)  # Emit to file_received signal
        elif msg_type == 'file_sent_confirmation':
            print(f"File sent confirmation: {message.get('message')}")
        elif msg_type == 'group_notification':
            self.group_notification.emit(message.get('message', ''), message.get('group', ''))
        elif msg_type == 'error':
            self.error_occurred.emit(message.get('message'))

    def send_private_message(self, recipient, content):
        message = {
            'type': 'private_message',
            'recipient': recipient,
            'sender': self.username,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        return self.send_message(message)

    def send_group_message(self, group, content):
        message = {
            'type': 'group_message',
            'group': group,
            'sender': self.username,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        return self.send_message(message)

    def create_group(self, group_name, members):
        return self.send_message({
            'type': 'create_group', 
            'group_name': group_name,
            'members': members
        })

    def request_user_list(self):
        return self.send_message({'type': 'get_users'})

    def request_group_list(self):
        return self.send_message({'type': 'get_groups'})
    
    # CLIENT SIDE FIXES - Replace your file sending methods

    def send_file(self, recipient, filename, file_content_b64, file_size):
        """Send file to a specific user"""
        try:
            message = {
                "type": "file_transfer",
                "sender": self.username,
                "recipient": recipient,
                "filename": filename,
                "file_content": file_content_b64,
                "file_size": file_size,
                "is_group": False
            }
            return self.send_message(message)  # Remove json.dumps() - send_message already handles it
        except Exception as e:
            print(f"Error sending file: {e}")
            return False

    def send_group_file(self, group_name, filename, file_content_b64, file_size):
        """Send file to a group"""
        try:
            message = {
                "type": "group_file_transfer",
                "sender": self.username,
                "group": group_name,
                "filename": filename,
                "file_content": file_content_b64,
                "file_size": file_size,
                "is_group": True
            }
            return self.send_message(message)  # Remove json.dumps() - send_message already handles it
        except Exception as e:
            print(f"Error sending group file: {e}")
            return False

    
    
    
        
        # CLIENT SIDE - Add file handling methods to ChatClient
    def save_received_file(self, file_data):
        """Save received file to disk"""
        import base64
        import os
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        try:
            filename = file_data.get('filename')
            file_content_b64 = file_data.get('file_content')
            sender = file_data.get('sender')
            
            if not all([filename, file_content_b64, sender]):
                print("Missing file data")
                return False
            
            # Decode base64 content
            file_content = base64.b64decode(file_content_b64)
            
            # Ask user where to save the file
            save_path, _ = QFileDialog.getSaveFileName(
                None, 
                f"Save file from {sender}", 
                filename,
                "All Files (*)"
            )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(file_content)
                
                QMessageBox.information(
                    None, 
                    "File Saved", 
                    f"File '{filename}' saved successfully to:\n{save_path}"
                )
                return True
            else:
                print("File save cancelled by user")
                return False
                
        except Exception as e:
            print(f"Error saving file: {e}")
            QMessageBox.critical(
                None, 
                "Error", 
                f"Failed to save file: {str(e)}"
            )
            return False
        
        
    
    
    
    

# --- Main Chat Window ---
class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = None
        self.current_chat = None
        self.current_chat_type = None  # 'user' or 'group'
        self.user_groups = []
        self.init_ui()
        apply_styles(self)

    def init_ui(self):
        self.setWindowTitle("TCP Chat App")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        central_widget.setLayout(QHBoxLayout())
        central_widget.layout().addWidget(main_splitter)

        # Left panel
        left_panel = QWidget()
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)

        # Connection section
        conn_frame = QFrame()
        conn_frame.setFrameStyle(QFrame.Box)
        conn_layout = QVBoxLayout(conn_frame)
        
        # Connection inputs
        conn_inputs = QHBoxLayout()
        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit("12345")
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_to_server)

        conn_inputs.addWidget(QLabel("Host:"))
        conn_inputs.addWidget(self.host_input)
        conn_inputs.addWidget(QLabel("Port:"))
        conn_inputs.addWidget(self.port_input)
        conn_layout.addLayout(conn_inputs)
        conn_layout.addWidget(self.connect_btn)
        left_layout.addWidget(conn_frame)

        # Tabs for users and groups
        self.tabs = QTabWidget()
        
        # Users tab
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        users_layout.addWidget(QLabel("Online Users:"))
        self.users_list = QListWidget()
        self.users_list.itemClicked.connect(self.select_user)
        users_layout.addWidget(self.users_list)
        self.tabs.addTab(users_tab, "Users")

        # Groups tab
        groups_tab = QWidget()
        groups_layout = QVBoxLayout(groups_tab)
        
        # Group management buttons
        group_buttons = QHBoxLayout()
        self.create_group_btn = QPushButton("Create Group")
        self.create_group_btn.clicked.connect(self.create_group)
        self.create_group_btn.setEnabled(False)
        
        self.manage_group_btn = QPushButton("Manage Group")
        self.manage_group_btn.clicked.connect(self.manage_group)
        self.manage_group_btn.setEnabled(False)
        
        group_buttons.addWidget(self.create_group_btn)
        group_buttons.addWidget(self.manage_group_btn)
        groups_layout.addLayout(group_buttons)
        
        groups_layout.addWidget(QLabel("My Groups:"))
        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.select_group)
        groups_layout.addWidget(self.groups_list)
        self.tabs.addTab(groups_tab, "Groups")
        
        left_layout.addWidget(self.tabs)
        main_splitter.addWidget(left_panel)

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Chat info
        self.chat_info_label = QLabel("Select a user or group to start chatting")
        self.chat_info_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0;")
        right_layout.addWidget(self.chat_info_label)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)

        # Message input
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setPlaceholderText("Type your message here...")
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)
        right_layout.addLayout(input_layout)

        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 700])

        # Timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_lists)

    def connect_to_server(self):
        if self.client and self.client.connected:
            self.client.disconnect()
            self.connect_btn.setText("Connect")
            self.send_btn.setEnabled(False)
            self.create_group_btn.setEnabled(False)
            self.manage_group_btn.setEnabled(False)
            self.timer.stop()
            return

        username, ok = QInputDialog.getText(self, 'Username', 'Enter your username:')
        if not ok or not username:
            return

        host = self.host_input.text() or "localhost"
        port = int(self.port_input.text() or "12345")

        self.client = ChatClient()
        self.client.connection_status.connect(self.on_connection_status)
        self.client.message_received.connect(self.handle_message)
        self.client.user_list_updated.connect(self.update_users_list)
        self.client.group_list_updated.connect(self.update_groups_list)
        self.client.group_notification.connect(self.show_group_notification)
        self.client.error_occurred.connect(self.show_error)

        if self.client.connect_to_server(username, host, port):
            self.connect_btn.setText("Disconnect")
            self.send_btn.setEnabled(True)
            self.create_group_btn.setEnabled(True)
            self.timer.start(5000)  # Update every 5 seconds
            QMessageBox.information(self, "Connected", f"Connected as {username}")

    def on_connection_status(self, connected, message):
        if not connected:
            self.connect_btn.setText("Connect")
            self.send_btn.setEnabled(False)
            self.create_group_btn.setEnabled(False)
            self.manage_group_btn.setEnabled(False)
            self.timer.stop()
        self.statusBar().showMessage(message)

    def handle_message(self, message):
        sender = message.get('sender', 'Unknown')
        content = message.get('content', '')
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg_type = message.get('type')

        # Only show message if it's for the current chat
        if msg_type == 'group_message':
            group = message.get('group')
            if self.current_chat_type == 'group' and self.current_chat == group:
                self.chat_display.append(f"[{timestamp}] {sender}: {content}")
        elif msg_type == 'private_message':
            if self.current_chat_type == 'user' and \
               (sender == self.current_chat or message.get('recipient') == self.current_chat):
                self.chat_display.append(f"[{timestamp}] {sender}: {content}")

        if msg_type == 'file_received':
            if hasattr(self, 'file_received'):
                self.file_received.emit(message)
        elif msg_type == 'group_file_received':
            if hasattr(self, 'file_received'):
                self.file_received.emit(message)
        
        
        
        
        
        
        
        
        
        
        
    def send_message(self):
        if not self.client or not self.client.connected:
            QMessageBox.warning(self, "Error", "Not connected to server")
            return
        
        content = self.message_input.text().strip()
        if not content:
            return
        
        if not self.current_chat:
            QMessageBox.warning(self, "No chat selected", "Please select a user or group to chat with")
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.current_chat_type == "group":
            self.client.send_group_message(self.current_chat, content)
            self.chat_display.append(f"[{timestamp}] You: {content}")
        else:
            self.client.send_private_message(self.current_chat, content)
            self.chat_display.append(f"[{timestamp}] You: {content}")
        
        self.message_input.clear()

    def select_user(self, item):
        username = item.text().split(' ')[0]
        if self.client and username != self.client.username:
            self.current_chat = username
            self.current_chat_type = 'user'
            self.chat_info_label.setText(f"Private chat with {username}")
            self.manage_group_btn.setEnabled(False)
            self.load_chat_history()

    def select_group(self, item):
        group_name = item.text().split(' (')[0]  # Remove member count
        self.current_chat = group_name
        self.current_chat_type = 'group'
        
        # Find group info
        group_info = None
        for group in self.user_groups:
            if group['name'] == group_name:
                group_info = group
                break
        
        if group_info:
            member_count = len(group_info['members'])
            self.chat_info_label.setText(f"Group: {group_name} ({member_count} members)")
            self.manage_group_btn.setEnabled(group_info['is_creator'])
        
        self.load_chat_history()

    def create_group(self):
        if not self.client or not self.client.connected:
            return
        
        dialog = GroupManagementDialog(self.client, self)
        dialog.exec_()

    def manage_group(self):
        if not self.current_chat or self.current_chat_type != 'group':
            return
        
        # Find current group info
        group_info = None
        for group in self.user_groups:
            if group['name'] == self.current_chat:
                group_info = group
                break
        
        if group_info:
            dialog = GroupMemberDialog(self.client, group_info, self)
            dialog.exec_()

    def load_chat_history(self):
        if not self.client:
            return
        
        self.chat_display.clear()
        try:
            response = requests.get(f"http://localhost:8000/messages/{self.client.username}")
            if response.status_code == 200:
                messages = response.json()
                for msg in reversed(messages):
                    sender = msg.get('sender', 'Unknown')
                    content = msg.get('content', '')
                    timestamp = msg.get('timestamp', '')[11:19] if msg.get('timestamp') else ''
                    is_group_msg = msg.get('is_group', False)
                    receiver = msg.get('receiver', '')

                    if self.current_chat_type == 'user' and not is_group_msg:
                        if (sender == self.client.username and receiver == self.current_chat) or \
                           (sender == self.current_chat and receiver == self.client.username):
                            self.chat_display.append(f"[{timestamp}] {sender}: {content}")
                    elif self.current_chat_type == 'group' and is_group_msg and receiver == self.current_chat:
                        self.chat_display.append(f"[{timestamp}] {sender}: {content}")
        except Exception as e:
            self.chat_display.append(f"Failed to load chat history: {str(e)}")

    def update_lists(self):
        if self.client and self.client.connected:
            self.client.request_user_list()
            self.client.request_group_list()

    def update_users_list(self, users):
        self.users_list.clear()
        for user in users:
            if user != self.client.username:  # Don't show own username
                self.users_list.addItem(f"{user} 🟢")

    def update_groups_list(self, groups):
        self.user_groups = groups
        self.groups_list.clear()
        for group in groups:
            member_count = len(group['members'])
            creator_indicator = " (Creator)" if group['is_creator'] else ""
            self.groups_list.addItem(f"{group['name']} ({member_count} members){creator_indicator}")
            
            
            
    
    
    # Add this method to your ChatWindow class

    def handle_file_received(self, file_data):
        """Handle received file"""
        sender = file_data.get('sender')
        filename = file_data.get('filename')
        file_size = file_data.get('file_size')
        is_group = file_data.get('is_group', False)
        group_name = file_data.get('group_name', '')
        
        print(f"DEBUG: Handling file reception - {filename} from {sender}")
        
        # Show notification in chat
        if is_group:
            notification_text = f"📁 {sender} sent a file '{filename}' to group {group_name}"
        else:
            notification_text = f"📁 {sender} sent you a file '{filename}'"
        
        # Add to chat display (adapt this to your actual chat display method)
        timestamp = datetime.now().strftime('%H:%M')
        if hasattr(self, 'chat_display'):  # If you have a chat display widget
            self.chat_display.append(f"[{timestamp}] {notification_text}")
        else:
            print(f"[{timestamp}] {notification_text}")  # Fallback to console
        
        # Ask user if they want to save the file
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            "File Received", 
            f"Received file '{filename}' ({file_size} bytes) from {sender}.\n\nDo you want to save it?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.client.save_received_file(file_data)       
                
                
            
    
                
            
            
            
            

    def show_group_notification(self, message, group):
        QMessageBox.information(self, "Group Notification", message)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        if self.client and self.client.connected:
            self.client.disconnect()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())