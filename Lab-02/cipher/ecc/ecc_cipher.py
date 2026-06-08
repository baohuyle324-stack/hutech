import hashlib
import random

# secp256k1 parameters
P = 2**256 - 2**32 - 977
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def ext_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = ext_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inv(n, p):
    n = n % p
    g, x, y = ext_gcd(n, p)
    if g != 1:
        raise ValueError("Không có nghịch đảo modulo")
    return x % p

def ec_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 != y2:
        return None
    if x1 == x2:
        slope = (3 * x1 * x1 + A) * mod_inv(2 * y1, P) % P
    else:
        slope = (y2 - y1) * mod_inv(x2 - x1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)

def ec_mul(k, p):
    result = None
    addend = p
    while k:
        if k & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        k >>= 1
    return result

class ECCCipher:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Validate private key:
    #   - Chuỗi hex 64 ký tự (256-bit)
    #   - Giá trị phải nằm trong [1, N-1]
    # ------------------------------------------------------------------
    def _validate_private_key(self, private_key_hex: str) -> int:
        if not private_key_hex or not private_key_hex.strip():
            raise ValueError("Private key không được để trống.")
        pk = private_key_hex.strip()
        if len(pk) != 64:
            raise ValueError("Private key phải là chuỗi hex 64 ký tự (256-bit).")
        try:
            d = int(pk, 16)
        except ValueError:
            raise ValueError("Private key phải là chuỗi hex hợp lệ (0-9, a-f).")
        if not (1 <= d <= N - 1):
            raise ValueError("Private key phải nằm trong khoảng [1, N-1].")
        return d

    # ------------------------------------------------------------------
    # Validate public key:
    #   - Chuỗi hex 128 ký tự (2 toạ độ x, y mỗi cái 64 hex)
    #   - Điểm (x, y) phải nằm trên đường cong secp256k1: y² ≡ x³+7 (mod P)
    # ------------------------------------------------------------------
    def _validate_public_key(self, public_key_hex: str):
        if not public_key_hex or not public_key_hex.strip():
            raise ValueError("Public key không được để trống.")
        pk = public_key_hex.strip()
        if len(pk) != 128:
            raise ValueError("Public key phải là chuỗi hex 128 ký tự (2 × 64-bit toạ độ).")
        try:
            Qx = int(pk[:64], 16)
            Qy = int(pk[64:], 16)
        except ValueError:
            raise ValueError("Public key phải là chuỗi hex hợp lệ (0-9, a-f).")
        # Kiểm tra điểm nằm trên đường cong y² = x³ + 7 (mod P)
        if (Qy * Qy - Qx * Qx * Qx - B) % P != 0:
            raise ValueError("Public key không phải là điểm hợp lệ trên đường cong secp256k1.")
        return (Qx, Qy)

    # ------------------------------------------------------------------
    # Validate message: không rỗng
    # ------------------------------------------------------------------
    def _validate_message(self, message: str) -> None:
        if not message or not message.strip():
            raise ValueError("Thông điệp (message) không được để trống.")

    # ------------------------------------------------------------------
    # Validate signature: định dạng r:s, mỗi phần là hex 64 ký tự,
    #   r và s phải nằm trong [1, N-1]
    # ------------------------------------------------------------------
    def _validate_signature(self, signature: str):
        if not signature or not signature.strip():
            raise ValueError("Chữ ký không được để trống.")
        sig = signature.strip()
        if ":" not in sig:
            raise ValueError("Định dạng chữ ký không hợp lệ. Phải là 'r_hex:s_hex'.")
        r_hex, s_hex = sig.split(":", 1)
        if len(r_hex) != 64 or len(s_hex) != 64:
            raise ValueError("Chữ ký không hợp lệ: r và s phải là chuỗi hex 64 ký tự.")
        try:
            r = int(r_hex, 16)
            s = int(s_hex, 16)
        except ValueError:
            raise ValueError("Chữ ký không hợp lệ: r và s phải là chuỗi hex hợp lệ.")
        if not (1 <= r < N and 1 <= s < N):
            raise ValueError("Chữ ký không hợp lệ: r và s phải nằm trong [1, N-1].")
        return r, s

    def generate_key_pair(self):
        d = random.randint(1, N - 1)
        Q = ec_mul(d, G)
        private_key = f"{d:064x}"
        public_key  = f"{Q[0]:064x}{Q[1]:064x}"
        return {"private_key": private_key, "public_key": public_key}

    def encrypt(self, plain_text: str, public_key_hex: str) -> str:
        try:
            self._validate_message(plain_text)
            Q = self._validate_public_key(public_key_hex)

            k = random.randint(1, N - 1)
            R = ec_mul(k, G)
            S = ec_mul(k, Q)
            if S is None:
                return "Lỗi: Không tạo được điểm chung (Shared Secret)"

            shared_x = f"{S[0]:064x}".encode('utf-8')
            sym_key = hashlib.sha256(shared_x).digest()

            plaintext_bytes = plain_text.encode('utf-8')
            length = len(plaintext_bytes)
            
            keystream = b""
            counter = 0
            while len(keystream) < length:
                keystream += hashlib.sha256(sym_key + str(counter).encode('utf-8')).digest()
                counter += 1
            keystream = keystream[:length]

            ciphertext_bytes = bytes(a ^ b for a, b in zip(plaintext_bytes, keystream))
            
            Rx_hex = f"{R[0]:064x}"
            Ry_hex = f"{R[1]:064x}"
            ciphertext_hex = ciphertext_bytes.hex()
            
            return f"{Rx_hex}{Ry_hex}:{ciphertext_hex}"
        except Exception as e:
            return f"Lỗi mã hóa: {str(e)}"

    def decrypt(self, cipher_text_formatted: str, private_key_hex: str) -> str:
        try:
            # Validate private key theo chuẩn secp256k1
            d = self._validate_private_key(private_key_hex)

            # Validate định dạng bản mã: phải có dạng <128-hex>:<hex>
            if not cipher_text_formatted or not cipher_text_formatted.strip():
                return "Lỗi: Bản mã không được để trống."
            ctf = cipher_text_formatted.strip()
            if ":" not in ctf:
                return "Lỗi: Định dạng bản mã không hợp lệ (phải chứa dấu ':')."
            ephemeral_key_hex, ciphertext_hex = ctf.split(":", 1)
            if len(ephemeral_key_hex) != 128:
                return "Lỗi: Phần khóa tạm thời phải dài đúng 128 ký tự hex."
            try:
                bytes.fromhex(ciphertext_hex)
            except ValueError:
                return "Lỗi: Phần bản mã phải là chuỗi hex hợp lệ."

            Rx = int(ephemeral_key_hex[:64], 16)
            Ry = int(ephemeral_key_hex[64:], 16)
            R  = (Rx, Ry)

            S = ec_mul(d, R)
            if S is None:
                return "Lỗi: Không tạo được điểm chung (Shared Secret)."

            shared_x = f"{S[0]:064x}".encode('utf-8')
            sym_key  = hashlib.sha256(shared_x).digest()

            ciphertext_bytes = bytes.fromhex(ciphertext_hex)
            length           = len(ciphertext_bytes)

            keystream = b""
            counter   = 0
            while len(keystream) < length:
                keystream += hashlib.sha256(sym_key + str(counter).encode('utf-8')).digest()
                counter   += 1
            keystream = keystream[:length]

            plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext_bytes, keystream))
            return plaintext_bytes.decode('utf-8')
        except ValueError as e:
            return f"Lỗi: {e}"
        except Exception as e:
            return f"Lỗi giải mã: {str(e)}"

    def sign(self, message: str, private_key_hex: str) -> str:
        try:
            self._validate_message(message)
            d = self._validate_private_key(private_key_hex)
            h = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
            while True:
                k = random.randint(1, N - 1)
                R = ec_mul(k, G)
                if R is None:
                    continue
                r = R[0] % N
                if r == 0:
                    continue
                s = mod_inv(k, N) * (h + r * d) % N
                if s == 0:
                    continue
                break
            return f"{r:064x}:{s:064x}"
        except Exception as e:
            return f"Lỗi tạo chữ ký: {str(e)}"

    def verify(self, message: str, signature_formatted: str, public_key_hex: str) -> bool:
        try:
            self._validate_message(message)
            Q      = self._validate_public_key(public_key_hex)
            r, s   = self._validate_signature(signature_formatted)

            h      = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
            w      = mod_inv(s, N)
            u1     = h * w % N
            u2     = r * w % N

            P_point = ec_add(ec_mul(u1, G), ec_mul(u2, Q))
            if P_point is None:
                return False

            return (P_point[0] % N) == r
        except Exception:
            return False
