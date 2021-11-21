from itsdangerous import URLSafeTimedSerializer
import hashlib

class web_Token:

    # Constructor
    def __init__(self, email=None, token=None, key=None, salt=None):

        if email:
            self.email = email

        if token:
            self.token = token

        if key:
            self.key = key

        if salt:
            self.salt = salt

    # Generates the token with the given key, salt & email using the desired cryptograhic function
    def generate_confirmation_token(self) -> str:
        signer_args = {"key_derivation": "hmac", "digest_method": hashlib.sha512}
        serializer = URLSafeTimedSerializer(self.key, signer_kwargs=signer_args)
        return serializer.dumps(self.email, salt=self.salt)

    # Validates the token with the given key, salt & email is < 5min using the desired cryptograhic function
    def confirm_token(self) -> 'email or False':
        
        signer_args = {"key_derivation": "hmac", "digest_method": hashlib.sha512}
        serializer = URLSafeTimedSerializer(self.key, signer_kwargs=signer_args)

        try:
            email = serializer.loads(
                self.token,
                salt=self.salt,
                max_age=300
            )
        except:
            return False
        
        return email
