import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = base64.b64decode(key)

    def encrypt(self, raw):
        raw = pad(raw.encode(), self.bs)
        cipher = AES.new(self.key, AES.MODE_ECB)
        encrypted = cipher.encrypt(raw)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        decrypted = cipher.decrypt(enc)
        return unpad(decrypted, self.bs).decode('utf-8')
