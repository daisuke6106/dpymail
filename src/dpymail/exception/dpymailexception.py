import poplib

class DPyMailException(Exception):
    def __init__(self, message:str, org_exception:Exception = None):
        super().__init__(message)
        self.org_exception = org_exception

class MailServerConnectException(DPyMailException):
    def __init__(self, message:str, org_exception:Exception = None):
        super().__init__(message)
        self.org_exception = org_exception

class MailSearchException(DPyMailException):
    def __init__(self, message:str, org_exception:Exception = None):
        super().__init__(message)
        self.org_exception = org_exception

class MailLoadException(DPyMailException):
    def __init__(self, message:str, org_exception:Exception = None):
        super().__init__(message)
        self.org_exception = org_exception