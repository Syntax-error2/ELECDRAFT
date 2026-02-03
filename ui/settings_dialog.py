# ui/settings_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QCheckBox, QHBoxLayout, \
    QPushButton
from PySide6.QtCore import Qt


class ProjectSettingsDialog(QDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Settings")
        self.setFixedWidth(450)
        # Professional styling for the dialog
        self.setStyleSheet("background-color: #25282b; color: #adb5bd;")

        layout = QVBoxLayout(self)

        form = QFormLayout()
        # Initialize with current project data
        self.proj_name = QLineEdit(current_settings.get('name', 'New Project'))
        self.author = QLineEdit(current_settings.get('author', 'Engineer'))

        self.standard = QComboBox()
        self.standard.addItems(["PEC (Philippines)", "ANSI (US)", "IEC (International)"])
        self.standard.setCurrentText(current_settings.get('standard', 'PEC (Philippines)'))

        form.addRow("Project Name:", self.proj_name)
        form.addRow("Lead Author:", self.author)
        form.addRow("Design Standard:", self.standard)
        layout.addLayout(form)

        # Standards Checkboxes
        check_layout = QHBoxLayout()
        self.chk_dxf = QCheckBox("Export DXF")
        self.chk_pdf = QCheckBox("Export PDF")
        self.chk_pdf.setChecked(current_settings.get('export_pdf', True))
        check_layout.addWidget(self.chk_dxf)
        check_layout.addWidget(self.chk_pdf)
        layout.addLayout(check_layout)

        # Action Buttons
        btns = QHBoxLayout()
        save_btn = QPushButton("Apply Settings")
        save_btn.setStyleSheet("background-color: #34e7e4; color: black; font-weight: bold; padding: 8px;")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def get_settings(self):
        """Returns the dictionary of user-inputted settings."""
        return {
            "name": self.proj_name.text(),
            "author": self.author.text(),
            "standard": self.standard.currentText(),
            "export_pdf": self.chk_pdf.isChecked(),
            "export_dxf": self.chk_dxf.isChecked()
        }