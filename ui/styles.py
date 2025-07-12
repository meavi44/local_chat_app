"""
Modern Messaging App UI Styles - iOS/WhatsApp Inspired - PyQt5 Compatible Version
"""

LOGIN_DIALOG_STYLE = """
    QDialog {
        background: #000000;
        color: #FFFFFF;
        border-radius: 16px;
    }
    QLabel {
        color: #FFFFFF;
        font-size: 17px;
        font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QLineEdit {
        background: #1C1C1E;
        border: 1px solid #2C2C2E;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 16px;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QLineEdit:focus {
        border: 1px solid #007AFF;
        background: #2C2C2E;
    }
    QPushButton {
        background: #007AFF;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QPushButton:hover {
        background: #0056CC;
    }
    QPushButton:pressed {
        background: #004499;
    }
"""

MAIN_WINDOW_STYLE = """
    QMainWindow {
        background: #000000;
        color: #FFFFFF;
    }
    QWidget {
        background: #000000;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QListWidget {
        background: #1C1C1E;
        border: none;
        border-radius: 12px;
        padding: 8px;
        selection-background-color: #2C2C2E;
        outline: none;
    }
    QListWidget::item {
        padding: 16px 12px;
        border-radius: 8px;
        margin: 1px 0;
        font-size: 16px;
        font-weight: 500;
        border: none;
    }
    QListWidget::item:hover {
        background: #2C2C2E;
    }
    QListWidget::item:selected {
        background: #007AFF;
        color: #FFFFFF;
    }
    QTextEdit {
        background: #000000;
        border: none;
        padding: 16px;
        font-size: 16px;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QLineEdit {
        background: #1C1C1E;
        border: 1px solid #2C2C2E;
        border-radius: 20px;
        padding: 10px 16px;
        font-size: 16px;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QLineEdit:focus {
        border: 1px solid #007AFF;
        background: #2C2C2E;
    }
    QPushButton {
        background: #007AFF;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        font-size: 16px;
        font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QPushButton:hover {
        background: #0056CC;
    }
    QPushButton:pressed {
        background: #004499;
    }
    QPushButton:disabled {
        background: #2C2C2E;
        color: #8E8E93;
    }
    QLabel {
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QStatusBar {
        background: #1C1C1E;
        color: #8E8E93;
        border: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
"""

def get_message_bubble_style(sent=False, font_size="16px", max_width="300px"):
    """
    Generate HTML style for iOS-style chat message bubbles - PyQt5 Compatible
    
    Args:
        sent (bool): True if message is sent by current user, False if received
        font_size (str): Font size for the message
        max_width (str): Maximum width of the bubble in pixels
    
    Returns:
        str: HTML formatted message bubble with PyQt5-compatible styling
    """
    if sent:
        # Your own messages, right aligned, blue bubble like iOS
        return """
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td width="30%"></td>
                <td width="70%" align="right">
                    <table border="0" cellpadding="8" cellspacing="0" style="background-color: #007AFF; border-radius: 15px; margin: 4px;">
                        <tr>
                            <td style="color: #FFFFFF; font-size: """ + font_size + """; font-family: Arial, sans-serif; word-wrap: break-word;">
                                {content}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """
    else:
        # Others' messages, left aligned, gray bubble like iOS
        return """
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td width="70%" align="left">
                    <table border="0" cellpadding="8" cellspacing="0" style="background-color: #2C2C2E; border-radius: 15px; margin: 4px;">
                        <tr>
                            <td style="color: #FFFFFF; font-size: """ + font_size + """; font-family: Arial, sans-serif; word-wrap: break-word;">
                                {content}
                            </td>
                        </tr>
                    </table>
                </td>
                <td width="30%"></td>
            </tr>
        </table>
        """

