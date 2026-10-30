BG = "#0e1217"
PANEL = "#171d26"
BORDER = "#2a3342"
TEXT = "#e3e9f1"
MUTED = "#8593a6"
PLOT_BG = "#0b0f14"
PV = "#ffb020"
SP = "#38bdf8"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#f5c542"

STYLESHEET = f"""
QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: "Segoe UI", "Arial";
    font-size: 11pt;
}}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QLabel {{ background: transparent; }}
QStackedWidget, QStackedWidget > QWidget {{ background: transparent; }}
QFrame#card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QFrame#topBar {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QLabel#appTitle {{ font-size: 15pt; font-weight: 700; letter-spacing: 2px; }}
QLabel#cardTitle {{ color: {MUTED}; font-size: 9pt; font-weight: 700; letter-spacing: 1px; }}
QLabel#bigValue {{ font-size: 32pt; font-weight: 700; color: {PV}; }}
QLabel#midValue {{ font-size: 20pt; font-weight: 700; }}
QLabel#spValue {{ font-size: 20pt; font-weight: 700; color: {SP}; }}
QLabel#clock {{ color: {MUTED}; font-size: 12pt; }}
QLabel#hint {{ color: {MUTED}; font-size: 9pt; }}
QLabel#lockNote {{ color: {YELLOW}; font-size: 10pt; font-weight: 600; }}
QLabel#statusName {{ color: {MUTED}; }}
QLabel#statusValue {{ font-weight: 600; }}
QLabel#statusValue[level="error"] {{ color: {RED}; }}

QLabel#banner {{
    font-size: 15pt; font-weight: 700; padding: 10px; border-radius: 6px;
    qproperty-alignment: AlignCenter;
}}
QLabel#banner[level="ok"] {{ background: #123824; color: {GREEN}; border: 1px solid {GREEN}; }}
QLabel#banner[level="idle"] {{ background: #1c2430; color: {TEXT}; border: 1px solid {BORDER}; }}
QLabel#banner[level="warn"] {{ background: #3a3010; color: {YELLOW}; border: 1px solid {YELLOW}; }}
QLabel#banner[level="error"] {{ background: #43161a; color: #ff8a8a; border: 1px solid {RED}; }}

QLabel#linkIndicator {{ font-weight: 700; padding: 4px 10px; border-radius: 10px; }}
QLabel#linkIndicator[level="ok"] {{ color: {GREEN}; }}
QLabel#linkIndicator[level="warn"] {{ color: {YELLOW}; }}

QLabel#messageBar {{ padding: 6px 10px; border-radius: 6px; color: {MUTED}; }}
QLabel#messageBar[level="ok"] {{ color: {GREEN}; }}
QLabel#messageBar[level="error"] {{ color: #ff8a8a; }}

QPushButton {{
    background: #222c3a;
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}}
QPushButton:hover {{ background: #2b3748; }}
QPushButton:pressed {{ background: #1a222d; }}
QPushButton:disabled {{ color: #5b6778; background: #181e27; }}
QPushButton:checked {{ background: #1d4e75; border-color: {SP}; color: white; }}
QPushButton#modeButton {{ padding: 9px 10px; font-size: 12pt; }}
QPushButton#modeButton:checked {{ background: #1d4e75; border-color: {SP}; }}
QPushButton#modeButton:checked:disabled {{ background: #1a3347; color: #9fb8cc; }}
QPushButton#runButton {{ font-size: 16pt; font-weight: 800; padding: 13px; letter-spacing: 1px; }}
QPushButton#runButton[level="start"] {{ background: #176b3a; border-color: {GREEN}; color: white; }}
QPushButton#runButton[level="start"]:hover {{ background: #1c8447; }}
QPushButton#runButton[level="stop"] {{ background: #8a1f27; border-color: {RED}; color: white; }}
QPushButton#runButton[level="stop"]:hover {{ background: #a5262f; }}
QPushButton#runButton:disabled {{ background: #1b222c; border-color: {BORDER}; color: #5b6778; }}
QPushButton#exitButton {{ background: #3a1b20; border-color: #6b2a31; }}
QPushButton#exitButton:hover {{ background: #55242b; }}

QLineEdit {{
    background: {PLOT_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 14pt;
    font-weight: 600;
    selection-background-color: #1d4e75;
}}
QLineEdit:focus {{ border-color: {SP}; }}
QLineEdit:disabled {{ color: #6a7788; background: #12171e; }}

QComboBox {{
    background: #222c3a; border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QComboBox QAbstractItemView {{ background: {PANEL}; selection-background-color: #1d4e75; }}
QDateTimeEdit {{
    background: {PLOT_BG}; border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 8px;
}}
QDialog {{ background: {BG}; }}
QToolTip {{ background: {PANEL}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: #2f3a4b; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""
