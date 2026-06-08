from flask import Flask, request, jsonify
from cipher.caesar import CaesarCipher
from cipher.vigenere import VigenereCipher
from cipher.railfence import RailFenceCipher
# FIX CHÍNH XÁC: Trỏ thẳng vào file playfair_cipher và gọi class PlayFairCipher
from cipher.playfair.playfair_cipher import PlayFairCipher
from cipher.ecc import ECCCipher

app = Flask(__name__)

# ── Helper: trả về JSON lỗi 400 ────────────────────────────────────────────
def bad_request(msg: str):
    return jsonify({"error": msg}), 400

# ══════════════════════════════════════════════════════════════════════════════
#  Caesar Cipher
#  Ràng buộc chuẩn:
#    • plain_text / cipher_text : không rỗng
#    • key : số nguyên trong [1, 25]
# ══════════════════════════════════════════════════════════════════════════════
caesar_cipher = CaesarCipher()

@app.route('/api/caesar/encrypt', methods=['POST'])
def caesar_encrypt():
    data       = request.get_json()
    plain_text = data.get('plain_text') or data.get('plaintext', '')
    key        = data.get('key')

    if not plain_text or not str(plain_text).strip():
        return bad_request("plain_text không được để trống.")
    try:
        k = int(key)
    except (TypeError, ValueError):
        return bad_request("key phải là số nguyên.")
    if not (1 <= k <= 25):
        return bad_request("key Caesar phải nằm trong khoảng [1, 25].")

    encrypted_text = caesar_cipher.encrypt_text(plain_text, k)
    return jsonify({'encrypted_message': encrypted_text, 'encrypted_text': encrypted_text})

@app.route('/api/caesar/decrypt', methods=['POST'])
def caesar_decrypt():
    data        = request.get_json()
    cipher_text = data.get('cipher_text', '')
    key         = data.get('key')

    if not cipher_text or not str(cipher_text).strip():
        return bad_request("cipher_text không được để trống.")
    try:
        k = int(key)
    except (TypeError, ValueError):
        return bad_request("key phải là số nguyên.")
    if not (1 <= k <= 25):
        return bad_request("key Caesar phải nằm trong khoảng [1, 25].")

    decrypted_text = caesar_cipher.decrypt_text(cipher_text, k)
    return jsonify({'decrypted_message': decrypted_text, 'decrypted_text': decrypted_text})

# ══════════════════════════════════════════════════════════════════════════════
#  Vigenère Cipher
#  Ràng buộc chuẩn:
#    • plain_text / cipher_text : không rỗng, phải chứa ít nhất 1 chữ cái
#    • key : không rỗng, chỉ gồm chữ cái A-Z, tối thiểu 2 ký tự
# ══════════════════════════════════════════════════════════════════════════════
vigenere_cipher = VigenereCipher()

@app.route('/api/vigenere/encrypt', methods=['POST'])
def vigenere_encrypt():
    data       = request.get_json()
    plain_text = data.get('plain_text', '')
    key        = data.get('key', '')

    if not plain_text or not str(plain_text).strip():
        return bad_request("plain_text không được để trống.")
    if not key or not str(key).strip():
        return bad_request("key không được để trống.")
    if not key.isalpha():
        return bad_request("key Vigenère chỉ được chứa các chữ cái (A-Z).")
    if len(key) < 2:
        return bad_request("key Vigenère phải có ít nhất 2 ký tự.")

    encrypted_text = vigenere_cipher.encrypt_text(plain_text, key)
    return jsonify({'encrypted_text': encrypted_text})

@app.route('/api/vigenere/decrypt', methods=['POST'])
def vigenere_decrypt():
    data        = request.get_json()
    cipher_text = data.get('cipher_text', '')
    key         = data.get('key', '')

    if not cipher_text or not str(cipher_text).strip():
        return bad_request("cipher_text không được để trống.")
    if not key or not str(key).strip():
        return bad_request("key không được để trống.")
    if not key.isalpha():
        return bad_request("key Vigenère chỉ được chứa các chữ cái (A-Z).")
    if len(key) < 2:
        return bad_request("key Vigenère phải có ít nhất 2 ký tự.")

    decrypted_text = vigenere_cipher.decrypt_text(cipher_text, key)
    return jsonify({'decrypted_text': decrypted_text})

