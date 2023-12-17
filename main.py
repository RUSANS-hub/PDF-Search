import os
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QListWidget, QListWidgetItem, QLabel, QMessageBox

import PyPDF2

class PDFSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Search App")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Tambahkan layout untuk dua tombol di atasnya
        self.button_layout = QHBoxLayout()

        # Tombol Unduh
        self.download_button = QPushButton("Unduh")
        self.download_button.clicked.connect(self.unduh_file)
        self.button_layout.addWidget(self.download_button)

        # Tombol Cari
        self.search_button_top = QPushButton("Cari")
        self.search_button_top.clicked.connect(self.cari_teks)
        self.button_layout.addWidget(self.search_button_top)

        # Tambahkan layout tombol di atasnya
        self.layout.addLayout(self.button_layout)

        self.chat_layout = QVBoxLayout()

        self.file_list_widget = QListWidget()
        self.file_list_widget.itemClicked.connect(self.buka_file)
        self.chat_layout.addWidget(self.file_list_widget)

        self.result_label = QLabel()
        self.chat_layout.addWidget(self.result_label)

        self.layout.addLayout(self.chat_layout)

        self.search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Ketik teks pencarian...")
        self.search_layout.addWidget(self.search_box)

        self.search_button = QPushButton("Cari")
        self.search_button.clicked.connect(self.cari_teks)
        self.search_layout.addWidget(self.search_button)

        self.location_button = QPushButton("...")
        self.location_button.clicked.connect(self.pilih_lokasi)
        self.search_layout.addWidget(self.location_button)

        self.layout.addLayout(self.search_layout)

        self.central_widget.setLayout(self.layout)

    def tampilkan_pesan_alert(self):
        QMessageBox.information(self, "Informasi", "Klik titik tiga untuk mengubah lokasi folder", QMessageBox.Ok)

    def pilih_lokasi(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Dokumen", "")
        if folder_path:
            self.folder_path = folder_path
            self.file_list_widget.clear()
            self.file_list_widget.addItem(QListWidgetItem("Menampilkan file di: " + self.folder_path, None))

            self.tampilkan_file_di_lokasi()

    def cari_teks(self):
        if not self.folder_path:
            self.file_list_widget.clear()
            self.result_label.setText("Silakan pilih lokasi file terlebih dahulu.")
        else:
            teks_yang_dicari = self.search_box.text()
            self.file_list_widget.clear()
            self.result_label.clear()
            self.file_list_widget.addItem(QListWidgetItem(f"File Ketemu:", None))

            for filename in os.listdir(self.folder_path):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(self.folder_path, filename)
                    with open(file_path, "rb") as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text = page.extract_text().lower()
                            teks_yang_dicari_lower = teks_yang_dicari.lower()
                            if teks_yang_dicari_lower in text:
                                result_text = f'{filename}, halaman: {page_num + 1}\n'
                                self.file_list_widget.addItem(QListWidgetItem(result_text, None))

            if not self.file_list_widget.count() > 1:
                self.result_label.setText("Teks tidak ditemukan.")
            else:
                self.result_label.setText("File ditemukan.")

    def tampilkan_file_di_lokasi(self):
        if not self.folder_path:
            return

        self.file_list_widget.clear()
        self.file_list_widget.addItem(QListWidgetItem("Menampilkan file di: " + self.folder_path, None))

        for filename in os.listdir(self.folder_path):
            self.file_list_widget.addItem(QListWidgetItem(filename, None))

    def buka_file(self, item):
        if not item.text().startswith("Menampilkan file di:"):
            file_path = os.path.join(self.folder_path, item.text().split(", halaman:")[0])
            if os.path.isfile(file_path):
                self.file_list_widget.addItem(QListWidgetItem(f"Membuka file {item.text()}...", None))
                webbrowser.open(file_path, new=2)  # Membuka file dalam browser default

    def unduh_file(self):
        # Implementasi fungsi unduh file di sini
        pass

if __name__ == "__main__":
    app = QApplication([])
    window = PDFSearchApp()
    window.show()
    app.exec_()

