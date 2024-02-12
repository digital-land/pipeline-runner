from datetime import datetime
from application.services.json_schema_svc import ErrorMap


class URLException(Exception):
    """Exception raised when URL fetch function fails.
    Attributes: response
    """

    def __init__(self, log={}):
        self.log = log
        super().__init__(self.log)
        self.load(log)

    def load(self, log):
        self.detail = {
            "errCode": str(log["status"]),
            "errType": ErrorMap.USER_ERROR.value,
            "errMsg": str(log["message"]),
            "errTime": str(datetime.now()),
        }
