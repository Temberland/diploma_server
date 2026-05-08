from app.services.encryption import encrypt, decrypt


def test_encrypt_decrypt():
    original = "12345.67"
    encrypted = encrypt(original)
    assert encrypted != original
    assert decrypt(encrypted) == original


def test_encrypt_different_each_time():
    """Каждый раз разный результат из-за случайного IV"""
    value = "1000.00"
    enc1 = encrypt(value)
    enc2 = encrypt(value)
    assert enc1 != enc2  # разный IV
    assert decrypt(enc1) == decrypt(enc2)  # но расшифровываются одинаково


def test_encrypt_zero():
    assert decrypt(encrypt("0.00")) == "0.00"


def test_encrypt_large_number():
    value = "9999999.99"
    assert decrypt(encrypt(value)) == value


def test_encrypt_negative():
    value = "-500.00"
    assert decrypt(encrypt(value)) == value
