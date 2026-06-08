class RailFenceCipher:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Validate đầu vào theo chuẩn Rail Fence Cipher:
    #   - text      : không rỗng
    #   - num_rails : số nguyên >= 2
    #                 (1 ray = không mã hoá gì; phải < độ dài chuỗi)
    # ------------------------------------------------------------------
    def _validate(self, text: str, num_rails: int) -> None:
        if not text or not text.strip():
            raise ValueError("Văn bản không được để trống.")
        try:
            r = int(num_rails)
        except (ValueError, TypeError):
            raise ValueError("Số ray phải là số nguyên.")
        if r < 2:
            raise ValueError("Số ray (rails) phải lớn hơn hoặc bằng 2.")
        if r >= len(text):
            raise ValueError(
                f"Số ray ({r}) phải nhỏ hơn độ dài văn bản ({len(text)})."
            )

    def rail_fence_encrypt(self, plain_text: str, num_rails) -> str:
        try:
            self._validate(plain_text, num_rails)
            num_rails = int(num_rails)

            rails     = [[] for _ in range(num_rails)]
            rail_idx  = 0
            direction = 1   # 1 = xuống, -1 = lên

            for ch in plain_text:
                rails[rail_idx].append(ch)
                if rail_idx == 0:
                    direction = 1
                elif rail_idx == num_rails - 1:
                    direction = -1
                rail_idx += direction

            return ''.join(''.join(rail) for rail in rails)
        except ValueError as e:
            return f"Lỗi: {e}"

    def rail_fence_decrypt(self, cipher_text: str, num_rails) -> str:
        try:
            self._validate(cipher_text, num_rails)
            num_rails = int(num_rails)

            # Tính số ký tự trên từng ray
            rail_lengths = [0] * num_rails
            rail_idx     = 0
            direction    = 1
            for _ in range(len(cipher_text)):
                rail_lengths[rail_idx] += 1
                if rail_idx == 0:
                    direction = 1
                elif rail_idx == num_rails - 1:
                    direction = -1
                rail_idx += direction

            # Phân chia cipher_text thành từng ray
            rails = []
            start = 0
            for length in rail_lengths:
                rails.append(list(cipher_text[start:start + length]))
                start += length

            # Đọc lại theo đường zigzag
            plain_text = ""
            rail_idx  = 0
            direction = 1
            for _ in range(len(cipher_text)):
                plain_text += rails[rail_idx].pop(0)
                if rail_idx == 0:
                    direction = 1
                elif rail_idx == num_rails - 1:
                    direction = -1
                rail_idx += direction

            return plain_text
        except ValueError as e:
            return f"Lỗi: {e}"