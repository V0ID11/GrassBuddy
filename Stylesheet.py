
class Stylesheet:
    DARK_THEME = """
    /* General Window */
    QMainWindow, QWidget {
        background-color: #2E2E2E;
        color: #E0E0E0;
    }
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    
    /* Labels */
    QLabel {
        color: #E0E0E0;
    }
    QLabel#header_label {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50; /* Grass Green */
        margin-bottom: 10px;
    }
    QLabel#sub_header {
        font-size: 18px;
        color: #81C784;
        margin-bottom: 5px;
    }

    /* Buttons */
    QPushButton {
        background-color: #388E3C;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #4CAF50;
    }
    QPushButton:pressed {
        background-color: #2E7D32;
    }
    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }

    /* Secondary / Action Buttons */
    QPushButton#secondary_btn {
        background-color: #555555;
    }
    QPushButton#secondary_btn:hover {
        background-color: #666666;
    }

    /* Danger Buttons (Reject, etc.) */
    QPushButton#danger_btn {
        background-color: #D32F2F;
    }
    QPushButton#danger_btn:hover {
        background-color: #E53935;
    }

    /* Line Edits */
    QLineEdit {
        background-color: #424242;
        border: 1px solid #616161;
        border-radius: 4px;
        padding: 8px;
        color: white;
    }
    QLineEdit:focus {
        border: 1px solid #4CAF50;
    }

    /* List Widgets */
    QListWidget {
        background-color: #424242;
        border: 1px solid #616161;
        border-radius: 4px;
        padding: 5px;
        outline: 0;
    }
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #505050;
    }
    QListWidget::item:selected {
        background-color: #4CAF50;
        color: white;
    }

    /* Scroll Area */
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        border: 1px solid #616161;
        background-color: #2E2E2E;
    }
    QTabBar::tab {
        background-color: #424242;
        color: #E0E0E0;
        padding: 8px 16px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: #388E3C;
        color: white;
    }
    QTabBar::tab:hover {
        background-color: #505050;
    }

    /* Card Items (Feed, Friends, etc.) */
    QWidget#card {
        background-color: #424242;
        border-radius: 8px;
        border: 1px solid #505050;
    }
    """