def get_message_with_sender_style(sent=False, font_size="16px", max_width="300px"):
    """
    Generate HTML style for chat message bubbles with sender info and timestamp - PyQt5 Compatible
    """
    if sent:
        return """
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td width="30%"></td>
                <td width="70%" align="right">
                    <table border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            <td align="right">
                                <table border="0" cellpadding="8" cellspacing="0" style="background-color: #007AFF; border-radius: 15px; margin: 2px;">
                                    <tr>
                                        <td style="color: #FFFFFF; font-size: """ + font_size + """; font-family: Arial, sans-serif; word-wrap: break-word;">
                                            {content}
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td align="right" style="color: #8E8E93; font-size: 11px; font-family: Arial, sans-serif; padding-right: 8px;">
                                {timestamp}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """
    else:
        return """
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td width="70%" align="left">
                    <table border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            <td align="left" style="color: #007AFF; font-size: 12px; font-family: Arial, sans-serif; font-weight: bold; padding-left: 8px;">
                                {sender}
                            </td>
                        </tr>
                        <tr>
                            <td align="left">
                                <table border="0" cellpadding="8" cellspacing="0" style="background-color: #2C2C2E; border-radius: 15px; margin: 2px;">
                                    <tr>
                                        <td style="color: #FFFFFF; font-size: """ + font_size + """; font-family: Arial, sans-serif; word-wrap: break-word;">
                                            {content}
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td align="left" style="color: #8E8E93; font-size: 11px; font-family: Arial, sans-serif; padding-left: 8px;">
                                {timestamp}
                            </td>
                        </tr>
                    </table>
                </td>
                <td width="30%"></td>
            </tr>
        </table>
        """

# Example usage function
def format_message(content, sent=False, sender=None, timestamp=None, include_sender=False):
    """
    Format a message with the appropriate style
    
    Args:
        content (str): The message content
        sent (bool): True if sent by current user
        sender (str): Name of sender (for received messages)
        timestamp (str): Message timestamp
        include_sender (bool): Whether to include sender info
    
    Returns:
        str: Formatted HTML message
    """
    # Escape HTML content to prevent issues
    if content:
        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    if include_sender and not sent:
        template = get_message_with_sender_style(sent=sent)
        return template.format(content=content, sender=sender or "Unknown", timestamp=timestamp or "")
    elif include_sender and sent:
        template = get_message_with_sender_style(sent=sent)
        return template.format(content=content, timestamp=timestamp or "")
    else:
        template = get_message_bubble_style(sent=sent)
        return template.format(content=content)

# Chat window background
CHAT_WINDOW_STYLE = """
    QTextEdit {
        background: #000000;
        border: none;
        padding: 0;
        font-size: 16px;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
"""

# Input area styling
INPUT_AREA_STYLE = """
    QWidget {
        background: #1C1C1E;
        border-top: 1px solid #2C2C2E;
        padding: 8px;
    }
    QLineEdit {
        background: #2C2C2E;
        border: 1px solid #3A3A3C;
        border-radius: 20px;
        padding: 10px 16px;
        font-size: 16px;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
    }
    QLineEdit:focus {
        border: 1px solid #007AFF;
    }
    QPushButton {
        background: #007AFF;
        border: none;
        border-radius: 18px;
        padding: 9px;
        min-width: 36px;
        min-height: 36px;
        font-size: 16px;
        color: white;
        font-weight: 600;
    }
    QPushButton:hover {
        background: #0056CC;
    }
    QPushButton:pressed {
        background: #004499;
    }
    QPushButton:disabled {
        background: #2C2C2E;
        color: #8E8E93;
    }
"""

# Typing indicator - PyQt5 Compatible
TYPING_INDICATOR_STYLE = """
    <table width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td width="70%" align="left">
                <table border="0" cellpadding="8" cellspacing="0" style="background-color: #2C2C2E; border-radius: 15px; margin: 4px;">
                    <tr>
                        <td style="color: #8E8E93; font-size: 14px; font-family: Arial, sans-serif; font-style: italic;">
                            {sender} is typing...
                        </td>
                    </tr>
                </table>
            </td>
            <td width="30%"></td>
        </tr>
    </table>
"""

# System message style - PyQt5 Compatible
SYSTEM_MESSAGE_STYLE = """
    <table width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td align="center" style="color: #8E8E93; font-size: 12px; font-family: Arial, sans-serif; padding: 8px;">
                {content}
            </td>
        </tr>
    </table>
"""

# Date separator - PyQt5 Compatible
DATE_SEPARATOR_STYLE = """
    <table width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td align="center" style="padding: 12px;">
                <table border="0" cellpadding="4" cellspacing="0" style="background-color: #1C1C1E; border-radius: 12px;">
                    <tr>
                        <td style="color: #8E8E93; font-size: 11px; font-family: Arial, sans-serif; font-weight: bold;">
                            {date}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
"""