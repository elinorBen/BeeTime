from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTimeEdit, QSpacerItem, QSizePolicy, QLineEdit
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QPixmap, QIcon
import os


class WorkDialogManager:
    def __init__(self):
        self.dialog_style = """
        QDialog {
            background-color: #f8f8f0;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        QLabel {
            font-size: 14px;
            color: #2e2e2e;
        }
        QPushButton {
            font-size: 13px;
            padding: 6px 12px;
            border-radius: 5px;
        }
        QPushButton#ok {
            background-color: #a8d5a2;
            color: #2e2e2e;
        }
        QPushButton#cancel {
            background-color: #cccccc;
            color: #2e2e2e;
        }
        QPushButton#edit {
            background-color: #ffe680;
            color: #2e2e2e;
        }
        QPushButton#yes {
            background-color: #ffe680;
            color: #2e2e2e;
        }
        QPushButton#no {
            background-color: #cccccc;
            color: #2e2e2e;
        }
        """

    def _create_dialog(self, title, message, buttons, time_edit=False, text_input=False, icon_path=None):
        dialog = QDialog()
        dialog.setWindowTitle(f"BeeTime - {title}")
        dialog.setStyleSheet(self.dialog_style)

        # Set application icon if available
        app_icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "cute_beetime_icon.ico")
        if os.path.exists(app_icon_path):
            dialog.setWindowIcon(QIcon(app_icon_path))

        layout = QVBoxLayout()

        # Optional icon
        icon_path = icon_path or app_icon_path
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaledToWidth(64, Qt.TransformationMode.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        # Message
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Optional time input
        time_input = None
        if time_edit:
            time_input = QTimeEdit()
            time_input.setDisplayFormat("HH:mm")
            time_input.setTime(QTime.currentTime())
            time_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_input.setVisible(False)
            dialog.input = time_input
            layout.addWidget(time_input)

        # Optional text input
        text_input_field = None
        if text_input:
            text_input_field = QLineEdit()
            text_input_field.setPlaceholderText("e.g., Coffee break")
            text_input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dialog.input = text_input_field
            layout.addWidget(text_input_field)

        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Buttons
        button_layout = QHBoxLayout()
        for btn_text, btn_role, btn_id in buttons:
            button = QPushButton(btn_text)
            button.setObjectName(btn_id)
            if btn_role == "accept":
                button.clicked.connect(lambda _, d=dialog: d.accept())
            elif btn_role == "reject":
                button.clicked.connect(lambda _, d=dialog: d.reject())
            elif btn_role == "edit":
                button.clicked.connect(lambda _, d=dialog: d.done(2))
            button_layout.addWidget(button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        result = dialog.exec()

        # Handle edit mode for time input
        if result == 2 and time_edit:
            dialog.input.setVisible(True)
            dialog.input.setFocus()
            dialog.input.selectAll()
            result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            if time_edit:
                return dialog.input.time().toString("HH:mm")
            elif text_input:
                return dialog.input.text().strip()
            return True

        return None if (time_edit or text_input) else False

    def show_start_work_dialog(self, location):
        message = f"Good morning!\nYou're connected from: {location}\nPlease confirm your start time:"
        buttons = [
            ("OK", "accept", "ok"),
            ("Edit", "edit", "edit"),
            ("Cancel", "reject", "cancel")
        ]
        return self._create_dialog("Start Work Day", message, buttons, time_edit=True)

    def show_finish_dialog_met_target(self):
        message = "You have met the working hours target for today."
        buttons = [("OK", "accept", "ok"), ("Cancel", "reject", "cancel")]
        return self._create_dialog("Workday Complete", message, buttons)

    def show_finish_dialog_not_met_target(self, remaining_time_str):
        message = f"You didn't meet the working hours target for today.\nYou have {remaining_time_str} left.\nAre you sure you are done for today?"
        buttons = [("Yes", "accept", "yes"), ("No", "reject", "no")]
        return self._create_dialog("Workday Not Complete", message, buttons)

    def show_break_dialog(self):
        message = "You're about to take a break.\nEnter a note (optional):"
        buttons = [("OK", "accept", "ok"), ("Cancel", "reject", "cancel")]
        return self._create_dialog("Break Time", message, buttons, text_input=True)
