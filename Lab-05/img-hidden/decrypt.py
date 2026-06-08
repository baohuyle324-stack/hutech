# =============================================================
#  decrypt.py - Trích xuất tin ẩn từ ảnh đã mã hoá bằng LSB
#  Cách dùng: python decrypt.py <encoded_image_path>
#  Ví dụ   : python decrypt.py encoded_image.png
# =============================================================

import sys
from PIL import Image


# -------------------------------------------------------------
# Hàm đọc toàn bộ chuỗi nhị phân từ ảnh đã mã hoá
#   - Duyệt từng pixel theo cùng thứ tự như khi giấu tin
#   - Lấy LSB (bit cuối) của từng kênh R, G, B
#   - Ghép lại thành chuỗi nhị phân liên tục
# -------------------------------------------------------------
def extract_binary(img) -> str:
    pixels     = list(img.getdata())   # Danh sách pixel (R, G, B)
    binary_str = ''                    # Chuỗi nhị phân kết quả

    for pixel in pixels:
        r, g, b = pixel

        # Lấy LSB của từng kênh màu bằng phép AND với 1
        binary_str += str(r & 1)   # LSB kênh R
        binary_str += str(g & 1)   # LSB kênh G
        binary_str += str(b & 1)   # LSB kênh B

    return binary_str


# -------------------------------------------------------------
# Hàm chuyển chuỗi nhị phân thành văn bản
#   - Cắt từng 8 bit một → chuyển sang ký tự ASCII
#   - Dừng khi gặp ký tự rỗng '\0' (NULL character)
#     hoặc khi phát hiện chuỗi kết thúc 16-bit "1111111111111110"
# -------------------------------------------------------------
def binary_to_message(binary_str: str) -> str:
    message     = ''
    end_marker  = '1111111111111110'   # Chuỗi kết thúc 16 bit

    # Duyệt từng nhóm 8 bit (1 byte = 1 ký tự)
    for i in range(0, len(binary_str) - 7, 8):
        byte = binary_str[i:i + 8]   # Lấy 8 bit tiếp theo

        # Chuyển 8 bit nhị phân sang số nguyên
        char_code = int(byte, 2)

        # Dừng nếu gặp ký tự NULL '\0' (ASCII 0)
        if char_code == 0:
            break

        # Chuyển sang ký tự và thêm vào kết quả
        message += chr(char_code)

        # Kiểm tra xem phần nhị phân vừa đọc có chứa marker kết thúc không
        # Marker nằm ngay sau phần message nên kiểm tra 16 bit tiếp theo
        next_16 = binary_str[i + 8: i + 24]
        if next_16 == end_marker:
            break   # Gặp chuỗi kết thúc → dừng lại

    return message


# -------------------------------------------------------------
# Hàm chính: mở ảnh và giải mã thông điệp ẩn
# -------------------------------------------------------------
def decode_image(encoded_image_path: str) -> None:
    # --- Bước 1: Mở ảnh đã mã hoá ---
    img = Image.open(encoded_image_path)

    # Đảm bảo ảnh ở chế độ RGB (3 kênh màu)
    img = img.convert('RGB')

    # --- Bước 2: Trích xuất chuỗi nhị phân từ LSB của các kênh RGB ---
    binary_str = extract_binary(img)

    # --- Bước 3: Chuyển chuỗi nhị phân thành văn bản ---
    message = binary_to_message(binary_str)

    # --- Bước 4: In kết quả ---
    print(f"Decoded message: {message}")


# =============================================================
#  Điểm vào chương trình
# =============================================================
if __name__ == '__main__':
    # Kiểm tra số lượng tham số dòng lệnh
    if len(sys.argv) < 2:
        print("Cách dùng: python decrypt.py <encoded_image_path>")
        print("Ví dụ    : python decrypt.py encoded_image.png")
        sys.exit(1)

    encoded_image_path = sys.argv[1]   # Đường dẫn ảnh đã mã hoá

    try:
        decode_image(encoded_image_path)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file ảnh '{encoded_image_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        sys.exit(1)