# ══════════════════════════════════════════════════════════════════════════════
#  Rail Fence Cipher
#  Ràng buộc chuẩn:
#    • plain_text / cipher_text : không rỗng
#    • key (num_rails) : số nguyên >= 2, nhỏ hơn độ dài chuỗi
# ══════════════════════════════════════════════════════════════════════════════
railfence_cipher = RailFenceCipher()

@app.route('/api/railfence/encrypt', methods=['POST'])
def railfence_encrypt():
    data       = request.get_json()
    plain_text = data.get('plain_text', '')
    key        = data.get('key')

    if not plain_text or not str(plain_text).strip():
        return bad_request("plain_text không được để trống.")
    try:
        k = int(key)
    except (TypeError, ValueError):
        return bad_request("key (số ray) phải là số nguyên.")
    if k < 2:
        return bad_request("Số ray phải >= 2.")
    if k >= len(plain_text):
        return bad_request(f"Số ray ({k}) phải nhỏ hơn độ dài văn bản ({len(plain_text)}).")

    encrypted_text = railfence_cipher.rail_fence_encrypt(plain_text, k)
    return jsonify({'encrypted_text': encrypted_text})

@app.route('/api/railfence/decrypt', methods=['POST'])
def railfence_decrypt():
    data        = request.get_json()
    cipher_text = data.get('cipher_text', '')
    key         = data.get('key')

    if not cipher_text or not str(cipher_text).strip():
        return bad_request("cipher_text không được để trống.")
    try:
        k = int(key)
    except (TypeError, ValueError):
        return bad_request("key (số ray) phải là số nguyên.")
    if k < 2:
        return bad_request("Số ray phải >= 2.")
    if k >= len(cipher_text):
        return bad_request(f"Số ray ({k}) phải nhỏ hơn độ dài bản mã ({len(cipher_text)}).")

    decrypted_text = railfence_cipher.rail_fence_decrypt(cipher_text, k)
    return jsonify({'decrypted_text': decrypted_text})

# ══════════════════════════════════════════════════════════════════════════════
#  Playfair Cipher
#  Ràng buộc chuẩn:
#    • key  : chỉ gồm chữ cái A-Z, tối thiểu 2 ký tự khác nhau
#    • text : chỉ gồm chữ cái A-Z, tối thiểu 2 ký tự
#    • bản mã khi giải mã phải có độ dài chẵn
# ══════════════════════════════════════════════════════════════════════════════
playfair_cipher = PlayFairCipher()

@app.route('/api/playfair/creatematrix', methods=['POST'])
def playfair_creatematrix():
    data = request.json
    key  = data.get('key', '')
    if not key or not str(key).strip():
        return bad_request("key không được để trống.")
    if not key.replace(" ", "").isalpha():
        return bad_request("key Playfair chỉ được chứa các chữ cái (A-Z).")
    playfair_matrix = playfair_cipher.create_playfair_matrix(key)
    return jsonify({"playfair_matrix": playfair_matrix})

@app.route('/api/playfair/encrypt', methods=['POST'])
def playfair_encrypt():
    data       = request.get_json()
    plain_text = data.get('plain_text', '')
    key        = data.get('key', '')

    if not plain_text or not str(plain_text).strip():
        return bad_request("plain_text không được để trống.")
    if not key or not str(key).strip():
        return bad_request("key không được để trống.")
    if not key.replace(" ", "").isalpha():
        return bad_request("key Playfair chỉ được chứa các chữ cái (A-Z).")

    playfair_matrix = playfair_cipher.create_playfair_matrix(key)
    encrypted_text  = playfair_cipher.playfair_encrypt(plain_text, playfair_matrix)
    return jsonify({'encrypted_text': encrypted_text})

