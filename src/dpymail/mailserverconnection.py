from abc import ABC, abstractmethod
import imaplib
import socket

from mail import Mail, IMAPMail
from exception.dpymailexception import MailServerConnectException, MailLoadException


class MailServerConnection(ABC):
    """メールサーバとの接続を表す抽象クラス
    """

    @abstractmethod
    def create_checkpoint(self) -> "MailCheckPoint":
        pass


class IMAPSSLConnection(MailServerConnection):
    """IMAPメールサーバとの接続を表すクラス

    Attributes:
        imap (IMAP4_SSL): IMAP接続インスタンス
    """

    def __init__(self, host: str, port: int, username: str, password: str, timeout: float = 10, mailbox: str = "INBOX"):
        """コンストラクタ

        引数に指定されたIMAPサーバ接続情報を元にIMAP接続を実施し、接続できた場合その接続を保持する。

        Args:
            host (str): IMAPサーバホスト名
            port (int): IMAPサーバポート番号
            username (str): IMAPサーバユーザ名
            password (str): IMAPサーバパスワード
            timeout (float, optional): 接続タイムアウト時間. Defaults to 10.
            mailbox (str): 参照先メールボックス. Detaults to "INBOX"

        Raises:
            MailServerConnectException: IMAPサーバへの接続に失敗した場合
        """
        try:
            self.imap = imaplib.IMAP4_SSL(
                host=host, port=port, timeout=timeout)
        except socket.gaierror as e:
            raise MailServerConnectException(
                f"Fail to Access Server. host={host}, port={port}, timeout={timeout}", e)
        try:
            self.imap.login(username, password)
        except imaplib.IMAP4.error as e:
            raise MailServerConnectException(
                f"Fail to Login. username={username}, password=**********", e)
        self.imap.select(mailbox)

    def lastest_mail(self) -> Mail:
        """メールボックスから最も新しいメールを取得する

        メールが存在しない場合Noneを返却する。

        Returns:
            Mail: 最も新しいメール
        """
        lastestmail = self.lastest_mail_by_count(1)
        if lastestmail:
            return lastestmail
        else:
            return None

    def lastest_mail_by_count(self, getmailcount: int) -> list[Mail]:
        """メールボックスから最も新しいメールを指定された数取得する

        メールが存在しない場合空のリストを返却する。

        Args:
            getmailcount (int): 取得対象のメール数

        Returns:
            list[Mail]: 最も新しいメール一覧
        """
        uid_list = self._search_all()
        # メールがない場合、Noneを返却
        if uid_list is None:
            return []

        lastest_uid_list = None
        # 全メールが取得対象個数以下の場合、全量を返却
        if len(uid_list) <= getmailcount:
            lastest_uid_list = uid_list

        # 取得対象個数を最後から切り出して返却
        else:
            lastest_uid_list = uid_list[(getmailcount * -1):]

        # UIDからメール情報をロードし、メールインスタンスへ変換し返却
        return [self.__load_mail_by_uid(uid) for uid in lastest_uid_list]

    def _search_all(self) -> list[bytes]:
        """メールボックスから全メールのUIDを取得する

        Raises:
            MailServerConnectException: メールボックスのメール検索に失敗した場合

        Returns:
            list[bytes]: 全メールのUIDを取得する
        """
        return self._search("ALL")

    def _search_unseen(self) -> list[bytes]:
        """メールボックスから全未読メールのUIDを取得する

        Raises:
            MailServerConnectException: メールボックスのメール検索に失敗した場合

        Returns:
            list[bytes]: 全未読メールのUIDを取得する
        """
        return self._search("UNSEEN")

    def _search(self, criterion: str) -> list[bytes]:
        """メールボックスから指定のメールのUIDを取得する

        Args:
            criterion (str): 検索条件

        Raises:
            MailServerConnectException: メールボックスのメール検索に失敗した場合

        Returns:
            list[bytes]: 検索条件に合致したメールのUID一覧
        """
        # 指定の基準でメールを検索
        # msg_numsはlist、要素[0]にはb'1 2 3 4 5 6 7 8...'が格納されている
        status, uid_list = self.imap.search(None, criterion)
        if status != "OK":
            raise MailServerConnectException(
                f"Fail to Mail Search. criterion={criterion}, status={status}")

        # メールがない場合、Noneを返却
        if not uid_list[0]:
            return None

        # スペース区切りでスプリット
        return uid_list[0].split()

    def __load_mail_by_uid(self, uid: bytes) -> Mail:
        """UIDを元にメールボックスからメール情報をロードし、メールインスタンスとして返却するｊ

        Args:
            uid (bytes): ロード対象のメールのUID

        Raises:
            MailLoadException: メール読み込みに失敗した場合

        Returns:
            Mail: メールインスタンス
        """
        status, msg_data = self.imap.fetch(uid, "(RFC822)")
        if status != "OK":
            raise MailLoadException(
                f"Fail to load Mail. status={status}, uid={uid}")
        return self._create_lmap_mail_instalce(uid=uid, msg_data=msg_data)

    def _create_lmap_mail_instalce(self, uid: bytes, msg_data) -> IMAPMail:
        """メールインスタンスを生成して返却

        引数にしていられたUID、ロードしたメール情報からメールインスタンスを生成し返却

        Args:
            uid (bytes): メールUID
            msg_data: ロードしたメール情報

        Returns:
            IMAPMail: メールインスタンス
        """
        return IMAPMail(uid=uid, msg_data=msg_data, mailserveronnection=self)

    def create_checkpoint(self) -> "MailCheckPoint":
        pass


IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
USERNAME = "daisuke6106@gmail.com"
APP_PASSWORD = "obrjizfnqbitczcn"
mailserverconnection = IMAPSSLConnection(
    IMAP_SERVER, IMAP_PORT, USERNAME, APP_PASSWORD)
mailserverconnection.lastest_mail_by_count(10)
