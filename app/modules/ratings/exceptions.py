class RatingNotFoundException(Exception):
    """Exception raised when a rating is not found."""

    def __init__(self, message="Rating not found"):
        self.message = message
        super().__init__(self.message)