@app.route('/api/playfair/decrypt', methods=['POST'])
def playfair_decrypt():
    import re
    data        = request.get_json()
    cipher_text = data.get('cipher_text', '')
    key         = data.get('key', '')

    if not cipher_text or not str(cipher_text).strip():
        return bad_request("cipher_text không được để trống.")
    if not key or not str(key).strip():
        return bad_request("key không được để trống.")
    if not key.replace(" ", "").isalpha():
        return bad_request("key Playfair chỉ được chứa các chữ cái (A-Z).")
    ct_letters = re.sub(r'[^A-Za-z]', '', cipher_text)
    if len(ct_letters) % 2 != 0:
        return bad_request("Độ dài bản mã Playfair phải là số chẵn (mã hoá theo từng cặp ký tự).")

    playfair_matrix = playfair_cipher.create_playfair_matrix(key)
    decrypted_text  = playfair_cipher.playfair_decrypt(cipher_text, playfair_matrix)
    return jsonify({'decrypted_text': decrypted_text})

# ══════════════════════════════════════════════════════════════════════════════
#  ECC Cipher (secp256k1)
#  Ràng buộc chuẩn:
#    • private_key : hex 64 ký tự, giá trị trong [1, N-1]
#    • public_key  : hex 128 ký tự, điểm hợp lệ trên đường cong secp256k1
#    • message     : không rỗng
#    • signature   : định dạng r:s, mỗi phần hex 64 ký tự, r,s trong [1, N-1]
# ══════════════════════════════════════════════════════════════════════════════
ecc_cipher = ECCCipher()

@app.route('/api/ecc/generate_keys', methods=['GET'])
def ecc_generate_keys():
    keys = ecc_cipher.generate_key_pair()
    return jsonify(keys)

@app.route('/api/ecc/encrypt', methods=['POST'])
def ecc_encrypt():
    data       = request.get_json()
    plain_text = data.get('plain_text', '')
    public_key = data.get('public_key', '')

    if not plain_text or not str(plain_text).strip():
        return bad_request("plain_text không được để trống.")
    if not public_key or not str(public_key).strip():
        return bad_request("public_key không được để trống.")

    encrypted_text = ecc_cipher.encrypt(plain_text, public_key)
    if str(encrypted_text).startswith("Lỗi"):
        return bad_request(encrypted_text)
    return jsonify({'encrypted_text': encrypted_text})

@app.route('/api/ecc/decrypt', methods=['POST'])
def ecc_decrypt():
    data        = request.get_json()
    cipher_text = data.get('cipher_text', '')
    private_key = data.get('private_key', '')

    if not cipher_text or not str(cipher_text).strip():
        return bad_request("cipher_text không được để trống.")
    if not private_key or not str(private_key).strip():
        return bad_request("private_key không được để trống.")

    decrypted_text = ecc_cipher.decrypt(cipher_text, private_key)
    if str(decrypted_text).startswith("Lỗi"):
        return bad_request(decrypted_text)
    return jsonify({'decrypted_text': decrypted_text})

@app.route('/api/ecc/sign', methods=['POST'])
def ecc_sign():
    data        = request.get_json()
    message     = data.get('message', '')
    private_key = data.get('private_key', '')

    if not message or not str(message).strip():
        return bad_request("message không được để trống.")
    if not private_key or not str(private_key).strip():
        return bad_request("private_key không được để trống.")

    signature = ecc_cipher.sign(message, private_key)
    if str(signature).startswith("Lỗi"):
        return bad_request(signature)
    return jsonify({'signature': signature})

@app.route('/api/ecc/verify', methods=['POST'])
def ecc_verify():
    data       = request.get_json()
    message    = data.get('message', '')
    signature  = data.get('signature', '')
    public_key = data.get('public_key', '')

    if not message or not str(message).strip():
        return bad_request("message không được để trống.")
    if not signature or not str(signature).strip():
        return bad_request("signature không được để trống.")
    if not public_key or not str(public_key).strip():
        return bad_request("public_key không được để trống.")

    valid = ecc_cipher.verify(message, signature, public_key)
    return jsonify({'valid': valid})

# BỔ SUNG: Khởi chạy ứng dụng Flask Server
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)