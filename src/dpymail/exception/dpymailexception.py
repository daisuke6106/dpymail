class DPyMailException(Exception):
    """DPyMailの基本例外クラス
    """

    def __init__(self, message: str, org_exception: Exception = None):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
            org_exception (Exception, optional): 元例外情報. Defaults to None.
        """
        super().__init__(message)
        self.org_exception = org_exception


class MailServerConnectException(DPyMailException):
    """メールサーバ接続例外クラス
    """

    def __init__(self, message: str, org_exception: Exception = None):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
            org_exception (Exception, optional): 元例外情報. Defaults to None.
        """
        super().__init__(message)
        self.org_exception = org_exception


class MailSearchException(DPyMailException):
    """メール検索例外クラス
    """

    def __init__(self, message: str, org_exception: Exception = None):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
            org_exception (Exception, optional): 元例外情報. Defaults to None.
        """
        super().__init__(message)
        self.org_exception = org_exception


class MailLoadException(DPyMailException):
    """メールロード例外クラス
    """

    def __init__(self, message: str, org_exception: Exception = None):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
            org_exception (Exception, optional): 元例外情報. Defaults to None.
        """
        super().__init__(message)
        self.org_exception = org_exception


class MailMessageDataNotFoundException(DPyMailException):
    """メールメッセージデータ未検出例外クラス
    """

    def __init__(self, message: str):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
            org_exception (Exception, optional): 元例外情報. Defaults to None.
        """
        super().__init__(message)


class MailMonitoringTimeoutException(DPyMailException):
    """メール監視タイムアウト例外クラス
    """

    def __init__(self, message: str):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
            org_exception (Exception, optional): 元例外情報. Defaults to None.
        """
        super().__init__(message)
