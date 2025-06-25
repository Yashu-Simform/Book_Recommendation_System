class UserAlreadyExistsException(Exception):
    """Exception raised when a user already exists."""

    def __init__(self, message="User already exists."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"UserAlreadyExistsException: {self.message}"

class UserNotFound(Exception):
    def __init__(self, msg='User Not Found!'):
        self.msg = msg

    def __str__(self):
        return self.msg
    
class UniqueIdNotProvided(Exception):
    def __init__(self, msg = 'No Unique ID provided to get the User.'):
        self.msg = msg

    def __str__(self):
        return self.msg