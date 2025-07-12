import os
import subprocess
import platform
import base64  # Add this import for base64 encoding/decoding
from datetime import datetime
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import requests
from client import ChatClient
from .styles import MAIN_WINDOW_STYLE, get_message_with_sender_style


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = ChatClient()
        self.current_chat = None  # 'user:username' or 'group:groupname'
        self.chat_history = {}  # Store chat history for each conversation
        self.user_groups = []  # Store user's groups with full info
        # self.client.file_received.connect(self.handle_file_received)
        self.setup_ui()
        self.setup_connections()
        self.setup_styles()

    def setup_ui(self):
        self.setWindowTitle("PyQt5 Chat Application")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Not connected")

    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        users_label = QLabel("Online Users")
        users_label.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px 0;")
        left_layout.addWidget(users_label)

        self.users_list = QListWidget()
        self.users_list.itemDoubleClicked.connect(self.user_double_clicked)
        left_layout.addWidget(self.users_list)

        groups_label = QLabel("Groups")
        groups_label.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px 0;")
        left_layout.addWidget(groups_label)

        self.groups_list = QListWidget()
        self.groups_list.itemDoubleClicked.connect(self.group_double_clicked)
        left_layout.addWidget(self.groups_list)

        group_buttons = QHBoxLayout()
        self.create_group_btn = QPushButton("Create Group")
        self.create_group_btn.clicked.connect(self.create_group)
        group_buttons.addWidget(self.create_group_btn)

        self.join_group_btn = QPushButton("Join Group")
        self.join_group_btn.clicked.connect(self.join_group)
        group_buttons.addWidget(self.join_group_btn)

        left_layout.addLayout(group_buttons)

        left_widget.setLayout(left_layout)
        return left_widget

    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        self.chat_header = QLabel("Select a user or group to start chatting")
        self.chat_header.setStyleSheet("font-weight: bold; font-size: 18px; padding: 10px; background: #4C566A; border-radius: 5px;")
        self.chat_header.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.chat_header)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        self.file_btn = QPushButton("📎 File")
        self.file_btn.clicked.connect(self.send_file)
        input_layout.addWidget(self.file_btn)

        right_layout.addLayout(input_layout)

        self.message_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.file_btn.setEnabled(False)

        right_widget.setLayout(right_layout)
        return right_widget

    def setup_connections(self):
        self.client.message_received.connect(self.on_message_received)
        self.client.connection_status.connect(self.on_connection_status)
        self.client.user_list_updated.connect(self.on_user_list_updated)
        self.client.group_list_updated.connect(self.on_group_list_updated)
        try:
            self.client.file_received.connect(self.on_file_received)
        except AttributeError:
            pass
        self.client.error_occurred.connect(self.on_error_occurred)

    def setup_styles(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE)

    def connect_to_server(self, username, host, port):
        success = self.client.connect_to_server(username, host, port)
        if success:
            self.setWindowTitle(f"Chat - {username}")

    def user_double_clicked(self, item):
        username = item.text()
        if username != self.client.username:
            self.current_chat = f"user:{username}"
            self.chat_header.setText(f"Private Chat with {username}")
            self.load_chat_history()
            self.enable_input_controls()

    def group_double_clicked(self, item):
        # Extract group name from the list item text
        group_text = item.text()
        # Remove any extra info like member count or creator indicator
        group_name = group_text.split(' (')[0]
        
        self.current_chat = f"group:{group_name}"
        
        # Find group info to display better header
        group_info = None
        for group in self.user_groups:
            if group['name'] == group_name:
                group_info = group
                break
        
        if group_info:
            member_count = len(group_info['members'])
            creator_info = " (Creator)" if group_info['is_creator'] else ""
            self.chat_header.setText(f"Group: {group_name} ({member_count} members){creator_info}")
        else:
            self.chat_header.setText(f"Group Chat: {group_name}")
            
        self.load_chat_history()
        self.enable_input_controls()

    def enable_input_controls(self):
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        # Enable file button for both private and group chats
        if self.current_chat and (self.current_chat.startswith('user:') or self.current_chat.startswith('group:')):
            self.file_btn.setEnabled(True)
        else:
            self.file_btn.setEnabled(False)
        self.message_input.setFocus()



    def disable_input_controls(self):
        self.message_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.file_btn.setEnabled(False)

    def send_message(self):
        message = self.message_input.text().strip()
        if not message or not self.current_chat:
            return

        chat_type, chat_name = self.current_chat.split(':', 1)

        if chat_type == 'user':
            success = self.client.send_private_message(chat_name, message)
        elif chat_type == 'group':
            success = self.client.send_group_message(chat_name, message)

        if success:
            self.add_message_to_chat(self.client.username, message, sent=True)
            self.message_input.clear()

    def send_file(self):
        if not self.current_chat:
            return

        chat_type, chat_name = self.current_chat.split(':', 1)

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select file to send", "", "All Files (*)"
        )

        if file_path:
            try:
                # Check file size (limit to 10MB)
                file_size = os.path.getsize(file_path)
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    QMessageBox.warning(self, "Error", "File size exceeds 10MB limit")
                    return

                # Read file content and encode to base64
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                    file_content_b64 = base64.b64encode(file_content).decode('utf-8')

                filename = os.path.basename(file_path)
                file_size_mb = round(file_size / (1024 * 1024), 2)

                # Send file through TCP socket
                if chat_type == 'user':
                    success = self.client.send_file(chat_name, filename, file_content_b64, file_size)
                elif chat_type == 'group':
                    success = self.client.send_group_file(chat_name, filename, file_content_b64, file_size)

                if success:
                    file_message = f"📎 Sent file: {filename} ({file_size_mb}MB)"
                    self.add_message_to_chat(
                        self.client.username,
                        file_message,
                        sent=True
                    )
                    QMessageBox.information(self, "Success", f"File '{filename}' sent successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to send file")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to send file: {str(e)}")

    def create_group(self):
        # Get available online users
        try:
            response = requests.get("http://localhost:8000/users")
            if response.status_code == 200:
                users = response.json()
                available_users = [u['username'] for u in users 
                                 if u['username'] != self.client.username and u.get('is_online', False)]
                
                if not available_users:
                    QMessageBox.information(self, "Info", "No online users available to add to group")
                    return
                
                # Create group dialog
                dialog = GroupCreationDialog(available_users, self)
                if dialog.exec_() == QDialog.Accepted:
                    group_name = dialog.group_name
                    selected_members = dialog.selected_members
                    
                    if group_name and selected_members:
                        success = self.client.create_group(group_name, selected_members)
                        if not success:
                            QMessageBox.warning(self, "Error", "Failed to create group")
            else:
                QMessageBox.warning(self, "Error", "Failed to get user list")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create group: {str(e)}")

    def join_group(self):
        if not self.user_groups:
            QMessageBox.information(self, "Info", "No groups available")
            return

        # For now, just show available groups (this could be enhanced)
        group_names = [group['name'] for group in self.user_groups]
        QMessageBox.information(self, "Groups", f"Available groups: {', '.join(group_names)}")

    def add_message_to_chat(self, sender, content, sent=False, timestamp=None):
        if not timestamp:
            timestamp = datetime.now().strftime('%H:%M')

        if self.current_chat not in self.chat_history:
            self.chat_history[self.current_chat] = []

        self.chat_history[self.current_chat].append({
            'sender': sender,
            'content': content,
            'timestamp': timestamp,
            'sent': sent
        })

        # Get the appropriate bubble style
        bubble_template = get_message_with_sender_style(sent=sent)
        
        # Format the message with the bubble template
        if sent:
            message_html = bubble_template.format(
                content=content,
                timestamp=timestamp
            )
        else:
            message_html = bubble_template.format(
                sender=sender,
                content=content,
                timestamp=timestamp
            )

        self.chat_display.append(message_html)
       
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def load_chat_history(self):
        self.chat_display.clear()

        try:
            if not self.current_chat:
                return

            chat_type, name = self.current_chat.split(":", 1)

            url = f"http://localhost:8000/messages/{self.client.username}"
            response = requests.get(url)
            if response.status_code == 200:
                messages = response.json()
                for msg in messages:
                    sender = msg.get('sender')
                    receiver = msg.get('receiver')
                    content = msg.get('content')
                    timestamp = msg.get('timestamp')
                    is_group = msg.get('is_group', False)

                    # Display only relevant messages
                    if chat_type == 'user':
                        if ((sender == name and receiver == self.client.username) or 
                            (sender == self.client.username and receiver == name)):
                            self.add_message_to_chat(sender, content, sent=(sender == self.client.username), timestamp=timestamp)
                    elif chat_type == 'group':
                        if is_group and receiver == name:
                            self.add_message_to_chat(sender, content, sent=(sender == self.client.username), timestamp=timestamp)

            
                # Load file records
            files_url = f"http://localhost:8000/files/{self.client.username}"
            files_response = requests.get(files_url)
            if files_response.status_code == 200:
                files = files_response.json()
                for file_record in files:
                    sender = file_record.get('sender')
                    receiver = file_record.get('receiver')
                    filename = file_record.get('filename')
                    file_size = file_record.get('file_size', 0)
                    timestamp = file_record.get('timestamp')
                    is_group = file_record.get('is_group', False)
                    
                    file_size_mb = round(file_size / (1024 * 1024), 2) if file_size > 0 else 0
                    
                    # Display only relevant file records
                    if chat_type == 'user':
                        if ((sender == name and receiver == self.client.username) or 
                            (sender == self.client.username and receiver == name)):
                            if sender == self.client.username:
                                file_message = f"📎 Sent file: {filename} ({file_size_mb}MB)"
                            else:
                                file_message = f"📎 Received file: {filename} ({file_size_mb}MB)"
                            self.add_message_to_chat(sender, file_message, sent=(sender == self.client.username), timestamp=timestamp)
                    elif chat_type == 'group':
                        if is_group and receiver == name:
                            if sender == self.client.username:
                                file_message = f"📎 Sent file: {filename} ({file_size_mb}MB)"
                            else:
                                file_message = f"📎 Received file: {filename} ({file_size_mb}MB)"
                            self.add_message_to_chat(sender, file_message, sent=(sender == self.client.username), timestamp=timestamp)
            
            
            
            
            
            
        except Exception as e:
            self.chat_display.append(f"❌ Error loading chat history: {str(e)}")

    def on_message_received(self, message):
        msg_type = message.get('type')

        if msg_type == 'private_message':
            sender = message.get('sender')
            content = message.get('content')
            timestamp = message.get('timestamp')

            chat_key = f"user:{sender}"

            if self.current_chat == chat_key:
                self.add_message_to_chat(sender, content, sent=False, timestamp=timestamp)
            else:
                if chat_key not in self.chat_history:
                    self.chat_history[chat_key] = []
                self.chat_history[chat_key].append({
                    'sender': sender,
                    'content': content,
                    'timestamp': timestamp,
                    'sent': False
                })
                self.show_notification(f"New message from {sender}", content)

        elif msg_type == 'group_message':
            sender = message.get('sender')
            group = message.get('group')
            content = message.get('content')
            timestamp = message.get('timestamp')

            chat_key = f"group:{group}"

            # Only display message if it's not from the current user (avoid duplicates)
            if sender != self.client.username:
                if self.current_chat == chat_key:
                    self.add_message_to_chat(sender, content, sent=False, timestamp=timestamp)
                else:
                    if chat_key not in self.chat_history:
                        self.chat_history[chat_key] = []
                    self.chat_history[chat_key].append({
                        'sender': sender,
                        'content': content,
                        'timestamp': timestamp,
                        'sent': False
                    })
                    self.show_notification(f"New message in {group}", f"{sender}: {content}")

        elif msg_type in ['create_group_response', 'join_group_response', 'file_sent_confirmation']:
            success = message.get('success', True)
            msg_content = message.get('message', '')

            if success:
                QMessageBox.information(self, "Success", msg_content)
                # Refresh group list after successful group creation
                if msg_type == 'create_group_response':
                    self.client.request_group_list()
            else:
                QMessageBox.warning(self, "Error", msg_content)

        elif msg_type == 'group_notification':
            notification_msg = message.get('message', '')
            group_name = message.get('group', '')
            QMessageBox.information(self, "Group Notification", notification_msg)
            # Refresh group list after group changes
            self.client.request_group_list()

    def on_connection_status(self, connected, message):
        self.status_bar.showMessage(message)

        if connected:
            self.create_group_btn.setEnabled(True)
            self.join_group_btn.setEnabled(True)
        else:
            self.disable_input_controls()
            self.create_group_btn.setEnabled(False)
            self.join_group_btn.setEnabled(False)
            self.users_list.clear()
            self.groups_list.clear()
            self.user_groups.clear()

    def on_user_list_updated(self, users):
        self.users_list.clear()
        for user in users:
            if user != self.client.username:
                self.users_list.addItem(user)

    def on_group_list_updated(self, groups):
        self.user_groups = groups  # Store full group info
        self.groups_list.clear()
        for group in groups:
            member_count = len(group['members'])
            creator_indicator = " (Creator)" if group['is_creator'] else ""
            display_text = f"{group['name']} ({member_count} members){creator_indicator}"
            self.groups_list.addItem(display_text)

    def on_file_received(self, file_info):
        sender = file_info.get('sender')
        filename = file_info.get('filename')
        file_size = file_info.get('file_size', 0)
        file_content_b64 = file_info.get('file_content')
        timestamp = file_info.get('timestamp')
        is_group = file_info.get('is_group', False)
        group_name = file_info.get('group_name', '')

        file_size_mb = round(file_size / (1024 * 1024), 2) if file_size > 0 else 0

        # Determine chat key based on whether it's a group or private message
        if is_group:
            chat_key = f"group:{group_name}"
            file_message = f"📎 Received file: {filename} ({file_size_mb}MB)"
        else:
            chat_key = f"user:{sender}"
            file_message = f"📎 Received file: {filename} ({file_size_mb}MB)"

        # Add to chat history
        if self.current_chat == chat_key:
            self.add_message_to_chat(sender, file_message, sent=False, timestamp=timestamp)
        else:
            if chat_key not in self.chat_history:
                self.chat_history[chat_key] = []
            self.chat_history[chat_key].append({
                'sender': sender,
                'content': file_message,
                'timestamp': timestamp,
                'sent': False
            })

        # Show notification based on chat type
        if is_group:
            self.show_notification(f"File received in {group_name}", f"{sender} sent: {filename}")
        else:
            self.show_notification(f"File received from {sender}", filename)

        # Ask user if they want to download the file
        if is_group:
            reply = QMessageBox.question(
                self, "File Received",
                f"Received file '{filename}' ({file_size_mb}MB) from {sender} in group {group_name}.\nDownload file?",
                QMessageBox.Yes | QMessageBox.No
            )
        else:
            reply = QMessageBox.question(
                self, "File Received",
                f"Received file '{filename}' ({file_size_mb}MB) from {sender}.\nDownload file?",
                QMessageBox.Yes | QMessageBox.No
            )

        if reply == QMessageBox.Yes:
            try:
                # Choose download location
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "Save File", filename, "All Files (*)"
                )
                
                if save_path:
                    # Decode base64 content and save file
                    file_content = base64.b64decode(file_content_b64)
                    with open(save_path, 'wb') as file:
                        file.write(file_content)
                    
                    QMessageBox.information(self, "Success", f"File saved to: {save_path}")
                    
                    # Ask if user wants to open file location
                    reply = QMessageBox.question(
                        self, "File Saved",
                        "File downloaded successfully. Open file location?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        if platform.system() == 'Windows':
                            subprocess.run(['explorer', '/select,', save_path])
                        elif platform.system() == 'Darwin':  # macOS
                            subprocess.run(['open', '-R', save_path])
                        else:  # Linux
                            subprocess.run(['xdg-open', os.path.dirname(save_path)])
                            
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}")

    def on_error_occurred(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def show_notification(self, title, message):
        self.status_bar.showMessage(f"{title}: {message}", 3000)

    def closeEvent(self, event):
        if self.client.connected:
            self.client.disconnect()
        event.accept()

    # def handle_file_received(self, file_data):
    #     """Handle received file - this is a simplified version for compatibility"""
    #     # This method should call on_file_received with the proper format
    #     self.on_file_received(file_data)


class GroupCreationDialog(QDialog):
    def __init__(self, available_users, parent=None):
        super().__init__(parent)
        self.available_users = available_users
        self.group_name = ""
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
        
        self.member_checkboxes = {}
        for user in self.available_users:
            checkbox = QCheckBox(user)
            scroll_layout.addWidget(checkbox)
            self.member_checkboxes[user] = checkbox
        
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
        
        self.group_name = group_name
        self.selected_members = selected_members
        self.accept()