import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from app.config import settings
import os


def _get_key() -> bytes:
    return bytes.fromhex(settings.AES_KEY)


def encrypt(value: str) -> str:
    key = _get_key()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(value.encode()) + encryptor.finalize()
    return base64.b64encode(iv + encrypted).decode()


def decrypt(value: str) -> str:
    key = _get_key()
    raw = base64.b64decode(value.encode())
    iv = raw[:16]
    encrypted = raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return (decryptor.update(encrypted) + decryptor.finalize()).decode()
