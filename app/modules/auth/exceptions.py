class TokenAlreadyExist(Exception):
    def __init__(self, msg = 'Token Already Exists!'):
        self.msg = msg

    def __str__(self):
        return self.msg
    
class TokenDoesNotExists(Exception):
    def __init__(self, msg='Token Does Not Exists!'):
        self.msg = msg

    def __str__(self):
        return self.msg