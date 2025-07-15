class ServiceUnavailable(Exception):
    """Custom exception for when external services fail."""
    def __init__(self, service_name: str, status_code: int, detail: str):
        self.service_name = service_name
        self.status_code = status_code
        self.detail = detail