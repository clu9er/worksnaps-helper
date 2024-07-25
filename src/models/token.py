class Token:
    def __init__(self, token: str, rate: float):
        self.token = token
        self.rate = rate

class UserToken:
    def __init__(self, token_id: int, api_token: str, worksnaps_user_id: int, rate: float, currency: str, user_id: int):
        self.token_id = token_id
        self.api_token = api_token
        self.worksnaps_user_id = worksnaps_user_id
        self.rate = rate
        self.currency = currency
        self.user_id = user_id
    
    def to_json(self):
        return {
            'token_id': self.token_id,
            'api_token': self.api_token,
            'user_id': self.worksnaps_user_id,
            'rate': self.rate,
            'currency': self.currency,
            'user_id': self.user_id
        }
    
    def from_json(json):
        return UserToken(
            json['token_id'],
            json['api_token'],
            json['user_id'],
            json['rate'],
            json['currency'],
            json['user_id']
        )