# =============================================================
#  encrypt.py - Giấu tin trong ảnh bằng phương pháp LSB
#  Cách dùng: python encrypt.py <image_path> <message>
#  Ví dụ   : python encrypt.py image.jpg thongdiep
# =============================================================

import sys
from PIL import Image


# -------------------------------------------------------------
# Hàm chuyển chuỗi văn bản sang chuỗi nhị phân
# Mỗi ký tự được mã hoá thành 8 bit (ASCII)
# Thêm chuỗi kết thúc "1111111111111110" (16 bit) vào cuối
# để decrypt.py biết điểm dừng
# -------------------------------------------------------------
def message_to_binary(message: str) -> str:
    # Chuyển từng ký tự sang 8-bit nhị phân, nối lại thành 1 chuỗi
    binary = ''.join(format(ord(ch), '08b') for ch in message)

    # Chuỗi kết thúc (delimiter) – 16 bit toàn 1 trừ bit cuối
    end_marker = '1111111111111110'

    return binary + end_marker


# -------------------------------------------------------------
# Hàm nhúng chuỗi nhị phân vào ảnh bằng kỹ thuật LSB
#   - Duyệt từng pixel theo thứ tự từ trên xuống, trái sang phải
#   - Với mỗi pixel, thay bit cuối (LSB) của R, G, B lần lượt
#     bằng từng bit trong chuỗi nhị phân cần giấu
# -------------------------------------------------------------
def encode_image(image_path: str, message: str) -> None:
    # --- Bước 1: Mở ảnh gốc ---
    img = Image.open(image_path)

    # Chuyển về chế độ RGB để đảm bảo có đủ 3 kênh màu
    img = img.convert('RGB')

    # Lấy kích thước ảnh
    width, height = img.size

    # --- Bước 2: Chuyển message sang nhị phân (có thêm marker kết thúc) ---
    binary_message = message_to_binary(message)
    total_bits     = len(binary_message)

    # --- Bước 3: Kiểm tra ảnh có đủ dung lượng không ---
    # Mỗi pixel chứa 3 kênh (R, G, B), mỗi kênh giấu 1 bit
    max_bits = width * height * 3
    if total_bits > max_bits:
        raise ValueError(
            f"Ảnh quá nhỏ! Cần {total_bits} bit nhưng ảnh chỉ chứa được {max_bits} bit."
        )

    # --- Bước 4: Nhúng từng bit vào LSB của kênh màu ---
    bit_index = 0   # Chỉ số bit đang được giấu trong binary_message
    pixels    = list(img.getdata())   # Lấy toàn bộ danh sách pixel (R, G, B)
    new_pixels = []

    for pixel in pixels:
        r, g, b = pixel

        # Thay LSB của kênh R
        if bit_index < total_bits:
            # Xoá LSB cũ bằng  AND 0b11111110 (& ~1)
            # Sau đó đặt bit mới bằng OR với giá trị bit cần giấu
            r = (r & ~1) | int(binary_message[bit_index])
            bit_index += 1

        # Thay LSB của kênh G
        if bit_index < total_bits:
            g = (g & ~1) | int(binary_message[bit_index])
            bit_index += 1

        # Thay LSB của kênh B
        if bit_index < total_bits:
            b = (b & ~1) | int(binary_message[bit_index])
            bit_index += 1

        new_pixels.append((r, g, b))

        # Dừng sớm khi đã giấu hết tất cả các bit
        if bit_index >= total_bits:
            # Giữ nguyên các pixel còn lại
            new_pixels.extend(pixels[len(new_pixels):])
            break

    # --- Bước 5: Tạo ảnh mới từ danh sách pixel đã chỉnh sửa ---
    encoded_img = Image.new('RGB', img.size)
    encoded_img.putdata(new_pixels)

    # --- Bước 6: Lưu ảnh kết quả ---
    output_path = 'encoded_image.png'
    encoded_img.save(output_path)

    print(f"Steganography complete. Encoded image saved as {output_path}")


# =============================================================
#  Điểm vào chương trình
# =============================================================
if __name__ == '__main__':
    # Kiểm tra số lượng tham số dòng lệnh
    if len(sys.argv) < 3:
        print("Cách dùng: python encrypt.py <image_path> <message>")
        print("Ví dụ    : python encrypt.py image.jpg thongdiep")
        sys.exit(1)

    image_path = sys.argv[1]      # Đường dẫn ảnh gốc
    message    = sys.argv[2]      # Thông điệp cần giấu

    try:
        encode_image(image_path, message)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file ảnh '{image_path}'")
        sys.exit(1)
    except ValueError as e:
        print(f"Lỗi: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        sys.exit(1)
