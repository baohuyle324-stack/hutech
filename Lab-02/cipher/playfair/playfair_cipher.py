import re

class PlayFairCipher:
    # Bảng chữ cái Playfair (25 ký tự, J gộp vào I)
    ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Validate đầu vào theo chuẩn Playfair Cipher:
    #   - key  : không rỗng, chỉ gồm chữ cái (A-Z), không phân biệt hoa/thường,
    #            tối thiểu 1 ký tự (thực tế >= 2 để có ma trận ý nghĩa),
    #            tối đa 25 ký tự duy nhất (do bảng 5x5)
    #   - text : không rỗng, chỉ chứa chữ cái (A-Z, không tính J vì gộp với I),
    #            độ dài tối thiểu 2 ký tự (Playfair mã hoá từng cặp)
    # ------------------------------------------------------------------
    def _validate_key(self, key: str) -> None:
        if not key or not key.strip():
            raise ValueError("Khóa không được để trống.")
        if not key.replace(" ", "").isalpha():
            raise ValueError("Khóa Playfair chỉ được chứa các chữ cái (A-Z).")
        unique_letters = set(key.upper().replace("J", "I").replace(" ", ""))
        if len(unique_letters) < 2:
            raise ValueError("Khóa Playfair phải có ít nhất 2 ký tự chữ cái khác nhau.")

    def _validate_text(self, text: str, operation: str = "mã hoá") -> None:
        if not text or not text.strip():
            raise ValueError("Văn bản không được để trống.")
        cleaned = re.sub(r'[^A-Za-z]', '', text)
        if len(cleaned) < 2:
            raise ValueError(
                f"Văn bản cần {operation} phải có ít nhất 2 ký tự chữ cái."
            )

    # ------------------------------------------------------------------
    # Tạo ma trận Playfair 5x5 từ khóa
    # ------------------------------------------------------------------
    def create_playfair_matrix(self, key: str):
        try:
            self._validate_key(key)
        except ValueError as e:
            return f"Lỗi: {e}"

        key     = key.upper().replace("J", "I").replace(" ", "")
        seen    = []
        for ch in key:
            if ch not in seen:
                seen.append(ch)
        for ch in self.ALPHABET:
            if ch not in seen:
                seen.append(ch)

        return [seen[i:i + 5] for i in range(0, 25, 5)]

    def find_letter_coords(self, matrix, letter: str):
        for row in range(5):
            for col in range(5):
                if matrix[row][col] == letter:
                    return row, col
        return None, None

    # ------------------------------------------------------------------
    # Chuẩn bị chuỗi plaintext trước khi mã hoá:
    #   - Chuyển hoa, thay J→I, loại ký tự không phải chữ cái
    #   - Tách thành các cặp, chèn 'X' nếu 2 ký tự trong cặp giống nhau
    #   - Thêm 'X' nếu tổng số ký tự lẻ
    # ------------------------------------------------------------------
    def _prepare_plaintext(self, text: str) -> str:
        text    = re.sub(r'[^A-Za-z]', '', text).upper().replace("J", "I")
        prepared = ""
        i = 0
        while i < len(text):
            a = text[i]
            if i + 1 < len(text):
                b = text[i + 1]
                if a == b:          # Hai ký tự giống nhau → chèn X vào giữa
                    prepared += a + "X"
                    i += 1
                else:
                    prepared += a + b
                    i += 2
            else:                   # Ký tự cuối lẻ → thêm X
                prepared += a + "X"
                i += 1
        return prepared

    def playfair_encrypt(self, plain_text: str, matrix) -> str:
        try:
            if isinstance(matrix, str):   # matrix là thông báo lỗi
                return matrix
            self._validate_text(plain_text, "mã hoá")

            text    = self._prepare_plaintext(plain_text)
            result  = ""

            for i in range(0, len(text), 2):
                a, b         = text[i], text[i + 1]
                r1, c1       = self.find_letter_coords(matrix, a)
                r2, c2       = self.find_letter_coords(matrix, b)

                if r1 == r2:                            # Cùng hàng → dịch phải
                    result += matrix[r1][(c1 + 1) % 5] + matrix[r2][(c2 + 1) % 5]
                elif c1 == c2:                          # Cùng cột → dịch xuống
                    result += matrix[(r1 + 1) % 5][c1] + matrix[(r2 + 1) % 5][c2]
                else:                                   # Hình chữ nhật → hoán vị cột
                    result += matrix[r1][c2] + matrix[r2][c1]

            return result
        except ValueError as e:
            return f"Lỗi: {e}"

    def playfair_decrypt(self, cipher_text: str, matrix) -> str:
        try:
            if isinstance(matrix, str):
                return matrix
            self._validate_text(cipher_text, "giải mã")

            text   = re.sub(r'[^A-Za-z]', '', cipher_text).upper()
            if len(text) % 2 != 0:
                raise ValueError(
                    "Độ dài bản mã Playfair phải là số chẵn (mã hoá theo từng cặp ký tự)."
                )

            result = ""
            for i in range(0, len(text), 2):
                a, b   = text[i], text[i + 1]
                r1, c1 = self.find_letter_coords(matrix, a)
                r2, c2 = self.find_letter_coords(matrix, b)

                if r1 == r2:                            # Cùng hàng → dịch trái
                    result += matrix[r1][(c1 - 1) % 5] + matrix[r2][(c2 - 1) % 5]
                elif c1 == c2:                          # Cùng cột → dịch lên
                    result += matrix[(r1 - 1) % 5][c1] + matrix[(r2 - 1) % 5][c2]
                else:                                   # Hình chữ nhật → hoán vị cột
                    result += matrix[r1][c2] + matrix[r2][c1]

            # Loại bỏ ký tự X chèn thêm (nằm cuối hoặc giữa 2 ký tự giống nhau)
            cleaned = ""
            i = 0
            while i < len(result):
                if result[i] == 'X':
                    # X ở cuối → bỏ
                    if i == len(result) - 1:
                        i += 1
                        continue
                    # X ở giữa 2 ký tự giống nhau → bỏ
                    if i > 0 and i < len(result) - 1 and result[i - 1] == result[i + 1]:
                        i += 1
                        continue
                cleaned += result[i]
                i += 1

            return cleaned
        except ValueError as e:
            return f"Lỗi: {e}"