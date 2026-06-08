from cipher.caesar import ALPHABET

class CaesarCipher:
    def __init__(self):
        self.alphabet     = ALPHABET
        self.alphabet_len = len(self.alphabet)   # 26

    # ------------------------------------------------------------------
    # Validate đầu vào theo chuẩn Caesar Cipher:
    #   - text  : không rỗng, phải chứa ít nhất 1 chữ cái
    #   - key   : số nguyên, nằm trong [1, 25]
    #             (key=0 hoặc key=26 không có tác dụng mã hoá)
    # ------------------------------------------------------------------
    def _validate(self, text: str, key) -> None:
        if not text or not text.strip():
            raise ValueError("Văn bản không được để trống.")
        if not any(ch.isalpha() for ch in text):
            raise ValueError("Văn bản phải chứa ít nhất một ký tự chữ cái.")
        try:
            k = int(key)
        except (ValueError, TypeError):
            raise ValueError("Khóa phải là số nguyên.")
        if not (1 <= k <= 25):
            raise ValueError("Khóa Caesar phải nằm trong khoảng [1, 25].")

    def encrypt_text(self, text: str, key) -> str:
        try:
            self._validate(text, key)
            key = int(key)
            result = []
            for ch in text:
                if ch.upper() in self.alphabet:
                    idx        = self.alphabet.index(ch.upper())
                    new_idx    = (idx + key) % self.alphabet_len
                    new_ch     = self.alphabet[new_idx]
                    result.append(new_ch if ch.isupper() else new_ch.lower())
                else:
                    result.append(ch)   # Giữ nguyên ký tự không phải chữ cái
            return "".join(result)
        except ValueError as e:
            return f"Lỗi: {e}"

    def decrypt_text(self, text: str, key) -> str:
        try:
            self._validate(text, key)
            key = int(key)
            result = []
            for ch in text:
                if ch.upper() in self.alphabet:
                    idx        = self.alphabet.index(ch.upper())
                    new_idx    = (idx - key) % self.alphabet_len
                    new_ch     = self.alphabet[new_idx]
                    result.append(new_ch if ch.isupper() else new_ch.lower())
                else:
                    result.append(ch)
            return "".join(result)
        except ValueError as e:
            return f"Lỗi: {e}"