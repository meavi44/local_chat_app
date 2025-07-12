"""
UI Package for PyQt5 Chat Application
"""

from .login_dialog import LoginDialog
from .chat_window import ChatWindow
from .styles import LOGIN_DIALOG_STYLE, MAIN_WINDOW_STYLE, get_message_bubble_style

__all__ = ['LoginDialog', 'ChatWindow', 'LOGIN_DIALOG_STYLE', 'MAIN_WINDOW_STYLE', 'get_message_bubble_style']