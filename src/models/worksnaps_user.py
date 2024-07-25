class WorksnapsUser: 
    def __init__(self, user_id: int, first_name: str, last_name: str, email: str, api_token: str):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.api_token = api_token

    def to_json(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'api_token': self.api_token
        }
    
    def from_json(json):
        return WorksnapsUser(
            json['user_id'],
            json['first_name'],
            json['last_name'],
            json['email'],
            json['api_token']
        )
