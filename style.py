"""
Styles for the TCP Chat Application
"""

def apply_styles(window):
    """Apply modern styles to the chat application"""
    
    style = """
    /* Main Window */
    QMainWindow {
        background-color: #f5f5f5;
        color: #333;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: bold;
        min-height: 20px;
    }
    
    QPushButton:hover {
        background-color: #45a049;
    }
    
    QPushButton:pressed {
        background-color: #3d8b40;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    /* Connect/Disconnect Button */
    QPushButton#connect_btn {
        background-color: #2196F3;
    }
    
    QPushButton#connect_btn:hover {
        background-color: #1976D2;
    }
    
    /* Send Button */
    QPushButton#send_btn {
        background-color: #FF9800;
        min-width: 60px;
    }
    
    QPushButton#send_btn:hover {
        background-color: #F57C00;
    }
    
    /* Create Group Button */
    QPushButton#create_group_btn {
        background-color: #9C27B0;
    }
    
    QPushButton#create_group_btn:hover {
        background-color: #7B1FA2;
    }
    
    /* Manage Group Button */
    QPushButton#manage_group_btn {
        background-color: #607D8B;
    }
    
    QPushButton#manage_group_btn:hover {
        background-color: #455A64;
    }
    
    /* Input Fields */
    QLineEdit {
        border: 2px solid #ddd;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 14px;
        background-color: white;
        selection-background-color: #4CAF50;
    }
    
    QLineEdit:focus {
        border-color: #4CAF50;
        outline: none;
    }
    
    /* Message Input */
    QLineEdit#message_input {
        border: 2px solid #2196F3;
        font-size: 15px;
        padding: 10px 15px;
    }
    
    QLineEdit#message_input:focus {
        border-color: #1976D2;
    }
    
    /* Text Areas */
    QTextEdit {
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
        background-color: white;
        line-height: 1.4;
    }
    
    /* Chat Display */
    QTextEdit#chat_display {
        border: 2px solid #2196F3;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        background-color: #fafafa;
    }
    
    /* List Widgets */
    QListWidget {
        border: 2px solid #ddd;
        border-radius: 6px;
        background-color: white;
        alternate-background-color: #f9f9f9;
        selection-background-color: #4CAF50;
        selection-color: white;
        font-size: 14px;
        padding: 5px;
    }
    
    QListWidget::item {
        padding: 8px 12px;
        border-bottom: 1px solid #eee;
        border-radius: 4px;
        margin: 2px;
    }
    
    QListWidget::item:hover {
        background-color: #e8f5e8;
    }
    
    QListWidget::item:selected {
        background-color: #4CAF50;
        color: white;
    }
    
    /* Users List */
    QListWidget#users_list::item {
        color: #2E7D32;
        font-weight: bold;
    }
    
    /* Groups List */
    QListWidget#groups_list::item {
        color: #7B1FA2;
        font-weight: bold;
    }
    
    /* Labels */
    QLabel {
        font-size: 14px;
        color: #333;
        font-weight: normal;
    }
    
    /* Section Headers */
    QLabel#section_header {
        font-size: 16px;
        font-weight: bold;
        color: #2196F3;
        padding: 5px 0;
    }
    
    /* Chat Info Label */
    QLabel#chat_info {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        border-radius: 6px;
        padding: 10px;
        font-weight: bold;
        color: #1976D2;
    }
    
    /* Tab Widget */
    QTabWidget {
        background-color: transparent;
    }
    
    QTabWidget::pane {
        border: 2px solid #ddd;
        border-radius: 6px;
        background-color: white;
        padding: 10px;
    }
    
    QTabWidget::tab-bar {
        alignment: center;
    }
    
    QTabBar::tab {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 8px 20px;
        margin-right: 2px;
        font-size: 14px;
        font-weight: bold;
    }
    
    QTabBar::tab:selected {
        background-color: #4CAF50;
        color: white;
    }
    
    QTabBar::tab:hover {
        background-color: #e8f5e8;
    }
    
    /* Frames */
    QFrame {
        border: 1px solid #ddd;
        border-radius: 6px;
        background-color: white;
        padding: 10px;
    }
    
    /* Splitter */
    QSplitter::handle {
        background-color: #ddd;
        width: 3px;
        height: 3px;
    }
    
    QSplitter::handle:hover {
        background-color: #4CAF50;
    }
    
    /* Checkboxes */
    QCheckBox {
        font-size: 14px;
        color: #333;
        padding: 4px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #ddd;
        border-radius: 3px;
        background-color: white;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4CAF50;
        border-color: #4CAF50;
    }
    
    QCheckBox::indicator:checked:hover {
        background-color: #45a049;
    }
    
    /* Scroll Area */
    QScrollArea {
        border: 1px solid #ddd;
        border-radius: 6px;
        background-color: white;
    }
    
    /* Scroll Bars */
    QScrollBar:vertical {
        background-color: #f0f0f0;
        border: none;
        border-radius: 6px;
        width: 12px;
        margin: 0;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4CAF50;
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #45a049;
    }
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #2196F3;
        color: white;
        font-size: 13px;
        padding: 5px;
    }
    
    /* Group Box */
    QGroupBox {
        font-size: 14px;
        font-weight: bold;
        border: 2px solid #ddd;
        border-radius: 6px;
        margin-top: 10px;
        padding: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 10px 0 10px;
        color: #2196F3;
    }
    
    /* Dialog Styles */
    QDialog {
        background-color: #f5f5f5;
        border-radius: 8px;
    }
    
    QDialog QLabel {
        color: #333;
    }
    
    /* Message Box */
    QMessageBox {
        background-color: white;
        font-size: 14px;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
        padding: 6px 12px;
    }
    """
    
    window.setStyleSheet(style)
    
    # Set object names for specific styling
    if hasattr(window, 'connect_btn'):
        window.connect_btn.setObjectName('connect_btn')
    if hasattr(window, 'send_btn'):
        window.send_btn.setObjectName('send_btn')
    if hasattr(window, 'create_group_btn'):
        window.create_group_btn.setObjectName('create_group_btn')
    if hasattr(window, 'manage_group_btn'):
        window.manage_group_btn.setObjectName('manage_group_btn')
    if hasattr(window, 'message_input'):
        window.message_input.setObjectName('message_input')
    if hasattr(window, 'chat_display'):
        window.chat_display.setObjectName('chat_display')
    if hasattr(window, 'users_list'):
        window.users_list.setObjectName('users_list')
    if hasattr(window, 'groups_list'):
        window.groups_list.setObjectName('groups_list')
    if hasattr(window, 'chat_info_label'):
        window.chat_info_label.setObjectName('chat_info')

# Color scheme constants
COLORS = {
    'primary': '#4CAF50',
    'secondary': '#2196F3',
    'accent': '#FF9800',
    'purple': '#9C27B0',
    'grey': '#607D8B',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3',
    'light': '#f5f5f5',
    'dark': '#333333',
    'border': '#dddddd'
}