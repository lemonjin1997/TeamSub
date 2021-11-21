import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Random import get_random_bytes
from hashlib import sha256


class crypto(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = sha256(key.encode()).digest()

    def encrypt(self, plaintext):
        # plaintext = self._pad(plaintext).encode()
        plaintext = str(plaintext).encode()
        cipher = AES.new(self.key, AES.MODE_GCM,
                         nonce=get_random_bytes(AES.block_size))

        ciphertext, tag = cipher.encrypt_and_digest(plaintext)

        json_k = ['nonce', 'ciphertext', 'tag']
        json_v = [b64encode(x).decode('utf-8')
                  for x in [cipher.nonce, ciphertext, tag]]
        ciphertext = json.dumps(dict(zip(json_k, json_v)))

        return ciphertext

    def decrypt(self, ciphertext):
        try:
            b64 = json.loads(ciphertext)
            print(b64)
            json_k = ['nonce', 'ciphertext', 'tag']
            jv = {k: b64decode(b64[k]) for k in json_k}
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=jv['nonce'])

            plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])

            return plaintext.decode()

        except ValueError as ve:
            print("Incorrect decryption")
            return False
        except KeyError as ke:
            print("Incorrect decryption")
            return False