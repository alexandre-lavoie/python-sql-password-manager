import secrets
import string
from Crypto.Cipher import AES
from pbkdf2 import PBKDF2
from base64 import b64encode, b64decode

class Password:
    key: bytes
    salt: str

    def __init__(self, master: str, salt: str, iterations: int=1000):
        self.salt = salt
        self.key = PBKDF2(master, salt=self.salt.encode(), iterations=iterations).read(32)

    @classmethod
    def generate_password(cls, length: int) -> str:
        characters = string.ascii_letters + string.digits

        password = ''.join(secrets.choice(characters) for _ in range(length))

        return password

    @classmethod
    def generate_salt(cls) -> str:
        return "SALT-" + cls.generate_password(32)

    def generate_challenge(self) -> str:
        return self.encrypt("CHALLENGE-" + self.generate_password(32))

    def validate_challenge(self, challenge: str) -> bool:
        try:
            challenge_decrypt = self.decrypt(challenge)

            return challenge_decrypt.startswith("CHALLENGE-")
        except Exception:
            return False

    def encrypt(self, password: str) -> str:
        cipher = AES.new(self.key, AES.MODE_EAX) 

        nonce = cipher.nonce

        ciphertext, tag = cipher.encrypt_and_digest(password.encode()) 

        add_nonce = ciphertext + nonce

        encoded_ciphertext = b64encode(add_nonce).decode()

        return encoded_ciphertext

    def decrypt(self, password: str) -> str:
        if len(password) % 4 != 0:
            password += '=' * (4 - len(password) % 4)

        convert = b64decode(password)

        nonce = convert[-16:]

        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)

        plaintext = cipher.decrypt(convert[:-16]).decode()

        return plaintext
