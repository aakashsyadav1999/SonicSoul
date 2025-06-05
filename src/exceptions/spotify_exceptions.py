class SpotifyAuthError(Exception):
    def __init__(self, message: str, auth_url: str = None):
        self.message = message
        self.auth_url = auth_url
        super().__init__(self.message)
