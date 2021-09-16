from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from emily_password.share.utils import path
from emily_password.share.constants import *


def generate_key(password):
    try:
        with open(path(password_dir, config["salt_file_name"]), "rb") as f:
            salt = f.read()

    except FileNotFoundError:
        salt = b""

    kdf = PBKDF2HMAC(algorithm=hash_algorithm, length=hash_length, salt=salt, iterations=hash_iterations)

    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encryptor(password: str, pw: list[Password]) -> None:
    key = generate_key(password)
    with open(path(password_dir, config.encrypted_file()), "wb+") as f:
        f.write(Fernet(key).encrypt(Password.dump_list(pw).encode()))


def unlock_with_password(password: str) -> list | bool:
    key = generate_key(password)

    try:
        content = Fernet(key).decrypt(config.encrypted_file_contents()).decode()
        return [Password(**item) for item in json.loads(content)]
    except (InvalidToken, TypeError):
        return False

def generate_salt():
    if os.path.exists((old_file := path(config.salt_file()))):
        f, ext = os.path.splitext(old_file)
        f = f + f"({str(int(time.time()))})"
        os.rename(old_file, f + ext)

    with open(old_file, "wb") as f:
        f.write(os.urandom(salt_length))
