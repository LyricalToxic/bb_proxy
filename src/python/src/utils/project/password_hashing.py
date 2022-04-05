from cryptocode import encrypt, decrypt

from settings import SALT_KEY


def hash_password(password):
    key = encrypt(password, SALT_KEY)
    return key


def decrypt_password(password):
    key = decrypt(password, SALT_KEY)
    return key


def verify_password(password_hash, password_to_check):
    return hash_password(password_to_check) == password_hash
