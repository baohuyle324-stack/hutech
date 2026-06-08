import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui.railfence import Ui_MainWindow
import requests

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_encrypt.clicked.connect(self.call_api_encrypt)
        self.ui.btn_decrypt.clicked.connect(self.call_api_decrypt)

        # Show constraints on startup
        self.show_constraints_info()

    def show_constraints_info(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Lưu ý sử dụng - Rail Fence Cipher")
        msg.setText(
            "Ràng buộc thuật toán Rail Fence Cipher:\n"
            "1. Văn bản (Plain text / Cipher text) không được để trống.\n"
            "2. Khóa (Key - Số ray/hàng) phải là số nguyên >= 2.\n"
            "3. Số ray/hàng phải nhỏ hơn độ dài của văn bản."
        )
        msg.exec_()

    def validate_inputs(self, text, key):
        if not text.strip():
            QMessageBox.warning(self, "Cảnh báo", "Văn bản không được để trống!")
            return False
        try:
            k = int(key)
            if k < 2:
                QMessageBox.warning(self, "Cảnh báo", "Khóa (Số hàng/ray) phải >= 2!")
                return False
            if k >= len(text):
                QMessageBox.warning(
                    self, 
                    "Cảnh báo", 
                    f"Số hàng/ray ({k}) phải nhỏ hơn độ dài văn bản ({len(text)})!"
                )
                return False
        except ValueError:
            QMessageBox.warning(self, "Cảnh báo", "Khóa (Key) phải là một số nguyên!")
            return False
        return True

    def call_api_encrypt(self):
        plaintext = self.ui.txt_plain_text.text()
        key = self.ui.txt_key.text()

        if not self.validate_inputs(plaintext, key):
            return

        url = "http://127.0.0.1:5000/api/railfence/encrypt"
        payload = {
            "plain_text": plaintext,
            "key": key
        }
        try:
            response = requests.post(url, json=payload)
            print("Response status code:", response.status_code)
            print("Response text:", response.text)

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.ui.txt_cipher.setText(data.get("encrypted_text", ""))
                    QMessageBox.information(self, "Thành công", "Encrypted Successfully")
                except requests.exceptions.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
            else:
                try:
                    err_msg = response.json().get("error", "Error while calling API")
                except:
                    err_msg = "Error while calling API"
                QMessageBox.warning(self, "Lỗi từ Server", err_msg)

        except requests.exceptions.RequestException as e:
            print(f"Error while calling API: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể kết nối đến Flask API Server:\n{str(e)}")

    def call_api_decrypt(self):
        ciphertext = self.ui.txt_cipher.text()
        key = self.ui.txt_key.text()

        if not self.validate_inputs(ciphertext, key):
            return

        url = "http://127.0.0.1:5000/api/railfence/decrypt"
        payload = {
            "cipher_text": ciphertext,
            "key": key
        }
        try:
            response = requests.post(url, json=payload)
            print("Response status code:", response.status_code)
            print("Response text:", response.text)

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.ui.txt_plain_text.setText(data.get("decrypted_text", ""))
                    QMessageBox.information(self, "Thành công", "Decrypted Successfully")
                except requests.exceptions.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
            else:
                try:
                    err_msg = response.json().get("error", "Error while calling API")
                except:
                    err_msg = "Error while calling API"
                QMessageBox.warning(self, "Lỗi từ Server", err_msg)

        except requests.exceptions.RequestException as e:
            print(f"Error while calling API: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể kết nối đến Flask API Server:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
