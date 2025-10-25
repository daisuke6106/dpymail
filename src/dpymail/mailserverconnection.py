from abc import ABC, abstractmethod
import imaplib
import socket

from mail import Mail, IMAPMail
from exception.dpymailexception import MailServerConnectException, MailLoadException, MailMonitoringTimeoutException, MailMessageDataNotFoundException


class MailServerConnection(ABC):
    """メールサーバとの接続を表す抽象クラス
    """

    def create_checkpoint(self) -> "MailCheckPoint":
        """メールサーバのチェックポイントを作成する

        Returns:
            MailCheckPoint: チェックポイントインスタンス
        """
        lastest_mail = self.lastest_mail()
        return MailCheckPoint(self, lastest_mail)

    @abstractmethod
    def lastest_mail(self) -> Mail:
        """メールボックスから最も新しいメールを取得する

        メールが存在しない場合Noneを返却する。

        Returns:
            Mail: 最も新しいメール
        """
        pass

    @abstractmethod
    def lastest_mail_by_count(self, getmailcount: int) -> list[Mail]:
        """メールボックスから最も新しいメールを指定された数取得する

        メールが存在しない場合空のリストを返却する。

        Args:
            getmailcount (int): 取得対象のメール数

        Returns:
            list[Mail]: 最も新しいメール一覧
        """
        pass

    @abstractmethod
    def lastest_mail_over_than_arg_mail(self, mail: Mail) -> list[Mail]:
        """メールボックスから指定されたメールよりも新しいメールを取得する

        メールが存在しない場合空のリストを返却する。

        Args:
            mail (Mail): 基準メール

        Returns:
            list[Mail]: 指定されたメールよりも新しいメール一覧
        """
        pass

    @abstractmethod
    def create_new_mail_server_connection(self) -> "MailServerConnection":
        """新しいメールサーバコネクションを作成する

        Returns:
            MailServerConnection: 新しいメールサーバコネクションインスタンス
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """メールサーバコネクションを切断する
        """
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
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._timeout = timeout
        self._mailbox = mailbox

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
            return lastestmail[0]
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

    def lastest_mail_over_than_arg_mail(self, mail: Mail) -> list[Mail]:
        """メールボックスから指定されたメールよりも新しいメールを取得する

        メールが存在しない場合空のリストを返却する
        Args:
            mail (Mail): 基準メール

        Returns:
            list[Mail]: 指定されたメールよりも新しいメール一覧
        """
        uid_list = self._search_over_than_uid(mail._uid)
        # メールがない場合、Noneを返却
        if uid_list is None:
            return []

        # UIDからメール情報をロードし、メールインスタンスへ変換し返却
        mails = []
        for uid in uid_list:
            try:
                mails.append(self.__load_mail_by_uid(uid))
            except MailMessageDataNotFoundException:
                # UIDに該当するメールデータが存在しない場合はその時点でスキップ
                break
        return mails

    def create_new_mail_server_connection(self) -> "MailServerConnection":
        """新しいメールサーバコネクションを作成する

        Returns:
            MailServerConnection: 新しいメールサーバコネクションインスタンス
        """
        return self.__class__(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            timeout=self._timeout,
            mailbox=self._mailbox
        )

    def disconnect(self) -> None:
        """メールサーバコネクションを切断する
        """
        try:
            self.imap.close()
            self.imap.logout()
        except Exception:
            pass

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

    def _search_over_than_uid(self, uid: bytes) -> list[bytes]:
        """メールボックスから指定UIDよりも新しいメールのUIDを取得する

        Args:
            uid (bytes): 基準UID

        Raises:
            MailServerConnectException: メールボックスのメール検索に失敗した場合

        Returns:
            list[bytes]: 指定UIDよりも新しいメールのUID一覧
        """
        return self._search_by_uid(f"{int(uid)+1}:*")

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

    def _search_by_uid(self, criterion: str) -> list[bytes]:
        """メールボックスから指定UIDのメールを取得する

        Args:
            criterion (str): 検索条件

        Raises:
            MailServerConnectException: メールボックスのメール検索に失敗した場合

        Returns:
            list[bytes]: 検索条件に合致したメールのUID一覧
        """
        # 指定の基準でメールを検索
        # msg_numsはlist、要素[0]にはb'1 2 3 4 5 6 7 8...'が格納されている
        status, uid_list = self.imap.uid('search', None, "UID", criterion)
        if status != "OK":
            raise MailServerConnectException(
                f"Fail to Mail Search by UID. criterion={criterion}, status={status}")

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
        status, msg_data = self.imap.fetch(uid, "(RFC822 INTERNALDATE)")
        if status != "OK":
            raise MailLoadException(
                f"Fail to load Mail. status={status}, uid={uid}")
        # UIDに該当するメールデータが存在しない場合、例外を送出
        # Gmailの場合、最新のメールUID+1を指定してfetchした場合、statusはOKとなりmsg_dataは空になることが判明したため
        # そのための考慮。
        if not msg_data or msg_data[0] is None:
            raise MailMessageDataNotFoundException(
                f"Mail Message Data Not Found. uid={uid}")
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


class MailCheckPoint:
    """メールサーバのチェックポイントを表すクラス
    """

    def __init__(self, mailserverconnection: MailServerConnection, checkpoint_mail: Mail):
        """コンストラクタ

        メールサーバコネクションとチェックポイントメールを元にチェックポイントインスタンスを生成する

        Args:
            mailserverconnection (MailServerConnection): メールサーバコネクション
            checkpoint_mail (Mail): チェックポイントメール
        """
        self._mailserverconnection = mailserverconnection
        self._checkpoint_mail = checkpoint_mail

    def get_checkpoint_mail(self) -> Mail:
        """チェックポイントメールを取得する

        Returns:
            Mail: チェックポイントメール
        """
        return self._checkpoint_mail

    def get_mailserver_connection(self) -> MailServerConnection:
        """メールサーバコネクションを取得する

        Returns:
            MailServerConnection: メールサーバコネクション
        """
        return self._mailserverconnection

    def get_mails_over_than_checkpoint(self) -> list[Mail]:
        """チェックポイントメールよりも新しいメールを取得する

        チェックポイントより新しいメールが存在しない場合、空のリストを返却する。

        Returns:
            list[Mail]: チェックポイントメールよりも新しいメール一覧
        """
        return self._mailserverconnection.lastest_mail_over_than_arg_mail(self._checkpoint_mail)

    def monitoring_new_mails(self, func, interval_sec: int, timeout_sec: int) -> None:
        """チェックポイントメールよりも新しいメールが到着した場合にコールバック関数を実行する

        Args:
            func (function): 新しいメールが到着した場合に実行するコールバック関数
            interval_sec (int): 新しいメール到着確認間隔秒数
            timeout_sec (int): タイムアウト秒数

        Raises:
            MonitoringTimeoutException: 監視がタイムアウトした場合
        """
        import time

        start_time = time.time()
        while True:
            old_connection = self._mailserverconnection
            self._mailserverconnection = old_connection.create_new_mail_server_connection()
            old_connection.disconnect()

            new_mails = self.get_mails_over_than_checkpoint()
            if new_mails:
                is_fin = func(new_mails)
                # コールバック関数よりの終了指示があった場合、監視を終了
                if is_fin:
                    break
                # チェックポイントメールを最新のメールに更新
                # self._checkpoint_mail = new_mails[-1]

            # タイムアウト判定
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout_sec:
                raise MailMonitoringTimeoutException(
                    f"Mail Monitoring Timeout. timeout_sec={timeout_sec}")

            time.sleep(interval_sec)
