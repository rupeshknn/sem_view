from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Signal, Qt


class AutoAreaControl(QWidget):
    add_requested = Signal()
    trim_requested = Signal()
    finish_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Auto Area Refinement")

        layout = QVBoxLayout(self)

        self.info_label = QLabel("Refine the detected area:")
        layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Region")
        self.add_btn.setCheckable(True)
        self.add_btn.clicked.connect(self.on_add_clicked)
        btn_layout.addWidget(self.add_btn)

        self.trim_btn = QPushButton("Trim Region")
        self.trim_btn.setCheckable(True)
        self.trim_btn.clicked.connect(self.on_trim_clicked)
        btn_layout.addWidget(self.trim_btn)

        layout.addLayout(btn_layout)

        self.finish_btn = QPushButton("Finish")
        self.finish_btn.clicked.connect(self.finish_requested.emit)
        layout.addWidget(self.finish_btn)

    def on_add_clicked(self, checked):
        if checked:
            self.trim_btn.setChecked(False)
            self.add_requested.emit()
        else:
            # If unchecking, maybe go back to view mode?
            # For now, let main window handle state
            pass

    def on_trim_clicked(self, checked):
        if checked:
            self.add_btn.setChecked(False)
            self.trim_requested.emit()
        else:
            pass

    def reset(self):
        self.add_btn.setChecked(False)
        self.trim_btn.setChecked(False)
