import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os

def decrypt_system_prompt():
    load_dotenv(".env.local")
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        raise ValueError("ENCRYPTION_KEY not found in environment variables")
    with open("system_prompt_encrypted.txt", "r", encoding='utf-8') as f:
        encrypted_data = f.read().strip()
    try:
        try:
            key_str = encryption_key.replace("-", "")
            key_bytes = bytes.fromhex(key_str[:64])
            if len(key_bytes) < 32:
                key_bytes = key_bytes.ljust(32, b'\x00')
            encrypted_bytes = base64.b64decode(encrypted_data)
            if encrypted_bytes.startswith(b"Salted__"):
                salt = encrypted_bytes[8:16]
                encrypted_content = encrypted_bytes[16:]
                import hashlib
                def derive_key_iv(password, salt, key_len=32, iv_len=16):
                    d = d_i = b''
                    while len(d) < (key_len + iv_len):
                        d_i = hashlib.md5(d_i + password + salt).digest()
                        d += d_i
                    return d[:key_len], d[key_len:key_len+iv_len]
                key, iv = derive_key_iv(encryption_key.encode('utf-8'), salt)
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_padded = decryptor.update(encrypted_content) + decryptor.finalize()
                padding_length = decrypted_padded[-1]
                if padding_length <= 16:
                    decrypted_text = decrypted_padded[:-padding_length].decode('utf-8')
                    return decrypted_text
        except Exception as e1:
            print(f"Approach 1 failed: {e1}")
        try:
            password = encryption_key.encode('utf-8')
            encrypted_bytes = base64.b64decode(encrypted_data)
            if encrypted_bytes.startswith(b"Salted__"):
                salt = encrypted_bytes[8:16]
                encrypted_content = encrypted_bytes[16:]
                import hashlib
                key_iv = hashlib.pbkdf2_hmac('sha256', password, salt, 10000, 48)  # 32 + 16
                key = key_iv[:32]
                iv = key_iv[32:48]
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_padded = decryptor.update(encrypted_content) + decryptor.finalize()
                padding_length = decrypted_padded[-1]
                if padding_length <= 16:
                    decrypted_text = decrypted_padded[:-padding_length].decode('utf-8')
                    return decrypted_text
        except Exception as e2:
            print(f"Approach 2 failed: {e2}")
        raise ValueError("All decryption approaches failed")
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None