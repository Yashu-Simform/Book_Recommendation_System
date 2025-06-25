class TokenAlreadyExist(Exception):
    def __init__(self, msg = 'Token Already Exists!'):
        self.msg = msg

    def __str__(self):
        return self.msg
    
class TokenNotFound(Exception):
    def __init__(self, msg='Token Does Not Exists!'):
        self.msg = msg

    def __str__(self):
        return self.msg
    
class InvalidToken(Exception):
    def __init__(self, msg='Token is invalid!'):
        self.msg = msg

    def __str__(self):
        return self.msg