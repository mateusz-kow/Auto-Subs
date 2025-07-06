from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # --- Układ główny ---
        layout = QHBoxLayout()
        self.setLayout(layout)

        # --- Panel po lewej (boczny) ---
        self.side_panel = QStackedWidget()
        layout.addWidget(self.side_panel, 1)

        # --- Panel treściowy po prawej ---
        self.content_area = QVBoxLayout()
        layout.addLayout(self.content_area, 3)

        # Etykieta, którą można kliknąć
        self.label = QLabel("Kliknij mnie, aby edytować")
        self.label.setObjectName("editableLabel")
        self.label.setStyleSheet("font-size: 18px;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.mousePressEvent = self.label_clicked  # "podpięcie" zdarzenia kliknięcia

        self.content_area.addWidget(self.label)

        # --- Widok 1: styl tekstu ---
        self.style_widget = QWidget()
        style_layout = QVBoxLayout(self.style_widget)
        style_button = QPushButton("Zmień kolor (przykład)")
        style_button.clicked.connect(self.change_style)
        style_layout.addWidget(style_button)

        # --- Widok 2: edytor tekstu ---
        self.text_edit_widget = QWidget()
        edit_layout = QVBoxLayout(self.text_edit_widget)
        self.text_edit = QLineEdit()
        save_button = QPushButton("Zapisz tekst")
        save_button.clicked.connect(self.save_text)
        edit_layout.addWidget(self.text_edit)
        edit_layout.addWidget(save_button)

        # --- Dodaj oba widoki do panelu bocznego ---
        self.side_panel.addWidget(self.style_widget)  # index 0
        self.side_panel.addWidget(self.text_edit_widget)  # index 1

        # Startujemy z widokiem do stylizacji
        self.side_panel.setCurrentIndex(0)

    def label_clicked(self, event):
        # Przejście do widoku edycji tekstu
        self.text_edit.setText(self.label.text())
        self.side_panel.setCurrentIndex(1)

    def save_text(self):
        self.label.setText(self.text_edit.text())
        self.side_panel.setCurrentIndex(0)

    def change_style(self):
        # Przykład zmiany stylu
        self.label.setStyleSheet("color: red; font-size: 18px;")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    app.exec_()
