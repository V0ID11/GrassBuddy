
class Stylesheet:
    DARK_THEME = """
    /* General Window */
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2b2b2b, stop:1 #121212);
        color: #E0E0E0;
    }
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        font-size: 18px;
        color: #E0E0E0;
        background-color: transparent; /* Let gradients shine through or specific widgets set their own */
    }

    QWidget#centralWidget {
         background: transparent;
    }
    
    /* Labels */
    QLabel {
        color: #E0E0E0;
        background-color: transparent;
    }
    QLabel#header_label {
        font-size: 38px;
        font-weight: bold;
        color: #66BB6A; /* Lighter Grass Green */
        margin-bottom: 25px;
        margin-top: 15px;
    }
    QLabel#sub_header {
        font-size: 28px;
        color: #A5D6A7;
        margin-bottom: 12px;
    }

    /* Buttons */
    QPushButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43A047, stop:1 #2E7D32);
        color: white;
        border: 1px solid #1B5E20;
        padding: 5px 30px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 20px;
        margin: 5px;
    }
    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #66BB6A, stop:1 #388E3C);
    }
    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1B5E20, stop:1 #43A047);
    }
    QPushButton:disabled {
        background-color: #424242;
        color: #757575;
        border: none;
    }

    /* Secondary / Action Buttons */
    QPushButton#secondary_btn {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #607D8B, stop:1 #455A64);
        border: 1px solid #37474F;
    }
    QPushButton#secondary_btn:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #78909C, stop:1 #546E7A);
    }

    /* Danger Buttons (Reject, etc.) */
    QPushButton#danger_btn {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E53935, stop:1 #C62828);
        border: 1px solid #B71C1C;
    }
    QPushButton#danger_btn:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF5350, stop:1 #D32F2F);
    }

    /* Line Edits */
    QLineEdit {
        background-color: #2C2C2C;
        border: 2px solid #424242;
        border-radius: 8px;
        padding: 12px;
        color: white;
        font-size: 16px;
        selection-background-color: #66BB6A;
    }
    QLineEdit:focus {
        border: 2px solid #66BB6A;
        background-color: #333333;
    }

    /* List Widgets */
    QListWidget {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 10px;
        outline: 0;
    }
    QListWidget::item {
        padding: 12px;
        border-bottom: 1px solid #333333;
        border-radius: 4px;
    }
    QListWidget::item:selected {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43A047, stop:1 #2E7D32);
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
        border: 1px solid #424242;
        background-color: #1E1E1E;
        border-radius: 4px;
    }
    QTabBar::tab {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #424242, stop:1 #2C2C2C);
        color: #BDBDBD;
        padding: 12px 24px;
        font-size: 16px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 4px;
    }
    QTabBar::tab:selected {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #43A047, stop:1 #2E7D32);
        color: white;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #606060, stop:1 #404040);
    }

    /* Card Items (Feed, Friends, etc.) */
    QWidget#card {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2C2C2C, stop:1 #1E1E1E);
        border-radius: 12px;
        border: 1px solid #333333;
        margin-bottom: 10px;
    }
    """
