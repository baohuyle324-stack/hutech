class VigenereCipher:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Validate đầu vào theo chuẩn Vigenère Cipher:
    #   - text : không rỗng, phải chứa ít nhất 1 chữ cái
    #   - key  : không rỗng, chỉ gồm các chữ cái (A-Z / a-z),
    #            không chứa số hay ký tự đặc biệt,
    #            độ dài >= 1 (thông thường >= 2 để có ý nghĩa mã hoá)
    # ------------------------------------------------------------------
    def _validate(self, text: str, key: str) -> None:
        if not text or not text.strip():
            raise ValueError("Văn bản không được để trống.")
        if not any(ch.isalpha() for ch in text):
            raise ValueError("Văn bản phải chứa ít nhất một ký tự chữ cái.")
        if not key or not key.strip():
            raise ValueError("Khóa không được để trống.")
        if not key.isalpha():
            raise ValueError("Khóa Vigenère chỉ được chứa các chữ cái (A-Z).")
        if len(key) < 2:
            raise ValueError("Khóa Vigenère phải có ít nhất 2 ký tự.")

    def encrypt_text(self, plain_text: str, key: str) -> str:
        try:
            self._validate(plain_text, key)
            encrypted = ""
            key_index = 0
            for ch in plain_text:
                if ch.isalpha():
                    shift = ord(key[key_index % len(key)].upper()) - ord('A')
                    if ch.isupper():
                        encrypted += chr((ord(ch) - ord('A') + shift) % 26 + ord('A'))
                    else:
                        encrypted += chr((ord(ch) - ord('a') + shift) % 26 + ord('a'))
                    key_index += 1
                else:
                    encrypted += ch   # Giữ nguyên ký tự không phải chữ cái
            return encrypted
        except ValueError as e:
            return f"Lỗi: {e}"

    def decrypt_text(self, encrypted_text: str, key: str) -> str:
        try:
            self._validate(encrypted_text, key)
            decrypted = ""
            key_index = 0
            for ch in encrypted_text:
                if ch.isalpha():
                    shift = ord(key[key_index % len(key)].upper()) - ord('A')
                    if ch.isupper():
                        decrypted += chr((ord(ch) - ord('A') - shift) % 26 + ord('A'))
                    else:
                        decrypted += chr((ord(ch) - ord('a') - shift) % 26 + ord('a'))
                    key_index += 1
                else:
                    decrypted += ch
            return decrypted
        except ValueError as e:
            return f"Lỗi: {e}"