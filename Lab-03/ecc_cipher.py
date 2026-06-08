import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ECCApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECC Cipher")
        self.setFixedSize(420, 320)

        # State
        self.private_key = None
        self.public_key = None

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 10, 12, 8)
        main_layout.setSpacing(8)
        central_widget.setLayout(main_layout)

        # ── Title row ──────────────────────────────────────────
        top_layout = QHBoxLayout()

        title_label = QLabel("ECC CIPHER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        self.btn_generate_keys = QPushButton("Generate Keys")
        self.btn_generate_keys.setFont(QFont("Arial", 9))
        self.btn_generate_keys.setFixedHeight(26)
        self.btn_generate_keys.clicked.connect(self.generate_keys)
        top_layout.addWidget(self.btn_generate_keys)

        main_layout.addLayout(top_layout)

        # ── Information row ────────────────────────────────────
        info_layout = QHBoxLayout()
        info_label = QLabel("Information:")
        info_label.setFixedWidth(75)
        info_label.setFont(QFont("Arial", 9))
        info_layout.addWidget(info_label, alignment=Qt.AlignTop)

        self.txt_information = QTextEdit()
        self.txt_information.setFont(QFont("Arial", 9))
        self.txt_information.setFixedHeight(75)
        info_layout.addWidget(self.txt_information)

        main_layout.addLayout(info_layout)

        # ── Signature row ──────────────────────────────────────
        sig_layout = QHBoxLayout()
        sig_label = QLabel("Signature:")
        sig_label.setFixedWidth(75)
        sig_label.setFont(QFont("Arial", 9))
        sig_layout.addWidget(sig_label, alignment=Qt.AlignTop)

        self.txt_signature = QTextEdit()
        self.txt_signature.setFont(QFont("Arial", 9))
        self.txt_signature.setFixedHeight(75)
        sig_layout.addWidget(self.txt_signature)

        main_layout.addLayout(sig_layout)

        # ── Sign / Verify buttons ──────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_sign = QPushButton("Sign")
        self.btn_sign.setFixedWidth(90)
        self.btn_sign.setFont(QFont("Arial", 9))
        self.btn_sign.clicked.connect(self.sign_message)
        btn_layout.addWidget(self.btn_sign)

        btn_layout.addSpacing(50)

        self.btn_verify = QPushButton("Verify")
        self.btn_verify.setFixedWidth(90)
        self.btn_verify.setFont(QFont("Arial", 9))
        self.btn_verify.clicked.connect(self.verify_signature)
        btn_layout.addWidget(self.btn_verify)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ── Footer label ───────────────────────────────────────
        self.lbl_author = QLabel("LeHuyBao-2380600139")
        self.lbl_author.setAlignment(Qt.AlignCenter)
        self.lbl_author.setFont(QFont("Arial", 9))
        self.lbl_author.setStyleSheet("color: #555555; margin-top: 2px;")
        main_layout.addWidget(self.lbl_author)

    def generate_keys(self):
        url = "http://127.0.0.1:5000/api/ecc/generate_keys"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.private_key = data.get("private_key", "")
                self.public_key = data.get("public_key", "")
                
                # Show key generation results in a popup
                QMessageBox.information(
                    self, 
                    "Keys Generated", 
                    f"Cặp khóa đã được sinh thành công!\n\n"
                    f"Private Key:\n{self.private_key}\n\n"
                    f"Public Key:\n{self.public_key}"
                )
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể sinh khóa. Mã lỗi API: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể kết nối đến Flask API Server:\n{str(e)}")

    def sign_message(self):
        if not self.private_key:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng sinh khóa trước bằng cách nhấn nút 'Generate Keys'!")
            return
        
        message = self.txt_information.toPlainText()
        if not message:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập nội dung cần ký vào ô 'Information'!")
            return
            
        url = "http://127.0.0.1:5000/api/ecc/sign"
        payload = {
            "message": message,
            "private_key": self.private_key
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                sig = data.get("signature", "")
                if sig.startswith("Lỗi"):
                    QMessageBox.warning(self, "Lỗi", sig)
                else:
                    self.txt_signature.setPlainText(sig)
                    QMessageBox.information(self, "Thành công", "Đã ký thành công!")
            else:
                QMessageBox.critical(self, "Lỗi", f"Mã lỗi từ API: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể kết nối đến Flask API Server:\n{str(e)}")

    def verify_signature(self):
        if not self.public_key:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng sinh khóa trước bằng cách nhấn nút 'Generate Keys'!")
            return
            
        message = self.txt_information.toPlainText()
        signature = self.txt_signature.toPlainText()
        
        if not message:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập nội dung tin nhắn cần xác minh!")
            return
            
        if not signature:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập chữ ký cần xác minh!")
            return
            
        url = "http://127.0.0.1:5000/api/ecc/verify"
        payload = {
            "message": message,
            "signature": signature,
            "public_key": self.public_key
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                valid = data.get("valid", False)
                if valid:
                    QMessageBox.information(self, "Kết quả xác minh", "Chữ ký HỢP LỆ! (Signature is Valid)")
                else:
                    QMessageBox.warning(self, "Kết quả xác minh", "Chữ ký KHÔNG hợp lệ! (Signature is Invalid)")
            else:
                QMessageBox.critical(self, "Lỗi", f"Mã lỗi từ API: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể kết nối đến Flask API Server:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ECCApp()
    window.show()
    sys.exit(app.exec_())
