from utils.aes_cipher import AESCipher

from config_reader import config

class Token:
    def __init__(self, token: str, rate: float):
        self.token = token
        self.rate = rate

class UserToken:
    def __init__(self, token_id: int, api_token: str, worksnaps_user_id: int, rate: str, currency: str, user_id: int):
        self.token_id = token_id
        self.api_token = api_token
        self.worksnaps_user_id = worksnaps_user_id
        self.rate = rate
        self.currency = currency
        self.user_id = user_id
    
    def to_json(self):
        result = {
            'token_id': self.token_id,
            'api_token': self.api_token,
            'user_id': self.user_id,
            'worksnaps_user_id': self.worksnaps_user_id,
            'currency': self.currency,
            'rate': self.rate
        }
        return result

    def from_json(json):
        cipher = AESCipher(config.encryption.key)
        return UserToken(
            token_id=json['token_id'],
            api_token=cipher.decrypt(json['api_token']),
            worksnaps_user_id=json['worksnaps_user_id'],
            rate=cipher.decrypt(json['rate']) if json['rate'] else None,
            currency=json['currency'],
            user_id=json['user_id']
        )